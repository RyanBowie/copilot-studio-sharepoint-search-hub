# Native Markdown preview formatting

Candidate search pages use `[docid]` ascending within each bounded batch.
The preview is not relevance-ranked best ten. This paging change leaves every
formatter expression and workbook byte unchanged; the M365 observations below
are historical `3a4b9ca0...` evidence, not a post-change native run.
See [stable paging](stable-paging.md).

The result keeps four separate columns:
**File or page | Created (UTC) | Modified (UTC) | Stored tags**.
Titles are bold links, with a small glyph inside the same link. Date columns use
Markdown center-alignment markers. M365/Teams controls table colors, borders,
fonts and whether alignment/code styles are honored; this is not custom CSS or
a replacement Adaptive Card table. The tested M365 host **does not honor the
date centering** and displays those values left-aligned. The owner approved the
current layout; the markers remain portable hints, not a centering guarantee.

The glyph reuses the existing permission-checked file/page test:
`Read_preview_item.File.Name` ending in `.aspx` means page; other supplied
filenames mean file. A missing filename gets no inferred glyph. The exported
`Type` value is untouched: it can contain an arbitrary stored `DocumentType`,
not just a binary file/page kind, so it is not used to guess a glyph.

Stored tag labels use inline code only for short values of at most 16 characters
that pass the ASCII/URI round-trip safety check and have no surrounding
whitespace. Internal spaces are permitted. Long/wide values, backticks, pipes,
Markdown/HTML-like data and other unsafe cases remain escaped wrapping text.
Empty segments and delimiters are retained. Missing tags remain plain
`Not supplied`. The existing semicolon display spacing and line-break
normalization are unchanged. Literal ampersands/entities are escaped in table
text so source characters cannot turn into different HTML characters.

The existing 200-character preview cutoff is applied before styling and retains
the `... (full tags in Excel)` notice. It bounds the label projection even for a
very long source field. Full raw Excel tags/timestamps, workbook bytes, URLs,
canonical source dates and missing-date markers are unchanged.

The flow adds one bounded **Select** data operation inside the already verified
preview branch. There are no new connectors, flow inputs/outputs, topic/banner
bindings or agent-model changes. Ten preview rows, twenty checked preview
candidates, 100-row paging and export/privacy limits remain unchanged.

Offline tests evaluate the generated expression subset and parse the table with
Markdown-it; they do not predict every host's rendering. The separate
`3a4b9ca0...` published-M365 owner-account IT/devices run passed **23/23 runtime
checks and 15/15 source-date/parsed-markup checks**: four results (one page,
three documents), four private Excel rows, eight exact timestamp/calendar
comparisons and one email-connector acceptance.

Bold linked titles, inside-link verified glyphs, **monospace** short tags and
plain wrapped long tags were visible at 100%, without losing rows or tag text.
These are not colored tag pills. **`HOST_ALIGNMENT_NOT_HONORED`** records the
actual left-aligned M365 dates despite `:---:` and offline `text-align:center`.
Centering did not pass; this is not a blanket visual success. Keep the approved
source markers without CSS or space-padding workarounds.

The preceding `ebfc9aa...` HR/IT banner evidence remains separately scoped.
Teams, non-owner/negative-ACL/revocation and other hosts remain unverified.
Email acceptance is not inbox receipt. This four-row run does not repeat the
historical 112-result paging proof, a deep workbook-UI audit, or a full-banner
capture.

## Test dependencies

The originating workspace uses `requirements-formatting.txt` for the Markdown
parser, alongside its existing workbook/YAML dependencies and
`cards/requirements.txt` for banner-schema tests. The portable reference includes
all of these dependencies in its `requirements.txt`. Use Python 3.10 or later.
No dependency or test command authenticates, publishes or invokes a search.
