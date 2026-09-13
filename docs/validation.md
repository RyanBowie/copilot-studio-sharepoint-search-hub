# Evidence and limitations

## Evidence categories

This repository separates **source capability**, **observed runtime behavior**
and **work still requiring verification**. A source definition is not proof of
an executed flow; an upload is not proof of indexing; a populated workbook is
not proof of non-owner permission trimming.

Live tenant identifiers, account details, connection IDs, populated exports
and raw run links remain outside this publication-oriented repository.

## 512-result native export - 13 September 2026

**PASS: 512 actual exported rows, not just an index estimate.** The owner
started one published M365 `Search SharePoint -> All -> hubspokeverify` request.
Its native run started at **10:42:24 UTC** and completed at **11:09:10 UTC**,
taking **26m46s**. Verification read only that existing run; it did not submit
another query, invoke a fallback flow or create another workbook/email.

| Evidence | Observed result |
|---|---|
| Native source paging | StartRow 0, 100, 200, 300, 400, 500; RowLimit 100; document-ID ascending only on every request. |
| Actual page counts | 100 + 100 + 100 + 100 + 100 + 12, pairwise disjoint and exactly matching the 512-source oracle. |
| Current caller source reads | All 512 locators hydrated in their correct page iterations: 499 documents and 13 pages across ten collections. |
| Chat preview | Ten distinct linked rows, each included in the complete export; four-column title/glyph/tag/date fidelity checked. |
| Excel readback | 512 real rows, retrieved as 250 + 250 + 12; exact titles, department, raw tags, types and URLs. |
| Source dates | 1,024 full-timestamp/calendar comparisons matched; no formula-error values or sentinel row. |
| Completion | Complete; zero omissions, duplicate index hits, raw-metadata mismatches, processing errors or upstream truncation. |
| Access and delivery | Final owner-private ACL verified; one email to the verified profile accepted. Inbox receipt remains unverified. |

**25 final checks, 23 paging checks and 15 date/markup checks passed.** The
date/markup group includes an offline parser alignment check, not a claim that
M365 centers dates: the visible host still left-aligns them. Export processing
took about 25m13s within the 45-minute loop limit; readback took about six seconds
within its five-minute limit. These are observed timings, not a service guarantee.

Revision attribution uses the unchanged canonical/management definition and
workflow ETag before, during and after the run, plus the actual DocId-sorted
requests. The revision is `80f131a2368450fa21ae6ebfe44db5192121032828da8ab41362a96253aff36a`.
The management API did not expose an immutable per-run definition/version
payload; the evidence is an unchanged-record envelope, not a claimed download
of a frozen run definition. Agent/tool/publication, connections and template
were preserved.

The owner's earlier different-term no-match is separate activity, not a retry
of this positive run. The supplied screenshot shows the initial pending-export
response; completion comes from the same run's actual connector evidence.
No new workbook UI/download inspection, permission workaround, Teams test,
non-owner denial/revocation test, new-tenant import or production-scale claim
is implied.

[Safe runtime summary](scale-runtime-validation-summary.json) ·
[Genuine owner-provided preview](screenshots.md#owner-provided-512-item-preview)

## 512-source creation and indexing - 13 September 2026

The scale fixture adds **400 real Word documents**, 40 in each of the ten
existing approved collections. Together with the prior marker corpus it has
**512 distinct matching sources: 499 documents and 13 pages**. New files are
evenly divided between library roots and existing nested folders.

All 400 local packages passed Office Open XML/schema and exact body-text
validation. Every uploaded file was downloaded and its body/package integrity,
metadata, path, publication and inherited access checked. Fresh topology/audience
audits surrounded provisioning; no broader access was granted. The dedicated
provisioner was stopped after each stage and is not a runtime result source.

A document-ID-ordered diagnostic query returned the exact 512-source set in
**100, 100, 100, 100, 100, 12** rows with no page overlap. A separate content-only
marker returned all 400 new documents; that marker is absent from names, titles
and stored tags. These are index-readiness checks, **not an agent export test**.

**Scale finding:** relevance-ordered pages overlapped even after the index count
reached 512. Adding document ID only as a secondary rank tie-break still returned
478 unique sources across 512 rows. Document-ID-only ascending order returned all
512 exactly. The subsequent stable-paging change adds document-ID ascending
sorting to both native request paths, with no other search/export change.
The actual 512-row native run subsequently passed the separate gate above;
its preview is a bounded verified sample, not the best ten by rank.

[Source/index checkpoint and counts](scale-source-validation-summary.json) ·
[Reproducible corpus and 512-item blueprint](../fixtures/corpnet-demo/README.md#500-plus-scale-fixture)

## Unmanaged reference solution - 13 September 2026

The repository now includes a real unmanaged package derived from a supported
Dataverse export and rebuilt with Microsoft PAC 1.47.1 SolutionPackager.
It contains one agent, 16 active bot components, one current runtime workflow,
five connection references and the required tool/workflow relationship.
Provisioning, retired flows and disabled diagnostic components are excluded.

**13 package tests and 68 portable-agent tests passed.** ZIP CRC/integrity and
an official unpack/pack/unpack roundtrip preserved all 39 source files
semantically. The initial package export added only a packaging container and
membership, without modifying source components. The subsequent scale fix
intentionally added two native-flow `SortList` leaves and synchronized the
package: only its workflow JSON entry changed. Agent/topic/model, connections,
workbook bytes and owner publication were preserved.

The neutral package contains fictional site/hub targets and no source-tenant
connection bindings or fixture data. Publication is disabled, channels are empty,
and the packaged workflow is stopped. Those requested defaults still require
verification after an actual import. A narrowly retained intrinsic workflow
identity maintains internal references; all tenant/account locators remain excluded.

**New-tenant import and runtime are UNVERIFIED.** HR/IT-like departments and
topics require customization, as do inventory, metadata, connections,
authentication, model availability and sharing. Packing is not evidence that
those target prerequisites are satisfied.

[Solution and customization guide](../solutions/README.md) ·
[Package validation snapshot](../solutions/validation.json) ·
[Component/identifier inventory](../solutions/component-inventory.json)

## Published M365 table polish - 12 September 2026

One actual **Search SharePoint -> IT -> devices** request against flow revision
`3a4b9ca0...` passed **23/23 runtime checks and 15/15 source-date/parsed-markup
checks**. It returned four source-verified results: one page and three documents.
All four private Excel rows, eight source timestamps and their corresponding
calendar-date values matched. Owner-private ACL and one verified-profile email
acceptance were checked; there was no retry or additional test query.

**Actual visual result:** bold source-linked titles, file/page glyphs inside
the links, four distinct columns and monospace short tags rendered. Long plain
tags wrapped with all text visible and no table clipping at verified 100% zoom.

**Visual limitation, not a pass:** M365 did not honor date-centering markers.
The source and offline parser request centered alignment, but the actual host
keeps date values left-aligned. The current layout was retained with this limit
explicit, rather than adding HTML/CSS, spacing hacks or a replacement card table.
The code-styled tags are not custom-colored pills.

The verified change has only four approved definition deltas: one bounded tag
Select in the already verified preview branch, the row expression and its
dependency, and header alignment markers. Reversing those deltas reproduces
the prior complete definition. Topic/banner, caller connections, model, policy,
workbook bytes and the owner's existing publication were unchanged.

Genuine inputs and the complete table/footer were captured at 100% zoom. An
optional zoom attempt was bounded and restored; intermediate images are not
mislabelled as 100%. This run does not repeat 112-row paging, prove inbox receipt,
test non-owner restrictions or establish Teams rendering.

[Runtime summary including the failed alignment check](table-polish-validation-summary.json) ·
[Actual input/output gallery](screenshots.md#published-m365-table-polish)

## Published M365 banner runtime - 12 September 2026

After the owner republished the topic, two actual M365 Copilot conversations
passed **25/25 runtime checks and 13/13 source-date checks** against flow
revision `ebfc9aa...`. The topic's dynamic scope binding remained intact.

**HR / annual leave:** the purple banner and labelled SharePoint icon rendered,
followed by two genuine rows in four separate columns. Both source records,
four full timestamps and four numeric calendar-date values matched the complete
two-row private Excel export. Final ACL was owner-private and one email to the
verified profile was accepted, not independently confirmed in the inbox.

**IT / unique no-match token:** the blue banner and icon rendered; the actual
transcript/native result explicitly reported no matches. All workbook/email
writes were skipped. The banner is contextual, not a success claim.

The complete HR response was captured at 67% browser zoom; a separate 100%
crop shows readable rows with dates on one line. The IT banner crop does not
include the no-match message, which has separate transcript/run evidence.
Zoom was restored to 100%. No source, authentication, connection or publication
change was made by Test. Separate owner activity is not counted as Test retries;
the two attributed M365 tests produced one export/accepted-email path.

These captures predate table-specific polish. They establish M365 image
transport and this two-row/no-match behavior, not Teams, negative ACLs,
revocation, inbox receipt, ten-row client layout or another 100+12 paging run.

[Safe runtime summary](m365-validation-summary.json) ·
[Published capture gallery](screenshots.md#published-m365-banner-runtime)

## Contextual banner draft - 12 September 2026

The draft topic adds one contextual Adaptive Card before the existing guarded
Markdown result. Removing that node reproduces the prior topic object. The
flow, sole `result` output, table formatter, workbook bytes, model and caller
connections remain unchanged.

Actual Studio card-editor previews rendered HR and IT artwork plus the labelled
SharePoint icon. The final topic checker reported **zero errors and warnings**.
Preview-only scope substitutions were discarded; the persisted dynamic topic
source and unchanged cloud configuration were independently read back.
This is product-loading/designer evidence, not a published-channel runtime test.

All five scope cards pass schema checks and are below 12,000 UTF-8 bytes.
Images are hash-checked local PNG data URIs, not externally hosted content.
The owner reported republishing this topic enhancement at 22:07 UTC on
12 September 2026. The separate M365 runtime evidence above subsequently
verified HR/IT image transport and the two-row result layout. Teams remains
unverified; designer success alone never established either channel.

[Designer capture and limits](screenshots.md#department-banner-designer) ·
[Banner implementation](../agent/cards/README.md)

## Styled HR runtime and documentation captures - 12 September 2026

The success-formatting revision passed **28/28 runtime/style checks and 13/13
source-date checks** in one owner-account Studio conversation:
**Search SharePoint -> HR -> annual leave**. The result contained exactly
two verified rows: **Annual leave guidance** (SharePoint page) and
**Leave and working time policy** (Word document).

Both rows, their metadata, four full timestamps and four numeric calendar-date
values matched the caller-checked source and actual Excel read-back. No formula
error values, omissions, duplicate hits or processing errors occurred. Final
ACL was owner-private and the verified-profile email action was accepted.
The agent response preceded that email and correctly said delivery was pending.

The actual bot activity matched the returned styled heading, scope/index
summary, callout, four-column table and bounds/footer. The complete definition
and workbook bytes remained unchanged during read-only designer capture.
The style release had changed only the success formatter, not retrieval logic.

**Capture boundaries:** M365 and standalone Power Automate required account
selection, so neither was used. The test used a fresh Studio context and its
already-authenticated Flows view. Thirteen genuine crops cover inputs, result
rows/footer, binding and native flow stages. Initially the complete heading/
callout was verified as bot text but could not be reliably captured in pixels
because of scroll/focus constraints. Narrow Studio wrapping remains visible.
Designer excerpts are not a full-flow image or proof that this two-row run
exercised next-page retrieval.

[Runtime summary](styled-validation-summary.json) ·
[Capture provenance](styled-capture-provenance.json) ·
[Input/output and flow gallery](screenshots.md#styled-run-inputs-output-and-flow)

## Owner-provided published M365 Copilot view - 12 September 2026

After publishing the agent themselves, the owner supplied a screenshot of
**HR / annual leave** in M365 Copilot. Two source-linked rows and separate
Created/Modified UTC columns are readable without the severe Studio wrapping.
The fixture records identify one SharePoint page and one Word document.

This establishes a user-provided view of that published result, not an
independently captured input sequence or a hash-pinned published runtime test.
It predates the message-styling refinement and does not establish export/email
completion, ten-row channel rendering, Teams behaviour or non-owner permissions.

[Privacy-cropped published output](screenshots.md#owner-provided-published-m365-copilot-output)

## Four-column draft runtime - 12 September 2026

**45/45 functional checks passed**, with an explicit narrow-pane readability
caveat. One actual owner-account GPT-5 Chat conversation produced ten rows in
four separate columns: **File or page | Created (UTC) | Modified (UTC) | Stored
tags**. Title cells contained links only; dates were not under the names.
All ten rows' links, tags and UTC dates matched current caller-checked source
metadata and the full export. This preview contained four pages and six documents.

The same run retrieved actual **100+12** source candidates at StartRow **0 then
100**, retaining RowLimit 100, and verified **112 unique Excel rows: 99 documents,
13 pages**. All 12 second-page items were caller-hydrated. All 224 full timestamps
and numeric calendar-date values matched; no formula error values, omissions,
duplicates or processing errors occurred. Owner-private ACL and verified-profile
email acceptance passed. The actual blank template bytes were unchanged from
the preceding compact-workbook run.

**Readability limitation:** the narrow Studio pane wraps headers and dates
severely, including within years. Ten rows require vertical scrolling. The
requested four-column structure is present, but this is **not** a polished
narrow/mobile rendering result or Teams verification. No publication occurred.

[Final safe runtime summary](four-column-validation-summary.json) ·
[Actual four-column captures](screenshots.md#current-four-column-chat)

## Verified source dates and compact workbook - 12 September 2026

A subsequent owner draft run passed **41/41 runtime checks** and again verified
exactly **112 unique rows**, actual **100+12 paging**, and all ten preview URLs
in the export. All **224 full canonical timestamp strings** matched current
source metadata, and all 224 visible calendar-date values read back as matching
Excel serial dates.

The actual generated workbook was opened in the authorized owner's browser.
Its scope/query and **112 rows / 99 files / 13 pages / Complete** summary,
compact top-aligned sample rows, readable UTC dates, hidden raw/technical
columns, B9 freeze boundaries and date/hyperlink/summary formulas were checked
without edits. Private ACL and verified-recipient email acceptance passed.
This resolves the earlier lack of a populated-workbook UI capture without
changing Graph permissions.

**Chat superseded:** this run placed dates beneath the link in a two-column
table. The user subsequently required four separate columns; this run is not
acceptance of that corrected layout. No live missing/fractional timestamp
fixtures occurred, and sampled workbook rows are not an all-row-height audit.

[Safe workbook verification summary](workbook-validation-summary.json) ·
[Actual workbook capture](screenshots.md#actual-generated-workbook)

## Verified native paging beyond 100 matches - 12 September 2026

One actual owner-account GPT-5 Chat draft conversation searched `All` /
`hubspokeverify` across ten approved collections. The unchanged native
**RowLimit 100** produced actual SharePoint requests at **StartRow 0 and 100**,
returning **100 + 12 disjoint candidates**. All 12 second-page items received
caller-authenticated source hydration.

The page union and Excel connector read-back each contained exactly the
**112 expected unique URLs: 99 documents and 13 pages**. All five linked/tagged
preview rows were included. All 32 checks passed, with no missing/unexpected
rows, duplicate hits, metadata mismatches, omissions, processing errors or
truncation. The final workbook ACL was owner-private and the email action to
the verified profile was accepted with HTTP 200, not proof of inbox receipt.

This is actual source paging, not the separate 500-row indexing-readiness
probe or management API `nextLink` pagination. The run completed in about
7 minutes 9 seconds, including continuation; this is not an initial-response
latency or performance guarantee. This observation predates the requested
created/modified-date chat enhancement.

[Publication-safe paging summary](paging-validation-summary.json) ·
[Genuine paging-run chat capture](screenshots.md#paging-run-linked-results)

## Historical expanded owner draft — 12 September 2026

The ten-collection, two-column draft was independently checked, then exercised
through actual Copilot Studio conversations using the owner's native runtime
connections. No provisioning flow or fixture row data supplied the runtime
results.

| Conversation | Verified result |
|---|---|
| `All` / `hubspokeverify` | **52/52 exact expected URLs**, ten collections, 39 documents and 13 pages. |
| `HR` / `hubspokeverify` | **16/16 exact expected URLs**, three HR collections, 12 documents and four pages. |
| `HR` / `path:secret` | Rejected by the topic before a native search run; no workbook/email. |
| `All` / `zzznomatchcorpnet999` | Zero matches; workbook creation and every email action skipped. |

Both positive runs returned five linked/tagged rows in two columns and
completed the same-run export continuation. Excel read-back matched every
expected URL, title, department, tag value and document type, with no missing
or unexpected rows. All 13 nested-folder rows and three intentionally empty-tag
fixtures were verified.

Both runs reported Complete, zero omissions and no processing errors. Final
ACL checks were owner-private, and the successful email actions targeted the
verified profile mailbox. HTTP 200 establishes connector acceptance, not inbox
receipt or independent Outlook sender attestation.

Total native-run durations, including continuation, were approximately
4 minutes 57 seconds for All and 2 minutes 24 seconds for HR. These are
point-in-time observations, not initial chat-response times or a performance SLA.

**Metadata gap:** `PolicyStatus` is neither selected nor exported. Two authored
Draft items and one Archived item were returned, but their statuses were not
preserved in runtime output or used as filters. Do not describe this as
approved-only policy retrieval. `ReviewDate` is also not selected/exported;
the actual date column is `ModifiedUTC`.

[Publication-safe result summary](validation-summary.json) ·
[Genuine expanded screenshot](screenshots.md#expanded-linked-search-results)

## Recovered demonstration baseline

The preceding development session recorded an owner-account search returning
**17 permission-checked results across four separate collections**:

| Collection | Files | Pages |
|---|---:|---:|
| Corporate hub | 3 | 2 |
| HR | 2 | 2 |
| Finance | 2 | 2 |
| IT | 2 | 2 |

This is a recovered point-in-time observation, not a fresh claim that the
current draft returns those exact counts. Subsequent content additions and
indexing can change them.

The historical native run was independently re-read through authenticated
management APIs on 12 September 2026. It ran on 11 September from approximately
23:48 to 23:50 UTC and reported:

| Observation | Verified historical result |
|---|---|
| Native run | Succeeded. |
| Chat preview | Five current-item reads supplied five linked rows with stored tags. |
| Workbook | Excel connector read-back contained 17 rows: nine files and eight pages. |
| Completion | Complete, zero omitted rows and no recorded processing errors. |
| Account alignment | Selected profile, source directory profile and personal-drive owner IDs matched. |
| Private output | Final ACL contained a single matching owner principal. |
| Email action | Succeeded with HTTP 200 and the verified profile mailbox as recipient; this establishes connector acceptance, not human inbox receipt. |
| Runtime connections | All five caller-provided (`Invoker`); embedded fallback disabled. |

The [screenshots](screenshots.md) show that existing draft conversation and
native binding. No fresh agent invocation was used to manufacture a new
baseline, and no populated workbook UI screenshot is claimed.

## Synthetic expansion

The expanded fixture adds **39 Word documents and 13 published pages** to the
original estate. It covers **10 separate hub-associated collections**:
the corporate hub plus a main, Operations and Field Team collection for each
of HR, Finance and IT.

The source includes repeated page titles, nested library folders, three
documents with intentionally empty tags, different policy statuses and a
shared literal search marker, `hubspokeverify`.

The tenant blocks new classic subsites. Field Team collections are separate
modern spokes, not nested webs. That restriction was left unchanged.

Provisioning, metadata verification, indexing and actual agent coverage are
separate checkpoints. Do not infer full agent coverage merely from the number
of created collections or uploaded files.

The portable reference deliberately contains **four fictional Contoso
collection entries**, not live inventory identifiers. The larger corpus is
reproducible source data, not an automatic change to that runtime policy.

The initial 68 authored artifacts did not establish next-page retrieval.
A further **60 documents**, six per collection, raised the `hubspokeverify`
matching set from 52 to **112**. Their additional `pagingverify` marker matches
only those 60 additions and is not itself a greater-than-100 paging test.
The actual two-page verification above establishes continuation for this
112-item owner-account case, not the configured 1,000-row maximum.

The later 400-document scale addition raised the shared marker corpus to 512.
Its source/index checks and completed six-page native export are documented
separately above. Neither the 112-row nor 512-row run exercises the configured
1,000-row maximum.

## Portable-source checks

The publication-safe agent package builds offline and its **68 focused tests
pass**, covering ten-row bounds, source dates, workbook formatting/contracts
and authoring serialization, plus the success-message wrapper, recipient
escaping, verbatim non-success output and retained caveats. Ten banner tests
cover the scope mapping, image hashes, schema/size bounds and preservation of
the existing result contract. Eleven table-formatting tests cover verified
glyphs, bold source links, separate date alignment, safe/unsafe tag labels,
length limits and metadata fidelity, including 100 deterministic injection-fuzz
cases parsed with Markdown-it. These are offline checks, not client screenshots.
Five stable-paging checks cover identical document-ID-only ascending ordering,
the two-leaf change boundary and a tie-heavy 512-item paging case. They do not
replace the actual native-run evidence.
The original and expansion fixture generation
commands previously ran successfully, and their **47 generated Word documents**
passed document-package validation. The separate connected paging fixture
pipeline validated its additional 60 documents before upload and runtime testing.
The architecture SVG and editable diagram were structurally checked.

These checks apply to the portable copy. They do not replace the original
environment's separate runtime tests. The early expanded run belongs to the
historical ten-collection/two-column draft; later four-column and 512-row cases
are separately identified above. The portable policy remains four fictional
Contoso entries.

## Required end-to-end checks

These requirements apply to each deployment. Passing the connected demo cases
above does not transfer that evidence to a customized tenant.

| Check | Evidence needed |
|---|---|
| Topic routing | Actual draft conversation starts the controlled topic. |
| Scope handling | `All` and each department invoke the intended approved inventory. |
| Multiple spokes | Verified result locations include more than one collection in a department. |
| Folder coverage | Actual nested-folder files appear with their exact source locations. |
| Pagination | A run retrieves and verifies beyond its first search page; local batching tests alone do not qualify. |
| Metadata | Displayed tags equal stored column values; empty tags remain explicit. |
| Chat | No more than ten actual linked/date-bearing rows; no invented titles, dates or tags; verify narrow-client rendering. |
| Workbook | Genuine populated Excel table, working source links, accurate row count and honest partial/completion status. |
| Workbook layout | Compact top-aligned rows, readable genuine dates, exact hidden raw timestamps, untruncated tags and correct metadata summary. |
| Private delivery | Verified destination access and email action to the verified account mailbox. |
| Identity | All runtime connections are caller-provided and the effective accounts align. |
| Negative permissions | Separate non-owner account cannot receive restricted titles, snippets, tags, links or facts. |
| Failure paths | No unscoped fallback, success-shaped zero count or false completion claim. |

## Not established by this reference

- Production coverage or latency across an estate of 150 or more collections.
- Multi-user authorization or negative permission trimming from owner-only runs.
- Classic-subsite traversal in a tenant that refuses classic-subsite creation.
- Stored policy-status retrieval/export or approval-status filtering.
- A fully imported portable solution in another environment.
- Multi-user channel/connector identity equivalence or SharePoint-hosted/Teams
  behaviour. The actual owner-account M365 run has the narrower evidence scope
  described above; it does not independently attest every connector principal.
- An open-source license grant or production support commitment. Public source
  and documentation hosting do not establish either.

The release checklist deliberately keeps these boundaries visible instead of
presenting a demonstration as a production certification.
