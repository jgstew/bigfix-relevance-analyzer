// esbuild entry for the browser bundle.
//
// jco's transpiled module exports `analyze`, `version` and (because of
// --tla-compat) an `$init` promise. A bundle can't hand ES module exports to an
// inline <script type="module"> in the page, so publish the namespace on a
// global instead. Doing it through a wrapper module rather than an esbuild
// --footer matters: minification renames the entry module's own bindings, and a
// footer referring to them by name would break.
import * as component from "./transpiled/analyzer.js";

globalThis.__component = component;
