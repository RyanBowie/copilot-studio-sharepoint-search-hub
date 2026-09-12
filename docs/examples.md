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

## Observed polished M365 table

The actual **IT / devices** request returned four verified results: one page
and three documents. Bold source links with page/file glyphs and monospace
short-tag labels rendered, while long tags wrapped normally. The four-row
private export and verified-recipient email acceptance were checked.

**M365 leaves dates left-aligned**, even though the Markdown uses centering
markers. The illustration below may render differently in GitHub; use the
[actual M365 input/output](screenshots.md#published-m365-table-polish) for the
observed host behavior, not this document's own table renderer.

## Observed published M365 banners

Actual published M365 conversations selected **HR / annual leave** and **IT /
a unique no-match token**. HR showed the purple banner, SharePoint icon and two
source-linked results, with a complete two-row private export. IT showed the
blue banner/icon and an explicit no-match result without workbook/email writes.

The [genuine M365 gallery](screenshots.md#published-m365-banner-runtime) includes
the prepared HR input, full HR output at 67% zoom, its table at 100%, and the
IT banner. The table in these captures predates table-specific polish. These
are owner-account observations, not Teams or negative-permission evidence.

## Current observed four-column output

The final owner-account `All` / `hubspokeverify` run returned **ten rows** in
separate File or page, Created (UTC), Modified (UTC) and Stored tags columns.
Its preview contained four pages and six documents, all included in the
**112-row export**. Dates and tags matched the current source, and actual
100+12 paging was reverified.

The narrow Studio pane wraps date values and headers heavily. See the
[genuine captures](screenshots.md#current-four-column-chat), not an illustrative
table, for actual rendering. Teams remains an owner-operated separate check.

## Historical paging output

After 60 further indexed fixtures were added, the owner-account `All` /
`hubspokeverify` conversation retrieved actual pages of **100 and 12** at
StartRow **0 and 100**, without reducing the native 100-row page size.
Excel read-back verified **112 unique rows: 99 documents and 13 pages**,
including all five preview links. This run used GPT-5 Chat and predates the
created/modified-date chat enhancement.

See the [paging evidence](validation.md#verified-native-paging-beyond-100-matches---12-september-2026).
These are snapshot counts, not expected totals for every future query.

## Historical expanded output

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

The following is an **illustrative rendering of the intended four-column
preview**, not a transcript or a promise that these exact rows will appear for
every query. Links and recipient use example domains. The message styling uses
Markdown headings, restrained icons and an export-status blockquote, not
HTML/CSS or a card table. A separate contextual Adaptive Card banner precedes
this message in the agent; that image is not reconstructed in this illustration.

### 🔎 SharePoint results

**Scope:** HR · **Index estimate:** 2

> 📄 **Private Excel export started**
>
> **Verified recipient:** example.user@example.invalid
>
> Delivery is pending. A private workbook link will be emailed only after row
> and access verification.

#### Verified matches

Created and last modified dates are UTC (YYYY-MM-DD).

| File or page | Created (UTC) | Modified (UTC) | Stored tags |
|:---|:---:|:---:|:---|
| [**📄 Leave and working time policy**](https://contoso.sharepoint.com/sites/HR/Shared%20Documents/Leave-and-Working-Time-Policy.docx) | 2026-01-05 | 2026-09-10 | `leave`; `wellbeing`; `meadow-27` |
| [**🌐 Annual leave guidance**](https://contoso.sharepoint.com/sites/HR/SitePages/Annual-Leave.aspx) | 2026-02-12 | 2026-09-11 | `hr`; `leave`; `people-policy` |

---

**Preview:** up to 10 results from at most 20 checked candidates.

**Export bounds:** 1000 rows · 2000 candidates · 40 search pages · 12 batches of 20 sites.

Source permissions still apply. Excel includes these matches and the remaining
verified results within those bounds. Exports may be partial; the index estimate
can differ from the final exported-row count. Completion and omission details
are recorded in Excel.

**End of illustrative message.**

An initial status should communicate **export started**, not “email sent.”
The actual response also qualifies the index estimate, effective account and
any applicable limitations. At most ten verified rows are displayed, with
dates from the current file/page, not its containing site's creation date.
These fictional dates illustrate content only, not exact client rendering.
Created and modified dates occupy their own columns, not the name/link cell.
The earlier success-formatting revision changed only the message wrapper.
Table-specific polish adds bold links, verified file/page glyphs, date alignment
markers and short safe tag labels. This example uses eligible labels; long or
unsafe source values remain escaped wrapping text rather than large code boxes.
The host controls their actual appearance. Error/no-match responses, source
values, workbook templates, permissions and retrieval bounds are unchanged.

There is no result row when no accessible source was verified. The agent must
not fill an empty result table with plausible company policies.

## Workbook output

The deliverable is a genuine `.xlsx` file with a filterable Excel table,
readable source hyperlinks and the verified exported metadata. It includes
the preview rows and remaining verified matches within the declared bounds;
it is not merely the remaining results after the first ten.

Columns include source title/link, department, stored tags, document type and
created and modified dates. Visible `Created (UTC)` and `Modified (UTC)`
columns use genuine Excel dates with `yyyy-mm-dd` formatting; full raw
timestamps remain in hidden `CreatedUTC` and `ModifiedUTC` columns.
`SourceSite` and technical `SourceURL` are also hidden.
Neither `PolicyStatus` nor `ReviewDate` is selected or exported;
draft/archived content is not filtered out. Completion information must distinguish
the index estimate from rows actually exported and disclose omissions or caps.

The compact chat preview omits the separate document-type column to preserve
space. Document type remains useful in Excel.

The workbook uses compact top-aligned rows, wraps only visible titles/tags,
and shows actual scope/query and completion summary values above the table.
Long tags remain complete; they can legitimately make individual rows taller.
These template changes apply to new exports, not previously delivered files.

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
| Source timestamp is absent | Chat and visible date cells use `Not supplied`; hidden raw timestamps remain empty. |
| Query includes raw KQL or a URL | Reject unsupported input before scoped retrieval. |
| Selected connector accounts do not align | Explicit failure; no maker-account fallback. |
| Row, candidate, page or batch limit is reached | Identify partial/capped work; do not call it exhaustive. |
| Workbook or email fails after initial response | Preserve the failure in continuation evidence; do not reinterpret the earlier acknowledgement as success. |

See [validation](validation.md) for actual evidence. Example output shapes are
not substitutes for flow-run and workbook verification.
