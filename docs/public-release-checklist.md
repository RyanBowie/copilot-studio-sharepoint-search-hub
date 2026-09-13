# Public-release checklist

The owner explicitly authorized a public repository and GitHub Pages project
site on **13 September 2026**. Publication is a reference/documentation decision,
not a claim that every production-deployment check below has passed.
Future additions still require privacy and rights review before publication.

## Content and rights

- [x] Confirm the owner approves public distribution of every included source
      file and generated artifact.
- [x] Document the deliberate absence of a project-wide open-source license,
      matching the companion Power BI reference. See [rights notice](../NOTICE.md).
- [x] Review third-party notices and retain required attribution.
- [x] Review the Microsoft Fabric Assets License and visual guidelines for the
      separately labelled SharePoint icon. It is not an agent logo and is not
      covered by any future project license; original banner artwork is separate.
- [x] Confirm every example is synthetic and not real company guidance.
- [x] Remove internal hostnames, emails, tenant/environment/agent/site/flow/
      connection identifiers, local paths and organization-specific details.
- [x] Review the solution's one narrowly retained intrinsic workflow identity
      and exact path allowlist; do not expand that exception to tenant locators,
      account bindings or credentials.
- [x] Scan both text and binary content, including ZIP-based Office files and
      image metadata, for secrets and sensitive data.
- [x] Inspect all 40 unique PNGs at full resolution. No visible disclosure
      blockers were found; recipient masking replaces pixels in an opaque,
      single-frame raster with no embedded original or removable layer.
      Historical 112-row Studio captures remain explicitly labelled.
- [x] Check commit history as well as the current working tree. The initial
      review covered 12 commits and 287 distinct path/blob pairs, including both
      historical solution ZIP versions; no historical-only PNG versions occurred.

## Connected-reference checks and remaining deployment work

- [x] Reproduce the local checks from a clean checkout: 68 agent checks with
      pinned dependencies, 13 as-shipped package checks and five fixture checks
      after generating the required definitions. Preserve PAC source CRLF endings.
- [ ] Recreate/rebind the reference in a separate target environment using the
      documented supported product workflow.
- [ ] Actually import the unmanaged solution into a separate target environment;
      PAC packing/roundtrip is not an import test. Customize the sample
      departments/topics, target inventory, metadata, accounts and security group.
- [x] Confirm native flow registration and Studio topic loading in the connected demo.
- [x] Exercise all five runtime connectors as caller-provided connections in that demo.
- [x] Verify the populated private workbook and verified-recipient email path:
      512 rows and final private access passed; email acceptance is not inbox receipt.
- [ ] Test an allowed and denied non-owner account with genuinely restricted
      content.
- [x] Verify paging, multiple spokes per department, nested folders, source
      metadata fidelity and index readiness.
      Complete-path scale evidence is 512 rows over six pages; this does not
      prove every failure/cap scenario or the configured 1,000-row maximum.
- [ ] Exercise capped/partial completion and failure paths in the target
      environment before production use.
- [x] Record observed timing: the 512-row run completed in 26m46s, not a latency SLA.
- [x] Document exact channel evidence: owner-account M365 and Studio observations
      are separately scoped. SharePoint embedding is not advertised as verified.
- [ ] After an explicit Teams publication decision, verify desktop/mobile
      ten-row/date/link rendering, connector authentication and private delivery.
- [ ] Refresh screenshots and observed-output captions against the final
      release candidate.

## Publication decision

- [x] Review the repository description, topics, branch protections and
      dependency/secret-scanning settings. GitHub secret scanning and push
      protection are enabled. `main` is not branch-protected and automatic
      dependency-update pull requests are not enabled; no stronger policy is claimed.
- [x] Make a separate, explicit decision to change repository visibility:
      owner authorization on 13 September 2026.
- [x] Verify the reviewed HTTPS Pages deployment, all 24 anonymously accessible
      public files, exact solution bytes, live controls and tablet/mobile layouts.
      Only the curated static build is published; the two staging control files
      are not counted as user downloads.
- [x] Retain an honest support statement and known limitations. This is a public
      reference, not a production-certified release or an open-source license grant.

No item on this list should be inferred complete from the existence of the
repository alone. See the [source/artifact review record](publication-review.json);
deployment and anonymous-site verification remain separate from these checks.
