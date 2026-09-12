const fs = require("node:fs");
const path = require("node:path");

const root = __dirname;
const expansion = JSON.parse(fs.readFileSync(path.join(root, "expansion-content.json"), "utf8"));
const marker = "hubspokeverify";
const topics = [
  ["Queue handover", "The fictional handover checklist has four review steps."],
  ["Service review", "The fictional service review uses a 25-minute discussion slot."],
  ["Planning checkpoint", "The fictional planning checkpoint reviews six sample work items."],
  ["Document ownership", "The fictional document owner reviews this example every 90 days."],
  ["Training coordination", "The fictional training coordinator reserves two demonstration sessions per month."],
  ["Readiness checklist", "The fictional readiness checklist has eight synthetic completion criteria."],
];
let sequence = 0;
const fixture = {
  fixtureId: "CORPNET-PAGING-20260912",
  synthetic: true,
  notice: expansion.notice,
  sitePrefix: expansion.sitePrefix,
  reviewDate: expansion.reviewDate,
  metadataColumns: expansion.metadataColumns,
  searchMarker: marker,
  additionalMarker: "pagingverify",
  purpose: "Add 60 distinct documents to the 52-item expansion marker set, requiring real paging beyond the unchanged 100-row search page.",
  expectedCombinedMatches: 112,
  sites: expansion.sites.map((source) => ({
    key: source.key,
    department: source.department,
    title: source.title,
    url: source.url,
    siteSuffix: source.siteSuffix,
    layer: source.layer,
    webPath: source.webPath,
    pages: [],
    documents: topics.map(([topic, fact], index) => {
      sequence += 1;
      const number = String(sequence).padStart(3, "0");
      const nested = index >= 3;
      return {
        id: `PAGING-${source.key.toUpperCase()}-DOC-${String(index + 1).padStart(3, "0")}`,
        filename: `Paging-${number}-${source.key}-${marker}.docx`,
        title: `${topic} ${source.department} ${number} ${marker}`,
        documentType: "Guide",
        status: "Approved",
        access: "site",
        folderPath: nested ? "/Shared Documents/Runbooks/Quarter One" : "/Shared Documents",
        tags: ["paging-verification", `source-${source.key}`, `row-${number}`, nested ? "nested-folder" : "library-root"],
        sections: [
          { heading: "Fictional operating detail", paragraphs: [
            fact,
            `This synthetic ${source.department} record belongs to ${source.title}. Its unique reference is pagingrow${number}.`,
          ] },
          { heading: "Paging verification", paragraphs: [
            `Search markers: ${marker} and pagingverify. This is record ${sequence} of 60 additional paging-test documents.`,
            "The combined marker corpus contains 112 distinct expected items. An index count alone does not prove that every page was retrieved.",
            "The test must retain the normal 100-row page size, request a subsequent page, recheck current source access, and export every verified unique source URL.",
            "These are synthetic test facts, not real company guidance. Source ordering may change, so use the complete expected URL set rather than assuming which document will be row 101.",
          ] },
        ],
      };
    }),
  })),
};

const originalCount = expansion.sites.reduce((total, site) => total + site.documents.length + site.pages.length, 0);
if (sequence !== 60 || originalCount !== 52 || fixture.sites.length !== 10 || sequence + originalCount !== 112) {
  throw new Error("The paging test requires exactly 60 new documents plus 52 existing marker items across ten collections.");
}
const ids = fixture.sites.flatMap((site) => site.documents.map((document) => document.id));
if (new Set(ids).size !== ids.length) {
  throw new Error("Paging fixture document identifiers must be unique.");
}
fs.writeFileSync(path.join(root, "paging-content.json"), `${JSON.stringify(fixture, null, 2)}\n`);
console.log("Prepared 60 additional documents; expected combined hubspokeverify matches: 112.");
