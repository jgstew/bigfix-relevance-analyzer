// One namespace of the CodeMirror 6 names a page passes the shared client as
// `CM`, from this package's exact pins: what `npm test` gives the tests as
// CM_MODULE. NiceGUI's bundle (the debugger's) exports the same names from the
// same three packages, at the same versions.
export * from "@codemirror/state";
export * from "@codemirror/view";
export * from "@codemirror/language";
