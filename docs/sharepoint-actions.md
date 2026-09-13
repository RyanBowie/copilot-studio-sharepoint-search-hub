# SharePoint action request reference

Generated from the current portable flow by `scripts/build_site.py`.
Descriptions are maintained in `site/sharepoint-actions.json`; request JSON is read directly from source.
All 12 definitions use SharePoint **Send an HTTP request to SharePoint** (`HttpRequest`).
Loops can call an action repeatedly; this is not a count of requests in one run.
Contoso addresses and zero-pattern site IDs are placeholders, not live settings.

[On-page request catalogue](https://ryanbowie.github.io/copilot-studio-sharepoint-search-hub/#sharepoint-actions) · [Complete definition](../agent/flows/search-export/definition.json) · [New-tenant setup](setup.md#from-an-empty-sharepoint-tenant)

## Actual portable All-scope KQL

```text
(SiteID:"00000000-0000-4000-8000-000000000001" OR SiteID:"00000000-0000-4000-8000-000000000002" OR SiteID:"00000000-0000-4000-8000-000000000003" OR SiteID:"00000000-0000-4000-8000-000000000004") AND DepartmentId:00000000-0000-4000-8000-000000000001
```

## SharePoint_profile

Resolve the effective SharePoint connector account's personal-site URL and claims account name from the configured corporate site. This is the SharePoint connector's identity, not a directory identity supplied by the chat channel.

**Response use:** PersonalUrl feeds Personal_site_available, which checks the configured personal-site URL prefix before using it as a Site Address. AccountName is split at the final | by Source_directory_profile, an Office 365 Users action, to resolve the source directory profile for account alignment.

**Boundaries:** A GET with no body. The configured Contoso corporate site and personal-site prefix are portable placeholders requiring coordinated replacement. Failed startup processing reaches Startup_failure; there is no unscoped search fallback.

**Source JSON pointer:** `/actions/Start_search_export/actions/Valid_input/actions/SharePoint_profile`

```json
{
  "type": "OpenApiConnection",
  "inputs": {
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
      "connectionName": "shared_sharepointonline",
      "operationId": "HttpRequest"
    },
    "parameters": {
      "dataset": "https://contoso.sharepoint.com/sites/CorpNet",
      "parameters/method": "GET",
      "parameters/uri": "_api/SP.UserProfiles.PeopleManager/GetMyProperties?$select=PersonalUrl,AccountName",
      "parameters/headers": {
        "Accept": "application/json;odata=nometadata"
      }
    },
    "retryPolicy": {
      "type": "none"
    }
  },
  "runAfter": {
    "Literal_query": [
      "Succeeded"
    ]
  }
}
```

### Personal_site_available

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "If",
  "expression": "@startsWith(toLower(coalesce(body('SharePoint_profile')?['PersonalUrl'],'')),'https://contoso-my.sharepoint.com/personal/')",
  "runAfter": {
    "Selected_profile": [
      "Succeeded"
    ],
    "SharePoint_profile": [
      "Succeeded"
    ],
    "OneDrive_root": [
      "Succeeded"
    ]
  }
}
```

### Source_directory_profile

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "OpenApiConnection",
  "inputs": {
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_office365users",
      "connectionName": "shared_office365users",
      "operationId": "UserProfile_V2"
    },
    "parameters": {
      "id": "@last(split(body('SharePoint_profile')?['AccountName'],'|'))",
      "$select": "id,mail,userPrincipalName"
    },
    "retryPolicy": {
      "type": "none"
    }
  },
  "runAfter": {}
}
```

## Personal_drive

Use the verified PersonalUrl as the Site Address and call SharePoint's v2.0 drive endpoint to obtain the personal drive id, owner and webUrl. This is still a SharePoint connector HTTP request, not a separate Microsoft Graph agent tool.

**Response use:** Accounts_aligned compares owner.user.id with Selected_profile.id and Source_directory_profile.id, checks a nonempty drive id, and checks that OneDrive_root.Id begins with that drive id plus a period. The drive identity is also used by later workbook operations.

**Boundaries:** A GET with no body. The check aligns the selected profile, SharePoint source and private destination. It does not attest channel sign-in or independently attest the Excel/Outlook connection principals.

**Source JSON pointer:** `/actions/Start_search_export/actions/Valid_input/actions/Personal_site_available/actions/Personal_drive`

```json
{
  "type": "OpenApiConnection",
  "inputs": {
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
      "connectionName": "shared_sharepointonline",
      "operationId": "HttpRequest"
    },
    "parameters": {
      "dataset": "@body('SharePoint_profile')?['PersonalUrl']",
      "parameters/method": "GET",
      "parameters/uri": "_api/v2.0/drive?$select=id,owner,webUrl",
      "parameters/headers": {
        "Accept": "application/json;odata=nometadata"
      }
    },
    "retryPolicy": {
      "type": "none"
    }
  },
  "runAfter": {}
}
```

### Accounts_aligned

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "If",
  "expression": "@and(not(empty(body('Selected_profile')?['id'])),not(empty(body('Selected_profile')?['mail'])),not(contains(body('Selected_profile')?['mail'],';')),not(contains(body('Selected_profile')?['mail'],',')),equals(body('Selected_profile')?['id'],body('Source_directory_profile')?['id']),equals(body('Selected_profile')?['id'],body('Personal_drive')?['owner']?['user']?['id']),not(empty(body('Personal_drive')?['id'])),startsWith(body('OneDrive_root')?['Id'],concat(body('Personal_drive')?['id'],'.')))",
  "runAfter": {
    "Personal_drive": [
      "Succeeded"
    ],
    "Personal_site_user": [
      "Succeeded"
    ],
    "Source_directory_profile": [
      "Succeeded"
    ]
  }
}
```

## Personal_site_user

Read the current user's SharePoint site-local principal Id and LoginName from the selected account's personal site.

**Response use:** Private_report_verified and Delivery_acl_verified compare the report role-assignment Member.Id against this Id. A SharePoint principal integer is not the Entra directory GUID returned by Office 365 Users.

**Boundaries:** A GET with no body. It provides the ACL comparison principal; it does not create a user, grant access or send a recipient address to the flow.

**Source JSON pointer:** `/actions/Start_search_export/actions/Valid_input/actions/Personal_site_available/actions/Personal_site_user`

```json
{
  "type": "OpenApiConnection",
  "inputs": {
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
      "connectionName": "shared_sharepointonline",
      "operationId": "HttpRequest"
    },
    "parameters": {
      "dataset": "@body('SharePoint_profile')?['PersonalUrl']",
      "parameters/method": "GET",
      "parameters/uri": "_api/web/currentuser?$select=Id,LoginName",
      "parameters/headers": {
        "Accept": "application/json;odata=nometadata"
      }
    },
    "retryPolicy": {
      "type": "none"
    }
  },
  "runAfter": {}
}
```

## Initial_search

POST the Initial_request object to SharePoint Search REST. The endpoint is on the configured corporate site, but the KQL restricts the search to explicit approved SiteIDs AND the configured hub DepartmentId; Site Address alone is not that restriction.

**Response use:** Initial_response_valid requires non-null PrimaryQueryResult.RelevantResults.TotalRows and Table.Rows. Count_index_matches adds the index estimate; Remember_batch retains the batch KQL, approved site map, estimate and rows for later processing. Rows contain locator cells, not permission-checked display rows.

**Boundaries:** This POST is a read-only search, not a content write. The body requests 100 rows at StartRow 0, disables query rules and duplicate trimming, selects four locator properties, and sorts only by [docid] ascending. A failed/malformed startup does not fall back to another search.

**Source JSON pointer:** `/actions/Start_search_export/actions/Valid_input/actions/Personal_site_available/actions/Accounts_aligned/actions/Read_index_batches/actions/Initial_search`

```json
{
  "type": "OpenApiConnection",
  "inputs": {
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
      "connectionName": "shared_sharepointonline",
      "operationId": "HttpRequest"
    },
    "parameters": {
      "dataset": "https://contoso.sharepoint.com/sites/CorpNet",
      "parameters/method": "POST",
      "parameters/uri": "_api/search/postquery",
      "parameters/headers": {
        "Accept": "application/json;odata=nometadata",
        "Content-Type": "application/json;odata=nometadata"
      },
      "parameters/body": "@string(outputs('Initial_request'))"
    },
    "retryPolicy": {
      "type": "none"
    }
  },
  "runAfter": {
    "Initial_request": [
      "Succeeded"
    ]
  }
}
```

### Initial_request

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "Compose",
  "inputs": {
    "request": {
      "Querytext": "@concat('(', item()?['Kql'], ') AND (', outputs('Literal_query'), ') AND (contentclass:\"STS_ListItem_DocumentLibrary\" OR contentclass:\"STS_ListItem_WebPageLibrary\") AND (IsDocument:1 OR FileExtension:aspx)')",
      "RowLimit": 100,
      "StartRow": 0,
      "TrimDuplicates": false,
      "EnableQueryRules": false,
      "SortList": [
        {
          "Property": "[docid]",
          "Direction": 0
        }
      ],
      "SelectProperties": [
        "SPWebUrl",
        "SiteID",
        "ListID",
        "ListItemID"
      ]
    }
  },
  "runAfter": {}
}
```

### Literal_query

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "Compose",
  "inputs": "@if(equals(trim(coalesce(triggerBody()?['query'],'')),'*'),'*',join(body('Literal_tokens'),' AND '))",
  "runAfter": {
    "Literal_tokens": [
      "Succeeded"
    ]
  }
}
```

### Initial_response_valid

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "If",
  "expression": "@and(not(equals(body('Initial_search')?['PrimaryQueryResult']?['RelevantResults']?['TotalRows'],null)),not(equals(body('Initial_search')?['PrimaryQueryResult']?['RelevantResults']?['Table']?['Rows'],null)))",
  "runAfter": {
    "Initial_search": [
      "Succeeded"
    ]
  }
}
```

### Remember_batch

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "AppendToArrayVariable",
  "inputs": {
    "name": "Batches",
    "value": {
      "Kql": "@items('Read_index_batches')?['Kql']",
      "Sites": "@items('Read_index_batches')?['Sites']",
      "Total": "@body('Initial_search')?['PrimaryQueryResult']?['RelevantResults']?['TotalRows']",
      "Rows": "@body('Initial_search')?['PrimaryQueryResult']?['RelevantResults']?['Table']?['Rows']"
    }
  },
  "runAfter": {
    "Count_index_matches": [
      "Succeeded"
    ]
  }
}
```

## Make_report_private

Break role inheritance on the newly created report's backing list item, using copyRoleAssignments=false and clearSubscopes=true. Unlike the search POSTs, this action changes permissions.

**Response use:** No response fields are used as proof of privacy. Successful completion permits Private_file_acl to read the actual resulting assignments; Private_report_verified must pass before the positive report path proceeds.

**Boundaries:** The target is the new export workbook, not a source library or source document. Report_item_uri derives its server-relative path from ReportUrl, decodes the URI path and doubles apostrophes inside the OData string. Do not repurpose this mutation for existing documents or libraries without a separate access-management design.

**Source JSON pointer:** `/actions/Start_search_export/actions/Valid_input/actions/Personal_site_available/actions/Accounts_aligned/actions/Matching_content/actions/Make_report_private`

```json
{
  "type": "OpenApiConnection",
  "inputs": {
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
      "connectionName": "shared_sharepointonline",
      "operationId": "HttpRequest"
    },
    "parameters": {
      "dataset": "@body('SharePoint_profile')?['PersonalUrl']",
      "parameters/method": "POST",
      "parameters/uri": "@concat(outputs('Report_item_uri'),'/breakroleinheritance(copyRoleAssignments=false,clearSubscopes=true)')",
      "parameters/headers": {
        "Accept": "application/json;odata=nometadata"
      }
    },
    "retryPolicy": {
      "type": "none"
    }
  },
  "runAfter": {
    "Report_item_uri": [
      "Succeeded"
    ]
  }
}
```

### Report_item_uri

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "Compose",
  "inputs": "@concat('_api/web/GetFileByServerRelativePath(decodedurl=',decodeUriComponent('%27'),replace(decodeUriComponent(uriPath(variables('ReportUrl'))),decodeUriComponent('%27'),concat(decodeUriComponent('%27'),decodeUriComponent('%27'))),decodeUriComponent('%27'),')/ListItemAllFields')",
  "runAfter": {
    "Remember_report_url": [
      "Succeeded"
    ]
  }
}
```

## Private_file_acl

GET the report list item's HasUniqueRoleAssignments and expanded role-assignment members and role definitions after the inheritance change.

**Response use:** Private_report_verified requires unique permissions, exactly one role assignment, the same Member.Id as Personal_site_user.Id, and RoleTypeKind 5 on the first role binding (Administrator/Full Control). Merely succeeding at breakroleinheritance is not accepted as proof.

**Boundaries:** This initial check explicitly selects HasUniqueRoleAssignments. The later final check uses the RoleAssignments collection instead and does not select this property again. The positive owner-account proof is not a comprehensive permission-denial or tenant-administrator-access audit.

**Source JSON pointer:** `/actions/Start_search_export/actions/Valid_input/actions/Personal_site_available/actions/Accounts_aligned/actions/Matching_content/actions/Private_file_acl`

```json
{
  "type": "OpenApiConnection",
  "inputs": {
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
      "connectionName": "shared_sharepointonline",
      "operationId": "HttpRequest"
    },
    "parameters": {
      "dataset": "@body('SharePoint_profile')?['PersonalUrl']",
      "parameters/method": "GET",
      "parameters/uri": "@concat(outputs('Report_item_uri'),'?$select=HasUniqueRoleAssignments,RoleAssignments/Member/Id,RoleAssignments/RoleDefinitionBindings/RoleTypeKind&$expand=RoleAssignments/Member,RoleAssignments/RoleDefinitionBindings')",
      "parameters/headers": {
        "Accept": "application/json;odata=nometadata"
      }
    },
    "retryPolicy": {
      "type": "none"
    }
  },
  "runAfter": {
    "Make_report_private": [
      "Succeeded"
    ]
  }
}
```

### Private_report_verified

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "If",
  "expression": "@and(equals(body('Private_file_acl')?['HasUniqueRoleAssignments'],true),equals(length(body('Private_file_acl')?['RoleAssignments']),1),equals(first(body('Private_file_acl')?['RoleAssignments'])?['Member']?['Id'],body('Personal_site_user')?['Id']),equals(first(first(body('Private_file_acl')?['RoleAssignments'])?['RoleDefinitionBindings'])?['RoleTypeKind'],5))",
  "runAfter": {
    "Private_file_acl": [
      "Succeeded"
    ]
  }
}
```

## Preview_metadata_fields

Use the current preview candidate's validated WebUrl and ListId to discover which optional stored metadata fields exist on that source list.

**Response use:** The endpoint returns value entries with InternalName. Preview_field_names selects those names; Read_preview_item appends them to its $select only when the result is nonempty. The filter requests only Department, TopicTags and DocumentType.

**Boundaries:** This avoids requesting nonexistent optional columns across heterogeneous lists. An absent optional column is not the same as an HTTP failure. This is a field-schema read, not tag filtering, taxonomy expansion or metadata inferred by the model.

**Source JSON pointer:** `/actions/Build_chat_preview/actions/Preview_batches/actions/Preview_batch_budget/actions/Each_preview_candidate/actions/Preview_candidate_budget/actions/Preview_metadata_fields`

```json
{
  "type": "OpenApiConnection",
  "inputs": {
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
      "connectionName": "shared_sharepointonline",
      "operationId": "HttpRequest"
    },
    "parameters": {
      "dataset": "@items('Each_preview_candidate')?['WebUrl']",
      "parameters/method": "GET",
      "parameters/uri": "@concat('_api/web/lists(guid',decodeUriComponent('%27'),items('Each_preview_candidate')?['ListId'],decodeUriComponent('%27'),')/fields?$select=InternalName&$filter=InternalName%20eq%20%27Department%27%20or%20InternalName%20eq%20%27TopicTags%27%20or%20InternalName%20eq%20%27DocumentType%27')",
      "parameters/headers": {
        "Accept": "application/json;odata=nometadata"
      }
    },
    "retryPolicy": {
      "type": "none"
    }
  },
  "runAfter": {
    "Count_preview_checked": [
      "Succeeded"
    ]
  }
}
```

### Preview_field_names

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "Select",
  "inputs": {
    "from": "@body('Preview_metadata_fields')?['value']",
    "select": "@item()?['InternalName']"
  },
  "runAfter": {
    "Preview_metadata_fields": [
      "Succeeded"
    ]
  }
}
```

## Read_preview_item

GET one current source list item by integer ItemId, with $expand=File and an explicit $select for title, filename, source URL and source timestamps, plus optional fields discovered in the preceding action.

**Response use:** Preview_item_verified checks the returned Id, a nonempty File.ServerRelativeUrl, the approved collection path prefix and absence from PreviewUrls. Preview_row and Remember_preview_line consume current source values only after the guard passes.

**Boundaries:** The source request runs through the caller's SharePoint connection. File.TimeCreated and File.TimeLastModified supply dates; stored TopicTags supply tags. A denied, missing or unverifiable item is not replaced with raw index metadata. The preview has a 20-candidate budget and can contain fewer than ten rows.

**Source JSON pointer:** `/actions/Build_chat_preview/actions/Preview_batches/actions/Preview_batch_budget/actions/Each_preview_candidate/actions/Preview_candidate_budget/actions/Read_preview_item`

```json
{
  "type": "OpenApiConnection",
  "inputs": {
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
      "connectionName": "shared_sharepointonline",
      "operationId": "HttpRequest"
    },
    "parameters": {
      "dataset": "@items('Each_preview_candidate')?['WebUrl']",
      "parameters/method": "GET",
      "parameters/uri": "@concat('_api/web/lists(guid',decodeUriComponent('%27'),items('Each_preview_candidate')?['ListId'],decodeUriComponent('%27'),')/items(',string(int(items('Each_preview_candidate')?['ItemId'])),')?$select=Id,Title,File/Name,File/ServerRelativeUrl,File/TimeLastModified,File/TimeCreated',if(empty(body('Preview_field_names')),'',concat(',',join(body('Preview_field_names'),','))),'&$expand=File')",
      "parameters/headers": {
        "Accept": "application/json;odata=nometadata"
      }
    },
    "retryPolicy": {
      "type": "none"
    }
  },
  "runAfter": {
    "Preview_field_names": [
      "Succeeded"
    ]
  }
}
```

### Preview_item_verified

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "If",
  "expression": "@and(equals(body('Read_preview_item')?['Id'],int(items('Each_preview_candidate')?['ItemId'])),not(empty(body('Read_preview_item')?['File']?['ServerRelativeUrl'])),startsWith(toLower(coalesce(body('Read_preview_item')?['File']?['ServerRelativeUrl'],'')),concat(toLower(decodeUriComponent(uriPath(items('Preview_batches')?['Sites']?[items('Each_preview_candidate')?['SiteId']]?['url']))),'/')),not(contains(variables('PreviewUrls'),toLower(concat('https://contoso.sharepoint.com',replace(replace(uriComponent(coalesce(body('Read_preview_item')?['File']?['ServerRelativeUrl'],'')),'%2F','/'),'%2f','/'))))))",
  "runAfter": {
    "Read_preview_item": [
      "Succeeded"
    ]
  }
}
```

## Available_metadata_fields

Perform the export-stage optional-field discovery for each grouped source WebUrl/ListId, rather than assuming every list has the same columns or reusing the preview's metadata.

**Response use:** Metadata_field_names extracts returned InternalName values for the export GET's $select. Group_filter_parts separately constructs numeric Id eq N predicates from the current group's indexed candidates.

**Boundaries:** Only Department, TopicTags and DocumentType are requested here. PolicyStatus and ReviewDate are not selected, exported or used to filter approved content. This action does not filter results by stored tag values.

**Source JSON pointer:** `/actions/Continue_private_export/actions/Export_rows/actions/Each_metadata_group/actions/Group_budget/actions/Available_metadata_fields`

```json
{
  "type": "OpenApiConnection",
  "inputs": {
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
      "connectionName": "shared_sharepointonline",
      "operationId": "HttpRequest"
    },
    "parameters": {
      "dataset": "@items('Each_metadata_group')?['WebUrl']",
      "parameters/method": "GET",
      "parameters/uri": "@concat('_api/web/lists(guid',decodeUriComponent('%27'),items('Each_metadata_group')?['ListId'],decodeUriComponent('%27'),')/fields?$select=InternalName&$filter=InternalName%20eq%20%27Department%27%20or%20InternalName%20eq%20%27TopicTags%27%20or%20InternalName%20eq%20%27DocumentType%27')",
      "parameters/headers": {
        "Accept": "application/json;odata=nometadata"
      }
    },
    "retryPolicy": {
      "type": "none"
    }
  },
  "runAfter": {
    "Group_filter_parts": [
      "Succeeded"
    ]
  }
}
```

### Metadata_field_names

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "Select",
  "inputs": {
    "from": "@body('Available_metadata_fields')?['value']",
    "select": "@item()?['InternalName']"
  },
  "runAfter": {
    "Available_metadata_fields": [
      "Succeeded"
    ]
  }
}
```

### Group_filter_parts

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "Select",
  "inputs": {
    "from": "@body('Group_candidates')",
    "select": "@concat('Id eq ',string(int(item()?['ItemId'])))"
  },
  "runAfter": {
    "Group_ids": [
      "Succeeded"
    ]
  }
}
```

## Read_current_items

Read current source items in a group using one list REST GET: $top=100, a URL-encoded OR filter of integer item IDs, explicit selected fields and $expand=File. This is grouped hydration, not another SharePoint Search query.

**Response use:** Valid_current_items reads the response's value array and keeps only requested Group_ids with a nonempty File.ServerRelativeUrl under the approved collection path. Later unique-result and export-limit checks govern writing. Count_group_failure increments Failures if this request fails or times out.

**Boundaries:** The $top=100 limit here is distinct from Search REST RowLimit and StartRow paging. Preview results are re-read for export; source content or permissions may have changed. A successful list request does not establish that every originally indexed item was returned.

**Source JSON pointer:** `/actions/Continue_private_export/actions/Export_rows/actions/Each_metadata_group/actions/Group_budget/actions/Read_current_items`

```json
{
  "type": "OpenApiConnection",
  "inputs": {
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
      "connectionName": "shared_sharepointonline",
      "operationId": "HttpRequest"
    },
    "parameters": {
      "dataset": "@items('Each_metadata_group')?['WebUrl']",
      "parameters/method": "GET",
      "parameters/uri": "@concat('_api/web/lists(guid',decodeUriComponent('%27'),items('Each_metadata_group')?['ListId'],decodeUriComponent('%27'),')/items?$top=100&$filter=',uriComponent(join(body('Group_filter_parts'),' or ')),'&$select=Id,Title,File/Name,File/ServerRelativeUrl,File/TimeLastModified,File/TimeCreated',if(empty(body('Metadata_field_names')),'',concat(',',join(body('Metadata_field_names'),','))),'&$expand=File')",
      "parameters/headers": {
        "Accept": "application/json;odata=nometadata"
      }
    },
    "retryPolicy": {
      "type": "none"
    }
  },
  "runAfter": {
    "Metadata_field_names": [
      "Succeeded"
    ]
  }
}
```

### Valid_current_items

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "Query",
  "inputs": {
    "from": "@body('Read_current_items')?['value']",
    "where": "@and(contains(body('Group_ids'),item()?['Id']),not(empty(item()?['File']?['ServerRelativeUrl'])),startsWith(toLower(coalesce(item()?['File']?['ServerRelativeUrl'],'')),concat(toLower(decodeUriComponent(uriPath(variables('CurrentBatch')?['Sites']?[items('Each_metadata_group')?['SiteId']]?['url']))),'/')))"
  },
  "runAfter": {
    "Read_current_items": [
      "Succeeded"
    ]
  }
}
```

### Count_group_failure

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "IncrementVariable",
  "inputs": {
    "name": "Failures",
    "value": 1
  },
  "runAfter": {
    "Read_current_items": [
      "Failed",
      "TimedOut"
    ]
  }
}
```

## Next_search_page

POST Next_request to the same Search REST endpoint when Need_next_page permits continuation. It retains CurrentBatch.Kql and Literal_query while taking StartRow from PageStart.

**Response use:** Next_page_valid requires a non-null PrimaryQueryResult.RelevantResults.Table.Rows. Use_next_page assigns those rows to PageRows. Unlike the initial response guard, it does not require TotalRows again. Count_page_failure increments Failures on a failed or timed-out request.

**Boundaries:** RowLimit stays 100 and [docid] ascending remains the only sort on every page. The verified run used offsets 0, 100, 200, 300, 400 and 500. This is bounded offset paging, not Graph nextLink, an index snapshot or a relevance-ranked best-ten preview.

**Source JSON pointer:** `/actions/Continue_private_export/actions/Export_rows/actions/Need_next_page/actions/Next_search_page`

```json
{
  "type": "OpenApiConnection",
  "inputs": {
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
      "connectionName": "shared_sharepointonline",
      "operationId": "HttpRequest"
    },
    "parameters": {
      "dataset": "https://contoso.sharepoint.com/sites/CorpNet",
      "parameters/method": "POST",
      "parameters/uri": "_api/search/postquery",
      "parameters/headers": {
        "Accept": "application/json;odata=nometadata",
        "Content-Type": "application/json;odata=nometadata"
      },
      "parameters/body": "@string(outputs('Next_request'))"
    },
    "retryPolicy": {
      "type": "none"
    }
  },
  "runAfter": {
    "Next_request": [
      "Succeeded"
    ]
  }
}
```

### Next_request

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "Compose",
  "inputs": {
    "request": {
      "Querytext": "@concat('(', variables('CurrentBatch')?['Kql'], ') AND (', outputs('Literal_query'), ') AND (contentclass:\"STS_ListItem_DocumentLibrary\" OR contentclass:\"STS_ListItem_WebPageLibrary\") AND (IsDocument:1 OR FileExtension:aspx)')",
      "RowLimit": 100,
      "StartRow": "@variables('PageStart')",
      "TrimDuplicates": false,
      "EnableQueryRules": false,
      "SortList": [
        {
          "Property": "[docid]",
          "Direction": 0
        }
      ],
      "SelectProperties": [
        "SPWebUrl",
        "SiteID",
        "ListID",
        "ListItemID"
      ]
    }
  },
  "runAfter": {}
}
```

### Next_page_valid

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "If",
  "expression": "@not(equals(body('Next_search_page')?['PrimaryQueryResult']?['RelevantResults']?['Table']?['Rows'],null))",
  "runAfter": {
    "Next_search_page": [
      "Succeeded"
    ]
  }
}
```

### Use_next_page

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "SetVariable",
  "inputs": {
    "name": "PageRows",
    "value": "@body('Next_search_page')?['PrimaryQueryResult']?['RelevantResults']?['Table']?['Rows']"
  },
  "runAfter": {}
}
```

### Count_page_failure

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "IncrementVariable",
  "inputs": {
    "name": "Failures",
    "value": 1
  },
  "runAfter": {
    "Next_search_page": [
      "Failed",
      "TimedOut"
    ]
  }
}
```

## Final_file_acl

After actual Excel readback has passed Written_rows_verified, GET the report item's RoleAssignments collection again, selecting and expanding member IDs and role-binding kinds.

**Response use:** Delivery_acl_verified requires the returned value array to contain exactly one assignment for Personal_site_user.Id, with RoleTypeKind 5 on its first role binding. Only the guarded branch sends the workbook link; changed access has explicit notification/stop paths.

**Boundaries:** This checks the observed ACL at delivery time; it is not an atomic lock preventing later access changes. Unlike Private_file_acl, this URI returns the role collection and does not re-read HasUniqueRoleAssignments. Outlook performs the email action, not this SharePoint GET.

**Source JSON pointer:** `/actions/Continue_private_export/actions/Finalize_workbook/actions/Written_rows_verified/actions/Final_file_acl`

```json
{
  "type": "OpenApiConnection",
  "inputs": {
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
      "connectionName": "shared_sharepointonline",
      "operationId": "HttpRequest"
    },
    "parameters": {
      "dataset": "@body('SharePoint_profile')?['PersonalUrl']",
      "parameters/method": "GET",
      "parameters/uri": "@concat(outputs('Report_item_uri'),'/RoleAssignments?$select=Member/Id,RoleDefinitionBindings/RoleTypeKind&$expand=Member,RoleDefinitionBindings')",
      "parameters/headers": {
        "Accept": "application/json;odata=nometadata"
      }
    },
    "retryPolicy": {
      "type": "none"
    }
  },
  "runAfter": {
    "Complete_metadata": [
      "Succeeded"
    ]
  }
}
```

### Delivery_acl_verified

Supporting source excerpt; nested branches omitted.

```json
{
  "type": "If",
  "expression": "@and(equals(length(body('Final_file_acl')?['value']),1),equals(first(body('Final_file_acl')?['value'])?['Member']?['Id'],body('Personal_site_user')?['Id']),equals(first(first(body('Final_file_acl')?['value'])?['RoleDefinitionBindings'])?['RoleTypeKind'],5))",
  "runAfter": {
    "Final_file_acl": [
      "Succeeded"
    ]
  }
}
```
