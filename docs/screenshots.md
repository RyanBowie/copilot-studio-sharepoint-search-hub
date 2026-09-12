# Genuine product screenshots

These are **real Copilot Studio draft captures**, cropped to remove browser
addresses, environment identifiers, account names/email and avatars. They are
not mockups. Cropping is visibly marked in each image; the displayed result
pixels were not fabricated or rewritten.

The current four-column, preceding paging and expanded captures show different
point-in-time owner draft runs. Three further images preserve the historical four-site baseline,
including its older three-column preview. Captions distinguish the versions
rather than relabel an old screenshot as a new test.

## Current four-column chat

![Actual current chat headers, with severe narrow-pane wrapping preserved](images/live-chat-four-column-headers.png)

![Actual middle rows with separate date cells and link-only titles](images/live-chat-four-column-middle.png)

![Actual final rows and bounded-preview notice](images/live-chat-four-column-last.png)

The current owner draft returned ten genuine rows in four columns, with dates
separate from the linked title. These crops preserve actual product rendering,
including heavy header/date wrapping, scrolling and text selection. The run
passed 45 functional checks and exported 112 exact rows; it is not a polished
narrow-pane or Teams-client rendering claim.

Each title URL, tag value and UTC date matched caller-authenticated source
metadata and the same-run export. Screenshots show excerpts rather than a
fabricated single-screen view of all ten rows.

## Paging-run linked results

![Genuine GPT-5 Chat preview from the 112-row paging run](images/live-chat-paging.png)

Prompt sequence: **`Search SharePoint` -> `All` -> `hubspokeverify`**.
The actual native source-search requests returned **100 + 12 rows** with
RowLimit 100 and StartRow 0 then 100. Excel connector read-back verified
**112 unique rows**, including all five preview URLs. Private ACL and
verified-recipient email acceptance were checked.

The caption summarizes separate runtime evidence; the screenshot itself
shows the chat preview, not search cursors or workbook rows. This capture
predates the created/modified-date chat enhancement.

## Expanded linked search results

![Actual ten-collection draft showing five linked results in two columns](images/live-chat-expanded.png)

Prompt sequence: **`Search SharePoint` → `All` → `hubspokeverify`**.
The same native run exported and read back **52/52 expected rows across ten
approved collections**. It verified actual source metadata, a private owner
ACL and the email action to the verified profile mailbox.

The repeated page titles are deliberate fixture data. Each of these five rows
links to a different real source, and every preview URL was present in that
run's full export. Only the five-row preview appears in chat.

This is not proof of non-owner authorization, published-channel behavior or
search paging beyond 100 matching rows.

## Historical linked search results

![Actual draft chat showing five linked files or pages and stored tags](images/live-chat-baseline.png)

Prompt sequence: **`Search SharePoint` → `All` → `*`**.
The matching historical flow run exported and read back 17 rows. Five verified
source links and stored tags are visible in this chat capture. Narrow rendering
of the Type column motivated the newer two-column source presentation.

The initial response indicates that export has started. It is not evidence
that email delivery was already complete at that moment.

## Registered native flow binding

![Actual topic showing native Power Automate input and result bindings](images/native-flow-wiring-baseline.png)

The topic passes search words and department to the native Power Automate
tool, then binds its string `result` to `SearchResult`. The existing card retains
an older **Count** display label; the independently checked active backend is
the search/export flow. A display label alone is not proof of runtime behavior.

## Controlled response and topic checker

![Actual topic showing controlled SearchResult response and zero topic checker errors](images/topic-response-baseline.png)

The topic handles an unusable response explicitly and otherwise sends the
controlled `SearchResult`. The visible checker reports zero topic errors.
That observation does not replace conversation, connector or permission tests.

## Actual generated workbook

![Actual private 112-row workbook inspected in Excel web](images/live-workbook-compact.png)

This is the **actual generated workbook**, not a blank template or fictional
render. The visible sample shows the live scope/query, 112 rows / 99 files /
13 pages / Complete summary, compact top-aligned content and separate Created
and Modified UTC date columns. Full raw timestamps and technical URLs remain
in hidden columns. The generic `Open file` link label also opens page results;
the Type column distinguishes pages.

The associated run used the now-superseded two-column chat layout. Its workbook
evidence remains valid; it does not prove the later four-column chat correction.
All 112 rows and 224 date values were checked through connector read-back;
visual row-height checks covered a sample.

Earlier direct Graph workbook downloads were blocked. This capture used the
authorized owner's existing browser access, without changing permissions or
authentication settings. Historical exports read back 17, 52 and 16 rows;
both later paging and compact-workbook runs read back 112.

Blank workbook templates are included under [`agent/`](../agent/); they are
not screenshots or copies of a user's populated export.

## Offline workbook layout illustration

![Native Excel render of the compact template with clearly labelled fictional data](images/workbook-layout-fictional.png)

This is an **offline fictional layout check, not a live search workbook**.
It shows the compact masthead, actual-summary formula layout, top-aligned
rows, readable calendar dates, missing-date markers and a full long-tag stress
case. An isolated native Excel calculation reported zero formula errors.
The long final row is required by visible tag content, not hidden URL wrapping.

The historical template reproduced AutoFit row heights up to 409.5 points
when hidden raw URLs wrapped. Disabling hidden wrapping reduced that case
to 42 points; the compact layout then measured 14.5 points for its ordinary
short row. These controlled measurements identify a template defect and fix;
they are not measurements taken from the user's delivered workbook.
