# Synthetic SharePoint fixture source

All policies, figures, queue names and documents are fictional. They must not
be presented as real company guidance.

`content.json` defines the original four-site, 16-artifact corpus. The
expansion generator adds **39 documents and 13 pages** across ten collection
targets, producing **68 authored artifacts** when both corpora are deployed.

The expanded collection model is a corporate hub plus a main, Operations and
Field Team site for each department. Field Team sites are separate modern
collections, not classic subsites. The demonstration tenant blocked classic
subsite creation; no tenant policy was changed.

## Generate locally

From this directory, with Node.js and npm:

```powershell
npm ci
npm run generate
npm run generate:expansion
```

For the separate greater-than-100 paging fixture, generate the expansion
first, then run:

```powershell
npm run generate:paging
```

This adds definitions for 60 distinct Word documents, six per existing
collection, taking the shared `hubspokeverify` set from 52 to **112 expected
matches**. The unchanged native search page size is 100. Generation and an
index count do not prove paging: verify a real next-page request and exact
unique exported URL coverage through the agent. The additional `pagingverify`
marker identifies only the 60 new documents.

The owner-account demonstration subsequently verified actual native pages of
**100 + 12**, StartRow **0 then 100**, and exactly **112 unique Excel rows**.
See [paging evidence](../../docs/validation.md). That observed run does not
mean generating these files locally has provisioned or tested your tenant.
All three corpora together define 128 authored artifacts; only 112 share the
`hubspokeverify` marker.

The commands generate real `.docx` packages and local upload manifests. They
do **not** create sites, upload files, publish pages, change permissions, update
the agent inventory or prove search indexing.

The example target hostname is `contoso.sharepoint.com`. Replace it with an
approved target in your private deployment configuration; it is not a live
fixture endpoint supplied by this repository.

## 500-plus scale fixture

After generating the expansion and paging definitions, run:

```powershell
npm run generate:scale
npm run test:scale
```

The scale generator adds **400 genuine Word documents**, 40 per existing
collection: 20 in the library root and 20 in `Runbooks/Quarter One`.
The combined common-marker corpus is **512 distinct items: 499 documents and
13 pages**. Including the original non-marker examples, all four source corpora
define **528 authored artifacts**.

The checked-in [512-item blueprint](scale-expected-results.example.json)
contains every expected source ID, type, metadata record and example target
URL. It uses fictional Contoso locations. It is not an uploaded-data manifest
and must never be supplied to the runtime instead of actual SharePoint reads.
The generated document files and machine-specific upload manifests are ignored.

Use **`All` / `hubspokeverify`** for the greater-than-500 paging case. The
`scaleverify` marker matches only the 400 additions. `bodyonlyscaleverify`
occurs in their paragraph content but not their names, titles or stored tags,
so it provides a separate 400-item body-indexing check. New content avoids
changing the smaller `annual leave` and `devices` examples.

The unchanged native RowLimit 100 should yield six pages:
**100, 100, 100, 100, 100, 12**. Verify the exact 512-URL union, current source
reads, preview inclusion, full private workbook and delivery outcome. A generated
blueprint, uploaded file count or diagnostic index query is not an agent test.
Earlier 112-item evidence remains a separate historical snapshot.

The connected source deployment subsequently passed this exact case:
**512 caller-hydrated sources and 512 private Excel rows**, with no missing
or duplicate rows, in 26m46s. See the
[native-run evidence](../../docs/scale-runtime-validation-summary.json).
That result does not populate or validate these fictional targets in a new tenant.

**Tenant setup is required.** These are ten collection targets, while the
portable agent's default policy deliberately retains four fictional references.
Approve and verify the actual ten sites/hub association before updating that
inventory; generation does not expand authorization. Rebind metadata and
selected-user connections, and preserve existing permissions. Importing an
agent solution does not provision or index this SharePoint content.

## Coverage cases

| Fixture feature | Purpose |
|---|---|
| `hubspokeverify` in every expansion item | A common literal query spanning the added corpus. |
| Multiple collections per department | Avoid accidentally searching only one departmental site. |
| Nested `Runbooks/Quarter One` folders | Exercise actual library-folder depth. |
| Repeated “Getting started” page titles | Require exact source disambiguation. |
| Three documents with no tags | Check explicit missing metadata, not inferred labels. |
| Draft and archived items | Expose the current limitation: status is stored in the source but not selected, exported or filtered by the agent. |
| Metadata-only tag values | Distinguish stored-column retrieval from model inference. |
| Original restricted HR document definition | Require a real item ACL and a separate non-owner test; a metadata label is not protection. |

`TopicTags` is semicolon-delimited text, not managed taxonomy. The `Department`
business column is distinct from SharePoint's hub-associated `DepartmentId`
search property.

No live deployment manifest, owner identity, collection GUID, populated export
or raw flow-run evidence is included here.
