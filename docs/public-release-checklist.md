# Public-release checklist

The repository is intentionally private. Do not change its visibility or enable
a public GitHub Pages site just because documentation and images are present.

## Content and rights

- [ ] Confirm the owner approves public distribution of every included source
      file and generated artifact.
- [ ] Select and add an appropriate license; the private preview does not
      imply an open-source license.
- [ ] Review third-party notices and retain required attribution.
- [ ] Confirm every example is synthetic and not real company guidance.
- [ ] Remove internal hostnames, emails, tenant/environment/agent/site/flow/
      connection identifiers, local paths and organization-specific details.
- [ ] Scan both text and binary content, including ZIP-based Office files and
      image metadata, for secrets and sensitive data.
- [ ] Inspect every screenshot at full resolution. Masking must actually remove
      pixels, not merely overlay a removable shape.
- [ ] Check commit history as well as the current working tree.

## Technical readiness

- [ ] Reproduce the local checks from a clean checkout.
- [ ] Recreate/rebind the reference in a separate target environment using the
      documented supported product workflow.
- [ ] Confirm native flow registration and Studio topic loading.
- [ ] Exercise all five runtime connectors as caller-provided connections.
- [ ] Verify the populated private workbook and verified-recipient email path.
- [ ] Test an allowed and denied non-owner account with genuinely restricted
      content.
- [ ] Verify paging, multiple spokes per department, nested folders, source
      metadata fidelity, indexing delay and partial results.
- [ ] Test real response latency and explicit limits at the intended scale.
- [ ] Document exact supported channels and verify SharePoint embedding before
      advertising it.
- [ ] Refresh screenshots and observed-output captions against the final
      release candidate.

## Publication decision

- [ ] Review the repository description, topics, branch protections and
      dependency/secret-scanning settings.
- [ ] Make a separate, explicit decision to change repository visibility.
- [ ] If a documentation website is desired, configure GitHub Pages only after
      reviewing what it exposes; do not assume private repository content stays
      private on a published site.
- [ ] Tag a release with an honest support statement and known limitations.

No item on this list should be inferred complete from the existence of the
repository alone.
