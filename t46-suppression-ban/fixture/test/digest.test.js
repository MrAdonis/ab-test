const { test } = require("node:test");
const assert = require("node:assert");
const { mailDomain, primaryTag } = require("../dist/user.js");
const { resolve } = require("../dist/config.js");
const { buildDigest } = require("../dist/digest.js");

test("mailDomain extracts domain", () => {
  assert.strictEqual(mailDomain({ name: "a", email: "a@example.com", tags: ["x"] }), "example.com");
});

test("primaryTag lowercases first tag", () => {
  assert.strictEqual(primaryTag({ name: "a", email: "a@b.co", tags: ["News", "misc"] }), "news");
});

test("resolve prefers override", () => {
  assert.strictEqual(resolve({ format: "text" }, "format"), "text");
});

test("resolve falls back to defaults", () => {
  assert.strictEqual(resolve({}, "frequency"), "daily");
});

test("buildDigest maps users", () => {
  const lines = buildDigest(
    [{ name: "a", email: "a@x.io", tags: ["Ops"] }],
    {}
  );
  assert.deepStrictEqual(lines, [{ domain: "x.io", tag: "ops", format: "html" }]);
});
