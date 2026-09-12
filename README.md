# SharePoint Search Hub

**One Copilot Studio agent. Multiple approved SharePoint sites. Source-linked results and a private Excel export.**

SharePoint Search Hub is a reference implementation for searching a corporate
hub-and-spoke estate without creating a separate agent for every department.
The agent guides the user through a scope and keyword search, shows a compact
preview with real source links, source dates and stored tags, and continues the same request
into a filterable workbook delivered through the selected account's mailbox.

> **Private preview, prepared for future public review.**
> This repository contains publication-safe reference source, not a
> tenant-connected solution export or a production-ready release. Keep it
> private until the [public-release checklist](docs/public-release-checklist.md)
> is complete. GitHub Pages is not enabled.

## What it does

| Capability | Behavior |
|---|---|
| Guided search | Select `All`, `CorpNet`, `HR`, `Finance`, or `IT`, then supply plain search words or `*`. |
| Hub-and-spoke coverage | Search an explicit inventory of approved site collections, including multiple sites in one department. A hub URL alone is not automatic discovery. |
| Files and pages | Retrieve matching documents and SharePoint pages, subject to indexing, current access and configured bounds. |
| Useful chat preview | Show up to ten verified rows in four separate columns: linked file/page, Created (UTC), Modified (UTC), and stored tags. Missing metadata is not invented. |
| Private workbook | Continue into a genuine Excel table containing verified exported rows, source links and metadata, including the previewed rows when they remain accessible. |
| Verified-account delivery | Use caller-provided connectors and the verified profile's mailbox, not an email address supplied in chat. |
| Honest outcomes | Distinguish an index estimate, displayed results, export started, completed rows, partial completion and the email action. |

The current source adds a compact workbook with top-aligned rows, readable
calendar dates, full timestamps retained in hidden columns, and an actual
scope/query/completion summary. Ten preview rows are selected through bounded
retrieval, not a guarantee of a globally ranked top ten across the estate.
Historical screenshots retain their original five-row presentation; current
four-column captures explicitly show the narrow-pane wrapping limitation.

This is a **controlled search-and-export experience**, not a general-purpose
policy-answering bot. It does not synthesize company policy from the model's
general knowledge or fall back to an unrestricted web search.

## Architecture at a glance

![SharePoint Search Hub architecture](docs/images/architecture.svg)

[Architecture and trust boundaries](docs/architecture.md) ·
[Example prompts and outputs](docs/examples.md) ·
[Setup and adaptation](docs/setup.md) ·
[Evidence and limitations](docs/validation.md)

## Quick demonstration

Start with **`Search SharePoint`**, choose **`HR`**, then enter **`leave`**.
Use **`All`** and **`*`** to exercise the configured cross-site search rather
than only the corporate hub.

The chat presents a small result preview; the workbook is the place for the
larger result set. It must not claim an email was sent merely because the flow
returned an initial response.

The [examples guide](docs/examples.md) separates observed demonstration
behavior from illustrative output. Counts are snapshots, not fixed values for
another tenant.

## Real product screenshots

<img src="docs/images/live-workbook-compact.png" width="900" alt="Actual compact 112-row workbook with separate created and modified date columns">

**Verified owner-account draft, 12 September 2026.** The final four-column
`All` / `hubspokeverify` conversation passed **45 functional checks**, including
ten linked/date-bearing rows, actual **100 + 12 search pages**, and **112 exact
Excel rows across ten collections**. All ten preview links were included;
224 source timestamps/calendar values, private ACL and email acceptance matched.

The actual workbook capture above comes from the preceding run using the
identical template. **Current four-column chat headers and dates wrap severely
in the narrow Studio pane**; this is not polished narrow-client or Teams proof.
Browser and account identifiers are cropped out.

[View all screenshots, including the clearly labeled historical baseline](docs/screenshots.md).
These are genuine captures, not mockups. This is owner-only draft evidence,
not non-owner permission, published-channel or production-scale proof.

## Repository guide

| Area | Purpose |
|---|---|
| [`agent/`](agent/) | Portable agent/source reference and component-specific instructions. |
| [`docs/architecture.md`](docs/architecture.md) | Components, request lifecycle, identity boundaries and search semantics. |
| [`docs/examples.md`](docs/examples.md) | Guided prompts, output shapes and negative-path examples. |
| [`docs/screenshots.md`](docs/screenshots.md) | Genuine cropped chat, native-tool binding and topic-response captures, with their evidence limits. |
| [`docs/setup.md`](docs/setup.md) | Environment preparation and safe adaptation to a different tenant. |
| [`docs/validation.md`](docs/validation.md) | What was observed, what remains unproven and how to repeat the checks. |
| [`docs/public-release-checklist.md`](docs/public-release-checklist.md) | Review gates before changing visibility or enabling a public site. |

## Important boundaries

- A department is a relevance filter, **not an authorization boundary**.
- The selected authenticated connector account is the effective identity. It
  is not assumed to be identical to the chat channel's sign-in account.
- Runtime SharePoint, profile, OneDrive, Excel and email connections remain
  **provided by the invoking user**. Provisioning credentials are not a
  search fallback.
- `TopicTags` is a semicolon-delimited text column, not managed taxonomy.
  Displaying stored tags does not mean tag filtering is implemented.
- `PolicyStatus` is not selected, exported or filtered. Draft and archived
  documents can be returned; this is not an approved-policy-only search.
- Search indexing is eventually consistent. Newly published content can be
  present in SharePoint before it appears in search.
- The implementation has explicit row, candidate, page and site-batch limits.
  A capped or failed export must not be described as complete.
- Owner-account demonstration evidence is not a non-owner permission-denial
  test, a 150-site performance result or a SharePoint-channel rollout.

All demonstration policies and facts are fictional. There is no open-source
license grant yet; licensing is a deliberate public-release decision.
