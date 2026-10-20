// A split analyzer set (../SPLIT_ANALYZER.md, format 1) made from a built single-file
// playground page, for test_reports.mjs: the real producer is the analyzer's
// release build, this is a stand-in so the Web Report can be tested against
// the contract before that exists.

import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { gunzipSync } from "node:zlib";

import { extract } from "./loader.mjs";

const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex");

// Writes outDir/{editor.js, glue.mjs, analyzer.core*.wasm.gz, manifest.json}
// (the manifest last) and returns the manifest.
export function writeSplitSet(playgroundHtml, outDir, version = "0.0.0-fixture") {
  const pieces = extract(readFileSync(playgroundHtml, "utf8"));
  mkdirSync(outDir, { recursive: true });
  const write = (path, data) => {
    const bytes = Buffer.from(data);
    writeFileSync(join(outDir, path), bytes);
    return { path, size: bytes.length, sha256: sha256(bytes) };
  };
  const manifest = {
    format: 1,
    package: "bigfix-relevance-analyzer",
    version,
    editor: write("editor.js", pieces.editor),
    glue: write("glue.mjs", pieces.glue),
    cores: Object.entries(pieces.cores).map(([name, b64]) => {
      const gz = Buffer.from(b64, "base64");
      const raw = gunzipSync(gz);
      return { name, ...write(`${name}.gz`, gz), encoding: "gzip", raw_size: raw.length, raw_sha256: sha256(raw) };
    }),
  };
  writeFileSync(join(outDir, "manifest.json"), JSON.stringify(manifest, null, 2) + "\n");
  return manifest;
}
