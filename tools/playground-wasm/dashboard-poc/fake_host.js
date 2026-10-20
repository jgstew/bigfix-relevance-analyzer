// A pretend BigFix console or Web Reports, for trying the pages in a plain
// browser. build_poc.py --fake-hosts inlines it, after setting
// window.FAKE_HOST to "console" or "webreports". Never part of a real build.
// It mimics what was measured in a real console and Web Reports (README.md):
// Relevance() returns native values, and our "as strings" wrapper one string.
// window.__fake records what the page sent.
(function () {
  "use strict";
  var mode = window.FAKE_HOST === "webreports" ? "webreports" : "console";
  var fake = (window.__fake = { mode: mode, relevance: [], posts: [], gets: [] });
  var IDS = ["101", "102", "103", "104", "105", "106", "107", "108"];
  var DELIM = "<~rdbg~>";
  var CLIENT_ONLY = /operating system|running application|registry/;

  window.Relevance = function (query, callbacks) {
    fake.relevance.push(query);
    var wrapped = /^concatenation "<~rdbg~>" of \(\(it as string\) of \((.*)\)\)$/.exec(query);
    var inner = wrapped ? wrapped[1] : query;
    setTimeout(function () {
      if (/nonexistent/.test(inner)) return callbacks.failure("Singular expression refers to nonexistent object.");
      if (CLIENT_ONLY.test(inner)) return callbacks.failure('The property "' + CLIENT_ONLY.exec(inner)[0] + '" is not defined.');
      if (wrapped && /^bes computers( whose \(false\))?$/.test(inner)) return callbacks.failure('The operator "string" is not defined.');
      var values;
      if (/ids of bes computers/.test(inner)) values = IDS.slice(0);
      else if (inner === "in web reports context") values = [mode === "webreports"];
      else if (inner === "now") values = [new Date()];
      else if (inner === "number of bes computers") values = [IDS.length];
      else if (/whose \(false\)/.test(inner)) values = [];
      else values = ["answer one", "answer two"];
      if (wrapped) return callbacks.success(values.map(String).join(DELIM));
      // Measured: Web Reports hands back an empty string for no answers.
      if (!values.length) return callbacks.success(mode === "webreports" ? "" : values);
      callbacks.success(values.length === 1 ? values[0] : values);
    }, 50);
  };
  window.EvaluateRelevance = function () {
    throw new Error("the fake host only implements Relevance()");
  };

  if (mode !== "console") return;

  var polls = 0;
  window.API = {
    Post: function (path, body, cb) {
      fake.posts.push({ path: path, body: body });
      polls = 0;
      setTimeout(function () {
        cb(null, 200, '<?xml version="1.0"?><BESAPI><ClientQuery Resource="x"><ID>42</ID></ClientQuery></BESAPI>');
      }, 50);
    },
    Get: function (path, cb) {
      fake.gets.push(path);
      polls++;
      var targets = (fake.posts[fake.posts.length - 1].body.match(/<ComputerID>(\d+)/g) || []).map(function (m) {
        return m.replace("<ComputerID>", "");
      });
      // One more computer answers per poll; the last target never answers.
      var answered = targets.slice(0, Math.min(polls, targets.length - 1));
      var results = answered.map(function (id) {
        var failed = id === targets[0];
        return { computerID: +id, computerName: "HOST" + id, subQueryID: 1, isFailure: failed, result: failed ? "Singular expression refers to nonexistent object." : "Windows Server 2022", ResponseTime: 1000 };
      });
      setTimeout(function () {
        cb(null, 200, JSON.stringify({ results: results }));
      }, 50);
    },
  };
})();
