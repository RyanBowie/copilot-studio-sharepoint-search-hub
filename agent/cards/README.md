# Contextual SharePoint banners

This is a **banner-only** Adaptive Card 1.5 presentation. It does not replace the
results table, parse Markdown, carry result rows, change the native flow output,
or claim that a search/export succeeded.

The controlled topic sends the card immediately before the existing result
message, after the scope and usable-response guards. Its heading is contextual, for example **HR
SharePoint search**. Five fixed themes use original PNG artwork: HR purple,
IT blue, Finance green, All teal, and CorpNet navy/teal. A separately labelled,
unmodified Microsoft SharePoint icon illustrates the integration; see
[NOTICE.md](NOTICE.md) for rights and release-review requirements.

## Why the table stays native Markdown

The results remain a native Markdown table with four separate columns:
**File or page | Created (UTC) | Modified (UTC) | Stored tags**. Moving these
columns into a potentially narrower Adaptive Card has not demonstrated better
readability. The only ColumnSet in the banner has two columns, for the small
product icon and its label. There are no actions, inputs, result links, HTML,
CSS, remote image URLs, public hosting changes, or new connectors.

The `query`, `scope` → `result` flow contract, ten-row/twenty-candidate preview,
100-row paging, private Excel bytes, canonical dates, full stored Excel tags,
Invoker connections and all existing safety/error behavior are unchanged.
The originating agent's owner republished the banner topic and verified it in
published M365 Copilot, as scoped below. Applying these topic sources in another
environment still requires that environment's owner-controlled publication.

## Rebuild

With the existing Python dependencies and `cards/requirements.txt` installed:

```powershell
python -B scripts\build-rich-card-assets.py
python -B scripts\build-rich-banner.py
python -B -m unittest discover -s tests -p test_rich_banner.py -v
```

The checked-in icon/schema are used locally. Only an explicit
`--fetch-official` request downloads their recorded official URLs; changed
upstream hashes fail for review. The banner generator requires the pinned Pillow
version for byte reproducibility. `build-rich-banner.py` updates only its own
topic node and the context-only HR example, not the flow or workbooks.

## Host validation and fallback limits

- The official 1.5 schema says PNG data URIs are supported by Image.url from
  Adaptive Cards 1.2. Schema support does **not** prove rendering in a particular
  Copilot Studio, M365 Copilot or Teams host.
- Each fully materialized scope card is bounded to 12,000 UTF-8 bytes; image
  source hashes are checked. No result rows can be removed by this budget,
  because the card contains none.
- `fallbackText` is contextual text for unsupported-card handling. It does not
  guarantee recovery from channel content filtering or image transport failure.
- The node's `disabled` property is the source-level feature gate. Disable it
  if the intended host does not render the banner correctly. Do not replace the
  established four-column results layout as a workaround.
- Validate the full product-loaded topic and Message card editor in a fresh,
  same-profile authoring context without invoking the flow. An actual
  M365/Teams result-rendering check requires an owner-approved release
  and host test; offline examples are not evidence of that outcome.

Official schema validation and offline checks passed. In the originating draft,
the native Copilot Studio Message card editor rendered HR and IT banners and the
SharePoint icon, with the formula evaluated as a Record and no topic errors.
Those checks used reversible, unsaved scope literals in the designer; the dynamic
binding was restored and the local preview edits discarded. They were not
conversations, live searches, exports, or M365/Teams delivery tests. That dated
designer evidence remains historical and separate from the later runtime proof.

## Published M365 owner-account proof

The owner-published agent passed **25/25 runtime checks and 13/13 source-date
checks** on 2026-09-12, using banner-only flow revision
`ebfc9aa634c835c8ee7ac93c74d10048647457b3d55c8e2cbbddb318fdea8019`.

- **HR / annual leave:** the purple banner and labelled SharePoint icon rendered
  with two genuine results, one page and one document, in four separate columns.
  Two private Excel rows and the canonical source dates were verified; one
  verified-profile email was accepted by the connector.
- **IT / deliberate no-match:** the blue banner and SharePoint icon rendered.
  The exact no-match response was verified in the M365 transcript and native
  run; workbook and email actions were skipped.
- The complete HR banner/header/pending callout/table/footer was captured at
  67% zoom, and the table was legible at 100%. IT's approved public crop proves
  its banner/icon; an unrelated later full-output crop was excluded.

These are owner-account M365 results, not Teams desktop/mobile, non-owner,
revocation/negative-ACL, other-host or other-theme runtime proof. Connector email
acceptance is not inbox receipt. The two-row run does not repeat the historical
112-result paging test or establish 150-site scale.

## Later table-polish result and host limitation

The separate published-M365 **IT / devices** run on `3a4b9ca0...` passed
**23/23 functional runtime checks and 15/15 source-date/parsed-markup checks**.
It returned four rows (one page and three documents), verified four private
Excel rows and eight exact source timestamp/calendar comparisons, and obtained
one verified-profile email acceptance.

At verified 100% zoom, bold linked titles and inside-link file/page glyphs were
visible. Short tags rendered as **monospace inline code, not colored pills**;
long plain tags wrapped, with all four rows and tag text visible without clipping.
**`HOST_ALIGNMENT_NOT_HONORED`: M365 left-aligns date values despite the source
`:---:` markers.** This is functional verification with a recorded host limitation,
not a blanket visual pass. The owner approved keeping this layout and the portable
markers; no CSS, padding workaround or redeployment is required.

This newer test captured its inputs and table/full footer, not a new full-banner
composite. The earlier HR/IT banner proof remains scoped to `ebfc9aa...`.
Teams, non-owner/negative-ACL/revocation and other-host behavior remain unverified;
email acceptance is not inbox receipt, and four rows do not repeat the historical
112-result paging run or the earlier deep workbook-UI audit. Other environments
must validate their own rendering and caller connections. No turnkey import or
channel-wide success is implied.
