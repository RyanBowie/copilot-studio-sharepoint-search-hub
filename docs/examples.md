# Example prompts and outputs

## Use the guided topic

The reliable starting prompt is **`Search SharePoint`**. The topic then asks for
scope and keywords. Do not assume that a long natural-language prompt will
populate every input or that the agent is a free-form policy-answering system.

| Start | Select | Enter | What this exercises |
|---|---|---|---|
| `Search SharePoint` | `All` | `*` | Files and pages across every approved department collection. |
| `Search SharePoint` | `HR` | `leave` | Department selection and literal keyword retrieval. |
| `Search SharePoint` | `Finance` | `expenses` | A departmental document/page search. |
| `Search SharePoint` | `IT` | `access` | IT source links and actual stored metadata. |
| `Search SharePoint` | `All` | `getting started` | Similar page titles in different source sites. |
| `Search SharePoint` | `All` | `hubspokeverify` | The expanded synthetic corpus, once added to the inventory and indexed. |
| `Search SharePoint` | `All` | `zzznomatchcorpnet999` | An honest no-match path. |
| `Search SharePoint` | `HR` | `path:secret` | Reject raw search operators rather than change the scope. |

`hubspokeverify` is a deliberately fictional fixture marker, not a product
keyword. New content may need time to appear in SharePoint's index.

## Observed expanded output

On 12 September 2026, the actual guided `All` / `hubspokeverify` request
produced **52 verified Excel rows across ten collections: 39 documents and
13 pages**. The HR-only equivalent produced **16 rows across three HR
collections: 12 documents and four pages**.

Both initial chat responses contained five real links and stored tags in
two columns. The corresponding complete exports included those same preview
URLs. The All preview intentionally contained repeated “Getting started”
titles, each pointing to a different real source.

![Actual expanded two-column chat preview](images/live-chat-expanded.png)

The private workbook checks and verified-profile email actions succeeded
for both runs. These observations establish connector acceptance, not a
human confirming inbox receipt. See [validation](validation.md) for scope
and remaining gaps.

## Historical baseline output

The historical owner-account `All` / `*` run returned 17 exported/read-back
rows. Its visible five-row preview contained:

| File or page | Type | Stored tags |
|---|---|---|
| Annual leave guidance | Page | hr; leave; people-policy |
| Expenses and purchasing | Page | finance; expenses; procurement |
| Department directory | Page | directory; departments; navigation |
| Devices and access | Page | it; devices; access |
| Corporate working guide | Guide | corporate; working-guide; cobalt-directory |

The original rows were clickable. Live tenant URLs are intentionally omitted
from this transcription. See the [genuine screenshot](screenshots.md#historical-linked-search-results).
This is a historical four-collection observation, not the larger fixture or a
fresh run against the prepared ten-collection policy.

## Chat output shape

The following is an **illustrative rendering of the intended two-column
preview**, not a transcript or a promise that these exact rows will appear for
every query. Links use an example tenant.

| File or page | Stored tags |
|---|---|
| [Leave and working time policy](https://contoso.sharepoint.com/sites/HR/Shared%20Documents/Leave-and-Working-Time-Policy.docx) | leave; wellbeing; meadow-27 |
| [Annual leave guidance](https://contoso.sharepoint.com/sites/HR/SitePages/Annual-Leave.aspx) | hr; leave; people-policy |

An initial status should communicate **export started**, not “email sent.”
The actual response also qualifies the index estimate, effective account and
any applicable limitations. At most five verified rows are displayed.

There is no result row when no accessible source was verified. The agent must
not fill an empty result table with plausible company policies.

## Workbook output

The deliverable is a genuine `.xlsx` file with a filterable Excel table,
readable source hyperlinks and the verified exported metadata. It includes
the preview rows and remaining verified matches within the declared bounds;
it is not merely the “remaining results after the first five.”

Columns include source title/link, department, stored tags, document type and
modified time. `SourceSite` and technical `SourceURL` are retained as hidden
columns. Neither `PolicyStatus` nor `ReviewDate` is selected or exported;
draft/archived content is not filtered out. Completion information must distinguish
the index estimate from rows actually exported and disclose omissions or caps.

The compact chat preview omits the separate document-type column to preserve
space. Document type remains useful in Excel.

## Email output

**Illustrative description, not a sent-message transcript:** an email from
the configured caller-provided connection to the verified profile mailbox,
containing a private workbook link and accurate completion/limitation details.

The recipient is not taken from a prompt. A prompt such as “send it to this
other address” must not replace the verified recipient.

## Negative-path expectations

| Condition | Required outcome |
|---|---|
| No indexed matches | A qualified no-match response, not fabricated rows. |
| Index candidate is no longer accessible | Omit it from disclosed/exported rows and account for the omission. |
| Stored tags are absent | Chat uses `Not supplied`; the workbook retains an empty value. Do not infer tags from the title. |
| Query includes raw KQL or a URL | Reject unsupported input before scoped retrieval. |
| Selected connector accounts do not align | Explicit failure; no maker-account fallback. |
| Row, candidate, page or batch limit is reached | Identify partial/capped work; do not call it exhaustive. |
| Workbook or email fails after initial response | Preserve the failure in continuation evidence; do not reinterpret the earlier acknowledgement as success. |

See [validation](validation.md) for actual evidence. Example output shapes are
not substitutes for flow-run and workbook verification.
