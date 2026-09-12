# Setup and safe adaptation

This is a **source reference**, not a one-click deployment package. It does not
contain a live tenant connection, a complete exported Dataverse solution ZIP,
or permission to publish an agent into another environment.

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

## Adaptation sequence

1. **Create or clone a real agent in the intended environment.** Work against
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

The verified paging draft used **GPT-5 Chat** (`GPT5Chat`), upgraded from an
actual UI-confirmed GPT-4.1/default configuration. A local model hint alone
had not established the live setting. GPT-5 Reasoning was offered as Preview
with cross-geo requirements in that environment and was not selected; no
preview or cross-geo opt-in was enabled. Availability can differ by tenant.
Classic controlled orchestration and caller-provided connections remained
unchanged. Verify the effective model in the connected product, and treat
publication as a separate release decision.

## Teams publication is a separate check

The owner subsequently published the agent and supplied an M365 Copilot
screenshot. That two-row visual is documented in [screenshots](screenshots.md);
it is not a Teams rendering test. No Teams publication or successful Teams
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
future public release.

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
