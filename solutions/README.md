# Unmanaged solution reference

[`CorpNetSearchHubReference_1_0_0_0_unmanaged.zip`](https://ryanbowie.github.io/copilot-studio-sharepoint-search-hub/downloads/CorpNetSearchHubReference_1_0_0_0_unmanaged.zip)
is a **real unmanaged Power Platform solution package**, not a ZIP of authoring YAML.
It was produced from a supported Dataverse solution export of the existing agent
and native runtime flow, adapted offline, and rebuilt with **PAC 1.47.1
SolutionPackager**.

**Exact download: native Sandbox import SUCCEEDED on 21 September 2026 UTC.**
The async operation completed successfully, the import job reached 100% with no
failed result stages, and all **24 expected solution memberships** were present:
one bot, 16 components, one workflow, five references and one tool relationship,
with no extras. The 183-action workflow was **Off**; agent publication fields
were empty, `publishOnImport=false`, and `channels=[]`. All five references were
unbound and retained Invoker behavior. The exact tested ZIP bytes are distributed
here, not a subsequent untested repack.

**This proves one isolated import, not a configured deployment.** Cross-tenant
portability, runtime identity/permissions, native UI/save editability and production
readiness remain unverified. No connections, permissions, tenant configuration,
publication or runtime execution were changed after import. Inactive test
components were left in the sandbox.

**Earlier failures are preserved.** Two individually authorized 20 September
attempts used the original 64,159-byte ZIP. The first request was rejected with
`0x80040216`; a corrected minimal request reached an async operation that failed
with the wrong-child-node exception in `SourceControlHandler.ImportEntityFromFile`.
Neither left matching components. Comparing authentic native export format
identified a leading XML declaration on the public bot fragment. Removing only
that declaration and its CRLF (40 bytes) preserved the entire bot element and
all other 38 entry payloads. The separately authorized third attempt, after a
fresh zero-collision preflight, imported the corrected archive successfully.
This strongly supports the narrow format correction without attributing every
earlier error to a single cause.
See the [sanitized target-verification record](import-verification.json).
The instructions below describe the setup still required after import.

## Import, not a source archive

Download the ZIP above and select **that file directly** in the solution importer.
Do not extract/re-ZIP it or import the GitHub source archive, a flow JSON download,
or the blank workbook. This is one solution containing the actual agent and its
one complete runtime flow: search, preview, paging, workbook creation/readback and
email continuation are stages of that flow, not missing separate flow packages.

The verified download is **64,130 bytes**, with 39 entries and root
`solution.xml`, `customizations.xml`, and `[Content_Types].xml`.
Its SHA-256 is
`c4e0fed185ded365d51fb676b588d162780a55b91c2f23494f52304321989dad`.
The [component inventory](component-inventory.json) records every entry's hash
and classifies the identifiers intentionally retained. A matching checksum
establishes the exact tested download, not universal import/runtime compatibility.
The filename and solution version are unchanged from the earlier failed archive;
compare the checksum and byte count, not just its name.

## Import then set up

### 1. Prepare an isolated target

Use a fresh development environment with Dataverse and Copilot Studio, at least
the applicable System Customizer/create privileges, and permission to import
unmanaged customizations. Confirm licenses, capacity, consent and DLP permit all
five Microsoft connectors below, including their combined use. Have a target
owner and a separate authorized test user. Keep the sample department names for
the first pilot to avoid changing the conversation as well as tenant settings.

Caller-provided connections must be supported by the environment and intended
channel. Microsoft's current [agent-flow guidance](https://learn.microsoft.com/microsoft-copilot-studio/advanced-flow-create#manage-which-connections-are-used-by-the-flow)
excludes customer-managed-key (CMK) environments from this caller-credentials
path. Treat an unsupported environment as a blocker, **not** a reason to replace
Invoker connections with a maker account.

Do not use the original demonstration environment or an environment containing
matching component identities. An unmanaged import can overwrite existing
customizations; deleting its solution container does not undo those changes.
Before importing, explicitly select the target environment and check its solution
and component lists against [the inventory](component-inventory.json): solution
`cnh_CorpNetSearchHubReference`, agent schema `cnh_corpnetSearchHub`, workflow
`96794fbd-20ae-f111-aaab-002248403bef`, component schemas and all five reference
logical names. **Stop on any collision**, even if the solution container itself
is absent. Do not accept an implicit/default environment or overwrite existing
components as a smoke test; an intentional update requires a separate review.

### 2. Import the unchanged ZIP without activation

1. Select the intended environment in Power Apps or Copilot Studio and open
   **Solutions → Import solution → This device → Browse**. Select the downloaded
   `CorpNetSearchHubReference_1_0_0_0_unmanaged.zip`, then **Next**.
2. Check the solution identity `cnh_CorpNetSearchHubReference`, version `1.0.0.0`,
   and unmanaged type. Under **Advanced settings**, clear
   **Enable Plugin steps and flows included in the solution**. This does not
   deactivate an already-active target flow, which is another reason to use a
   fresh environment. Do not enable or publish as part of setup.
3. When prompted, select/create approved **target-tenant** connections for the
   five references below. There are no environment variables in this package;
   the absence of a tenant-configuration prompt is expected.
4. Review all dependency warnings. Resolve actual missing prerequisites through
   supported administration; never strip required objects to force success.
   Complete the import only after reviewing the selected target and bindings.
5. Wait for the import outcome. On failure, download the import log and keep the
   environment unchanged while diagnosing it. On success, inspect the solution:
   one agent, 14 topics, one GPT component, one native-flow tool, one workflow,
   five connection references and the tool-to-workflow relationship. Verify the
   actual flow is **Off**, the agent is unpublished and no channel is enabled.

The verified sandbox import deliberately left all five references unbound; no
connection was created or selected. The steps above remain the target owner's
setup responsibilities. See Microsoft's [solution import steps](https://learn.microsoft.com/en-us/power-apps/maker/data-platform/import-update-export-solutions)
and [agent import/authentication guidance](https://learn.microsoft.com/microsoft-copilot-studio/authoring-solutions-import-export#import-the-solution-with-your-agent).

### 3. Bind connections without changing caller identity

| Packaged logical reference | Target connector | Runtime purpose |
| --- | --- | --- |
| `cnh_corpnetsearch_sharepoint` | SharePoint | Scoped search, current-source reads and private-report ACL checks |
| `cnh_corpnetexport_r3_profile` | Office 365 Users | Selected profile, directory identity and verified mail |
| `cnh_corpnetexport_r3_onedrive` | OneDrive for Business | Personal-drive root and workbook creation |
| `cnh_corpnetexport_r3_excel` | Excel Online (Business) | Write and read back the actual workbook |
| `cnh_corpnetexport_r3_outlook` | Office 365 Outlook | Verified-profile notification and workbook-link email |

Open the imported flow's **Run-only users → Edit** settings where supported and
keep all five connections **Provided by run-only user**. Preserve
`runtimeSource: invoker`, tool `mode: Invoker`, and no embedded maker fallback.
Import-time bindings alone do not establish runtime caller credentials. If the
product cannot preserve these settings, stop rather than substituting an owner.
Each pilot caller needs provisioned OneDrive, directory mail, source permissions
and supported connector consent. Internal profile/SharePoint/drive alignment is
checked; channel sign-in and Excel/Outlook principal attestation are not proven.

### 4. Configure the imported implementation for your tenant

**Unmanaged does not prove editability.** Read-only inspection of the imported
sandbox records found the following managed properties; it did not exercise
the native editor or save changes:

| Imported records | Observed `IsCustomizable` | Setup boundary |
| --- | --- | --- |
| Search/export workflow | `true` | Compiled tenant-policy edits belong here; an actual UI/save was not tested |
| Profile, OneDrive, Excel and Outlook references | `true` | Target bindings still need owner review; none were configured in verification |
| Bot and all 16 bot components | `false` | Do not assume topics, instructions, model or authentication are editable |
| SharePoint reference | `false` | Target binding/edit behavior must be verified, not inferred from other references |

Keep these managed properties intact. If the product blocks authentication,
reference binding or required component editing, **stop** and obtain a supported
owner-reviewed ALM path; do not clear flags, substitute maker credentials or
strip components. A private rebuild and intentional update also need review:
successful base import does not prove that a configured update will be accepted.
Keeping the example department names avoids unnecessary bot authoring changes,
but does not remove the authentication and connection prerequisites.

Keep the flow off. Import brings the implementation into the target, but **does
not create or discover your SharePoint estate**. Follow the
[source-estate checklist and customization matrix](../docs/setup.md#from-an-empty-sharepoint-tenant):
register/select a hub, associate approved collections, establish permissions and
indexing, record real collection IDs, and verify optional metadata internal names.
No shared export library is required: output goes to the verified caller's
personal-drive root using the embedded blank workbook.

The tenant policy is compiled into multiple flow actions, not environment
variables. Filling connection IDs or changing only `Initial_search` Site Address
is insufficient. There is **no post-import setup wizard**. Choose either
coordinated changes to the imported flow through supported editors, using the
[complete request reference](../docs/sharepoint-actions.md), or a reviewed
private source rebuild as an intentional unmanaged update to this newly imported
solution. The [private build instructions](../agent/README.md) and
[rebuild section below](#rebuild-from-the-complete-included-source) explain that
route. Stock public-reference tests intentionally reject real tenant locators;
target validation must be adapted deliberately, not bypassed.

**Target editability is also unverified.** Some exported bot/component/reference
metadata carries `iscustomizable=0`. Do not infer unrestricted editing merely
from the unmanaged label. Confirm supported editing/loading in the sandbox;
if blocked, stop and retain the product's error rather than flipping exported
metadata or replacing the imported components with a disconnected scaffold.

Replace the fictional tenant origin, search site, hub ID and **every** approved
site URL/ID consistently with the derived personal-site origin, KQL and URL
validation checks. Retain the hub AND approved-site restrictions and all identity,
hydration and delivery gates. `All` means your explicit inventory, not all tenant
sites. Keep private configuration/exports out of this public repository.

For product-only configuration, open the solution-aware flow through
**Solutions → flow → Edit**, while stopped. The exact compiled locations below
are inside the packaged workflow's `properties.definition`. Find these named
actions in the designer/request reference; preserve all other expressions.
The builder is a reproducibility aid, not a runtime dependency.

| Compiled location | Coherent target change |
| --- | --- |
| `Approved_scopes.inputs` | One structured inventory: every scope/batch `Kql`, `Sites` dictionary key, `siteId`, `url`, `department`; update `All` and departmental copies. `DepartmentId` is the registered hub's collection GUID |
| `SharePoint_profile.inputs.parameters.dataset`, `Initial_search.inputs.parameters.dataset`, `Next_search_page.inputs.parameters.dataset` | Three corporate search/profile endpoint leaves |
| `Personal_site_available.expression`, `Remember_report_url.inputs.value` | Two derived personal-site origin/prefix leaves |
| `Preview_basic_locators.inputs.where`, `Preview_item_verified.expression`, `Preview_row.inputs.URL` | Three preview tenant-boundary/link-origin leaves |
| `Basic_locators.inputs.where`, `Select_verified_rows.inputs.select.URL` | Two export tenant-boundary/link-origin leaves |

That is **one inventory object plus ten additional leaves**, including dictionary
keys, not a single URL to replace. The unchanged package's
`fictional-reference` mode and false verification flags describe the local build
policy; they are **not an activation interlock** inside the flow. Keep it off
until the real configuration and permissions are verified.

Open the imported agent under **Objects → Agents** in Copilot Studio and
**reconfigure authentication after import**. Retain Integrated/Always
authentication and classic orchestration; verify effective model availability,
target audience/sharing and both topic/tool bindings to the imported flow.
The old `CorpNetSearchCount-CallerPermissions` tool schema calls the complete
search/export flow; do not replace it with a count-only action. The all-zero
security-group setting is not a valid configured audience.

### 5. Enable for a controlled smoke check, then publish separately

After configuration and flow/agent checker review, the target owner can enable
the flow for draft testing. If the product requires saving/publishing the flow,
that is separate from publishing/sharing the agent. Start with a small known
corpus and preserve the prompt sequence **Search SharePoint → HR → leave**
(or a term actually present in that target corpus).

| Check | Expected result / release gate |
| --- | --- |
| Loaded conversation/tool | Both questions load; topic and registered tool call the same flow with `query` and `scope`, returning `result` |
| Positive file and page | At most ten verified links, source UTC dates and actual stored tags; banner is context, not proof of success |
| Completed export | Startup preview is not completion; inspect the finished run and real Excel rows, including still-accessible preview rows, dates/tags and completion metadata |
| Private delivery | Verify final workbook permissions and verified-profile recipient; check actual inbox receipt separately from Outlook action acceptance |
| No-match and invalid input | Clear controlled result; genuine no-match creates no workbook or email; no invented results |
| Non-owner allowed/denied data | Only current accessible sources disclosed; denied items absent from preview/workbook; test failures/revocation without weakening guards |
| Connector mismatch or failure | Explicit failure, no success-shaped response or maker-account fallback |
| More than 100 matches | Follow paging, duplicates, bounded/partial outcomes and row readback; this is not required for the first small smoke check |

Only after target acceptance and an explicit owner release decision, **publish
the agent**, configure the intended channel and share with the approved audience.
Retest in that client (M365 and Teams are separate checks), including caller
sign-in. Importing a solution or deploying this website does not publish an agent.

### Troubleshooting

| Symptom | Check / safe next action |
| --- | --- |
| Importer rejects the file | Use the direct solution ZIP, not a GitHub HTML preview/source archive. Check filename, size, SHA-256 and the three root manifests; do not rename another ZIP |
| Import fails or reports missing dependencies | Download the import log / inspect solution history; verify environment features and required objects. A clean manifest/PAC pack is not proof of target dependency availability |
| Import blocked by policy or connector binding | Ask the environment owner to confirm unmanaged customizations, privileges, licenses, DLP and connector support. Do not broaden access to make a test pass |
| Flow is already On after import | Stop before invoking the agent; verify actual state and whether pre-existing components were updated. The unchecked activation option does not turn existing flows off |
| Agent asks only one question or tool cannot resolve | Inspect the fully loaded topic and both native-flow bindings in Studio; reopen a fresh authoring/test tab. YAML parsing alone does not prove product loading |
| No results despite working file links | Confirm compiled target policy, site/hub IDs, approved inventory, indexing and current caller access; do not remove hub/scope constraints |
| Preview returned but no delivery | Inspect continuation status, Excel write/readback, final ACL, identity/consent and notification branches. Startup is not completion; do not rerun blindly and create duplicate reports |
| Private-drive or account-alignment check fails | Verify OneDrive provisioning and selected connector accounts; retain fail-closed checks. Do not substitute a shared drive or user-entered recipient |
| Model, caller credentials or channel unavailable | Stop and establish supported target prerequisites; switching to an owner connection, anonymous auth or another orchestration mode is a redesign, not setup |

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
   deployment-settings template and runs the solution tests.

The build writes its current hash/entry inventory to ignored `build.local.json`.
ZIP timestamps can change the archive hash even when every component is identical.
`package-validation.json`, `import-verification.json` and `component-inventory.json`
identify the **exact tested download**. `validation.json` is the unchanged
historical snapshot for the earlier archive. A local rebuild does not silently
renew any of that evidence or inherit the tested ZIP's fingerprint.

Keep `bots/*/bot.xml` and `botcomponents/*/botcomponent.xml` element-first,
without XML declarations or document-level wrappers. They are native
source-control fragments, unlike the top-level solution manifests. The
fragment regression checks their actual bytes, not just parsed element equality.

Git preserves PAC's CRLF line endings under `solutions/src/`, so a fresh
checkout can satisfy the package's byte-for-byte source checks on every platform.
Run the as-shipped solution tests **before regenerating the agent's workbooks**:
regeneration changes ZIP metadata and the embedded template bytes. If you
regenerate the agent source, run the solution rebuild too before comparing
that new source with a package. Do not weaken the template-byte checks or treat
the older shipped ZIP as a newly rebuilt artifact.

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

The [current package snapshot](package-validation.json) records 18 solution tests,
68 portable-agent tests, ZIP integrity, and a supported PAC
**unpack → pack → unpack** roundtrip. All 39 source files were semantically equal
and all 39 repacked entry payloads byte-identical. The separately tracked
[native import evidence](import-verification.json) is terminal success plus
actual component/state observations, not an inference from packing or request
acceptance. No target runtime query, workbook export, email or agent publication
was performed.

The unchanged [historical snapshot](validation.json) still records the earlier
archive's 13 package tests and then-pending native status. Its source-environment
deployment changed only two `SortList` leaves; it is not retroactively rewritten
as proof for the corrected package. The later 512-row source-runtime evidence
also remains separate from this target's import-only result.

Current offline checks compare PAC-generated XML with the unpacked source,
decode/check the blank workbook and all six manifest-matched inline PNGs, and
check every published archive entry against the reviewed inventory. The
authentic original native export was inspected privately to establish the
bot-fragment format; raw connected exports and source identifiers are not
redistributed. This narrow provenance comparison is not a claim of full historical
runtime equivalence. No missing core search/export logic was found relative to
the complete included portable source. All 38 unaffected entry payloads and
the runtime definition remain unchanged from the reviewed archive.

Current M365 rendering evidence for the connected source shows readable bold
linked glyphs and monospace/wrapped tags; M365 ignores date-centering markers
(`HOST_ALIGNMENT_NOT_HONORED`). Those host observations do not validate this ZIP
in another tenant or Teams. Non-owner behavior, inbox receipt and production scale
remain independent validation work.

Read [`ASSET-NOTICE.md`](ASSET-NOTICE.md). Microsoft retains rights in its unmodified
product icon. This public reference grants no project-wide open-source license;
the [rights notice](../NOTICE.md) and upstream terms apply. Packing or publicly
hosting an asset does not broaden its license.
