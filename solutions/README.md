# Unmanaged solution reference

[`CorpNetSearchHubReference_1_0_0_0_unmanaged.zip`](CorpNetSearchHubReference_1_0_0_0_unmanaged.zip)
is a **real unmanaged Power Platform solution package**, not a ZIP of authoring YAML.
It was produced from a supported Dataverse solution export of the existing agent
and native runtime flow, adapted offline, and rebuilt with **PAC 1.47.1
SolutionPackager**.

**New-tenant import and runtime: UNVERIFIED.** Successful packing, roundtripping
and offline tests establish package/reference consistency, not successful import,
platform dependency availability, target permissions or production readiness.
The existing source-environment M365 evidence is not a test of this sanitized ZIP.

## Included—and deliberately excluded

| Included component | Count / purpose |
| --- | --- |
| CorpNet Search Hub agent | One authenticated classic-orchestration agent |
| Active bot components | 14 topics, one GPT instruction/model component, one native-flow tool |
| Native search/export flow | One flow; inputs `query`, `scope`; output `result` |
| Connection references | Five: SharePoint, Office 365 Users, OneDrive for Business, Excel Online (Business), Office 365 Outlook |
| Required relationship | Existing native-flow tool → packaged workflow |
| Embedded blank workbook | Exact portable runtime template; no populated search results |
| Contextual banners | Original five scope images and separately labelled official SharePoint icon, embedded in the topic |

The original solution also contained provisioning and retired flows. A separate
packaging-only container avoided exporting those workflows. Three disabled
diagnostic/legacy bot components and their two unused connector relationships
were excluded from the reference during allowlisted offline adaptation.

No fixture seeding flow, document corpus, SharePoint sites, lists, hub registration,
populated workbook, runtime history, channel conversation, token, credential,
source-tenant connection ID or connected workspace is included. Fixture content
and provisioning are separate repository materials, not solution components.
The original agent icon was omitted because its provenance was not established;
the separately labelled SharePoint integration icon remains subject to its own
rights notice.

## This is an HR/IT-like demonstration, not tenant discovery

The packaged policy intentionally contains **four fictional Contoso collections**:
CorpNet, HR, Finance and IT. `All` means all collections in that explicit inventory,
not every site in the tenant. The source environment's larger test corpus and
expanded inventory are not embedded here.

Before activation, customize and independently verify:

1. **Tenant and site inventory:** the SharePoint tenant origin, personal-site origin,
   hub collection GUID, each approved site collection GUID and `/sites/<name>`
   collection root. The builder derives the personal-site origin from the configured
   SharePoint tenant; this implementation does not support sovereign-cloud,
   cross-tenant, `/teams/`-root or arbitrary subweb inventory entries.
2. **Hub/search configuration:** registered hub and indexed association;
   every query is constrained by approved `SiteID` batches **and** hub `DepartmentId`.
   Being associated with a hub does not automatically discover or authorize a site.
3. **Source metadata:** verify index locators (`SPWebUrl`, `SiteID`, `ListID`,
   `ListItemID`), current item/file access, `File.TimeCreated`,
   `File.TimeLastModified`, and optional source fields `Department`, `TopicTags`,
   `DocumentType`. Tags are stored semicolon-delimited text, not managed taxonomy.
4. **Departments/topics:** HR, IT, Finance, CorpNet and their example questions
   are demonstration choices. Renaming or adding departments requires coordinated
   changes to inventory, topic validation/choices, instructions, fixed banner
   mappings and tests—not merely renaming a banner. Department is relevance,
   never an authorization boundary.
5. **Accounts and connections:** configure all five target-tenant references.
   Retain `runtimeSource: invoker`, tool `mode: Invoker`, no embedded fallback,
   and **Provided by run-only user** for every runtime connection. Import-time
   reference binding is not permission to run under maker credentials.
6. **Platform prerequisites:** target environment with Dataverse and Copilot Studio,
   applicable connector/licensing/DLP permissions, authenticated user access,
   Microsoft 365 services and supported model availability. `GPT5Chat` is a model
   hint, not a guarantee that the target environment offers that model.
7. **Security and publication:** owner-controlled target access/security group,
   authentication and channel setup; validate the complete product-loaded topics,
   flow checker and caller account behavior. Only the target owner publishes.

The limits and fail-closed behavior remain those of the portable source:
10 preview rows within 20 candidates; 100 results per search page; at most
1,000 export rows, 2,000 candidates, 40 pages and 12 batches of 20 collections.
Index estimates are not verified-export counts. Chat confirms export startup,
not completion or inbox delivery. Private workbook checks precede verified-profile
email. These limits do not constitute production coverage or load validation.

Both packaged search request paths now sort **document-ID ascending**, not by
relevance. Preview candidates follow index order within each bounded batch;
up to ten verified results are not the relevance-ranked “best ten” or a globally
ranked top ten. Metadata hydration may reorder workbook rows. The change was
selected after source-owner read-only diagnostics covered 512 combined and 400
body-only matches without overlap, while rank-first requests still overlapped.
Those probes are **not native agent/export proof**. A subsequent owner-started
connected-source run separately verified all 512 caller-hydrated sources and
512 private Excel rows, with one accepted verified-profile email in 26m46s.
That does not test an import of this sanitized package. See
[stable paging](../agent/flows/search-export/stable-paging.md) and the
[completed native-run evidence](../docs/scale-runtime-validation-summary.json).

## Import safety defaults

The package sets **`publishOnImport: false`**, requests an empty channel list,
and includes the workflow with **StateCode 0 / StatusCode 1**. These are intentional
reference-package settings; actual target import behavior still needs verification.
Do not enable the flow or publish the agent while the fictional configuration
remains. The authentication mode is preserved; this is not an anonymous agent.

The PAC-generated [`deployment-settings.template.json`](deployment-settings.template.json)
contains:

- Five empty `ConnectionId` values, to be replaced with approved **target** bindings.
- An all-zero `CopilotAgents[].AadGroupId` scaffold value, **not a selected security
  group or evidence of a safe sharing policy**. Select an appropriate target Entra
  security group and verify sharing.
- No environment variables/current values. **Changing deployment settings alone
  does not retarget SharePoint URLs, hub IDs or inventory inside the flow.**

Copy it to ignored `deployment-settings.local.json` for target bindings. Never
commit filled settings, connected exports or target-policy copies.

Use the supported Power Apps **Solutions → Import** experience, or the supported
PAC import command with reviewed local deployment settings. This repository does
not execute an import, auto-publish or configure authentication. Review importer
warnings and required components rather than overriding missing dependencies.
After import, verify all bindings and disabled/unpublished status before any test.
Use a separate isolated development environment. **Do not import this reference
back into the original demonstration environment**, or another environment already
containing these schema/component identities, without a separately reviewed upgrade
plan: unmanaged import can merge into and change existing components.

## Rebuild from the complete included source

`src` is the actual supported unpacked solution layout, including bot metadata,
component data, relationship data, workflow metadata and manifests. The existing
`agent` tree remains the readable portable authoring source.

From this directory, after installing Power Platform CLI:

```powershell
python -m pip install -r ..\agent\requirements.txt
.\rebuild.ps1
# If pac is not on PATH:
.\rebuild.ps1 -Pac "C:\path\to\pac.cmd"
```

The build performs no cloud operation. It:

1. Compiles all 16 active components from the standing portable authoring source,
   removing local `mcs.metadata` and consistently rebinding both native `flowId`
   references to the **packaged intrinsic workflow identity**.
2. Copies the exact portable native flow definition into its exported workflow
   wrapper; it does not regenerate or alter the standing agent source.
3. Uses `pac solution pack --packagetype Unmanaged`, regenerates the unbound
   deployment-settings template and runs the 13 solution tests.

The build writes its current hash/entry inventory to ignored `build.local.json`.
ZIP timestamps can change the archive hash even when every component is identical.
`validation.json` and `component-inventory.json` are the **shipped release snapshot**;
a local rebuild does not silently renew that historical evidence.

To deliberately customize a **private local development copy**, follow the
configuration guidance in [`agent/README.md`](../agent/README.md), rebuild that
copy's generated flow with its existing builder, then run this solution build.
`runtime\search-policy.json` starts in `fictional-reference` mode with false
verification flags; `configured` mode rejects sample identifiers and unverified
configuration. Flags are owner assertions, not automated validation. Package
tests intentionally reject non-reference locators/GUIDs: adapt the private
validation policy explicitly when targeting a real tenant, and never publish
that connected package as this neutral reference.

The package keeps the intrinsic workflow GUID consistently in the manifest,
workflow filename/metadata, topic/tool bindings and relationship. Do **not**
blanket-replace GUIDs: that breaks solution references. Bot components and
connection references are identified here by schema/logical names. The retained
workflow identity is a solution-component key, not a tenant/site/connection locator.
See [`component-inventory.json`](component-inventory.json) for the narrow identifier
classification and all included source paths.

The older `CorpNetSearchCount-CallerPermissions` **tool schema name** is retained
for reference integrity; its implementation calls the current full search/export
flow. It is not the retired count-only workflow.

## Validation boundary and rights

The package has ZIP CRC/integrity checks, 13 package/reference tests, 68 complete
portable-agent tests and a supported PAC **unpack → pack → unpack** semantic
roundtrip. See [`validation.json`](validation.json) for the artifact hashes and
precise proof. No import, runtime query, export/email test or agent publication
was performed during package export/build. Its timestamped validation snapshot
therefore retains the then-pending native-test status; the later source-runtime
result is recorded separately above, not retroactively asserted as package
import evidence. The related source-environment deployment
intentionally changed only two native-flow `SortList` properties using fresh
ETag guards. Agent/topic/model/connection records and owner publication were
preserved; the reference package was then synchronized offline.

Current M365 rendering evidence for the connected source shows readable bold
linked glyphs and monospace/wrapped tags; M365 ignores date-centering markers
(`HOST_ALIGNMENT_NOT_HONORED`). Those host observations do not validate this ZIP
in another tenant or Teams. Non-owner behavior, inbox receipt and production scale
remain independent validation work.

Read [`ASSET-NOTICE.md`](ASSET-NOTICE.md). Microsoft retains rights in its unmodified
product icon; no project-wide license has been selected, and public redistribution
requires owner rights/license review. Packing an asset does not broaden its license.
