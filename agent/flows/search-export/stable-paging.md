# Stable document-ID search paging

Both `Initial_request` and `Next_request` use this same POST request property:

```json
"SortList": [{"Property": "[docid]", "Direction": 0}]
```

`Direction: 0` requests ascending order. There is no rank sort before it.
`RowLimit` remains 100; `StartRow` remains zero initially and the existing raw
page-length offset subsequently. No keyset query, extra search, new connector,
source field, output or authorization path was added.

## Why relevance-first was rejected

The source-environment owner performed read-only index diagnostics against an
independently enumerated fixture oracle:

| Ordering | Combined unique URLs | Body-only unique URLs | Cross-page overlap |
| --- | --- | --- | --- |
| Document-ID ascending | 512 / 512 (100 × 5 + 12) | 400 / 400 (100 × 4) | None |
| Rank descending, then document-ID ascending | 478 / 512 | 383 / 400 | 34 combined; 17 body-only |

Default relevance requests also overlapped. These results support the narrow
document-ID-only ordering choice; they do not establish the internal reason
rank ordering changed. Duplicate accounting avoids duplicate workbook rows but
cannot recover candidates skipped by shifting offset boundaries.

**These were provisioning-owner read-only index probes, not native agent/export
executions.** A subsequent owner-started native caller run separately passed:
six disjoint pages (100 x 5 + 12), all 512 caller-hydrated sources, 512 actual
Excel rows read back as 250 + 250 + 12, 1,024 timestamp/calendar comparisons,
final owner-private access and one accepted verified-profile email. It completed
in 26m46s without omissions or duplicate index hits. Verification was read-only;
no additional agent invocation was made.

[Completed native-run evidence](../../../docs/scale-runtime-validation-summary.json)
is distinct from the earlier owner index probes and offline synthetic tests.
The fictional four-collection portable policy does not contain the live expanded
fixture corpus. Existing M365 formatting, source-date and email evidence belongs
to explicitly identified revisions; earlier captures must not be relabelled as
this release's proof. New-tenant import/runtime and inbox receipt remain unverified.

## Meaning of the preview and export

- Preview candidates follow document-ID index order within each bounded batch.
  Up to ten verified results are **not relevance-ranked best ten**, not newest
  documents and not a global top ten across batches.
- The twenty-candidate preview budget, current-source permission/metadata reads,
  explicit SiteID **and** hub DepartmentId restriction remain unchanged.
- Export metadata hydration groups can reorder workbook rows; the sort guarantees
  neither a globally sorted workbook nor a source/index snapshot.
- Source changes, reindexing or changing permissions can still affect offset
  pagination. Document-ID ordering does not freeze the index.
- Existing 1,000-row, 2,000-candidate, 40-page and 12-batch export bounds remain.
  An index estimate is not a verified-row count or proof of completeness.
- Four-column Markdown, glyph/link/tag/date fidelity, the genuine blank workbook,
  private destination checks, five Invoker connections and verified-profile email
  behavior are unchanged.

## Offline regression coverage

Five added tests check identical clauses on both generated paths, the unchanged
query/locator/page contract, 512 synthetic tie-heavy rows over six 100-row pages,
400 synthetic rows with changing ranks, and nonshared mutable sort arrays.
The synthetic cases validate the local paging/sort contract, **not SharePoint's
runtime implementation or new-tenant behavior**.

The full two-leaf restore proof removes only `SortList` from the two generated
request objects and reproduces the preceding definition exactly.

Official references:
- [Search REST SortList](https://learn.microsoft.com/en-us/sharepoint/dev/general-development/sharepoint-search-rest-api-overview#sortlist)
- [Document-ID pagination](https://learn.microsoft.com/en-us/sharepoint/dev/general-development/pagination-for-large-result-sets)

The second reference describes keyset pagination for much larger result sets.
Its documented `[docid]` sort property is used here; this implementation retains
its existing bounded offset pagination and does not claim to implement that
article's keyset algorithm.
