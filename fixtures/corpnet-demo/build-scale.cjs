const fs = require("node:fs");
const path = require("node:path");

const marker = "hubspokeverify";
const bodyMarker = "bodyonlyscaleverify";
const perSite = 40;
const topics = [
  "Reference handover", "Review checkpoint", "Planning record", "Ownership register",
  "Coordination note", "Readiness record", "Quality review", "Records catalogue",
];

function artifactsFor(fixture) {
  return fixture.sites.flatMap((site) => [
    ...site.documents.map((document) => ({
      id: document.id, kind: "DOCX", siteKey: site.key, department: site.department,
      url: `${site.url}${document.folderPath}/${document.filename}`,
      metadata: {
        Title: document.title, Department: site.department, TopicTags: document.tags.join(";"),
        DocumentType: document.documentType, PolicyStatus: document.status, FixtureId: document.id,
      },
    })),
    ...site.pages.map((page) => ({
      id: page.id, kind: "Page", siteKey: site.key, department: site.department,
      url: `${site.url}/SitePages/${page.slug.replace(/\.aspx$/i, "")}.aspx`,
      metadata: {
        Title: page.title, Department: site.department, TopicTags: page.tags.join(";"),
        DocumentType: "Page", PolicyStatus: "Approved", FixtureId: page.id,
      },
    })),
  ]);
}

function buildScale(expansion, paging) {
  const previous = [...artifactsFor(expansion), ...artifactsFor(paging)];
  const sites = expansion.sites;
  if (previous.length !== 112 || previous.filter((item) => item.kind === "Page").length !== 13 ||
      sites.length !== 10 || new Set(sites.map((site) => site.key)).size !== 10 ||
      new Set(sites.map((site) => site.url.toLowerCase())).size !== 10) {
    throw new Error("Scale generation requires the unchanged 112-item baseline across ten distinct sites.");
  }
  let sequence = 0;
  const fixture = {
    fixtureId: "CORPNET-SCALE-20260913", synthetic: true, notice: expansion.notice,
    sitePrefix: expansion.sitePrefix, reviewDate: expansion.reviewDate,
    metadataColumns: expansion.metadataColumns, searchMarker: marker,
    additionalMarker: "scaleverify", bodyOnlyMarker: bodyMarker,
    documentsPerSite: perSite, documentsAdded: 400, previousMatchingArtifacts: 112,
    expectedCombinedMatches: 512, expectedCombinedFiles: 499, expectedCombinedPages: 13,
    purpose: "Add 400 genuine documents across the existing ten sites. Verify 512 matches without changing the native 100-row search page size.",
    sites: sites.map((site) => ({
      key: site.key, department: site.department, title: site.title, url: site.url,
      siteSuffix: site.siteSuffix, layer: site.layer, webPath: site.webPath, pages: [],
      documents: Array.from({ length: perSite }, (_, index) => {
        sequence += 1;
        const number = String(sequence).padStart(3, "0");
        const ordinal = String(index + 1).padStart(3, "0");
        const nested = index >= perSite / 2;
        return {
          id: `SCALE-${site.key.toUpperCase()}-DOC-${ordinal}`,
          filename: `Scale-${number}-${site.key}-${marker}.docx`,
          title: `${topics[index % topics.length]} ${site.department} ${number} ${marker}`,
          documentType: index % 10 === 0 ? "Policy" : "Guide", status: "Approved", access: "site",
          folderPath: nested ? "/Shared Documents/Runbooks/Quarter One" : "/Shared Documents",
          tags: ["scale", `record-${number}`, `scale-meta-${number}`, `source-${site.key}`],
          sections: [
            { heading: "Fictional reference", paragraphs: [
              `This synthetic ${site.department} reference belongs to ${site.title}. It records example ${sequence} of 400 additional documents.`,
              `Its demonstration checkpoint reviews ${3 + index % 8} sample records and uses reference cycle ${1 + Math.floor(index / 8)}.`,
              "The sample coordinator records an owner, a review outcome and a handover note. These invented details are not real company instructions.",
            ] },
            { heading: "Content-search check", paragraphs: [
              `The shared search terms are ${marker} and scaleverify.`,
              `Content-only markers: ${bodyMarker} and scalebody${number}. These tokens occur in document paragraphs, not filenames, titles or stored tags.`,
            ] },
            { heading: "Coverage and verification", paragraphs: [
              "The combined common-marker test set has 512 expected items: 499 documents and 13 pages. Earlier 112-item evidence remains a historical snapshot.",
              "Keep RowLimit 100 and compare all six result pages with the complete expected URL set. Search order can change; a larger index estimate alone is not complete retrieval proof.",
              "Source access, current metadata and the private workbook must be verified independently. This fixture is not a runtime result feed.",
            ] },
          ],
        };
      }),
    })),
  };
  const combined = [...previous, ...artifactsFor(fixture)];
  if (sequence !== 400 || combined.length !== 512 ||
      new Set(combined.map((item) => item.id)).size !== 512 ||
      new Set(combined.map((item) => item.url.toLowerCase())).size !== 512) {
    throw new Error("Scale fixture identifiers and target URLs must form exactly 512 distinct items.");
  }
  return {
    fixture,
    oracle: {
      synthetic: true, query: marker, scope: "All", expectedCount: 512,
      expectedFiles: 499, expectedPages: 13, expectedNativePageSizes: [100, 100, 100, 100, 100, 12],
      additionalMarker: "scaleverify", additionalMarkerCount: 400,
      bodyOnlyMarker: bodyMarker, bodyOnlyMarkerCount: 400, artifacts: combined,
      source: "Source-definition blueprint only. Verify actual uploaded URLs and metadata before runtime comparison. Never supply these rows to the agent.",
    },
  };
}

if (require.main === module) {
  const load = (name) => JSON.parse(fs.readFileSync(path.join(__dirname, name), "utf8"));
  const { fixture, oracle } = buildScale(load("expansion-content.json"), load("paging-content.json"));
  fs.writeFileSync(path.join(__dirname, "scale-content.json"), `${JSON.stringify(fixture, null, 2)}\n`);
  fs.writeFileSync(path.join(__dirname, "scale-expected-results.example.json"), `${JSON.stringify(oracle, null, 2)}\n`);
  console.log("Prepared 400 additional documents (40 per site); combined common-marker blueprint: 512 items.");
}

module.exports = { buildScale, artifactsFor };
