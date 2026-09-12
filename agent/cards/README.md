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

The working M365 Copilot four-column Markdown table is retained verbatim:
**File or page | Created (UTC) | Modified (UTC) | Stored tags**. Moving these
columns into a potentially narrower Adaptive Card has not demonstrated better
readability. The only ColumnSet in the banner has two columns, for the small
product icon and its label. There are no actions, inputs, result links, HTML,
CSS, remote image URLs, public hosting changes, or new connectors.

The `query`, `scope` → `result` flow contract, ten-row/twenty-candidate preview,
100-row paging, private Excel bytes, canonical dates, full stored Excel tags,
Invoker connections and all existing safety/error behavior are unchanged.
Already-published callers continue using their existing topic and Markdown.
Applying this new topic is a draft change; the owner decides whether and when
to republish after host validation.

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
conversations, live searches, exports, or M365/Teams delivery tests. A target
environment must still validate its own card transport/rendering after an
owner-approved release. No portable import or channel-wide success is implied.
