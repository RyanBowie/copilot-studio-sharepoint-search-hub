# Search Hub or Engineering Evidence?

**Documentation comparison prepared 15 November 2026. No live agents were run
for this update, and no matched head-to-head run exists.**

This is a historical evidence comparison, not a matched head-to-head test.

This community reference is shared as is under the [MIT licence](../LICENSE),
not as a Microsoft product or a production-readiness certificate. Demonstration
content is fictional; `SYNTHETIC-DEMO` engineering examples are not real
engineering authority.

## Recommendation by scenario

For a **new large, unstructured-document reasoning workload**, evaluate the
**Microsoft Copilot-harness Engineering Evidence example first**:
[companion repository](https://github.com/RyanBowie/copilot-studio-engineering-evidence)
and [companion Pages site](https://ryanbowie.github.io/copilot-studio-engineering-evidence/).
Publication evidence supplied **15 November 2026** identifies the repository
as **PUBLIC** at commit
[`8ea5798b521a4e98d99d4240816d32eb796b6c22`](https://github.com/RyanBowie/copilot-studio-engineering-evidence/commit/8ea5798b521a4e98d99d4240816d32eb796b6c22).
Pages is configured at the linked URL; a live Pages deployment has not yet
been verified. This publication status does not establish a new agent test or
a matched benchmark.

It is a better architectural starting point for extracting requirements and
exceptions, analysing conflicts across manuals, and creating native evidence
files. That is a recommendation about task fit and retained artifacts, **not
proof of exhaustive extraction or of superiority on Search Hub's workload**.

Keep **Standard-harness Search Hub** when the contract is literal search across
an approved SharePoint estate, current caller-hydrated metadata, a predictable
bounded preview and an explicitly engineered private Excel export. Publishing
Search Hub to the **Microsoft 365 Copilot channel** does not make it a
Microsoft Copilot-harness agent: channel and harness are different choices.
Likewise, “built with GitHub Copilot” describes development assistance, not the
runtime harness. Older evidence may use “GHCP” for the newer harness.

| Task / design choice | Search Hub, as supplied | Microsoft Copilot-harness engineering direction |
|---|---|---|
| Find matching files/pages | Literal words or `*`, explicit site allowlist and hub restriction; no automatic spoke discovery. | Not a demonstrated replacement for this exact scoped Search REST contract. |
| Return titles, dates and tags | Current source reads as the selected caller; stored metadata, not inferred values. | Maintain source permissions, provenance and authoritative-source checks when adapting retrieval. |
| Extract all relevant requirements and exceptions | Not implemented; indexed body search returns links/metadata, not answer passages or clause analysis. | Adaptive document reasoning and native file processing are a better fit; completeness still needs an independently checked ledger. |
| Analyse conflicts across manuals | Not implemented. | Appropriate design direction; the retained partial extraction does not certify every conflict was found. |
| Create evidence files | Deterministic Excel template, row writes/readback, personal-drive ACL and verified-profile email path. | Native file workspace can create reports/ledgers without reproducing that Excel row-write pipeline; it does not prove this email/private-destination contract. |
| Control execution | Classic, maker-authored topic and guarded flow; five Invoker connectors, one 183-action workflow. | More adaptive orchestration, larger context, Bash/filesystem and native processing; still requires explicit governance and validation. |

The Search Hub flow is more elaborate because it engineers scoped search,
stable paging, account alignment, current source hydration, row fidelity,
private destination checks and delivery. A secure sandbox removes some
file-processing plumbing, **not these obligations**. No automatic migration of
a working agent is implied; retain the working search/export path until a
replacement passes its own acceptance checks.

Standard is **not incapable of code execution**. Microsoft's structured-data
code interpreter uses Python for CSV/Excel analysis (preview; up to ten files,
16 MB per file). File analysis is disabled in this supplied Search Hub build.
That capability is not the same as the newer harness's broader native
Word/Excel/PowerPoint/PDF and filesystem workflow.

## Historical evidence comparison — different workloads

| Evidence | Search Hub | Engineering Evidence |
|---|---|---|
| Build/source provenance | Portable agent source first committed **12 September 2026** (`c161974`); this is not the original live build timestamp. Reference solution version **1.0.0.0**. | Initial build evidenced **6 November 2026**. Published version **8.0** status recorded **8 November 2026**. Public copies prepared **15 November 2026**. |
| Configured model | Source hint **`GPT5Chat`**; earlier **12 September** validation records describe GPT-5 Chat conversations. | Saved build model **Claude Opus 5.5**, series **`claude-opus-5-5`**. |
| Actual execution model | Exact model/version for the **13 September 512-row run** not retained. The source hint and earlier records do not independently identify that run. | Exact execution models/versions for the six later tests not retained or independently verified. **`GPT-ENG` names describe the GPT-compatible requested prompt ladder, not proof of GPT runtime.** |
| Run/report timing | **13 September 2026**, native run **10:42:24–11:09:10 UTC**, observed **26m46s**; full timestamps in the local safe runtime summary. | Six results **reported 13 November 2026**, not exact starts/ends. Native Studio screenshots captured **13 November, 20:10 UTC**. No comparable end-to-end latency retained. |
| Scope and unit | **499 Word documents + 13 SharePoint pages = 512 verified matches**, ten approved site collections, one marker query. | **21 manual identities / 37 Word/PDF representations** selected. Level 6 requested all relevant clauses within that same 21-manual scope. |
| Verified output | **512 caller-hydrated rows**, six disjoint source pages, exact Excel readback; final owner-private ACL and one accepted email. | Retained native HTML report and **2,609-row, 12-column CSV ledger**. **44 complete own-clause records from five manuals** and **144 ordered evidence items** matched an earlier independently retrieved DOCX; zero tested own-clause field differences. Ledger rows are not clause counts. |
| Remaining limits | Positive owner-account evidence, not non-owner denial/revocation, Teams, inbox receipt or configured cross-tenant runtime proof. | **176 candidates: 44 done, 132 pending**. No fully reviewed manual established. All five public substantive manual bodies, **320 research pages** and **18 identified figures** remain pending. |

The five historical USACE PDF representations have **449 / 205 / 448 / 392 /
476 physical pages: 1,970 pages available**, not 1,970 pages reviewed. The
original ambition of forty fully reviewed manuals was **not completed**.

Twenty-four ancillary pilot-context paragraphs differ from the retained DOCX;
unavailable synthetic PDFs prevent attributing those differences to an agent
omission. The zero-difference clause check is a bounded retained-output
comparison, not an audit of every source clause.

**Do not compare 512 search matches with 44 clause records as the same unit,
or claim “Microsoft always wins.”** The evidence supports preserving Search
Hub's search/export use case and evaluating the engineering direction for
document reasoning, while explicitly retaining incomplete coverage.

Local Search Hub evidence:
[native runtime summary](scale-runtime-validation-summary.json),
[source/index summary](scale-source-validation-summary.json),
[validation and limitations](validation.md),
[portable model source](../agent/agent.mcs.yml),
[current package evidence](../solutions/package-validation.json).
Engineering facts are a companion historical evidence summary supplied for
this update; its files and audits are owned by the companion publication, not
copied or independently rerun in this repository.

## Indicative test credits, not a low-cost or price claim

The following six values are **user-reported Copilot credits**, reported
**13 November 2026**. They are historical workload indicators, not an invoice,
currency conversion, tariff, repeat-controlled price or matched Standard
baseline. They do not establish which execution model consumed them.

| Engineering level | Requested manual identities | Reported credits | Evidence boundary |
|---|---:|---:|---|
| L1 | 1 | 22.35 | Narrow identity scope, not whole-corpus coverage. |
| L2 | 3 | 20.37 | Full response absent from the retained bundle. |
| L3 | 8 | 85.04 | Broader requested scope, not a completeness certificate. |
| L4 | 15 | 158.68 | Different workload from literal Search Hub search. |
| L5 | 21 | 162.06 | Twenty-one identities, not forty complete manuals. |
| L6 | 21, all relevant clauses requested | 290.00 | Partial coverage: 44 done / 132 pending candidates. |
| **Total** | **Six tests, not six equivalent repetitions** | **738.50** | **User-reported total only.** |

The native Level 6 screenshot separately shows an **estimate of 290.56
credits**. Do not replace the reported **290.00** with that estimate, add both
to the total or present either as reconciled billing.

Search Hub's retained 512-run evidence contains **no test-credit/cost figure**.
Unknown is not zero or “cheaper”. Its **26m46s** timing cannot establish a speed
winner without equivalent engineering latency and an equivalent workload.

## Fair future matched protocol — proposed, not executed

1. Freeze the **same approved source versions**, hashes and manual/page
   identities. Separate literal search/metadata/export and document-reasoning
   scenarios; prepare an independent expected-result and clause/exception/
   conflict oracle for each, including conflicting and no-match examples.
2. Record each agent's **build/version, configured model, actual run
   model/version if available, orchestration and run start/end UTC**. Use the
   same execution model where available; otherwise disclose the model
   confounder. Never infer runtime from a source default or prompt filename.
3. Use the **same authorised user permissions**, retrieval scope, export
   destination rules and environment constraints. Include denied/revoked
   sources and denied export destinations, without granting access to make a
   test succeed. Sandbox security is not source or destination authorisation.
4. Keep a per-manual/page/figure **coverage ledger** with done, pending,
   inaccessible and untested states. Measure clause/exception fidelity and
   omissions against the oracle, citation/locator accuracy, conflict quality,
   current metadata correctness and privacy boundaries.
5. Verify **export correctness** independently: real file bytes, Office/file
   opening, schema, exact rows/evidence text, private access and any requested
   delivery outcome. A filename, attachment card or accepted email is not
   sufficient evidence of those downstream outcomes.
6. Measure **usage and latency** per run with retries, partial failures and
   all relevant processing included. Separate reported credits, native
   estimates and confirmed consumption; disclose unknown costs and tariff
   dates rather than claim low cost.
7. Repeat comparable scenarios under recorded conditions and publish failures
   as well as successes. Mark **N/A — not implemented** for Search Hub's
   extraction/conflict scope rather than pretending it answered the same
   prompt. Any extended Standard variant is a separate, dated build.
   Pre-register scoring **without an expected winner**; recommend by observed
   task fit, fidelity, coverage, access/export correctness, usage and latency.

No runtime agent, solution or flow was modified for this documentation update.
This protocol needs separately authorised testing; it is not a test result.

## Official capability references

- [Choose a harness](https://learn.microsoft.com/microsoft-copilot-studio/guidance/choose-harness):
  adaptive orchestration, larger context, Bash/filesystem versus more
  maker-authored Standard execution paths; no automatic migration.
- [Harnesses overview](https://learn.microsoft.com/microsoft-copilot-studio/harnesses-overview):
  native Word, Excel, PowerPoint and PDF handling in a secure sandbox.
- [Standard structured-data code interpreter](https://learn.microsoft.com/microsoft-copilot-studio/knowledge-code-interpreter-structured-data):
  Python CSV/Excel analysis preview and file limits.

Capabilities and preview limits can change. These references explain
architectural fit, not evidence that either local demonstration passed a
new live test.
