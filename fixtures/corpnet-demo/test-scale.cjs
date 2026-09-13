const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const { buildScale } = require("./build-scale.cjs");

const load = (name) => JSON.parse(fs.readFileSync(path.join(__dirname, name), "utf8"));
const expansion = load("expansion-content.json");
const paging = load("paging-content.json");

test("400 additions produce an exact 512-item six-page blueprint", () => {
  const { fixture, oracle } = buildScale(expansion, paging);
  assert.equal(fixture.sites.length, 10);
  assert.equal(oracle.artifacts.length, 512);
  assert.equal(oracle.artifacts.filter((item) => item.kind === "DOCX").length, 499);
  assert.equal(oracle.artifacts.filter((item) => item.kind === "Page").length, 13);
  assert.deepEqual(oracle.expectedNativePageSizes, [100, 100, 100, 100, 100, 12]);
  assert.equal(new Set(oracle.artifacts.map((item) => item.id)).size, 512);
  assert.equal(new Set(oracle.artifacts.map((item) => item.url.toLowerCase())).size, 512);
});

test("every site receives 20 root and 20 nested documents with inherited access", () => {
  const { fixture } = buildScale(expansion, paging);
  for (const site of fixture.sites) {
    assert.equal(site.documents.length, 40);
    assert.equal(site.documents.filter((item) => item.folderPath === "/Shared Documents").length, 20);
    assert.equal(site.documents.filter((item) => item.folderPath.endsWith("/Runbooks/Quarter One")).length, 20);
    assert.ok(site.documents.every((item) => item.access === "site" && item.status === "Approved"));
  }
});

test("content-only markers and metadata-only tags stay in their intended locations", () => {
  const { fixture } = buildScale(expansion, paging);
  for (const site of fixture.sites) {
    for (const document of site.documents) {
      const body = document.sections.flatMap((section) => section.paragraphs).join(" ");
      assert.ok(body.includes(fixture.bodyOnlyMarker));
      assert.ok(body.includes(fixture.searchMarker));
      assert.ok(body.includes(fixture.additionalMarker));
      assert.ok(!JSON.stringify({
        id: document.id, filename: document.filename, title: document.title, tags: document.tags,
      }).includes(fixture.bodyOnlyMarker));
      assert.ok(!body.includes(document.tags[2]));
      assert.ok(!/\bdevices\b|annual leave/i.test(body + document.title + document.tags.join(" ")));
    }
  }
});

test("generation is deterministic and does not mutate either historical baseline", () => {
  const before = JSON.stringify({ expansion, paging });
  assert.deepEqual(buildScale(expansion, paging), buildScale(expansion, paging));
  assert.equal(JSON.stringify({ expansion, paging }), before);
});

test("changed baselines and duplicate target sites fail explicitly", () => {
  const missing = structuredClone(expansion);
  missing.sites[0].documents.pop();
  assert.throws(() => buildScale(missing, paging), /unchanged 112-item baseline/);
  const duplicate = structuredClone(expansion);
  duplicate.sites[1].url = duplicate.sites[0].url;
  assert.throws(() => buildScale(duplicate, paging), /ten distinct sites/);
});
