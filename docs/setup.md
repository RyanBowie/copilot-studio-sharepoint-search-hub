# Setup and safe adaptation

This is a **customizable reference**, not a one-click production deployment.
It includes an [unmanaged solution ZIP and complete unpacked source](../solutions/README.md),
but no live tenant connections or permission to publish into another environment.
The [exact downloadable ZIP passed native Sandbox import](../solutions/import-verification.json)
on 21 September 2026 UTC: all 24 expected solution memberships, a stopped flow,
empty agent publication fields/channels, and five unbound Invoker references.
Both earlier failed attempts remain in the record. **Cross-tenant import,
configured runtime and effective UI/save editability remain unverified.**
The workflow and four references report customizable metadata; the bot, its
16 components and SharePoint reference retain non-customizable managed properties.
No connection binding, tenant configuration, native editing, runtime test or
publication was performed. Do not infer those capabilities from "unmanaged."

## Solution package route

Follow the [import-then-setup guide](../solutions/README.md#import-then-set-up).
[Download the actual solution ZIP](https://ryanbowie.github.io/copilot-studio-sharepoint-search-hub/downloads/CorpNetSearchHubReference_1_0_0_0_unmanaged.zip)
and import it directly into a separate development environment, without unzipping
or substituting the GitHub source archive. It contains the agent,
current native runtime flow and required references, with fictional target
configuration, unbound connections, no auto-publication and a stopped workflow.
The [deployment-settings template](../solutions/deployment-settings.template.json)
does not retarget the embedded SharePoint policy by itself.

HR, IT, Finance and CorpNet are sample departments. Adapt their topics, scope
validation, instructions and banner mappings together with the site/hub
inventory, metadata, account connections and model availability. The
[512-item fixture corpus](../fixtures/corpnet-demo/README.md#500-plus-scale-fixture)
is separate: importing the agent does not create SharePoint content or index it.
Its ten collection targets also require an explicitly approved ten-site
inventory; the packaged default deliberately has only four fictional entries.

Do not import this unmanaged reference into the original demonstration
environment, or over existing matching component identities, without a
reviewed upgrade plan. It can merge into existing components. Check actual
disabled/unpublished state, bindings and sharing after import rather than
assuming package defaults were applied.

## Prerequisites

- A suitable Copilot Studio / Power Platform environment and permissions to
  create or manage an agent, native flow and dedicated solution.
- Approved SharePoint collections with an intentional permission model.
- Caller-provided SharePoint, Office 365 Users, OneDrive for Business, Excel
  Online (Business) and email connections supported by the target environment.
- A private workbook destination and a genuine blank Excel table template.
- An account for positive tests and a separately authorized non-owner account
  for meaningful permission-denial tests.

Licensing, data policies, connector availability and channel support must be
checked in the target tenant. A successful owner demonstration does not prove
those conditions for another environment.

## From an empty SharePoint tenant

**Import creates agent/runtime components, not the SharePoint estate.** It does
not register a hub, create sites/libraries/pages, seed the 512-item corpus, assign
source permissions, provision user OneDrives or make SharePoint index content.
The website presents this [new-tenant checklist directly on the page](https://ryanbowie.github.io/copilot-studio-sharepoint-search-hub/#setup).

1. **Choose an isolated development environment and owners.** Confirm Dataverse,
   Copilot Studio and the five connectors' licensing, consent and DLP support.
   Identify a SharePoint administrator for hub registration/association and an
   owner for agent access/sharing. Check model availability rather than assuming
   `GPT5Chat` exists in the target environment.
2. **Import inactive, then configure.** In **Solutions → Import solution**, select
   the actual ZIP and clear **Enable Plugin steps and flows included in the
   solution** under Advanced settings. Bind the five approved target connections
   and review dependencies. Download the import log on failure. Check the actual
   agent/flow/component inventory and stopped/unpublished state; this checkbox
   does not deactivate an existing flow. There is no post-import setup wizard,
   and no environment-variable prompts that retarget the compiled tenant policy.
3. **Create or select the source sites.** A straightforward pilot retains one
   corporate hub and HR, Finance and IT collections. Register the corporate site
   as a hub and associate each approved spoke through supported administration.
   Existing sites are acceptable within the current validator's supported shape:
   same-tenant commercial SharePoint HTTPS `/sites/<name>` collection roots.
   `/teams/` roots, arbitrary subweb inventory entries, sovereign-cloud and
   cross-tenant targets need a deliberate redesign, not a placeholder swap.
   If no hub is available, do not bypass the required `DepartmentId` restriction.
4. **Add a small real pilot corpus and permissions.** Create/select document
   libraries and Site Pages, add safe documents and published pages, and grant
   intentional source access. Hub association is not authorization. You do not
   need 512 items initially; fixture generation is optional and separate.
   Include allowed and denied items for a separately authorized non-owner test.
5. **Choose optional metadata.** For stored labels, use compatible text columns
   with internal names `Department`, `TopicTags` and `DocumentType`.
   `TopicTags` is semicolon-delimited text, not managed taxonomy. Discovery is
   dynamic; missing tags remain `Not supplied`. A renamed display label does
   not change the internal name. `DepartmentId` is the search hub-association
   property, not a custom list column to create. `PolicyStatus` and `ReviewDate`
   are not required or consumed by this flow.
6. **Record identifiers and verify indexing.** Obtain actual collection IDs
   through approved admin tooling or each site's `_api/site?$select=Id`; do not
   substitute list IDs or URL slugs. Verify hub registration/association, then
   allow indexing to catch up. Confirm search locators `SPWebUrl`, `SiteID`,
   `ListID`, `ListItemID` and current file/page reads under the intended caller.
   Working direct links alone do not establish indexed search coverage.
7. **Retarget a private source copy and regenerate coherently.** Use the matrix
   below. In `configured` mode, verification flags are owner assertions set only
   after their checks—not automated proof or a workaround for missing setup.
   Generate the target flow using the existing agent builder, then deliberately
   adapt the private reference-only package validation policy and rebuild if
   using the solution route. Stock package tests reject real tenant locators;
   do not remove runtime identity/scope checks to satisfy them.
8. **Apply and verify target configuration without publishing.** Apply a reviewed
   private rebuild as an intentional unmanaged update to the new target solution,
   or coordinate changes in the supported product editors. Bind all five target connections and
   keep every runtime connection **Provided by run-only user**, `invoker`,
   tool `Invoker`, and no embedded maker fallback. Verify the native tool is
   registered and both topic/tool references resolve to the same flow.
9. **Prepare callers and audience.** Reconfigure authentication on the imported
   agent in Copilot Studio; source-tenant auth/channel setup does not transfer
   as a verified target configuration. Pilot users need provisioned personal
   OneDrive sites, supported connection consent and nonempty directory mail.
   Selected profile, source and private-drive identities must align. The
   current flow writes `CorpNetSearchResults-<JobId>.xlsx` in the personal-drive
   root (`folderPath: "/"`): no pre-created shared export library or special
   folder is required. Select a real Entra audience group and retain
   Integrated/Always authentication. Keep classic orchestration to reproduce
   the tested version; a generative adaptation requires the corresponding
   setting, instructions/descriptions and validation changes described below.
10. **Validate in the target before release.** Start small: topic questions,
   tool binding, a positive query, no-match, invalid input, connector failure,
   allowed/denied source access, exact workbook rows/dates/tags, private ACL and
   mailbox delivery. Then exercise more than 100 matches, duplicates, caps,
   partial processing and changed access. Enable the configured flow only for
   controlled testing; the target owner publishes/shares after approval.
   M365 and Teams rendering/sign-in are separate target checks.

Use the [smoke-check matrix and troubleshooting guide](../solutions/README.md#5-enable-for-a-controlled-smoke-check-then-publish-separately)
to distinguish import, draft testing, flow enablement, agent publication and
verified delivery. An environment/channel that cannot support caller-provided
connections is a blocker; do not fall back to maker credentials.

### Target customization matrix

| Setting | Where and what to change |
|---|---|
| Tenant/search site | `agent/runtime/search-policy.json`: `tenantOrigin`, `searchSiteUrl`. Regenerate to update corporate datasets, canonical source URLs, path checks and the derived personal-site origin/prefix. Changing only `Initial_search` Site Address is incomplete. |
| Hub/approved inventory | Same policy: `hubSiteCollectionId`, every `sites[].url`, `sites[].siteId`, `sites[].department`. Generated `Approved_scopes` KQL and site lookup maps must match verified target facts. `All` means that inventory. |
| Configuration mode/assertions | `configurationMode: configured`; independently verify `hubRegistrationVerified`, `hubSearchVerified`, `metadataFieldsVerified`, `searchLocatorFieldsVerified`. Retain `scopeMode: approved-inventory`. Flags do not provision or test resources. |
| Business areas | Policy, `agent/topics/SearchSharePoint.mcs.yml`, `agent/agent.mcs.yml`, `agent/cards/`, generated flow and tests. Update prompts, normalized choices, validation, intent examples and fixed banner switches together. |
| Different metadata schema | Prefer the supported internal names/types; otherwise adapt builder field filters, selected fields, formatting and workbook mappings together. Taxonomy objects are not drop-in text tags. |
| Connections | Target connection references and private `solutions/deployment-settings.local.json`. For source wiring, also review `agent/runtime/connection-references.json` and `agent/connectionreferences.mcs.yml`. Import binding does not configure every caller's runtime connection. |
| Agent audience/model | Set real `CopilotAgents[].AadGroupId` in private deployment settings; check sharing in the product. Review `agent/settings.mcs.yml` and model/instructions in `agent/agent.mcs.yml`. The zero group is only a scaffold. |
| Flow identity | `agent/actions/SearchAndExport.mcs.yml` and `agent/topics/SearchSharePoint.mcs.yml` must bind the same registered flow. Preserve intrinsic package relationships; do not blanket-replace GUIDs. |
| Destination/template changes | The default uses a verified personal-drive root and included blank workbook. A shared drive, alternate folder or table-schema change needs coordinated creation, path, identity, ACL, write and readback changes, not only a replacement URL. |

### If the unchanged ZIP is already imported

Keep the flow stopped and agent unpublished. Provision/verify the source estate,
then apply coordinated target configuration through supported editors or an
intentional reviewed unmanaged update from a private rebuilt package. Recheck
the actual loaded topic, tool relationships and runtime connections. Editing
repository YAML does not modify imported components, and filling connection IDs
alone does not replace the embedded Contoso policy. Export your configured
target solution privately; do not publish tenant IDs, connections or real data
back into this neutral reference.

The [compiled-location map](../solutions/README.md#4-configure-the-imported-implementation-for-your-tenant)
enumerates the inventory object and ten additional tenant-dependent leaves.
Some exported records carry `iscustomizable=0`; target editability is not proven.
If supported editing is blocked, stop and investigate the product error rather
than changing metadata flags to force it. The fictional policy is not a runtime
activation interlock.

See the [request-by-request SharePoint action reference](sharepoint-actions.md)
for the actual corporate-site, current-source and personal-site requests that
must remain consistent.

## Adaptation sequence

1. **Import the reviewed solution, or create/clone a real agent in the intended environment.** Work against
   that connected agent, not a folder of unbound YAML. Place the agent and
   native flow in a dedicated solution.
2. **Review the portable source.** Follow the component instructions in
   [`agent/`](../agent/). Replace example inventory and binding values with
   explicitly approved target resources. Keep real settings out of public
   source control.
3. **Establish the approved inventory.** Record actual collection IDs, URLs,
   department classifications and verified hub association. Add every intended
   spoke explicitly; a hub URL alone is insufficient.
4. **Prepare source metadata.** Use actual list columns. `Department` is a
   business field; the SharePoint search `DepartmentId` property identifies
   hub association. They are not interchangeable.
5. **Create/configure the native flow.** Keep all runtime connectors
   caller-provided. Preserve identity alignment, current-source checks, private
   output validation and explicit retrieval limits.
6. **Register the flow through Copilot Studio.** Use the product's tool
   registration experience and preserve the resulting binding. Merely putting
   a workflow GUID into topic YAML was insufficient in the demonstration.
7. **Rebind and load the topic in Studio.** Preserve native YAML sequence
   indentation and avoid serializer-inserted soft wrapping of activity text.
   A generic YAML-valid payload loaded as a truncated one-message dialog in
   the demonstration. An unwrapped correction plus a fresh authoring/test tab
   in the same authorized browser restored the actual scope question; an
   older tab retained its stale compiled dialog. Generic validity alone does
   not prove Studio loaded every topic action or resolved its flow.
8. **Test the draft through the actual conversation.** Verify the linked
   ten-row/date-bearing preview, continuation run, populated workbook and verified-recipient email.
   Repeat with no matches, invalid input and connector failure.
9. **Test permissions and scale separately.** Exercise a non-owner allowed/
   denied account, changing source permissions, larger inventories, paging,
   caps and partial failures.
10. **Publish only after an explicit release decision.** Agent publication,
    SharePoint-channel embedding, repository visibility and GitHub Pages are
    separate operations.

## Agent model

Classic orchestration was selected to keep this demonstration topic-based.
It is not a requirement of the SharePoint flow. Generative orchestration is
an alternative: change the orchestration setting, update instructions and
topic/tool descriptions to invoke the same guarded capability, and validate
that variant. Keep instructions appropriate to either approach. The shipped
settings and published runtime evidence remain classic.

The department and search questions use free text simply for the test.
Department buttons/multiple-choice options can replace the typed scope if
desired, while preserving validation and the flow's `query`/`scope` contract.
Banners are optional styling; update their mappings if retained, or omit that
contextual message without removing the actual result message.

The verified paging draft used **GPT-5 Chat** (`GPT5Chat`), upgraded from an
actual UI-confirmed GPT-4.1/default configuration. A local model hint alone
had not established the live setting. GPT-5 Reasoning was offered as Preview
with cross-geo requirements in that environment and was not selected; no
preview or cross-geo opt-in was enabled. Availability can differ by tenant.
Classic controlled orchestration and caller-provided connections remained
unchanged. Verify the effective model in the connected product, and treat
publication as a separate release decision.

## Teams publication is a separate check

The owner subsequently published the agent, and actual M365 conversations
verified HR/IT banners and the polished four-row table as documented in
[screenshots](screenshots.md). Those are source-environment checks, not tests
of this solution in another tenant or in Teams. No Teams publication or successful Teams
rendering is established by Studio draft screenshots.
After publication, check desktop and mobile rendering, all ten source links,
date/tag readability, caller connector sign-in and the private workbook/email
path. Markdown table support can differ by channel; do not assume the Studio
table transfers unchanged or enable preview settings merely to force it.

## Do not copy these from a demonstration tenant

Live connection IDs, connection references bound to specific accounts,
environment/agent/workflow IDs, source inventory IDs, owner identities, callback
URLs, populated exports and management-run evidence are deployment state.
The repository uses reference values rather than carrying that state into a
future public release. One narrowly classified intrinsic workflow component
identity is retained in the solution's manifest, bindings and relationship so
the package remains consistent; it is not a tenant/site/connection locator.
Its exact occurrences are listed in the [component inventory](../solutions/component-inventory.json).

Do not remove required connection/tool components simply to make an incomplete
package pass an export command. A source reference and a verified importable
solution are different deliverables.

## Local checks versus product checks

Local source tests check contracts and generated artifacts. They cannot prove
actual caller authentication, connector consent, Studio topic loading,
SharePoint indexing, non-owner trimming or email delivery.

Keep both kinds of evidence and label them accurately. See
[validation](validation.md) and the source-specific local commands in
[`agent/`](../agent/).
