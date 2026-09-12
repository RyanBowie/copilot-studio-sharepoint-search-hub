# Portable agent reference source

This is an allowlisted, sanitized adaptation of an existing Copilot Studio agent,
not a solution ZIP, supported turnkey import package, or proof of production readiness.
`contoso.sharepoint.com`, every `00000000-...` GUID and every
`REPLACE_WITH_CALLER_...` connection name are **fictional placeholders**.
No connected workspace, credentials, live resource identifiers or populated workbooks
are included. The source previews up to ten verified linked results with UTC source
dates and stored tags, and generates a compact private workbook. This reference
tree and its offline tests do not establish a deployment or live runtime outcome.

## Local build and tests

From this `agent` directory, using Python 3.10 or later:

```powershell
python -m pip install -r requirements.txt
python -B scripts\build-reference.py
python -B -m unittest discover -s tests -p "test_*.py" -v
```

The commands generate only local artifacts. They do not authenticate, provision,
import, activate, publish or email anything. The build generates the blank base
workbook, native runtime workbook, flow definition and placeholder connection
references. Tests are offline structural/contract tests, not platform execution
or workbook-formula-engine validation.

## What to configure and rebind

1. In an isolated development environment, create an authenticated classic
   Copilot Studio agent and a native agent-callable Power Automate flow through
   the supported product experience. This tree alone does not register resources.
2. Independently verify the allowed tenant, hub registration, indexed hub
   association, each site collection ID, source permissions, index locators and
   source metadata. Update `runtime/search-policy.json` in an **unpublished local
   configuration copy**. Its `fictional-reference` mode and false verification
   flags permit offline compilation only; they do not attest to a deployment.
   `configured` mode rejects missing verification flags and sample identifiers.
   Verification flags are owner assertions, not automated proof.
3. Keep an explicit allowlist of separate site collections. The builder always
   combines `SiteID` batches with the configured hub's `DepartmentId` restriction.
   A hub URL never discovers or authorizes its spokes. Site URLs must be same-tenant
   HTTPS `/sites/<name>` collection roots. Runtime locators structurally permit
   descendant webs beneath an approved root with the same SiteID, but no live
   child-web validation is claimed. The inventory validator does not accept
   subweb entries, `/teams/` URLs, sovereign cloud hostnames or cross-tenant search.
4. Rebind **all five** connector references in
   `runtime/connection-references.json`, the generated flow and
   `connectionreferences.mcs.yml`: SharePoint, Office 365 Users, OneDrive for
   Business, Excel Online (Business), and Office 365 Outlook. Logical names in
   this tree are reference names, not existing environment resources.
   Keep flow runtime sources `invoker`, tool mode `Invoker`,
   `defaultToEmbeddedConnections: false`, and each run-only connection set to
   **Provided by run-only user**. Never substitute a maker or provisioning account.
   Product versions may serialize agent and flow connection references differently;
   recreate/rebind through the supported editor rather than treating this YAML
   manifest as an import contract.
5. Register/rebind the native flow tool and replace the shared flow GUID in
   `actions/SearchAndExport.mcs.yml` and `topics/SearchSharePoint.mcs.yml`.
   The action YAML preserves the observed tool shape with sanitized identity.
   The topic directly invokes the flow; it does not supply recipient, identity,
   raw KQL, token or site URL inputs. Preserve the `query`, `scope` -> `result`
   contract. The agent schema `cnh_corpnetSearchHub` is used in topic redirects;
   changing it requires consistent rebinding.
6. Recreate/apply and validate the topics, settings and instructions in Copilot
   Studio. Validate the native flow with the platform, verify run-only behavior
   under multiple users, and inspect actual source, destination and email results
   before any release. No cloud deployment scripts are supplied.
   The model hint is `GPT5Chat`; independently confirm supported availability in
   the target environment. Keep classic orchestration and existing security
   settings rather than enabling preview exceptions to match a reference.

Preserve long single-line topic values without soft wrapping. The included
`scripts/authoring_yaml.py` emits actual multiline strings as literal blocks and
does not soft-wrap single-line activity text. Validate the complete product-loaded
topic and scope prompt in a fresh authoring/test context after applying changes;
an old connected test tab can retain stale content.

## Current source contract

- Flow inputs: `query` and `scope` strings only. Supported topic areas are `All`,
  `CorpNet`, `HR`, `Finance`, `IT`; department is relevance, not authorization.
  Queries accept a single `*`, or 1–12 plain ASCII alphanumeric/hyphen-separated
  words within 160 characters. Raw KQL and stored-tag filters are not supported.
- Search: SharePoint REST index queries for files and pages, followed by current
  source reads using `SPWebUrl`, `SiteID`, `ListID`, `ListItemID` locators.
  Current file paths come from `File.ServerRelativeUrl`, not indexed titles/URLs.
  Optional stored fields are `Department`, `TopicTags`, `DocumentType`; metadata
  is discovered on each source list. `TopicTags` is semicolon-delimited text, not
  managed taxonomy. Missing tags display as `Not supplied`.
- Dates: both preview and export read canonical `File.TimeCreated` and
  `File.TimeLastModified` through the permission-checked current-item endpoint.
  These are source file/page dates, not crawl, export, library-item Modified or
  site-collection creation dates. Existing ModifiedUTC semantics are unchanged.
  PolicyStatus and ReviewDate are not selected/exported.
- Chat: up to 10 verified title links with source Created/Modified UTC calendar
  dates and stored tags, scanning at most 20 preview candidates. Ordering follows
  bounded batches, not a globally ranked top ten. The twenty-candidate budget can
  yield fewer than ten verified rows; the agent must not invent rows or imply that
  no other matches exist. Dates use `YYYY-MM-DD` with an explicit UTC legend;
  missing dates say `Not supplied`. Use four separate columns in this order:
  **File or page | Created (UTC) | Modified (UTC) | Stored tags**. The first cell
  contains only the working title link; dates must never appear beneath or beside
  the name. Retain the explicit four-column layout even in narrow panes; validate
  actual product readability without silently moving dates back into the title cell.
  Title/tag text is escaped for chat; tags exceeding 200 characters are shortened
  with a "full tags in Excel" notice. Excel retains full values.
- Success formatting: a restrained search heading, bold Scope/Index estimate
  summary and private-export-started callout identify the verified recipient while
  explicitly stating delivery is pending. The four-column table/row values are
  unchanged; two icons appear outside the table only. A separated footer retains
  privacy, preview/export bounds, partial-result and count-semantics caveats.
  No HTML/CSS or Adaptive Card redesign is used. No-match, failure and
  unavailable-preview responses retain their previous output.
- Export: 100-row search pages; caps of 1,000 written rows, 2,000 checked candidates,
  40 search pages, and 12 batches of 20 approved site collections. These are
  bounds, not a promise that a 240-site estate meets platform timeouts.
  The export loop has a 45-minute timeout; workbook read-back has a 5-minute
  timeout. These are configured loop ceilings, not measured latency or an SLA.
  Export continues in the same flow after the response; chat confirms startup
  only, not completion or delivery. Changed access, errors and caps can yield
  partial output. Zero index matches produce no workbook/email.
- Private workbook: `Results` filterable table and `ExportInfo` status/omission
  details. Source text is written literally; controlled hyperlink, date and
  metadata-summary formulas are the only calculated presentation fields. The
  sentinel row is intentional, not a sample result. Readback verifies full source
  values and normalized display dates before the link email.
- Identity: selected connector account is the effective identity, not proven equal
  to channel sign-in. Profile, SharePoint source and OneDrive destination ownership
  are checked; recipient is the verified profile's nonempty directory mail.
  Excel uses the verified drive and file, but the flow does not separately attest
  the Excel or Outlook connection's principal or email sender. No user-entered
  recipient is accepted. Workbook ACLs and written rows are verified before the
  successful link email; no anonymous/organization sharing link is created.

## Compact workbook and date contract

The base template has eight canonical source columns. The native runtime template
has eleven columns, initially `A8:K9`, with the **B9** freeze retaining the title
column and top rows:

| Column | Field | Presentation |
|---|---|---|
| A | Title | Verified title or filename fallback; wraps |
| B | Department | Stored value or approved-inventory fallback |
| C | Tags | Full stored value; wraps, never shortened in Excel |
| D | Type | Verified file/page type |
| E | ModifiedUTC | Hidden full `File.TimeLastModified` source string |
| F | SourceSite | Hidden approved collection root |
| G | URL | Controlled row-relative hyperlink displayed as Open file |
| H | CreatedUTC | Hidden full `File.TimeCreated` source string |
| I | Created (UTC) | Real numeric Excel calendar date, `yyyy-mm-dd` |
| J | Modified (UTC) | Real numeric Excel calendar date, `yyyy-mm-dd` |
| K | SourceURL | Hidden technical URL backing the hyperlink |

Hidden raw timestamps retain source precision, including fractional seconds.
Missing raw timestamps remain blank; visible date columns display `Not supplied`.
DATE formulas derive the UTC calendar date from those canonical values, without
changing them. The flow normalizes ISO-8601 or Excel-serial readback values before
comparing the displayed date with its expected source calendar date.

Body content is compact, top-aligned 10-point text. Only visible titles and tags
wrap; hidden raw/technical fields never wrap or contribute to intended row-height
calculations. Long visible tag content can legitimately require taller rows.
The smaller navy masthead preserves the existing style and filters. Scope/query
and row/file/page/status summaries look up actual ExportMetadata values, rather
than merely directing the reader elsewhere. This changes future generation only,
not already-delivered workbooks.

## Deliberate publication adaptations

Removed historical count-only/inline-search prototypes, pinned deployment scripts,
live exports, environment manifests, tools, connection metadata, evidence and old
documentation. Replaced the builder's dependencies on live deployment manifests
with explicit placeholder Invoker references. Replaced the legacy shared policy
compiler with a narrowly scoped native-flow policy validator; old 15-row, three-page
and tag-filter helper settings are **not** the active flow contract. Removed the
original publication timestamp and remapped a generated feedback node ID.
The core native search, preview, write, privacy and email action construction is
preserved. Blank workbooks are rebuilt from their reviewed layout code.
The reference runtime and base templates freeze at `B9`, matching the original
workbook layout and keeping the title column visible when scrolling horizontally.

The base and runtime templates remain blank: the only runtime row is the sentinel,
with controlled formulas and no source data. This package contains no run records,
populated layout examples, screenshots, connected deployment manifests or deployment
scripts. Native flow registration and connection rebinding remain product tasks.

No license has been selected. Private review comes first; the owner must decide
licensing and complete configuration, security, accessibility, performance and
deployment validation before public release.

## Packaging validation record

The local reference build and **42 offline tests** pass. Tests cover the four
fictional sites, fail-closed configuration, all five Invoker bindings, ten/twenty
preview bounds, 100-row source pages, canonical source-date selection, full raw
timestamp roundtrips, controlled date/display/readback expressions, hidden wrapping,
B9, summary formulas, hyperlinks and safe topic serialization. The embedded
workbook bytes match the included runtime template. No archived count-only test or
its connected-environment mismatch is included.
Five success-formatter tests use a small offline expression evaluator to check
hierarchy, unchanged row values, recipient escaping, caveats and verbatim
non-success responses. This evaluator is not the Power Automate cloud engine.

The blank base workbook has no formulas, hyperlinks or source rows. The runtime
template contains intentional controlled formulas, with full automatic calculation
enabled. These portable tests check structure/contracts and literal-data roundtrips;
they do not execute Power Automate expressions or calculate Excel formula caches.
Platform execution, native rendering, deployment and selected-user isolation remain
separate validation tasks. Neither historical live evidence nor the reference
inventory should be relabelled as proof of this feature revision.

## Teams publication boundary

Publication remains an owner operation; this source makes no channel,
authentication, tenant-policy or developer-preview changes. Do not assume that
Studio's four-column table will render identically in Teams desktop/mobile.
[Microsoft's Teams formatting documentation](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/format-your-bot-messages)
documents richer pipe-table support under `extendedmarkdown`, currently public
developer preview. This reference does not enable it. Ordinary links, UTC labels
and escaped text are retained, but actual Teams rendering and caller connections
must be verified separately before release.
