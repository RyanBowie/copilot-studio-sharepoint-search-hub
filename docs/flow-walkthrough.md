# Agent and native flow walkthrough

This guide connects the user experience to the actual source files and named
actions in the native flow. Screenshots illustrate the product; the JSON and
builder below are the implementation reference.

## Open the implementation

| Artifact | Purpose |
|---|---|
| [Agent instructions](../agent/agent.mcs.yml) | Controlled search/export behaviour, model hint and source-grounding rules. |
| [Search topic](../agent/topics/SearchSharePoint.mcs.yml) | Entry point, scope/question collection, input validation and native invocation. |
| [Registered-tool reference](../agent/actions/SearchAndExport.mcs.yml) | Agent-to-flow contract with placeholder binding and caller authentication. |
| [Complete native flow definition](../agent/flows/search-export/definition.json) | Full generated workflow JSON, not an abbreviated pseudo-flow. |
| [Flow builder](../agent/scripts/build-search-export-flow.py) | Maintainable construction of the workflow and its bounded retrieval/export logic. |
| [Approved-site policy](../agent/runtime/search-policy.json) | Four fictional Contoso collections for portable adaptation. |
| [Connection-reference configuration](../agent/runtime/connection-references.json) | Placeholder caller-provided connector references. |
| [Workbook layout code](../agent/exports/template/workbook_layout.py) | Columns, styles, formulas, hidden fields and freeze panes. |
| [Native blank workbook](../agent/flows/search-export/RuntimeSearchResults.template.xlsx) | Actual runtime table/formula template, with no populated search results. |
| [Offline tests](../agent/tests/) | Input, identity/configuration, paging, preview, date, workbook and serialization contracts. |

The live demonstration used ten collections; the portable policy deliberately
contains four fictional entries. Neither this JSON nor a screenshot is a
registered/importable solution. Recreate and bind resources in the target
environment as described in [setup](setup.md) and the [agent guide](../agent/README.md).

## 1. User inputs and the topic

The supported entry phrase is **Search SharePoint**. The topic asks for a scope
and then plain search words. For example:

```text
Start: Search SharePoint
Area:  HR
Words: annual leave
```

The native trigger is a request with `kind: Skills`. Its required input
properties are exactly:

```json
{
  "query": "annual leave",
  "scope": "HR"
}
```

The scope must be `All`, `CorpNet`, `HR`, `Finance` or `IT`. Search input is a
single `*`, or up to 12 plain ASCII alphanumeric/hyphen-separated words within
160 characters. The user cannot supply a site URL, raw KQL, recipient, claimed
directory identity or token through this contract.

`annual leave` becomes `"annual" AND "leave"` inside the approved scope.
Search can match indexed document/page content as well as titles. The flow
does not translate a natural-language question into keywords, retrieve source
passages for the model or synthesize a policy answer. It returns verified
source links and metadata.

## 2. Validate and establish the effective account

![Actual topic binding with two flow inputs and one result](images/styled-hr/topic-native-flow-binding.png)

`Start_search_export` contains the controlled processing path.
`Valid_input` rejects unsupported input before retrieval; `Literal_query`
constructs literal terms rather than trusting user-provided search syntax.

`Selected_profile`, `SharePoint_profile` and `OneDrive_root` participate in
resolving the selected caller identity and private destination.
`Accounts_aligned` requires the relevant profile, source identity and
personal-drive ownership checks to agree before work proceeds.

All five connections remain caller-provided: SharePoint, Office 365 Users,
OneDrive for Business, Excel Online (Business) and Outlook. There is no
embedded maker-account or provisioning-account fallback.

This alignment does **not** independently prove the connector identity equals
the channel sign-in, attest the Excel/Outlook connection principal, or establish
non-owner permission denial. Those boundaries remain explicit.

## 3. Scope SharePoint Search

The builder groups approved collection IDs into bounded batches. Each search
combines the batch's explicit `SiteID` allowlist **and** the configured hub
`DepartmentId`, followed by literal query terms and document/page restrictions.

`Department` is a business classification. The search property `DepartmentId`
identifies hub association; they are not interchangeable. A department filter
narrows relevance but grants no permissions. A hub URL alone does not discover
or approve every associated collection.

`Initial_search` requests 100 rows. It selects source locators such as
`SPWebUrl`, `SiteID`, `ListID` and `ListItemID`; an index title or URL is not
enough to authorize disclosure of a result.

The index count is an estimate. It is not the number of rows already verified
or written to Excel, and new content can exist before indexing catches up.

![Genuine native initial-search definition with 100-row limit](images/styled-hr/native-initial-search.png)

## 4. Hydrate current source items

The flow validates returned locators against the approved estate and reads
the actual current file/page through the caller's SharePoint connection.
`Read_preview_item` provides the preview's source values. Export processing
performs its own current reads; permission or content changes between the
two stages can legitimately change the later output.

| Output | Source semantics |
|---|---|
| Title/link | Current source title or verified filename fallback and current `File.ServerRelativeUrl`. |
| Department | Stored business field or approved-inventory fallback. |
| Tags | Stored `TopicTags`; not inferred from the title or body. |
| Type | Page classification or verified document type/file extension. |
| Created | `File.TimeCreated`. |
| Modified | `File.TimeLastModified`. |

Created/modified dates are not index crawl time, export time, list-item
`Modified` substitutions or site-collection creation dates. Missing dates
display as `Not supplied`; full raw timestamps remain empty when absent.
The source may store `PolicyStatus` and `ReviewDate`, but the current flow
neither selects nor exports them, and does not apply approval-status filtering.

## 5. Prepare a private workbook and return the preview

For a positive search, a genuine workbook is prepared and its initial private
access checked through `Private_file_acl`. The flow verifies at most 20 preview
candidates to produce up to ten actual rows. It never fills missing rows with
invented results.

`Format_chat_result` creates the Markdown string. `Respond_to_agent` returns
that string through the existing `result` output; the topic sends it as the
controlled response. The success message uses a search heading, compact
Scope/Index estimate summary, a **delivery-pending** private-export callout and
separated bounds/completeness notes. It is Markdown, not a new card contract.
The styling revision changes only this formatter leaf, leaving errors/no-match
responses, verified rows and the workbook unchanged.

The table has exactly four columns:

**File or page | Created (UTC) | Modified (UTC) | Stored tags**

Title cells contain only links. Dates use UTC calendar values. Long preview
tags can be shortened at 200 characters with a notice that Excel retains the
full value. Preview ordering follows bounded retrieval, not a guarantee of a
globally ranked top ten across a large estate.

The response announces **export startup**, not completion or inbox delivery.
There is no second queue or independent background worker in this reference:
the same native flow invocation continues after its agent response.

![Actual response followed by private-export continuation](images/styled-hr/native-response-and-continuation.png)

### Optional contextual banner in the topic

The department-banner enhancement is a separate Adaptive Card 1.5 message
immediately before the existing guarded result message. Its theme is selected
from the validated scope. It contains original department artwork and a clearly
labelled Microsoft SharePoint integration icon, but **no rows, actions, query
results or success claim**.

The native `query`, `scope` -> `result` flow contract is unchanged. Result rows,
four separate columns, current source dates/tags, error messages and workbook
bytes are not rebuilt or parsed by the banner. Keeping the working Markdown
table outside the card avoids assuming a narrower card will improve readability.

Images use local, hash-checked PNG data URIs; there is no runtime image-hosting
service or anonymous SharePoint link. Schema support is not host-rendering proof.
The node's `disabled` property is a source-level feature gate, while card
`fallbackText` is contextual only and cannot guarantee recovery from content
filtering. See [banner source, build and host limits](../agent/cards/README.md).
An owner republish is required for a changed topic to reach published callers.

## 6. Continue paging and write the full export

`Export_rows` drives bounded continuation. `Next_search_page` advances source
search paging while preserving the same approved scope and 100-row page size.
Current source verification, duplicate handling and omission/error accounting
apply before rows are disclosed or written.

The exported set includes the preview rows when they remain accessible,
plus the remaining verified matches. It is not merely the rows after the
first ten. Source strings are written literally; controlled presentation
formulas provide hyperlinks and visible dates.

The demonstration proved actual StartRow **0 then 100**, with **100 + 12**
disjoint candidates and 112 exact Excel rows. This is different from management
API `nextLink` pagination and from a diagnostic indexing-readiness query.

| Bound | Value |
|---|---:|
| Preview rows / checked preview candidates | 10 / 20 |
| SharePoint rows per page | 100 |
| Exported rows / checked candidates | 1,000 / 2,000 |
| Search pages | 40 |
| Collection batches / sites per batch | 12 / 20 |
| Export loop / read-back timeout | 45 minutes / 5 minutes |

These limits are ceilings, not latency promises, proven maximum scale or
guarantees that every combination fits the agent's initial-response window.

## 7. Workbook structure and read-back

`Finalize_workbook` records the actual result/completion metadata.
`Read_back_written_rows` checks genuine Excel connector output against the
expected verified values before successful delivery.

The `Results` table starts at row 8 and freezes at **B9**. Visible fields are
Title, Department, Tags, Type, URL, Created (UTC) and Modified (UTC).
Full `CreatedUTC`/`ModifiedUTC`, `SourceSite` and technical `SourceURL` remain
hidden. Visible calendar dates are genuine numeric Excel values formatted
`yyyy-mm-dd`, derived from the preserved raw timestamps.

The compact header looks up actual scope/query and row/file/page/completion
values from `ExportMetadata` on `ExportInfo`. Top-aligned rows wrap only
visible titles/tags: hidden raw URLs no longer inflate row heights. Full long
tags can still legitimately require a taller row.

`Open file` is a generic hyperlink label for both documents and pages; the
Type column distinguishes them. For example, **Annual leave guidance** is
a SharePoint page, while **Leave and working time policy** is a Word document.

## 8. Recheck privacy and deliver

`Final_file_acl` and `Delivery_acl_verified` recheck the destination before
`Send_private_workbook` sends its link to the verified profile's mailbox.
Changed access has explicit `Notify_changed_acl` / `Stop_changed_acl` paths.
No anonymous or organization-wide sharing link is created.

An email connector HTTP 200 establishes acceptance of that action, not human
inbox receipt or independent sender attestation. Completion metadata must
distinguish complete, partial/capped, omitted and failed processing rather than
reinterpret the earlier startup response as success.

## 9. What the evidence establishes

Use [screenshots](screenshots.md) for actual input/output and product views,
and [validation](validation.md) for revision-scoped runtime results. Keep
these evidence types separate:

- Source JSON/tests describe and check the implementation.
- A screenshot shows a particular client and moment, not all rows or permissions.
- A runtime report verifies its actual calls, source values and workbook rows.
- Owner-account success does not establish negative ACLs, revocation or scale.
- Published M365 Copilot rendering does not automatically establish Teams
  desktop/mobile rendering, another user's connector identity or inbox receipt.

The owner publishes the agent. Updating a shared native flow can affect its
subsequent calls, including calls from an already-published agent; it is not
the same operation as republishing the agent. Review the connected target and
preserve the caller-authentication contract when adapting this source.
