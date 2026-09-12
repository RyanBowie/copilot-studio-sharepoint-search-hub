const fs = require("node:fs/promises");
const path = require("node:path");
const { parseArgs } = require("node:util");
const {
  Document,
  Footer,
  HeadingLevel,
  Packer,
  PageNumber,
  Paragraph,
  TextRun,
} = require("docx");

const root = __dirname;
const text = (value) => new Paragraph({
  spacing: { after: 160 },
  children: [new TextRun(value)],
});

async function main() {
  const { values } = parseArgs({
    options: {
      content: { type: "string", default: "content.json" },
      manifest: { type: "string", default: "documents-manifest.json" },
      documents: { type: "string", default: "documents" },
    },
  });
  for (const value of Object.values(values)) {
    if (path.basename(value) !== value || value === "." || value === "..") {
      throw new Error("Fixture inputs and outputs must be named children of this directory.");
    }
  }
  const fixture = JSON.parse(await fs.readFile(path.join(root, values.content), "utf8"));
  const output = [];

  for (const site of fixture.sites) {
    const directory = path.join(root, values.documents, site.key);
    await fs.mkdir(directory, { recursive: true });
    for (const source of site.documents) {
      const children = [
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun(source.title)],
        }),
        new Paragraph({
          children: [new TextRun({ text: fixture.notice, bold: true })],
          spacing: { after: 240 },
        }),
        text(`Department: ${site.department} | Status: ${source.status}`),
        text(`Document identifier: ${source.id} | Fixture: ${fixture.fixtureId}`),
      ];
      for (const section of source.sections) {
        children.push(new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun(section.heading)],
        }));
        children.push(...section.paragraphs.map(text));
      }
      const document = new Document({
        creator: "CorpNet synthetic fixture",
        title: source.title,
        description: fixture.notice,
        subject: `${site.department} synthetic search fixture`,
        styles: {
          default: {
            document: { run: { font: "Arial", size: 22, color: "000000" } },
          },
          paragraphStyles: [
            {
              id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal",
              quickFormat: true,
              run: { font: "Arial", size: 32, bold: true, color: "000000" },
              paragraph: { outlineLevel: 0, spacing: { before: 240, after: 200 } },
            },
            {
              id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal",
              quickFormat: true,
              run: { font: "Arial", size: 26, bold: true, color: "000000" },
              paragraph: { outlineLevel: 1, spacing: { before: 200, after: 120 } },
            },
          ],
        },
        sections: [{
          properties: {
            page: {
              size: { width: 11906, height: 16838 },
              margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
            },
          },
          footers: {
            default: new Footer({
              children: [new Paragraph({
                children: [
                  new TextRun({ text: "Synthetic test content | Page ", size: 18 }),
                  new TextRun({ children: [PageNumber.CURRENT], size: 18 }),
                ],
              })],
            }),
          },
          children,
        }],
      });
      const destination = path.join(directory, source.filename);
      await fs.writeFile(destination, await Packer.toBuffer(document));
      output.push({
        id: source.id,
        siteKey: site.key,
        path: destination,
        filename: source.filename,
        ...(site.url ? { webUrl: site.url } : {}),
        ...(source.folderPath ? { folderPath: source.folderPath } : {}),
        access: source.access,
        metadata: {
          Title: source.title,
          Department: site.department,
          TopicTags: source.tags.join(";"),
          DocumentType: source.documentType,
          PolicyStatus: source.status,
          ReviewDate: fixture.reviewDate,
          FixtureId: source.id,
        },
      });
    }
  }
  await fs.writeFile(
    path.join(root, values.manifest),
    `${JSON.stringify({ fixtureId: fixture.fixtureId, documents: output }, null, 2)}\n`,
  );
  console.log(`Generated ${output.length} synthetic DOCX documents across ${fixture.sites.length} site/web targets.`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
