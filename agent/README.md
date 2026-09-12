# Portable agent reference source

This is an allowlisted, sanitized adaptation of an existing Copilot Studio agent,
not a solution ZIP, supported turnkey import package, or proof of production readiness.
`contoso.sharepoint.com`, every `00000000-...` GUID and every
`REPLACE_WITH_CALLER_...` connection name are **fictional placeholders**.
No connected workspace, credentials, live resource identifiers or populated workbooks
are included. The latest local source uses a two-column chat table; that does not
prove this version is deployed.

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
- Chat: up to 5 verified title links plus stored tags, scanning at most 20 preview
  candidates; ordering follows bounded batches, not a globally ranked top five.
  Title/tag text is escaped for chat; tags exceeding 200 characters are shortened
  with a "full tags in Excel" notice. Excel retains full values.
- Export: 100-row search pages; caps of 1,000 written rows, 2,000 checked candidates,
  40 search pages, and 12 batches of 20 approved site collections. These are
  bounds, not a promise that a 240-site estate meets platform timeouts.
  The export loop has a 45-minute timeout; workbook read-back has a 5-minute
  timeout. These are configured loop ceilings, not measured latency or an SLA.
  Export continues in the same flow after the response; chat confirms startup
  only, not completion or delivery. Changed access, errors and caps can yield
  partial output. Zero index matches produce no workbook/email.
- Private workbook: `Results` filterable table and `ExportInfo` status/omission
  details. Columns are Title, Department, Tags, Type, ModifiedUTC, SourceSite and
  URL, plus a hidden technical SourceURL column in the native runtime template.
  SourceSite is hidden by the existing layout. The runtime sentinel row and
  controlled row-relative HYPERLINK formula are intentional, not sample results.
  Source text is written literally. Only this controlled link formula is used.
- Identity: selected connector account is the effective identity, not proven equal
  to channel sign-in. Profile, SharePoint source and OneDrive destination ownership
  are checked; recipient is the verified profile's nonempty directory mail.
  Excel uses the verified drive and file, but the flow does not separately attest
  the Excel or Outlook connection's principal or email sender. No user-entered
  recipient is accepted. Workbook ACLs and written rows are verified before the
  successful link email; no anonymous/organization sharing link is created.

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
The runtime builder explicitly freezes at `A9` to reproduce the current runtime
template; the older base-template generator freezes its separate blank table at `B9`.

No license has been selected. Private review comes first; the owner must decide
licensing and complete configuration, security, accessibility, performance and
deployment validation before public release.

## Packaging validation record

Offline reference build succeeded and all **22 tests passed** on Python 3.14.3,
openpyxl 3.1.5 and PyYAML 6.0.3. A source/XML inspection covered all 34 packaged
files (62 expanded text/XML parts): no original tenant/connection/resource
identifiers, personal owner strings or local user paths were found; all GUID
literals are the documented fictional placeholders. The embedded workbook bytes
match the included runtime template. This is not an exhaustive secret audit.

LibreOffice was unavailable on the packaging host. The blank base workbook has no
formulas, hyperlinks or source rows; the runtime template's intentional controlled
HYPERLINK formula was inspected by the contract tests, not recalculated with an
Excel-compatible engine. Platform execution, rendering, deployment and selected-user
isolation remain separate validation tasks.
