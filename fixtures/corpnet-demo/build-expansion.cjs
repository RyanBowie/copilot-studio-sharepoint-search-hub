const fs = require("node:fs");
const path = require("node:path");

const root = __dirname;
const base = JSON.parse(fs.readFileSync(path.join(root, "content.json"), "utf8"));
const host = "https://contoso.sharepoint.com";
const marker = "hubspokeverify";
const fixture = {
  fixtureId: "CORPNET-EXPANSION-20260912",
  synthetic: true,
  notice: base.notice,
  sitePrefix: base.sitePrefix,
  reviewDate: base.reviewDate,
  metadataColumns: base.metadataColumns,
  searchMarker: marker,
  purpose: "Bounded functional coverage of hub, multiple spokes per department, team spokes, folders and search pagination; not production-scale or negative-permission proof.",
  classicSubsites: {
    supportedInThisTenant: false,
    observedError: "New subsites are not available for your organization. Create a new site instead.",
    alternative: "Field Team targets are separate hub-associated site collections, not child webs. No tenant setting was changed.",
  },
  sites: [],
};

const rootTopics = {
  CorpNet: [
    ["Continuity coordination", "The fictional continuity exercise runs on the second Wednesday of each quarter.", "continuity"],
    ["Internal communications", "The fictional editorial board reviews internal notices every Tuesday at 10:00 UK time.", "communications"],
    ["Records review", "The fictional records review has a 45-day review window before an owner must make a retention decision.", "records"],
  ],
  HR: [
    ["Benefits enrolment", "The fictional benefits enrolment window closes 21 calendar days after the start date.", "benefits"],
    ["Working patterns", "A fictional flexible-working trial lasts eight weeks before a manager and employee review it.", "working-patterns"],
    ["Career development", "The fictional career programme includes two development conversations per quarter.", "development"],
  ],
  Finance: [
    ["Forecast submissions", "The fictional monthly forecast is due by 12:00 UK time on the fourth working day.", "forecasting"],
    ["Cost centre coding", "The fictional demonstration cost centre for shared training is DEMO-410; it is not a real accounting code.", "cost-centres"],
    ["Supplier onboarding", "The fictional supplier review requires two independent checks before a supplier record is activated.", "suppliers"],
  ],
  IT: [
    ["Support priorities", "The fictional priority-two support target is an initial response within four working hours.", "support"],
    ["Software catalogue", "The fictional software catalogue is reviewed on the first Monday of each month.", "software"],
    ["Device returns", "The fictional device return appointment is arranged within five working days of an agreed return date.", "devices"],
  ],
};

const operationsTopics = {
  HR: [
    ["Recruitment intake", "The fictional recruitment intake panel meets every Thursday and requires a role brief two working days beforehand.", "recruitment"],
    ["Starter coordination", "The fictional starter checklist has seven checkpoints split between HR and the separate IT service.", "onboarding"],
    ["Leaver coordination", "The fictional leaver coordinator records the agreed final date and asks IT to schedule access removal.", "offboarding"],
    ["Training requests", "The fictional training request allowance is three learning days per half-year, subject to the training owner's approval.", "learning"],
    ["Wellbeing appointments", "The fictional wellbeing service offers 25-minute appointments through the DEMO-WELL queue.", "wellbeing"],
    ["Accessible onboarding", "The fictional accessible onboarding review takes place at least six working days before a planned start.", "accessibility"],
    ["Manager reference", "The fictional manager reference is a draft discussion aid and must not be presented as an approved policy.", "manager-reference"],
  ],
  Finance: [
    ["Expense reconciliation", "The fictional expense reconciliation checks three sample receipts per demonstration claim.", "expenses"],
    ["Budget transfers", "The fictional internal budget transfer over GBP 2,500 needs a second finance reviewer.", "budgeting"],
    ["Purchase approvals", "The fictional operations approval record includes the request owner, quote date and approving finance reviewer.", "purchasing"],
    ["Quarterly audit", "The fictional quarterly audit starts with a sample of 12 synthetic transaction records.", "audit"],
    ["Travel advances", "The fictional travel advance request is made eight working days before the planned journey.", "travel"],
    ["Grant tracking", "The fictional grant register is checked every 30 calendar days for upcoming reporting dates.", "grants"],
    ["Archived coding reference", "The fictional archived coding reference is retained for historical comparison and is not the current coding guide.", "archive"],
  ],
  IT: [
    ["Access requests", "The fictional access request owner confirms the named system and business need before approval.", "identity"],
    ["Laptop preparation", "The fictional laptop preparation queue reserves a 90-minute setup slot for each demonstration device.", "devices"],
    ["Recovery exercises", "The fictional recovery exercise checks restoration of a synthetic sample every 60 days.", "recovery"],
    ["Service handover", "The fictional service handover has four checklist sections: ownership, support, documentation and review.", "service"],
    ["Patch coordination", "The fictional patch coordination review is held on the third Wednesday of each month.", "patching"],
    ["Incident communications", "The fictional incident coordinator posts an internal status update every 40 minutes during the exercise.", "incidents"],
    ["Technical reference", "The fictional technical reference deliberately has no stored tags to exercise honest missing-metadata display.", "reference"],
  ],
};

function addDocument(site, topic, index, options = {}) {
  const [title, fact, tag] = topic;
  const id = `EXP-${site.key.toUpperCase()}-DOC-${String(index).padStart(3, "0")}`;
  const nested = options.nested || false;
  site.documents.push({
    id,
    filename: `${title.replaceAll(" ", "-")}-${marker}.docx`,
    title: `${title} ${marker}`,
    documentType: options.status ? "Guide" : "Policy",
    status: options.status || "Approved",
    access: "site",
    folderPath: nested ? "/Shared Documents/Runbooks/Quarter One" : "/Shared Documents",
    tags: options.noTags ? [] : [tag, `layer-${nested ? "folder" : site.layer}`, "expansion-20260912", `tagonly-${site.key}-${index}`],
    sections: [
      { heading: "Synthetic operating detail", paragraphs: [fact, `This item is owned by ${site.department} and stored in the ${site.title} web.`] },
      { heading: "Source and coverage", paragraphs: [
        `The search marker is ${marker}. This document exercises ${site.layer}${nested ? " and nested library folder" : ""} retrieval.`,
        "Search must cite the actual accessible source and read its stored columns. Access to a hub or a directory is not permission to read every linked item.",
        site.department === "HR"
          ? "HR owns people processes; the separate IT sites own account and device tasks. Search both departments when both kinds of source are needed."
          : site.department === "Finance"
            ? "Finance owns financial review; the separate HR sites own people policies and the IT sites own technical access."
            : site.department === "IT"
              ? "IT owns technical fulfilment; the separate HR sites own starter and leaver people processes."
              : "The corporate hub links separate HR, Finance and IT collections, and an approved inventory determines the searched collections.",
      ] },
    ],
  });
}

function addPage(site, index, title) {
  site.pages.push({
    id: `EXP-${site.key.toUpperCase()}-PAGE-${String(index).padStart(3, "0")}`,
    slug: `Expansion-${index}-${marker}`,
    title: `${title} ${marker}`,
    tags: [`layer-${site.layer}`, site.department.toLowerCase(), "expansion-20260912"],
    paragraphs: [
      `This is the ${site.title} entry in the synthetic ${marker} test collection.`,
      `Its owning department is ${site.department}. ${site.layer === "subweb" ? "This page lives in an actual child SharePoint web within its parent collection." : "This page lives in a separate approved SharePoint site collection."}`,
      "Document policies and guides in this web contain the detailed fictional operating facts. A search result should link to the exact page or file rather than substitute the hub homepage.",
      "The repeated Getting started title deliberately tests source disambiguation across different sites and webs. No values on this page are real company guidance.",
    ],
  });
}

function addSite(key, department, suffix, layer, webPath = "") {
  const site = {
    key, department, siteSuffix: suffix, webPath, layer,
    title: `CorpNet Search PoC - ${department} ${layer === "team-spoke" ? "Field Team" : layer === "spoke" ? "Operations" : "Main"}`,
    url: `${host}/sites/${base.sitePrefix}-${suffix}${webPath}`,
    documents: [], pages: [],
  };
  fixture.sites.push(site);
  return site;
}

for (const [department, topics] of Object.entries(rootTopics)) {
  const site = addSite(`${department.toLowerCase()}-main`, department, department, department === "CorpNet" ? "hub" : "department");
  topics.forEach((topic, index) => addDocument(site, topic, index + 1, { nested: index === 2 }));
  addPage(site, 1, "Getting started");
}

for (const [department, topics] of Object.entries(operationsTopics)) {
  const site = addSite(`${department.toLowerCase()}-operations`, department, `${department}-Operations`, "spoke");
  topics.forEach((topic, index) => addDocument(site, topic, index + 1, {
    nested: index === 4 || index === 5,
    noTags: index === 6,
    status: index === 6 ? department === "Finance" ? "Archived" : "Draft" : undefined,
  }));
  addPage(site, 1, "Getting started");
  addPage(site, 2, "Operations source directory");
  const child = addSite(`${department.toLowerCase()}-fieldteam`, department, `${department}-FieldTeam`, "team-spoke");
  addDocument(child, ["Field team handover", `The fictional ${department} field team hands over its queue at 15:30 UK time each working day.`, "handover"], 1);
  addDocument(child, ["Quarter One Planning", `The fictional ${department} field team reviews six work items in its quarter-one planning exercise.`, "planning"], 2, { nested: true });
  addPage(child, 1, "Getting started");
}

const documents = fixture.sites.reduce((count, site) => count + site.documents.length, 0);
const pages = fixture.sites.reduce((count, site) => count + site.pages.length, 0);
if (documents !== 39 || pages !== 13 || fixture.sites.length !== 10) {
  throw new Error("Unexpected bounded expansion size.");
}
fs.writeFileSync(path.join(root, "expansion-content.json"), `${JSON.stringify(fixture, null, 2)}\n`);
console.log(`Prepared ${documents} documents and ${pages} pages across ${fixture.sites.length} site/web targets.`);
