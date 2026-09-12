# Architecture and how it works

![SharePoint Search Hub architecture](images/architecture.svg)

[Editable Excalidraw source](images/architecture.excalidraw).
The diagram is an architecture illustration, not a product screenshot.

## Design intent

The agent is an authenticated front end to a bounded, deterministic retrieval
and export path. Copilot Studio manages the conversation; Power Automate
performs connector work; SharePoint remains the authority for content access
and source metadata.

The design deliberately avoids treating a list of document titles from a
search index as sufficient evidence to disclose or export a result.

## Components

| Component | Responsibility |
|---|---|
| Copilot Studio agent | Integrated authentication, controlled instructions and safe failure behavior. |
| Guided search topic | Ask for a known department scope and plain keywords; reject unsupported input; invoke the registered native flow. |
| Registered flow tool | Bind the topic to the actual solution-contained Power Automate flow using native caller authentication. |
| Approved-site inventory | Map each approved collection ID and URL to a department; retain multiple collections per department. |
| SharePoint Search | Retrieve index candidates using the approved scope, literal query terms and bounded paging. |
| Source verification | Check current access to the real source and read stored columns before disclosing or writing the row. |
| Chat preview | Return a compact table of up to five verified source links and tags, plus accurately qualified status. |
| Export continuation | Continue bounded retrieval and write verified rows into a private Excel workbook after the initial agent response. |
| Workbook and email checks | Check actual written rows and private destination access, then email the verified profile mailbox. |

The export continuation is part of the same flow invocation. It is not evidence
of a separate durable job queue, and the initial response is not proof that the
workbook or email has finished.

For a positive search path, the flow prepares and checks the private workbook
before the initial preview response; the diagram's later workbook stage is
the continuation's row-writing and completion verification. An index response
with zero matches creates no workbook and sends no email.

## Request lifecycle

```mermaid
sequenceDiagram
    actor User
    participant Topic as Copilot Studio topic
    participant Flow as Native caller flow
    participant SP as Approved SharePoint estate
    participant Excel as Private OneDrive / Excel
    participant Mail as Verified-account email
    User->>Topic: Search SharePoint
    Topic->>User: Select scope and enter keywords
    User->>Topic: All / plain search words
    Topic->>Flow: Validated query and known scope
    Flow->>Flow: Resolve and align connector identities
    Flow->>SP: Scoped index query
    SP-->>Flow: Candidate locators and index estimate
    Flow->>SP: Current access and stored-metadata checks
    SP-->>Flow: Verified rows or explicit failures
    Flow-->>Topic: Up to five linked rows and initial status
    Topic-->>User: Controlled preview; export started, not completed
    Flow->>SP: Continue bounded search and verification
    Flow->>Excel: Write verified rows into private workbook
    Flow->>Excel: Verify row count and private access
    Flow->>Mail: Send workbook link to verified mailbox
```

## What “hub and spoke” means here

A modern SharePoint hub associates separate site collections. A collection may
contain document libraries, folders and pages. These are different concepts:

| Structure | Meaning for this implementation |
|---|---|
| Corporate hub | Central corporate collection and verified hub association. |
| Department spoke | Separate approved collection, classified under a department. |
| Additional team spoke | Another collection under the same department, also explicitly approved. |
| Library folder | A path inside a collection; not a separate site or authorization grant. |
| Classic subsite / child web | A nested web inside a collection; not the same as a hub-associated collection. |

`All` uses the approved inventory and verified hub scope. A departmental
selection restricts the search to the configured collections for that
department. The native query combines the approved collection IDs with the
verified hub restriction for both `All` and departmental searches. Merely
linking to a site from a directory does not approve it or grant the caller
permission.

The demonstration tenant refused new classic subsites with:

> New subsites are not available for your organization. Create a new site instead.

The expansion therefore uses supported separate team collections and nested
library folders. No tenant setting was changed. This is **not a claim of
tested classic-subsite traversal**.

## Identity and permission boundaries

The native connector experience determines the effective caller account.
SharePoint, Office 365 Users, OneDrive, Excel and email connections must remain
caller-provided. The flow aligns the source identity, profile and OneDrive
ownership; the verified profile's nonempty mailbox determines email delivery.
Caller-provided configuration is not an independent attestation of the Excel
or Outlook connection principal or the email sender.

The topic does not accept tokens, recipient addresses, claimed directory IDs,
arbitrary site URLs or raw KQL. An opaque conversation user identifier is not
proof of an Entra directory object ID.

Department selection is not authorization. A user may legitimately search a
different department, but only content accessible to the effective account
may be returned. The provisioning flow is a separate administrative fixture
tool and is never a substitute runtime search connection.

The workbook must remain private. Anonymous or organization-wide sharing links
are not an acceptable shortcut.

## Retrieval semantics

1. **Index estimate:** a search-index observation, not a live inventory or an
   exported-row count.
2. **Verified result:** a candidate whose current source access and metadata
   passed the controlled flow's checks.
3. **Preview:** at most five verified rows, ordered by the bounded retrieval
   path; not a promise of a globally ranked top five across a large estate.
4. **Export:** the rows actually written and verified, subject to changing
   permissions, explicit bounds and connector failures.
5. **Delivery:** the successful email action, distinct from the initial chat
   acknowledgement and from a human confirming receipt.

Verified metadata includes title, business department, tags, document type
and core source/file locators. Missing values stay missing or use an explicit
display label; the agent must not infer tags.

The fixture also stores `PolicyStatus` and `ReviewDate`, but fixture columns
are not automatically runtime output columns. **Neither is selected or
exported.** `PolicyStatus` is not a filter: draft and archived documents can
be returned, and the current flow must not be described as approved-policy-only.

The export table columns are `Title`, `Department`, `Tags`, `Type`,
`ModifiedUTC`, `SourceSite`, `URL`, and technical `SourceURL`. `SourceSite`
and `SourceURL` are hidden in the workbook layout; `URL` provides the
source-link presentation.

## Bounded work

The current source declares limits of **1,000 exported rows**, **2,000 checked
candidates**, **40 search pages**, and **12 batches of at most 20 approved
collections**. Query input is bounded to **160 characters and 12 plain words**,
or standalone `*`.

Each search page requests **100 rows**. The preview checks at most **20
candidates** to produce up to five verified rows; displayed tags over **200
characters** are shortened. The export loop's **45-minute** and read-back's
**5-minute** timeouts are ceilings, not measured completion times.

These limits are not evidence that the demonstration exercised every
ceiling or that every combination fits connector latency constraints. The
initial response must remain within the native agent-flow response window.
More than 100 matching indexed items in one batch are needed to demonstrate
actual next-page retrieval; a 50-item corpus does not establish it.

## Failure behavior

Invalid input is rejected before retrieval. Authentication failure, unusable
connector responses, missing source access and export failures must remain
explicit. A failed search is not converted to a successful zero count; a
partial export is not called complete; an unavailable scoped search is not
replaced with an unrestricted search.

See [validation](validation.md) for the evidence boundary and
[setup](setup.md) for registration and deployment prerequisites.

## Microsoft references

- [Use flows with agents and configure caller-provided connections](https://learn.microsoft.com/microsoft-copilot-studio/advanced-flow-create)
- [Configure end-user authentication for tools](https://learn.microsoft.com/microsoft-copilot-studio/configure-enduser-authentication)
- [SharePoint Search REST overview](https://learn.microsoft.com/sharepoint/dev/general-development/sharepoint-search-rest-api-overview)
- [Create modern SharePoint sites with REST](https://learn.microsoft.com/sharepoint/dev/apis/site-creation-rest)
