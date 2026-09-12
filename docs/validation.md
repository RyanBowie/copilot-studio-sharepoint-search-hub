# Evidence and limitations

## Evidence categories

This repository separates **source capability**, **observed runtime behavior**
and **work still requiring verification**. A source definition is not proof of
an executed flow; an upload is not proof of indexing; a populated workbook is
not proof of non-owner permission trimming.

Live tenant identifiers, account details, connection IDs, populated exports
and raw run links remain outside this publication-oriented repository.

## Recovered demonstration baseline

The preceding development session recorded an owner-account search returning
**17 permission-checked results across four separate collections**:

| Collection | Files | Pages |
|---|---:|---:|
| Corporate hub | 3 | 2 |
| HR | 2 | 2 |
| Finance | 2 | 2 |
| IT | 2 | 2 |

This is a recovered point-in-time observation, not a fresh claim that the
current draft returns those exact counts. Subsequent content additions and
indexing can change them.

The historical native run was independently re-read through authenticated
management APIs on 12 September 2026. It ran on 11 September from approximately
23:48 to 23:50 UTC and reported:

| Observation | Verified historical result |
|---|---|
| Native run | Succeeded. |
| Chat preview | Five current-item reads supplied five linked rows with stored tags. |
| Workbook | Excel connector read-back contained 17 rows: nine files and eight pages. |
| Completion | Complete, zero omitted rows and no recorded processing errors. |
| Account alignment | Selected profile, source directory profile and personal-drive owner IDs matched. |
| Private output | Final ACL contained a single matching owner principal. |
| Email action | Succeeded with HTTP 200 and the verified profile mailbox as recipient; this establishes connector acceptance, not human inbox receipt. |
| Runtime connections | All five caller-provided (`Invoker`); embedded fallback disabled. |

The [screenshots](screenshots.md) show that existing draft conversation and
native binding. No fresh agent invocation was used to manufacture a new
baseline, and no populated workbook UI screenshot is claimed.

## Synthetic expansion

The expanded fixture adds **39 Word documents and 13 published pages** to the
original estate. It covers **10 separate hub-associated collections**:
the corporate hub plus a main, Operations and Field Team collection for each
of HR, Finance and IT.

The source includes repeated page titles, nested library folders, three
documents with intentionally empty tags, different policy statuses and a
shared literal search marker, `hubspokeverify`.

The tenant blocks new classic subsites. Field Team collections are separate
modern spokes, not nested webs. That restriction was left unchanged.

Provisioning, metadata verification, indexing and actual agent coverage are
separate checkpoints. Do not infer full agent coverage merely from the number
of created collections or uploaded files.

The portable reference deliberately contains **four fictional Contoso
collection entries**, not live inventory identifiers. The larger corpus is
reproducible source data, not an automatic change to that runtime policy.

The 68 authored artifacts are fewer than the current **100-row search page**.
They do not establish next-page retrieval. That needs more than 100 matching
indexed items in one batch and evidence of the continuation request.

## Portable-source checks

The publication-safe agent package builds offline and its **22 focused tests
pass**. Both fixture generation commands also ran successfully, and all
**47 generated Word documents** passed document-package validation.
The architecture SVG and editable diagram were structurally checked.

These checks apply to the portable copy. They do not replace the original
environment's separate draft tests or prove that the latest two-column local
presentation was deployed.

## Required end-to-end checks

| Check | Evidence needed |
|---|---|
| Topic routing | Actual draft conversation starts the controlled topic. |
| Scope handling | `All` and each department invoke the intended approved inventory. |
| Multiple spokes | Verified result locations include more than one collection in a department. |
| Folder coverage | Actual nested-folder files appear with their exact source locations. |
| Pagination | A run retrieves and verifies beyond its first search page; local batching tests alone do not qualify. |
| Metadata | Displayed tags equal stored column values; empty tags remain explicit. |
| Chat | No more than five actual linked rows; no invented titles or metadata. |
| Workbook | Genuine populated Excel table, working source links, accurate row count and honest partial/completion status. |
| Private delivery | Verified destination access and email action to the verified account mailbox. |
| Identity | All runtime connections are caller-provided and the effective accounts align. |
| Negative permissions | Separate non-owner account cannot receive restricted titles, snippets, tags, links or facts. |
| Failure paths | No unscoped fallback, success-shaped zero count or false completion claim. |

## Not established by this reference

- Production coverage or latency across an estate of 150 or more collections.
- Multi-user authorization or negative permission trimming from owner-only runs.
- Classic-subsite traversal in a tenant that refuses classic-subsite creation.
- A fully imported portable solution in another environment.
- Agent publication or SharePoint-hosted channel behavior.
- A public GitHub release, GitHub Pages site or open-source license grant.

The release checklist deliberately keeps these boundaries visible instead of
presenting a demonstration as a production certification.
