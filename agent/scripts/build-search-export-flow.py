"""Build caller-authenticated, paginated files/pages search and private XLSX delivery."""

import base64
import copy
import json
from pathlib import Path
import sys
import uuid
from urllib.parse import quote

from openpyxl import load_workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter
from openpyxl.workbook.properties import CalcProperties
from openpyxl.worksheet.table import Table, TableColumn, TableFormula, TableStyleInfo
from openpyxl.worksheet.filters import AutoFilter

from search_contract import CONTENT_SCOPE, load_policy, validate_policy


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "flows" / "search-export"
sys.path.insert(0, str(ROOT / "exports" / "template"))
from workbook_layout import HEADERS as EXPORT_HEADERS, HEADER_ROW, LINK_FORMAT

MAX_ROWS = 1000
MAX_CANDIDATES = 2000
PAGE_SIZE = 100
SITES_PER_BATCH = 20
MAX_BATCHES = 12
MAX_SEARCH_PAGES = 40
PREVIEW_ROWS = 10
PREVIEW_CANDIDATES = 20
SENTINEL = "__CORPNET_EMPTY_EXPORT__"
LINK_FORMULA = '=IF(SearchResults[[#This Row],[SourceURL]]="","",HYPERLINK(SearchResults[[#This Row],[SourceURL]],SearchResults[[#This Row],[SourceURL]]))'
HEADERS = list(EXPORT_HEADERS)
DATE_FIELDS = {"Created (UTC)": "CreatedUTC", "Modified (UTC)": "ModifiedUTC"}
DATE_FORMAT = "yyyy-mm-dd"
ALL_STATES = ["Succeeded", "Failed", "TimedOut", "Skipped"]
METADATA_KEYS = [
    "Query", "Scope", "RequestedBy", "GeneratedUTC", "CompletionStatus",
    "CountSemantics", "Sharing", "Snapshot", "Tags",
    "TextSafety", "JobId", "ExportedRowCount", "EstimatedIndexMatches",
    "UpstreamComplete", "WriterRowCap",
    "OmittedRowCount", "ProcessingErrors", "CompletionDetail",
    "TruncatedUpstream", "SourceTypes", "FileCount", "PageCount", "DuplicateIndexHits",
]


def after(*names, statuses=None):
    return {name: statuses or ["Succeeded"] for name in names}


def compose(value, *dependencies):
    return {"type": "Compose", "inputs": value, "runAfter": after(*dependencies)}


def set_var(name, value, *dependencies):
    return {"type": "SetVariable", "inputs": {"name": name, "value": value}, "runAfter": after(*dependencies)}


def increment(name, value=1, *dependencies):
    return {"type": "IncrementVariable", "inputs": {"name": name, "value": value}, "runAfter": after(*dependencies)}


def append(name, value, *dependencies):
    return {"type": "AppendToArrayVariable", "inputs": {"name": name, "value": value}, "runAfter": after(*dependencies)}


def condition(expression, actions, otherwise=None, dependencies=()):
    return {
        "type": "If", "expression": expression, "actions": actions,
        "else": {"actions": otherwise or {}}, "runAfter": after(*dependencies),
    }


def loop(items, actions, *dependencies):
    return {
        "type": "Foreach", "foreach": items, "actions": actions,
        "runtimeConfiguration": {"concurrency": {"repetitions": 1}},
        "runAfter": after(*dependencies),
    }


def op(connector, operation, parameters, *dependencies):
    return {
        "type": "OpenApiConnection",
        "inputs": {
            "host": {"apiId": "/providers/Microsoft.PowerApps/apis/" + connector,
                     "connectionName": connector, "operationId": operation},
            "parameters": parameters, "retryPolicy": {"type": "none"},
        },
        "runAfter": after(*dependencies),
    }


def sp(site, method, uri, *dependencies, body=None):
    parameters = {
        "dataset": site, "parameters/method": method, "parameters/uri": uri,
        "parameters/headers": {"Accept": "application/json;odata=nometadata"},
    }
    if body is not None:
        parameters["parameters/body"] = body
        parameters["parameters/headers"]["Content-Type"] = "application/json;odata=nometadata"
    return op("shared_sharepointonline", "HttpRequest", parameters, *dependencies)


def excel(operation, parameters=None, dependencies=(), table="SearchResults"):
    return op("shared_excelonlinebusiness", operation, {
        "source": "me", "drive": "@body('Personal_drive')?['id']",
        "file": "@last(split(variables('FileId'),'.'))", "table": table,
        **(parameters or {}),
    }, *dependencies)


def fail(code, message):
    return {"type": "Terminate", "inputs": {"runStatus": "Failed", "runError": {
        "code": code, "message": message,
    }}, "runAfter": {}}


def report_failure(name, code, message):
    notification = "Notify_" + name
    stopped = fail(code, message)
    stopped["runAfter"] = after(notification, statuses=ALL_STATES)
    return {
        notification: op("shared_office365", "SendEmailV2", {
            "emailMessage/To": "@body('Selected_profile')?['mail']",
            "emailMessage/Subject": "CorpNet search export could not be verified",
            "emailMessage/Body": "@concat('<p>Your search export could not be completed and verified. No finished workbook link is being reported.</p><p>Reason: "
                                 + code + ". Job reference: ',variables('JobId'),'. Please retry the search or contact the agent owner.</p>')",
            "emailMessage/Importance": "Normal",
        }),
        "Stop_" + name: stopped,
    }


def metadata_updates(name, pairs, *dependencies):
    return loop(pairs, {
        name + "_write": excel("PatchItem", {
            "idColumn": "Field", "id": "@item()?['Field']",
            "item": {"Value": "@concat(decodeUriComponent('%27'),string(item()?['Value']))"},
        }, table="ExportMetadata"),
    }, *dependencies)


def pairs(values):
    return [{"Field": key, "Value": value} for key, value in values.items()]


def compile_scopes(policy):
    validate_policy(policy)
    departments = {}
    seen = set()
    for site in policy["sites"]:
        identifier = str(uuid.UUID(site["siteId"]))
        if identifier in seen:
            raise ValueError("A site collection must appear only once in the approved inventory")
        seen.add(identifier)
        departments.setdefault(site["department"], []).append(identifier)
    inventory = {site["siteId"].lower(): site for site in policy["sites"]}
    inventories = {"All": list(inventory), **departments}
    scopes = {}
    for name, identifiers in inventories.items():
        batches = []
        for start in range(0, len(identifiers), SITES_PER_BATCH):
            group = identifiers[start:start + SITES_PER_BATCH]
            clause = "(" + " OR ".join(f'SiteID:"{identifier}"' for identifier in group) + ")"
            clause += " AND DepartmentId:" + policy["hubSiteCollectionId"]
            if len(clause) > policy["limits"]["scopeCharacters"]:
                raise ValueError("An approved site batch exceeds its scope budget")
            batches.append({"Kql": clause, "Sites": {identifier: inventory[identifier] for identifier in group}})
        if not batches or len(batches) > MAX_BATCHES:
            raise ValueError("Scope exceeds the bounded site-batch budget")
        scopes[name] = batches
    return scopes


def excel_date_formula(field):
    if field not in DATE_FIELDS.values():
        raise ValueError("Only canonical source timestamps can back display dates")
    source = f"SearchResults[[#This Row],[{field}]]"
    return (f'=IF({source}="","Not supplied",DATE(VALUE(LEFT({source},4)),'
            f'VALUE(MID({source},6,2)),VALUE(MID({source},9,2))))')


def metadata_formula(field):
    if field not in METADATA_KEYS:
        raise ValueError("Unknown export metadata field")
    lookup = f'INDEX(ExportMetadata[Value],MATCH("{field}",ExportMetadata[Field],0))'
    return f'IFERROR(IF({lookup}="","",{lookup}),"")'


def create_runtime_template():
    TARGET.mkdir(parents=True, exist_ok=True)
    book = load_workbook(ROOT / "exports" / "template" / "CorpNetSearchResults.template.xlsx")
    sheet = book["Results"]
    sheet.cell(HEADER_ROW + 1, 1, SENTINEL)
    table = sheet.tables["SearchResults"]
    for column, (label, field) in enumerate(DATE_FIELDS.items(), len(HEADERS) + 1):
        formula = excel_date_formula(field)
        sheet.cell(HEADER_ROW, column, label)._style = copy.copy(sheet.cell(HEADER_ROW, 5)._style)
        body = sheet.cell(HEADER_ROW + 1, column, formula)
        body._style = copy.copy(sheet.cell(HEADER_ROW + 1, 5)._style)
        body.number_format = DATE_FORMAT
        body.alignment = Alignment(vertical="top", wrap_text=False, indent=1)
        sheet.column_dimensions[get_column_letter(column)].width = 16
        sheet.cell(HEADER_ROW, column).comment = Comment(
            f"Real Excel UTC calendar date derived from hidden {field}. The full source timestamp remains unchanged there.",
            "CorpNet Search Hub",
        )
        table.tableColumns.append(TableColumn(
            id=column, name=label, calculatedColumnFormula=TableFormula(attr_text=formula[1:]),
        ))
    source_column = len(HEADERS) + len(DATE_FIELDS) + 1
    source_letter = get_column_letter(source_column)
    sheet.cell(HEADER_ROW, source_column, "SourceURL")
    sheet.cell(HEADER_ROW + 1, source_column)._style = copy.copy(sheet.cell(HEADER_ROW + 1, 6)._style)
    sheet.cell(HEADER_ROW + 1, source_column).number_format = "@"
    sheet.cell(HEADER_ROW + 1, source_column).alignment = Alignment(vertical="top", wrap_text=False)
    sheet.column_dimensions[source_letter].width = 80
    sheet.column_dimensions[source_letter].hidden = True
    for column in ("E", "H"):
        sheet.column_dimensions[column].hidden = True
    table.ref = f"A{HEADER_ROW}:{source_letter}{HEADER_ROW + 1}"
    table.autoFilter = AutoFilter(ref=table.ref)
    table.tableColumns.append(TableColumn(id=source_column, name="SourceURL"))
    table.tableColumns[6].calculatedColumnFormula = TableFormula(attr_text=LINK_FORMULA[1:])
    sheet.cell(HEADER_ROW + 1, 7, LINK_FORMULA)
    sheet.cell(HEADER_ROW + 1, 7).number_format = LINK_FORMAT
    visible_last = get_column_letter(source_column - 1)
    for area in list(sheet.merged_cells.ranges):
        if area.max_row <= 6:
            first = f"{get_column_letter(area.min_col)}{area.min_row}"
            last_row = area.max_row
            sheet.unmerge_cells(str(area))
            sheet.merge_cells(f"{first}:{visible_last}{last_row}")
    for row in (1, 2, 3):
        for column in range(len(HEADERS) + 1, source_column):
            sheet.cell(row, column)._style = copy.copy(sheet.cell(row, len(HEADERS))._style)
    sheet["A3"] = "PRIVATE SEARCH EXPORT | FILES AND PAGES"
    sheet["A4"], sheet["A5"] = "SEARCH", "RESULTS"
    sheet["B4"] = '="Scope: "&' + metadata_formula("Scope") + '&" | Query: "&' + metadata_formula("Query")
    sheet["B5"] = ('="Rows: "&' + metadata_formula("ExportedRowCount") + '&" | Files: "&'
                   + metadata_formula("FileCount") + '&" | Pages: "&' + metadata_formula("PageCount")
                   + '&" | Status: "&' + metadata_formula("CompletionStatus"))
    sheet["B4"].number_format = sheet["B5"].number_format = "General"
    sheet["A6"] = "Filter any column. Open file checks current access. Full timestamps are retained in hidden columns; details: ExportInfo."
    sheet.print_area = f"A1:{visible_last}{HEADER_ROW + 1}"
    book.calculation = CalcProperties(calcMode="auto", fullCalcOnLoad=True, forceFullCalc=True)
    info = book["ExportInfo"]
    for row in info:
        for cell in row:
            cell.value = None
    info["A1"], info["B1"] = "Field", "Value"
    for index, key in enumerate(METADATA_KEYS, 2):
        info.cell(index, 1, key)
        cell = info.cell(index, 2, "Not started" if key == "CompletionStatus" else "")
        cell.number_format = "@"
    if "ExportMetadata" in info.tables:
        del info.tables["ExportMetadata"]
    table = Table(displayName="ExportMetadata", ref=f"A1:B{len(METADATA_KEYS) + 1}")
    table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    info.add_table(table)
    path = TARGET / "RuntimeSearchResults.template.xlsx"
    book.save(path)
    book.close()
    return path.read_bytes()


def search_request(scope, start):
    return {
        "request": {
            "Querytext": "@concat('(', " + scope + ", ') AND (', outputs('Literal_query'), ') AND " + CONTENT_SCOPE + " AND (IsDocument:1 OR FileExtension:aspx)')",
            "RowLimit": PAGE_SIZE, "StartRow": start, "TrimDuplicates": False,
            "EnableQueryRules": False,
            "SelectProperties": ["SPWebUrl", "SiteID", "ListID", "ListItemID"],
        },
    }


def private_acl():
    return (
        "@and(equals(body('Private_file_acl')?['HasUniqueRoleAssignments'],true),"
        "equals(length(body('Private_file_acl')?['RoleAssignments']),1),"
        "equals(first(body('Private_file_acl')?['RoleAssignments'])?['Member']?['Id'],body('Personal_site_user')?['Id']),"
        "equals(first(first(body('Private_file_acl')?['RoleAssignments'])?['RoleDefinitionBindings'])?['RoleTypeKind'],5))"
    )


def row_export_actions(policy):
    row = "items('Each_verified_row')"
    item = {name: "@concat(decodeUriComponent('%27'),string(" + row + "?['" + name + "']))" for name in HEADERS}
    item["URL"] = LINK_FORMULA
    item["SourceURL"] = "@concat(decodeUriComponent('%27')," + row + "?['URL'])"
    item.update({label: excel_date_formula(field) for label, field in DATE_FIELDS.items()})
    write = condition("@equals(variables('Exported'),0)", {
        "Replace_placeholder": excel("PatchItem", {"idColumn": "Title", "id": SENTINEL, "item": item}),
    }, {
        "Append_result": excel("AddRowV2", {"item": item, "dateTimeFormat": "ISO 8601"}),
    })
    write["runAfter"] = after("Remember_verified_row")
    accepted = {
        "Remember_verified_row": append("ExpectedRows", "@" + row),
        "Write_result": write,
        "Remember_url": append("SeenUrls", "@toLower(" + row + "?['URL'])", "Write_result"),
        "Count_exported": increment("Exported", 1, "Remember_url"),
        "Count_content_type": condition(f"@endsWith(toLower({row}?['URL']),'.aspx')", {
            "Count_page": increment("PageCount"),
        }, {"Count_file": increment("FileCount")}, dependencies=("Count_exported",)),
        "Stop_after_write_error": set_var("StopExport", True),
    }
    accepted["Stop_after_write_error"]["runAfter"] = after("Write_result", statuses=["Failed", "TimedOut"])
    accepted["Count_write_error"] = increment("Failures", 1, "Stop_after_write_error")
    return {
        "Write_unique_result": condition(
            f"@and(not(contains(variables('SeenUrls'),toLower({row}?['URL']))),less(variables('Exported'),{MAX_ROWS}),equals(variables('StopExport'),false))",
            accepted,
            {"Duplicate_or_limit": condition(
                f"@contains(variables('SeenUrls'),toLower({row}?['URL']))",
                {"Count_duplicate": increment("Duplicates")},
                {"Mark_row_cap": set_var("Capped", True)},
            )},
        ),
    }


def export_batches(policy):
    cell = lambda name: f"xpath(xml(addProperty(json('{{}}'),'row',item())),'string(/row/Cells[translate(Key,\"ABCDEFGHIJKLMNOPQRSTUVWXYZ\",\"abcdefghijklmnopqrstuvwxyz\")=\"{name.lower()}\"]/Value)')"
    normalize_guid = lambda name: "toLower(replace(replace(" + cell(name) + ",'{',''),'}',''))"
    site = "variables('CurrentBatch')?['Sites']?[item()?['SiteId']]"
    group_site = "variables('CurrentBatch')?['Sites']?[items('Each_metadata_group')?['SiteId']]"
    invalid_guid = "item()?['ListId']"
    for character in "0123456789abcdef-":
        invalid_guid = f"replace({invalid_guid},'{character}','')"
    basic = (
        "@and(contains(variables('CurrentBatch')?['Sites'],item()?['SiteId']),"
        "equals(length(item()?['ListId']),36),empty(" + invalid_guid + "),"
        "equals(length(replace(item()?['ListId'],'-','')),32),equals(length(split(item()?['ListId'],'-')),5),"
        "isInt(item()?['ItemId']),startsWith(toLower(item()?['WebUrl']),'" + policy["tenantOrigin"].lower() + "/'),"
        "not(contains(item()?['WebUrl'],'?')),not(contains(item()?['WebUrl'],'#')))"
    )
    scoped = (
        "@and(greater(int(item()?['ItemId']),0),lessOrEquals(int(item()?['ItemId']),2147483647),"
        f"or(equals(toLower(item()?['WebUrl']),toLower({site}?['url'])),"
        f"startsWith(toLower(decodeUriComponent(uriPath(item()?['WebUrl']))),concat(toLower(decodeUriComponent(uriPath({site}?['url']))),'/'))))"
    )
    metadata = "item()"
    file = "item()?['File']"
    values = "item()"
    projection = {
        "Title": f"@if(empty({metadata}?['Title']),{file}?['Name'],{metadata}?['Title'])",
        "Department": f"@if(empty({values}?['Department']),{group_site}?['department'],{values}?['Department'])",
        "Tags": f"@coalesce({values}?['TopicTags'],'')",
        "Type": f"@if(endsWith(toLower({file}?['Name']),'.aspx'),'Page',if(empty({values}?['DocumentType']),toUpper(last(split({file}?['Name'],'.'))),{values}?['DocumentType']))",
        "ModifiedUTC": f"@coalesce({file}?['TimeLastModified'],'')",
        "SourceSite": f"@{group_site}?['url']",
        "URL": "@concat('" + policy["tenantOrigin"] + "',replace(replace(uriComponent(item()?['File']?['ServerRelativeUrl']),'%2F','/'),'%2f','/'))",
        "CreatedUTC": f"@coalesce({file}?['TimeCreated'],'')",
    }
    projection.update({label: "@" + display_date(f"{file}?['{source}']")
                       for label, source in (("Created (UTC)", "TimeCreated"), ("Modified (UTC)", "TimeLastModified"))})
    uri = (
        "@concat('_api/web/lists(guid',decodeUriComponent('%27'),items('Each_metadata_group')?['ListId'],decodeUriComponent('%27'),"
        f"')/items?$top={PAGE_SIZE}&$filter=',uriComponent(join(body('Group_filter_parts'),' or ')),"
        "'&$select=Id,Title,File/Name,File/ServerRelativeUrl,File/TimeLastModified,File/TimeCreated',"
        "if(empty(body('Metadata_field_names')),'',concat(',',join(body('Metadata_field_names'),','))),'&$expand=File')"
    )
    field_filter = quote("InternalName eq 'Department' or InternalName eq 'TopicTags' or InternalName eq 'DocumentType'", safe="")
    fields_uri = ("@concat('_api/web/lists(guid',decodeUriComponent('%27'),items('Each_metadata_group')?['ListId'],"
                  "decodeUriComponent('%27'),')/fields?$select=InternalName&$filter=" + field_filter + "')")
    groups = {
        "Group_candidates": {"type": "Query", "inputs": {
            "from": "@body('Scoped_locators')",
            "where": "@and(equals(item()?['SiteId'],items('Each_metadata_group')?['SiteId']),equals(item()?['ListId'],items('Each_metadata_group')?['ListId']),equals(item()?['WebUrl'],items('Each_metadata_group')?['WebUrl']))",
        }, "runAfter": {}},
        "Group_ids": {"type": "Select", "inputs": {"from": "@body('Group_candidates')", "select": "@int(item()?['ItemId'])"},
                      "runAfter": after("Group_candidates")},
        "Group_filter_parts": {"type": "Select", "inputs": {"from": "@body('Group_candidates')", "select": "@concat('Id eq ',string(int(item()?['ItemId'])))"},
                               "runAfter": after("Group_ids")},
        "Available_metadata_fields": sp("@items('Each_metadata_group')?['WebUrl']", "GET", fields_uri, "Group_filter_parts"),
        "Metadata_field_names": {"type": "Select", "inputs": {
            "from": "@body('Available_metadata_fields')?['value']", "select": "@item()?['InternalName']",
        }, "runAfter": after("Available_metadata_fields")},
        "Read_current_items": sp("@items('Each_metadata_group')?['WebUrl']", "GET", uri, "Metadata_field_names"),
        "Valid_current_items": {"type": "Query", "inputs": {
            "from": "@body('Read_current_items')?['value']",
            "where": f"@and(contains(body('Group_ids'),item()?['Id']),not(empty({file}?['ServerRelativeUrl'])),startsWith(toLower(coalesce({file}?['ServerRelativeUrl'],'')),concat(toLower(decodeUriComponent(uriPath({group_site}?['url']))),'/')))",
        }, "runAfter": after("Read_current_items")},
        "Count_unverified_ids": increment("Omitted", "@sub(length(union(body('Group_ids'),body('Group_ids'))),length(body('Valid_current_items')))", "Valid_current_items"),
        "Count_duplicate_ids": increment("Duplicates", "@sub(length(body('Group_ids')),length(union(body('Group_ids'),body('Group_ids'))))", "Count_unverified_ids"),
        "Select_verified_rows": {"type": "Select", "inputs": {"from": "@body('Valid_current_items')", "select": projection},
                                 "runAfter": after("Count_duplicate_ids")},
        "Each_verified_row": loop("@body('Select_verified_rows')", row_export_actions(policy), "Select_verified_rows"),
        "Count_group_failure": increment("Failures"),
        "Count_failed_items": increment("Omitted", "@length(union(body('Group_ids'),body('Group_ids')))", "Count_group_failure"),
        "Stop_failed_group": set_var("StopExport", True, "Count_failed_items"),
    }
    groups["Count_group_failure"]["runAfter"] = after("Read_current_items", statuses=["Failed", "TimedOut"])
    rows = {
        "Bounded_candidates": compose(f"@take(variables('PageRows'),max(0,sub({MAX_CANDIDATES},variables('Checked'))))"),
        "Count_checked": increment("Checked", "@length(outputs('Bounded_candidates'))", "Bounded_candidates"),
        "Detect_candidate_cap": condition("@less(length(outputs('Bounded_candidates')),length(variables('PageRows')))",
                                           {"Mark_candidate_cap": set_var("Capped", True)}, dependencies=("Count_checked",)),
        "Select_locators": {"type": "Select", "inputs": {
            "from": "@outputs('Bounded_candidates')",
            "select": {"WebUrl": "@" + cell("SPWebUrl"), "SiteId": "@" + normalize_guid("SiteID"),
                       "ListId": "@" + normalize_guid("ListID"), "ItemId": "@" + cell("ListItemID")},
        }, "runAfter": after("Detect_candidate_cap")},
        "Basic_locators": {"type": "Query", "inputs": {"from": "@body('Select_locators')", "where": basic}, "runAfter": after("Select_locators")},
        "Scoped_locators": {"type": "Query", "inputs": {"from": "@body('Basic_locators')", "where": scoped}, "runAfter": after("Basic_locators")},
        "Count_invalid_locators": increment("Omitted", "@sub(length(body('Select_locators')),length(body('Scoped_locators')))", "Scoped_locators"),
        "Metadata_groups": {"type": "Select", "inputs": {
            "from": "@body('Scoped_locators')", "select": {key: "@item()?['" + key + "']" for key in ("SiteId", "ListId", "WebUrl")},
        }, "runAfter": after("Count_invalid_locators")},
        "Distinct_metadata_groups": compose("@union(body('Metadata_groups'),body('Metadata_groups'))", "Metadata_groups"),
        "Each_metadata_group": loop("@outputs('Distinct_metadata_groups')", {
            "Group_budget": condition(f"@and(less(variables('Exported'),{MAX_ROWS}),equals(variables('StopExport'),false))",
                                      groups, {"Mark_group_cap": set_var("Capped", True)}),
        }, "Distinct_metadata_groups"),
        "Stop_page_processing_error": set_var("StopExport", True),
        "Count_processing_error": increment("Failures", 1, "Stop_page_processing_error"),
        "Advance_start": increment("PageStart", "@length(variables('PageRows'))"),
        "Count_processed_page": increment("ProcessedPages", 1, "Advance_start"),
    }
    rows["Stop_page_processing_error"]["runAfter"] = after("Each_metadata_group", statuses=["Failed", "TimedOut"])
    rows["Advance_start"]["runAfter"] = {"Each_metadata_group": ALL_STATES, "Count_processing_error": ["Succeeded", "Skipped"]}
    next_actions = {
        "Next_request": compose(search_request("variables('CurrentBatch')?['Kql']", "@variables('PageStart')")),
        "Next_search_page": sp(policy["searchSiteUrl"], "POST", "_api/search/postquery", "Next_request",
                               body="@string(outputs('Next_request'))"),
        "Next_page_valid": condition(
            "@not(equals(body('Next_search_page')?['PrimaryQueryResult']?['RelevantResults']?['Table']?['Rows'],null))",
            {"Use_next_page": set_var("PageRows", "@body('Next_search_page')?['PrimaryQueryResult']?['RelevantResults']?['Table']?['Rows']")},
            {"Count_bad_page": increment("Failures"), "Stop_bad_page": set_var("StopExport", True, "Count_bad_page")},
            dependencies=("Next_search_page",),
        ),
        "Count_page_failure": increment("Failures"),
        "Stop_failed_page": set_var("StopExport", True, "Count_page_failure"),
    }
    next_actions["Count_page_failure"]["runAfter"] = after("Next_search_page", statuses=["Failed", "TimedOut"])
    rows["Need_next_page"] = condition(
        f"@and(less(variables('PageStart'),variables('CurrentBatch')?['Total']),greater(length(variables('PageRows')),0),"
        f"less(variables('Exported'),{MAX_ROWS}),less(variables('Checked'),{MAX_CANDIDATES}),less(variables('ProcessedPages'),{MAX_SEARCH_PAGES}),equals(variables('StopExport'),false))",
        next_actions,
        {
            "Mark_remaining_matches": condition("@less(variables('PageStart'),variables('CurrentBatch')?['Total'])",
                                               {"Mark_page_cap": set_var("Capped", True)}),
            "Advance_batch": increment("BatchIndex", 1, "Mark_remaining_matches"),
            "More_batches": condition("@less(variables('BatchIndex'),length(variables('Batches')))", {
                "Use_next_batch": set_var("CurrentBatch", "@variables('Batches')[variables('BatchIndex')]"),
                "Use_batch_rows": set_var("PageRows", "@variables('CurrentBatch')?['Rows']", "Use_next_batch"),
                "Reset_page_offset": set_var("PageStart", 0, "Use_batch_rows"),
            }, dependencies=("Advance_batch",)),
        },
        dependencies=("Count_processed_page",),
    )
    return {
        "type": "Until",
        "expression": f"@or(greaterOrEquals(variables('BatchIndex'),length(variables('Batches'))),greaterOrEquals(variables('Exported'),{MAX_ROWS}),greaterOrEquals(variables('Checked'),{MAX_CANDIDATES}),greaterOrEquals(variables('ProcessedPages'),{MAX_SEARCH_PAGES}),equals(variables('StopExport'),true))",
        "limit": {"count": MAX_SEARCH_PAGES + 1, "timeout": "PT45M"}, "actions": rows,
        "runAfter": after("Load_first_page"),
    }


def markdown_text(expression):
    text = f"string(coalesce({expression},''))"
    text = f"replace(replace({text},decodeUriComponent('%0D'),' '),decodeUriComponent('%0A'),' ')"
    text = f"replace({text},decodeUriComponent('%5C'),concat(decodeUriComponent('%5C'),decodeUriComponent('%5C')))"
    for character in ("|", "[", "]", "*", "_", "`", "~", "!", "(", ")"):
        text = f"replace({text},'{character}',concat(decodeUriComponent('%5C'),'{character}'))"
    return f"replace(replace({text},'<','&lt;'),'>','&gt;')"


def display_date(value):
    return f"if(empty({value}),'Not supplied',formatDateTime({value},'yyyy-MM-dd'))"


def written_date(label):
    if label not in DATE_FIELDS:
        raise ValueError("Unknown display date")
    value = f"string(coalesce(item()?['{label}'],''))"
    serial = f"addDays('1899-12-30T00:00:00Z',int(first(split({value},'.'))),'yyyy-MM-dd')"
    return (f"if(or(empty({value}),equals({value},'Not supplied')),{value},"
            f"if(isFloat({value}),{serial},formatDateTime({value},'yyyy-MM-dd')))")


def preview_date(field):
    if field not in ("CreatedUTC", "ModifiedUTC"):
        raise ValueError("Only verified source dates can be formatted")
    value = f"outputs('Preview_row')?['{field}']"
    return display_date(value)


def preview_actions(policy):
    retrieval = export_batches(policy)["actions"]
    locators = copy.deepcopy(retrieval["Select_locators"])
    locators["inputs"]["from"] = "@items('Preview_batches')?['Rows']"
    locators["runAfter"] = {}
    basic = copy.deepcopy(retrieval["Basic_locators"])
    basic["inputs"]["from"] = "@body('Preview_locators')"
    basic["inputs"]["where"] = basic["inputs"]["where"].replace("variables('CurrentBatch')", "items('Preview_batches')")
    basic["runAfter"] = after("Preview_locators")
    scoped = copy.deepcopy(retrieval["Scoped_locators"])
    scoped["inputs"]["from"] = "@body('Preview_basic_locators')"
    scoped["inputs"]["where"] = scoped["inputs"]["where"].replace("variables('CurrentBatch')", "items('Preview_batches')")
    scoped["runAfter"] = after("Preview_basic_locators")
    candidate = "items('Each_preview_candidate')"
    site = "items('Preview_batches')?['Sites']?[" + candidate + "?['SiteId']]"
    current = "body('Read_preview_item')"
    file = current + "?['File']"
    url = "concat('" + policy["tenantOrigin"] + "',replace(replace(uriComponent(coalesce(" + file + "?['ServerRelativeUrl'],'')),'%2F','/'),'%2f','/'))"
    row = {
        "Title": f"@if(empty({current}?['Title']),{file}?['Name'],{current}?['Title'])",
        "Tags": f"@coalesce({current}?['TopicTags'],'')",
        "Type": f"@if(endsWith(toLower({file}?['Name']),'.aspx'),'Page',if(empty({current}?['DocumentType']),toUpper(last(split({file}?['Name'],'.'))),{current}?['DocumentType']))",
        "ModifiedUTC": f"@coalesce({file}?['TimeLastModified'],'')",
        "CreatedUTC": f"@coalesce({file}?['TimeCreated'],'')",
        "URL": "@" + url,
    }
    fields = quote("InternalName eq 'Department' or InternalName eq 'TopicTags' or InternalName eq 'DocumentType'", safe="")
    fields_uri = "@concat('_api/web/lists(guid',decodeUriComponent('%27')," + candidate + "?['ListId'],decodeUriComponent('%27'),')/fields?$select=InternalName&$filter=" + fields + "')"
    item_uri = (
        "@concat('_api/web/lists(guid',decodeUriComponent('%27')," + candidate + "?['ListId'],decodeUriComponent('%27'),')/items(',string(int("
        + candidate + "?['ItemId'])),')?$select=Id,Title,File/Name,File/ServerRelativeUrl,File/TimeLastModified,File/TimeCreated',"
        "if(empty(body('Preview_field_names')),'',concat(',',join(body('Preview_field_names'),','))),'&$expand=File')"
    )
    title = markdown_text("outputs('Preview_row')?['Title']")
    tags = "if(empty(outputs('Preview_row')?['Tags']),'Not supplied',replace(string(outputs('Preview_row')?['Tags']),';','; '))"
    short_tags = f"if(greater(length({tags}),200),concat(take({tags},200),'... (full tags in Excel)'),{tags})"
    line = ("@concat('| ['," + title + ",'](',outputs('Preview_row')?['URL'],') | ',"
            + preview_date("CreatedUTC") + ",' | '," + preview_date("ModifiedUTC")
            + ",' | '," + markdown_text(short_tags) + ",' |')")
    read = {
        "Count_preview_checked": increment("PreviewChecked"),
        "Preview_metadata_fields": sp("@" + candidate + "?['WebUrl']", "GET", fields_uri, "Count_preview_checked"),
        "Preview_field_names": {"type": "Select", "inputs": {
            "from": "@body('Preview_metadata_fields')?['value']", "select": "@item()?['InternalName']",
        }, "runAfter": after("Preview_metadata_fields")},
        "Read_preview_item": sp("@" + candidate + "?['WebUrl']", "GET", item_uri, "Preview_field_names"),
        "Preview_item_verified": condition(
            f"@and(equals({current}?['Id'],int({candidate}?['ItemId'])),not(empty({file}?['ServerRelativeUrl'])),"
            f"startsWith(toLower(coalesce({file}?['ServerRelativeUrl'],'')),concat(toLower(decodeUriComponent(uriPath({site}?['url']))),'/')),"
            f"not(contains(variables('PreviewUrls'),toLower({url}))))",
            {
                "Preview_row": compose(row),
                "Remember_preview_row": append("PreviewRows", "@outputs('Preview_row')", "Preview_row"),
                "Remember_preview_url": append("PreviewUrls", "@toLower(outputs('Preview_row')?['URL'])", "Remember_preview_row"),
                "Remember_preview_line": append("PreviewLines", line, "Remember_preview_url"),
            },
            dependencies=("Read_preview_item",),
        ),
    }
    batch = {
        "Preview_locators": locators, "Preview_basic_locators": basic, "Preview_scoped_locators": scoped,
        "Each_preview_candidate": loop(
            f"@take(body('Preview_scoped_locators'),max(0,sub({PREVIEW_CANDIDATES},variables('PreviewChecked'))))",
            {"Preview_candidate_budget": condition(
                f"@and(less(length(variables('PreviewRows')),{PREVIEW_ROWS}),less(variables('PreviewChecked'),{PREVIEW_CANDIDATES}))",
                read,
            )}, "Preview_scoped_locators",
        ),
    }
    return condition("@equals(variables('Started'),true)", {
        "Preview_batches": loop("@variables('Batches')", {
            "Preview_batch_budget": condition(
                f"@and(less(length(variables('PreviewRows')),{PREVIEW_ROWS}),less(variables('PreviewChecked'),{PREVIEW_CANDIDATES}))",
                batch,
            ),
        }),
    })


def finalize_actions():
    verify = {
        "Read_written_page": excel("GetItems", {"$top": 250, "$skip": "@variables('VerifyStart')", "dateTimeFormat": "ISO 8601"}),
        "Combine_written_rows": compose("@union(variables('ActualRows'),body('Read_written_page')?['value'])", "Read_written_page"),
        "Remember_written_rows": set_var("ActualRows", "@outputs('Combine_written_rows')", "Combine_written_rows"),
        "Advance_verification": increment("VerifyStart", "@length(body('Read_written_page')?['value'])", "Remember_written_rows"),
        "More_written_rows": set_var("VerifyMore", "@equals(length(body('Read_written_page')?['value']),250)", "Advance_verification"),
    }
    completion = "@if(or(variables('Capped'),greater(variables('Failures'),0),greater(variables('Omitted'),0),variables('StopExport')),'Partial','Complete')"
    final_values = pairs({
        "CompletionStatus": completion,
        "ExportedRowCount": "@variables('Exported')",
        "FileCount": "@variables('FileCount')", "PageCount": "@variables('PageCount')",
        "OmittedRowCount": "@variables('Omitted')", "ProcessingErrors": "@greater(variables('Failures'),0)",
        "DuplicateIndexHits": "@variables('Duplicates')", "TruncatedUpstream": "@variables('Capped')",
        "UpstreamComplete": "@not(or(variables('Capped'),greater(variables('Failures'),0),greater(variables('Omitted'),0),variables('StopExport')))",
        "CountSemantics": "@concat(string(variables('Exported')),' actual verified workbook rows. Index estimate: ',string(variables('IndexTotal')),'. These counts are not interchangeable.')",
        "CompletionDetail": f"@concat('Files: ',string(variables('FileCount')),'. Pages: ',string(variables('PageCount')),'. Unverified/omitted: ',string(variables('Omitted')),'. Processing errors: ',string(greater(variables('Failures'),0)),'. Export cap: {MAX_ROWS}; candidate cap: {MAX_CANDIDATES}; search-page cap: {MAX_SEARCH_PAGES}. Truncated: ',string(variables('Capped')),'.')",
    })
    valid = (
        "@and(equals(length(variables('ActualRows')),variables('Exported')),"
        "equals(length(union(body('Written_urls'),body('Written_urls'))),variables('Exported')),"
        "equals(length(intersection(body('Written_projection'),variables('ExpectedRows'))),variables('Exported')))"
    )
    return {
        "Incomplete_batches": condition("@less(variables('BatchIndex'),length(variables('Batches')))",
                                        {"Mark_incomplete_batches": set_var("Capped", True)}),
        "Remove_unused_placeholder": condition("@equals(variables('Exported'),0)", {
            "Delete_empty_placeholder": excel("DeleteItem", {"idColumn": "Title", "id": SENTINEL}),
        }, dependencies=("Incomplete_batches",)),
        "Read_back_written_rows": {
            "type": "Until", "expression": f"@or(equals(variables('VerifyMore'),false),greater(length(variables('ActualRows')),{MAX_ROWS}))",
            "limit": {"count": 6, "timeout": "PT5M"}, "actions": verify,
            "runAfter": after("Remove_unused_placeholder"),
        },
        "Written_projection": {"type": "Select", "inputs": {
            "from": "@variables('ActualRows')",
            "select": {**{key: "@coalesce(item()?['" + key + "'],'')" for key in HEADERS},
                       **{label: "@" + written_date(label) for label in DATE_FIELDS}},
        }, "runAfter": after("Read_back_written_rows")},
        "Written_urls": {"type": "Select", "inputs": {"from": "@variables('ActualRows')", "select": "@toLower(item()?['URL'])"},
                         "runAfter": after("Written_projection")},
        "Written_rows_verified": condition(valid, {
            "Complete_metadata_values": compose(final_values),
            "Complete_metadata": metadata_updates("Complete_metadata", "@outputs('Complete_metadata_values')", "Complete_metadata_values"),
            "Final_file_acl": sp("@body('SharePoint_profile')?['PersonalUrl']", "GET",
                                 "@concat(outputs('Report_item_uri'),'/RoleAssignments?$select=Member/Id,RoleDefinitionBindings/RoleTypeKind&$expand=Member,RoleDefinitionBindings')",
                                 "Complete_metadata"),
            "Delivery_acl_verified": condition(
                "@and(equals(length(body('Final_file_acl')?['value']),1),equals(first(body('Final_file_acl')?['value'])?['Member']?['Id'],body('Personal_site_user')?['Id']),equals(first(first(body('Final_file_acl')?['value'])?['RoleDefinitionBindings'])?['RoleTypeKind'],5))",
                {"Send_private_workbook": op("shared_office365", "SendEmailV2", {
                    "emailMessage/To": "@body('Selected_profile')?['mail']",
                    "emailMessage/Subject": "@concat('CorpNet search: ',string(variables('Exported')),' files/pages - ',triggerBody()?['scope'])",
                    "emailMessage/Body": "@concat('<p>Your CorpNet search export is ready.</p><p><strong>',string(variables('Exported')),' actual results: ',string(variables('FileCount')),' files and ',string(variables('PageCount')),' pages.</strong></p><p>Status: ',if(or(variables('Capped'),greater(variables('Failures'),0),greater(variables('Omitted'),0),variables('StopExport')),'PARTIAL - not all matches','Complete for the retrieved results'),'. Index estimate: ',string(variables('IndexTotal')),'. Omitted/unverified: ',string(variables('Omitted')),'.</p><p><a href=\"',variables('ReportUrl'),'\">Open your private, filterable workbook</a></p><p>Source links and stored tags are in the workbook. Source permissions still apply. Limits and completion details are on ExportInfo.</p>')",
                    "emailMessage/Importance": "Normal",
                })},
                report_failure("changed_acl", "ReportPrivacyChanged", "No workbook link sent: private access changed."),
                dependencies=("Final_file_acl",),
            ),
        }, report_failure("unverified_output", "WorkbookVerificationFailed", "No workbook link sent: actual rows do not match verified source records."),
           dependencies=("Written_urls",)),
    }


def build_definition(policy, template_bytes):
    scopes = compile_scopes(policy)
    variables = [
        ("Result", "string", "The search/export could not be started. No successful export or email is being reported."),
        ("JobId", "string", "@guid()"), ("IndexTotal", "integer", 0),
        ("Exported", "integer", 0), ("FileCount", "integer", 0), ("PageCount", "integer", 0),
        ("Checked", "integer", 0), ("Omitted", "integer", 0), ("Failures", "integer", 0),
        ("Duplicates", "integer", 0), ("Capped", "boolean", False), ("StopExport", "boolean", False),
        ("Started", "boolean", False), ("Batches", "array", []), ("PageRows", "array", []),
        ("CurrentBatch", "object", {}), ("BatchIndex", "integer", 0), ("ProcessedPages", "integer", 0),
        ("PageStart", "integer", 0), ("SeenUrls", "array", []),
        ("ExpectedRows", "array", []), ("ActualRows", "array", []),
        ("VerifyStart", "integer", 0), ("VerifyMore", "boolean", True),
        ("FileId", "string", ""), ("ReportUrl", "string", ""),
        ("PreviewRows", "array", []), ("PreviewUrls", "array", []),
        ("PreviewLines", "array", []), ("PreviewChecked", "integer", 0),
    ]
    actions = {}
    previous = None
    for name, kind, value in variables:
        key = "Initialize_" + name
        actions[key] = {"type": "InitializeVariable", "inputs": {"variables": [{"name": name, "type": kind, "value": value}]},
                        "runAfter": after(previous) if previous else {}}
        previous = key
    query = "trim(coalesce(triggerBody()?['query'],''))"
    total = "body('Initial_search')?['PrimaryQueryResult']?['RelevantResults']?['TotalRows']"
    initial_rows = "body('Initial_search')?['PrimaryQueryResult']?['RelevantResults']?['Table']?['Rows']"
    index = loop("@outputs('Approved_scopes')[triggerBody()?['scope']]", {
        "Initial_request": compose(search_request("item()?['Kql']", 0)),
        "Initial_search": sp(policy["searchSiteUrl"], "POST", "_api/search/postquery", "Initial_request",
                             body="@string(outputs('Initial_request'))"),
        "Initial_response_valid": condition(f"@and(not(equals({total},null)),not(equals({initial_rows},null)))", {
            "Count_index_matches": increment("IndexTotal", "@" + total),
            "Remember_batch": append("Batches", {"Kql": "@items('Read_index_batches')?['Kql']", "Sites": "@items('Read_index_batches')?['Sites']", "Total": "@" + total, "Rows": "@" + initial_rows},
                                     "Count_index_matches"),
        }, {"Count_bad_index": increment("Failures")},
           dependencies=("Initial_search",)),
    })
    initial_meta = pairs({
        "Query": "@" + query, "Scope": "@triggerBody()?['scope']",
        "RequestedBy": "@body('Selected_profile')?['mail']", "GeneratedUTC": "@utcNow()",
        "CompletionStatus": "Running", "JobId": "@variables('JobId')",
        "ExportedRowCount": "0", "EstimatedIndexMatches": "@variables('IndexTotal')",
        "WriterRowCap": str(MAX_ROWS), "SourceTypes": "Files and SharePoint pages",
        "Snapshot": "Each source is permission-checked before its row is written. Original links remain subject to current SharePoint access.",
        "Sharing": "Private to the verified source/profile/OneDrive account; no sharing link created.",
        "Tags": "Stored source values; use Text Filters > Contains for semicolon-delimited tags.",
        "TextSafety": "Source strings are literal; only controlled source-link HYPERLINK formulas are written.",
    })
    report_url = "@concat('" + policy["tenantOrigin"].replace(".sharepoint.com", "-my.sharepoint.com") + "',replace(uriComponent(decodeUriComponent(uriPath(body('Personal_drive')?['webUrl']))),'%2F','/'),'/CorpNetSearchResults-',variables('JobId'),'.xlsx')"
    report_uri = "@concat('_api/web/GetFileByServerRelativePath(decodedurl=',decodeUriComponent('%27'),replace(decodeUriComponent(uriPath(variables('ReportUrl'))),decodeUriComponent('%27'),concat(decodeUriComponent('%27'),decodeUriComponent('%27'))),decodeUriComponent('%27'),')/ListItemAllFields')"
    create = {
        "Create_blank_report": op("shared_onedriveforbusiness", "CreateFile", {
            "folderPath": "/", "name": "@concat('CorpNetSearchResults-',variables('JobId'),'.xlsx')",
            "body": {"$content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     "$content": base64.b64encode(template_bytes).decode()},
        }),
        "Remember_file_id": set_var("FileId", "@body('Create_blank_report')?['Id']", "Create_blank_report"),
        "Remember_report_url": set_var("ReportUrl", report_url, "Remember_file_id"),
        "Report_item_uri": compose(report_uri, "Remember_report_url"),
        "Make_report_private": sp("@body('SharePoint_profile')?['PersonalUrl']", "POST",
                                  "@concat(outputs('Report_item_uri'),'/breakroleinheritance(copyRoleAssignments=false,clearSubscopes=true)')",
                                  "Report_item_uri"),
        "Private_file_acl": sp("@body('SharePoint_profile')?['PersonalUrl']", "GET",
                               "@concat(outputs('Report_item_uri'),'?$select=HasUniqueRoleAssignments,RoleAssignments/Member/Id,RoleAssignments/RoleDefinitionBindings/RoleTypeKind&$expand=RoleAssignments/Member,RoleAssignments/RoleDefinitionBindings')",
                               "Make_report_private"),
        "Private_report_verified": condition(private_acl(), {
            "Initial_metadata_values": compose(initial_meta),
            "Initial_metadata": metadata_updates("Initial_metadata", "@outputs('Initial_metadata_values')", "Initial_metadata_values"),
            "Mark_started": set_var("Started", True, "Initial_metadata"),
            "Set_started_result": set_var("Result",
                "@concat('SharePoint reports ',string(variables('IndexTotal')),' indexed files and pages in ',triggerBody()?['scope'],'. Your private Excel export is running; its link will be emailed to ',body('Selected_profile')?['mail'],'.')",
                "Mark_started"),
        }, {"Stop_nonprivate_report": fail("PrivateOutputUnverified", "No source rows written: private output permissions could not be verified.")},
           dependencies=("Private_file_acl",)),
    }
    account_expression = (
        "@and(not(empty(body('Selected_profile')?['id'])),not(empty(body('Selected_profile')?['mail'])),"
        "not(contains(body('Selected_profile')?['mail'],';')),not(contains(body('Selected_profile')?['mail'],',')),"
        "equals(body('Selected_profile')?['id'],body('Source_directory_profile')?['id']),"
        "equals(body('Selected_profile')?['id'],body('Personal_drive')?['owner']?['user']?['id']),"
        "not(empty(body('Personal_drive')?['id'])),"
        "startsWith(body('OneDrive_root')?['Id'],concat(body('Personal_drive')?['id'],'.')))"
    )
    aligned = {
        "Read_index_batches": index,
        "Matching_content": condition("@and(equals(variables('Failures'),0),greater(variables('IndexTotal'),0))", create, {
            "Set_no_export_result": set_var("Result", "@if(greater(variables('Failures'),0),'No export was started: a SharePoint result batch was unusable. No completed export or email is being reported.',concat('No matching files or pages were found in ',triggerBody()?['scope'],'. No workbook or email was created.'))"),
        }, dependencies=("Read_index_batches",)),
    }
    personal = {
        "Personal_drive": sp("@body('SharePoint_profile')?['PersonalUrl']", "GET", "_api/v2.0/drive?$select=id,owner,webUrl"),
        "Personal_site_user": sp("@body('SharePoint_profile')?['PersonalUrl']", "GET", "_api/web/currentuser?$select=Id,LoginName"),
        "Source_directory_profile": op("shared_office365users", "UserProfile_V2", {
            "id": "@last(split(body('SharePoint_profile')?['AccountName'],'|'))", "$select": "id,mail,userPrincipalName",
        }),
        "Accounts_aligned": condition(account_expression, aligned, {
            "Set_account_mismatch": set_var("Result", "No search/export was started: the selected SharePoint, profile and OneDrive accounts do not match, or the directory mailbox is missing."),
        }, dependencies=("Personal_drive", "Personal_site_user", "Source_directory_profile")),
    }
    valid = {
        "Literal_tokens": {"type": "Select", "inputs": {"from": "@body('Keyword_tokens')", "select": "@concat('\"',item(),'\"')"}, "runAfter": {}},
        "Literal_query": compose("@if(equals(" + query + ",'*'),'*',join(body('Literal_tokens'),' AND '))", "Literal_tokens"),
        "Selected_profile": op("shared_office365users", "MyProfile_V2", {"$select": "id,mail,userPrincipalName"}, "Literal_query"),
        "SharePoint_profile": sp(policy["searchSiteUrl"], "GET", "_api/SP.UserProfiles.PeopleManager/GetMyProperties?$select=PersonalUrl,AccountName", "Literal_query"),
        "OneDrive_root": op("shared_onedriveforbusiness", "GetFileMetadataByPath", {"path": "/"}, "Literal_query"),
        "Personal_site_available": condition(
            "@startsWith(toLower(coalesce(body('SharePoint_profile')?['PersonalUrl'],'')),'"
            + policy["tenantOrigin"].replace(".sharepoint.com", "-my.sharepoint.com").lower() + "/personal/')",
            personal,
            {"Set_no_onedrive": set_var("Result", "No export was started: a personal OneDrive site for your SharePoint account could not be verified.")},
            dependencies=("Selected_profile", "SharePoint_profile", "OneDrive_root"),
        ),
    }
    startup = {
        "Approved_scopes": compose(scopes),
        "Invalid_characters": {"type": "Query", "inputs": {
            "from": f"@range(0,min(length({query}),161))",
            "where": f"@not(contains('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 -',substring({query},item(),1)))",
        }, "runAfter": after("Approved_scopes")},
        "Keyword_tokens": {"type": "Query", "inputs": {"from": f"@split(replace({query},'-',' '),' ')", "where": "@not(empty(item()))"},
                           "runAfter": after("Invalid_characters")},
        "Valid_input": condition(
            f"@and(contains(outputs('Approved_scopes'),coalesce(triggerBody()?['scope'],'')),greater(length({query}),0),lessOrEquals(length({query}),160),"
            f"or(equals({query},'*'),and(empty(body('Invalid_characters')),greater(length(body('Keyword_tokens')),0),lessOrEquals(length(body('Keyword_tokens')),12))))",
            valid, {"Set_invalid_input": set_var("Result", "No search was run. Choose All, CorpNet, HR, Finance or IT and up to 12 plain words (160 characters), or a single *.")},
            dependencies=("Keyword_tokens",),
        ),
    }
    actions["Start_search_export"] = {"type": "Scope", "actions": startup, "runAfter": after(previous)}
    actions["Startup_failure"] = set_var("Result", "The search/export could not be started. Check your own SharePoint, profile, OneDrive and Excel connections. No completed export or email is being reported.")
    actions["Startup_failure"]["runAfter"] = after("Start_search_export", statuses=["Failed", "TimedOut"])
    actions["Build_chat_preview"] = preview_actions(policy)
    actions["Build_chat_preview"]["runAfter"] = {"Start_search_export": ALL_STATES, "Startup_failure": ["Succeeded", "Skipped"]}
    actions["Format_chat_result"] = compose(
        "@if(and(equals(variables('Started'),true),greater(length(variables('PreviewRows')),0)),"
        "concat('## 🔎 SharePoint results',decodeUriComponent('%0A%0A'),"
        "'**Scope:** ',triggerBody()?['scope'],' · **Index estimate:** ',string(variables('IndexTotal')),decodeUriComponent('%0A%0A'),"
        "'> 📄 **Private Excel export started**',decodeUriComponent('%0A'),"
        "'> **Verified recipient:** '," + markdown_text("body('Selected_profile')?['mail']") + ",decodeUriComponent('%0A'),"
        "'> Delivery is pending. A private workbook link will be emailed only after row and access verification.',decodeUriComponent('%0A%0A'),"
        "'### Verified matches',decodeUriComponent('%0A%0A'),"
        "'Created and last modified dates are UTC (YYYY-MM-DD).',decodeUriComponent('%0A%0A'),"
        "'| File or page | Created (UTC) | Modified (UTC) | Stored tags |',decodeUriComponent('%0A'),"
        "'| --- | --- | --- | --- |',decodeUriComponent('%0A'),join(variables('PreviewLines'),decodeUriComponent('%0A')),"
        "decodeUriComponent('%0A%0A'),'---',decodeUriComponent('%0A%0A'),"
        f"'**Preview:** up to {PREVIEW_ROWS} results from at most {PREVIEW_CANDIDATES} checked candidates.',decodeUriComponent('%0A'),"
        f"'**Export bounds:** {MAX_ROWS} rows · {MAX_CANDIDATES} candidates · {MAX_SEARCH_PAGES} search pages · {MAX_BATCHES} batches of {SITES_PER_BATCH} sites.',decodeUriComponent('%0A%0A'),"
        "'Source permissions still apply. Excel includes these matches and the remaining verified results within those bounds. Exports may be partial; the index estimate can differ from the final exported-row count. Completion and omission details are recorded in Excel.'),"
        "concat(variables('Result'),if(equals(variables('Started'),true),"
        "concat(decodeUriComponent('%0A%0A'),'A verified chat preview is unavailable. The private export will still verify its results before delivery.'),'')))"
    )
    actions["Format_chat_result"]["runAfter"] = after("Build_chat_preview", statuses=ALL_STATES)
    actions["Respond_to_agent"] = {
        "type": "Response", "kind": "Skills",
        "inputs": {"statusCode": 200, "body": {"result": "@outputs('Format_chat_result')"},
                   "schema": {"type": "object", "properties": {"result": {"type": "string", "title": "Search/export status", "x-ms-content-hint": "TEXT"}}}},
        "runAfter": after("Format_chat_result"),
    }
    export = {
        "Load_first_batch": set_var("CurrentBatch", "@first(variables('Batches'))"),
        "Load_first_page": set_var("PageRows", "@variables('CurrentBatch')?['Rows']", "Load_first_batch"),
        "Export_rows": export_batches(policy),
        "Count_export_failure": increment("Failures"),
        "Finalize_workbook": {"type": "Scope", "actions": finalize_actions(),
                              "runAfter": {"Export_rows": ALL_STATES, "Count_export_failure": ["Succeeded", "Skipped"]}},
        "Notify_export_failure": op("shared_office365", "SendEmailV2", {
            "emailMessage/To": "@body('Selected_profile')?['mail']",
            "emailMessage/Subject": "CorpNet search export could not be completed",
            "emailMessage/Body": "@concat('<p>Your search export could not be completed and verified. No finished workbook link is being reported.</p><p>Job reference: ',variables('JobId'),'. Please retry your search or ask the agent owner to check the failed run.</p>')",
            "emailMessage/Importance": "Normal",
        }),
    }
    export["Count_export_failure"]["runAfter"] = after("Export_rows", statuses=["Failed", "TimedOut"])
    export["Notify_export_failure"]["runAfter"] = after("Finalize_workbook", statuses=["Failed", "TimedOut"])
    actions["Continue_private_export"] = condition("@equals(variables('Started'),true)", export, dependencies=("Respond_to_agent",))
    return {
        "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
        "contentVersion": "1.0.0.0", "metadata": {"defaultToEmbeddedConnections": False},
        "parameters": {"$authentication": {"type": "SecureObject", "defaultValue": {}},
                       "$connections": {"type": "Object", "defaultValue": {}}},
        "triggers": {"manual": {"type": "Request", "kind": "Skills", "inputs": {"schema": {
            "type": "object", "properties": {
                "query": {"title": "Search words", "type": "string", "x-ms-content-hint": "TEXT"},
                "scope": {"title": "Department", "type": "string", "x-ms-content-hint": "TEXT"},
            }, "required": ["query", "scope"],
        }}}},
        "actions": actions, "outputs": {},
    }


def connection_references():
    references = json.loads((ROOT / "runtime" / "connection-references.json").read_text(encoding="utf-8"))
    expected = {
        "shared_sharepointonline", "shared_office365users", "shared_onedriveforbusiness",
        "shared_excelonlinebusiness", "shared_office365",
    }
    if set(references) != expected:
        raise ValueError("All five caller-provided connector references are required")
    for connector, reference in references.items():
        if (
            reference.get("runtimeSource") != "invoker"
            or reference.get("api") != {"name": connector}
            or not reference.get("connection", {}).get("name")
            or not reference.get("connection", {}).get("connectionReferenceLogicalName")
        ):
            raise ValueError("Every connector must retain its API shape and Invoker-only binding")
    return references


if __name__ == "__main__":
    policy = load_policy()
    references = connection_references()
    template = create_runtime_template()
    definition = build_definition(policy, template)
    (TARGET / "definition.json").write_text(json.dumps(definition, indent=2) + "\n", encoding="utf-8")
    (TARGET / "connection-references.json").write_text(json.dumps(references, indent=2) + "\n", encoding="utf-8")
    print(f"Built files/pages search and private export: {MAX_ROWS} rows, {MAX_CANDIDATES} candidates, {MAX_BATCHES} site batches. No cloud changes.")
