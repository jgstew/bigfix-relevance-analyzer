/*
 * Relevance debugger dashboard, proof of concept: the core layer, shared by
 * the console and Web Reports builds (RDBG_BUILD.target). See README.md.
 *
 * ES5 ONLY. The BigFix console renders dashboards in its IE11 engine, where
 * one `let`, arrow function or template string is a syntax error that stops
 * this whole script. The analyzer exists only in the Web Reports build; it
 * loads separately and calls rdbg.onAnalyzer.
 *
 * Host functions used, as the older dashboards in jgstew/bigfix-content and
 * jgstew/C3-Query-Dashboard call them (none are documented, so shapes are
 * logged to the diagnostics panel):
 *   Relevance(q, {success, failure})   console session relevance, async
 *   EvaluateRelevance(q)               session relevance, sync (Web Reports)
 *   API.Post(path, body, cb) / API.Get(path, cb), cb(error, status, body)
 *   ActiveXObject                      IE engine only: runs the local qna
 */
(function () {
  "use strict";

  var SESSION_TARGETS = "ids of bes computers whose (last report time of it > now - 1 * hour)";
  var DELIM = "<~rdbg~>";
  var MAX_SHOWN = 200;
  // The Web Report fetches the analyzer after the page loads (analyzer_loader.html).
  var LOADING_NOTE = "loading (the first time downloads about 12 MB; after that it is cached in this browser)";
  // FastQuery polling backs off while waiting: the first check comes
  // POLL_FIRST_MS after the last, each gap grows by POLL_GROWTH up to
  // POLL_MAX_MS, and the last check lands on the timeout. Answers that have
  // not come in early are less likely to come in at all.
  var POLL_FIRST_MS = 2000;
  var POLL_GROWTH = 1.5;
  var POLL_MAX_MS = 15000;

  var host = null;
  var analyzer = null; // set by rdbg.onAnalyzer
  var analyzerNote = "not loaded yet";
  var editor = null; // {getText} once the analyzer mounts CodeMirror
  // The evaluation in progress, {cancelled, cancels: [fn]}. Each run's
  // callbacks hold their own one, so an abandoned run's late replies are
  // dropped rather than landing in the next run's results.
  var run = null;
  var facts = {}; // diagnostics, in insertion order via factOrder
  var factOrder = [];

  function $(id) {
    return document.getElementById(id);
  }

  function now() {
    return new Date().getTime();
  }

  function pad(n) {
    return n < 10 ? "0" + n : String(n);
  }

  function log(text) {
    var d = new Date();
    var stamp = pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds());
    var box = $("log");
    box.value += stamp + "  " + text + "\n";
    box.scrollTop = box.scrollHeight;
  }

  function setText(id, text, cls) {
    var node = $(id);
    node.innerHTML = "";
    node.appendChild(document.createTextNode(text));
    if (cls !== undefined) node.className = cls;
  }

  function errText(e) {
    if (e === null || e === undefined) return "unknown error";
    if (typeof e === "string") return e;
    return e.message || e.description || e.Message || String(e);
  }

  function fact(name, value) {
    if (!(name in facts)) factOrder.push(name);
    facts[name] = value;
    var lines = [];
    for (var i = 0; i < factOrder.length; i++) lines.push(factOrder[i] + ": " + facts[factOrder[i]]);
    $("diagText").value = lines.join("\n");
  }

  // Describe a host return value without assuming its shape.
  function shapeOf(value) {
    if (value === null) return "null";
    var t = typeof value;
    if (t !== "object") return t + (t === "string" ? " (length " + value.length + ")" : "");
    var keys = [];
    try {
      for (var k in value) {
        keys.push(k);
        if (keys.length > 8) break;
      }
    } catch (e) {}
    var first = keys.length ? " first item " + typeof value[keys[0]] : "";
    var kind = Object.prototype.toString.call(value); // "[object Date]", ...
    return kind + " keys [" + keys.join(", ") + "]" + first;
  }

  // A host result as a list of strings: an array, an object keyed "0".."n"
  // (the console's async Relevance), or a single value.
  function toList(value) {
    var out = [];
    if (value === null || value === undefined) return out;
    // A COM SAFEARRAY from the IE engine's host reports typeof "unknown".
    if (typeof value === "unknown" && typeof window.VBArray !== "undefined") {
      try {
        value = new window.VBArray(value).toArray();
      } catch (e) {}
    }
    if (value instanceof Array) {
      for (var i = 0; i < value.length; i++) out.push(String(value[i]));
      return out;
    }
    if (typeof value === "object") {
      for (var n = 0; String(n) in value; n++) out.push(String(value[String(n)]));
      if (out.length) return out;
      if (value instanceof Date) return [String(value)];
      // Anything else with no items, e.g. Web Reports' {} for an empty
      // result, is no answers.
      if (!("length" in value)) return out;
      for (var j = 0; j < value.length; j++) out.push(String(value[j]));
      return out;
    }
    return [String(value)];
  }

  // ---- load timings ----------------------------------------------------------

  // Milliseconds since the browser started the page request, or null where
  // the Navigation Timing API is missing (it exists in IE11).
  function sinceStart() {
    try {
      var t = window.performance.timing;
      return t.navigationStart ? now() - t.navigationStart : null;
    } catch (e) {
      return null;
    }
  }

  function seconds(ms) {
    return ms === null || ms === undefined || ms < 0 ? "?" : (ms / 1000).toFixed(2) + " s";
  }

  // Where the time goes before the page is usable: the server (request to
  // first byte: for a Web Report, its server-side processing), the download,
  // then the browser parsing it. Recorded once the load event has finished.
  function loadTimings() {
    var t;
    try {
      t = window.performance.timing;
    } catch (e) {
      return;
    }
    if (!t || !t.navigationStart) {
      fact("load timings", "not available in this browser");
      return;
    }
    var start = t.navigationStart;
    fact("time to first byte (server)", seconds(t.responseStart - (t.requestStart || start)));
    fact("download", seconds(t.responseEnd - t.responseStart));
    fact("DOM ready", seconds(t.domContentLoadedEventStart - start) + " after the request started");
    fact("page load", seconds(t.loadEventStart - start) + " after the request started");
    try {
      var nav = window.performance.getEntriesByType("navigation")[0];
      if (nav && nav.transferSize) {
        fact("transferred", Math.round(nav.transferSize / 1024) + " KB (" + Math.round(nav.decodedBodySize / 1024) + " KB decoded)");
      }
    } catch (e) {}
  }

  function hasGlobal(name) {
    try {
      return typeof window[name] !== "undefined" && window[name] !== null;
    } catch (e) {
      return false;
    }
  }

  function detectHost() {
    var h = {
      relevanceAsync: hasGlobal("Relevance"),
      relevanceSync: hasGlobal("EvaluateRelevance"),
      api: false,
      activeX: false,
      webReports: null,
    };
    try {
      h.api = !!(window.API && window.API.Post && window.API.Get);
    } catch (e) {}
    try {
      h.activeX = typeof window.ActiveXObject !== "undefined" || "ActiveXObject" in window;
    } catch (e) {}
    h.session = h.relevanceAsync || h.relevanceSync;
    return h;
  }

  function hostKind() {
    if (host.api) return "console";
    if (host.webReports === true) return "webreports";
    if (host.session) return host.webReports === false ? "console" : "webreports?";
    return "none";
  }

  // ---- session relevance -------------------------------------------------

  // One host call, async Relevance() if there is one, else sync
  // EvaluateRelevance(); cb(error, rawValue).
  function callHost(query, tag, cb) {
    if (host.relevanceAsync) {
      try {
        window.Relevance(query, {
          success: function (res) {
            fact("Relevance() success shape, " + tag, shapeOf(res));
            cb(null, res);
          },
          failure: function (e) {
            fact("Relevance() failure shape, " + tag, shapeOf(e) + ": " + errText(e).slice(0, 200));
            cb(errText(e));
          },
        });
      } catch (e) {
        cb("Relevance() threw: " + errText(e));
      }
      return;
    }
    if (host.relevanceSync) {
      var res;
      try {
        res = window.EvaluateRelevance(query);
      } catch (e) {
        fact("EvaluateRelevance() error, " + tag, errText(e).slice(0, 200));
        cb(errText(e));
        return;
      }
      fact("EvaluateRelevance() shape, " + tag, shapeOf(res));
      cb(null, res);
      return;
    }
    cb("no session relevance function on this page");
  }

  // done(error, answers, info). The host hands back native values (a boolean,
  // a Date for a time), so the answers are cast to strings in relevance and
  // joined into one string. Types with no string cast fail that, so the query
  // then runs as written: its answers are the host's values, and its error, if
  // any, is the query's own.
  function evalSession(query, done, label) {
    // Keyed by the query text, so a series of test queries adds up in the
    // diagnostics instead of each replacing the last.
    var shortQuery = query.replace(/\s+/g, " ");
    if (shortQuery.length > 60) shortQuery = shortQuery.slice(0, 57) + "...";
    var tag = label || '"' + shortQuery + '"';
    var started = now();
    var finished = false;
    function finish(err, answers, info) {
      if (finished) return;
      finished = true;
      clearTimeout(watchdog);
      done(err, answers || [], (info ? info + ", " : "") + (now() - started) + " ms");
    }
    var watchdog = setTimeout(function () {
      finish("no reply from the console within 120 s");
    }, 120000);
    var mode = host.relevanceAsync ? "async" : "sync";

    var wrapped = 'concatenation "' + DELIM + '" of ((it as string) of (' + query + "))";
    callHost(wrapped, tag + " as strings", function (err, res) {
      if (!err) {
        var text = toList(res).join(DELIM);
        finish(null, text === "" ? [] : text.split(DELIM), mode);
        return;
      }
      callHost(query, tag, function (err2, res2) {
        if (err2) finish(err2, [], mode);
        else finish(null, toList(res2), mode + ", host values (no string cast: " + err + ")");
      });
    });
  }

  // ---- client relevance on this machine (IE engine, ActiveX) -------------

  function findQna(fso, shell) {
    var dirs = [];
    var keys = [
      "HKLM\\SOFTWARE\\WOW6432Node\\BigFix\\EnterpriseClient\\EnterpriseClientFolder",
      "HKLM\\SOFTWARE\\BigFix\\EnterpriseClient\\EnterpriseClientFolder",
    ];
    for (var i = 0; i < keys.length; i++) {
      try {
        dirs.push(shell.RegRead(keys[i]));
      } catch (e) {}
    }
    dirs.push("C:\\Program Files (x86)\\BigFix Enterprise\\BES Client");
    dirs.push("C:\\Program Files\\BigFix Enterprise\\BES Client");
    for (var j = 0; j < dirs.length; j++) {
      var path = String(dirs[j]).replace(/\\+$/, "") + "\\qna.exe";
      if (fso.FileExists(path)) return path;
    }
    return null;
  }

  function parseQna(text) {
    var out = { answers: [], errors: [], times: [], types: [] };
    var lines = text.split(/\r?\n/);
    for (var i = 0; i < lines.length; i++) {
      // With stdin redirected, qna's "Q: " prompt is not followed by a newline,
      // so it prefixes the next output line ("Q: A: ...").
      var m = /^([AETI]): ?(.*)$/.exec(lines[i].replace(/^(Q: ?)+/, ""));
      if (!m) continue;
      if (m[1] === "A") out.answers.push(m[2]);
      else if (m[1] === "E") out.errors.push(m[2]);
      else if (m[1] === "T") out.times.push(m[2]);
      else out.types.push(m[2]);
    }
    return out;
  }

  // The relevance goes into a temp file and reaches qna on stdin, never on a
  // command line, so cmd metacharacters in it are harmless. Output goes to a
  // file too, so a large answer cannot fill the pipe and stall qna.
  function evalLocal(ctx, query, timeoutMs, done) {
    var fso, shell, exec, inFile, outFile;
    try {
      fso = new window.ActiveXObject("Scripting.FileSystemObject");
      shell = new window.ActiveXObject("WScript.Shell");
    } catch (e) {
      done("ActiveX blocked: " + errText(e));
      return;
    }
    var qna = findQna(fso, shell);
    fact("qna path", qna || "not found");
    if (!qna) {
      done("qna.exe not found (no BigFix client on this machine?)");
      return;
    }
    // qna reads one query per line.
    var oneLine = query.replace(/\s*[\r\n]+\s*/g, " ");
    var base = fso.GetSpecialFolder(2).Path + "\\" + fso.GetTempName();
    inFile = base + ".qna";
    outFile = base + ".out";
    try {
      var f = fso.CreateTextFile(inFile, true, false);
      f.WriteLine(oneLine);
      f.Close();
      exec = shell.Exec('cmd.exe /c ""' + qna + '" -t -showtypes < "' + inFile + '" > "' + outFile + '" 2>&1"');
    } catch (e) {
      done("could not start qna: " + errText(e));
      return;
    }
    var started = now();
    function cleanup() {
      try {
        fso.DeleteFile(inFile, true);
      } catch (e) {}
      try {
        fso.DeleteFile(outFile, true);
      } catch (e) {}
    }
    ctx.cancels.push(function () {
      try {
        exec.Terminate();
      } catch (e) {}
      cleanup();
    });
    function poll() {
      if (ctx.cancelled) return;
      if (exec.Status === 0) {
        if (now() - started > timeoutMs) {
          try {
            exec.Terminate();
          } catch (e) {}
          cleanup();
          done("qna did not finish within " + timeoutMs / 1000 + " s");
          return;
        }
        setTimeout(poll, 150);
        return;
      }
      var text = "";
      try {
        if (fso.FileExists(outFile)) {
          var r = fso.OpenTextFile(outFile, 1, false);
          if (!r.AtEndOfStream) text = r.ReadAll();
          r.Close();
        }
      } catch (e) {}
      cleanup();
      fact("qna output (first 300 chars)", text.slice(0, 300).replace(/\r?\n/g, " | "));
      var p = parseQna(text);
      var info = [];
      if (p.types.length) info.push("type " + p.types.join(", "));
      if (p.times.length) info.push("time " + p.times.join(", "));
      info.push(now() - started + " ms wall");
      done(p.errors.length ? p.errors.join("; ") : null, p.answers, info.join(", "));
    }
    poll();
  }

  // ---- client relevance via FastQuery (console REST API) -----------------

  function xmlEscape(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function shuffled(list) {
    var a = list.slice(0);
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i];
      a[i] = a[j];
      a[j] = t;
    }
    return a;
  }

  function parseIds(text) {
    var out = [];
    var parts = text.split(/[\s,;]+/);
    for (var i = 0; i < parts.length; i++) {
      if (/^\d+$/.test(parts[i])) out.push(parts[i]);
      else if (parts[i] !== "") return null;
    }
    return out;
  }

  // done(error, ids, why)
  function pickTargets(count, done) {
    var typed = $("ids").value;
    if (/\S/.test(typed)) {
      var ids = parseIds(typed);
      if (ids === null) done("IDs must be numbers separated by commas or spaces");
      else done(null, ids, "the IDs you entered");
      return;
    }
    evalSession(SESSION_TARGETS, function (err, answers) {
      if (err) {
        done("could not list recent computers: " + err);
        return;
      }
      if (!answers.length) {
        done("no computers reported in the last hour");
        return;
      }
      var pick = shuffled(answers).slice(0, count);
      done(null, pick, pick.length + " random of " + answers.length + " computers that reported in the last hour");
    }, "FastQuery targets");
  }

  function clientQueryXml(query, ids) {
    var targets = "";
    for (var i = 0; i < ids.length; i++) targets += "<ComputerID>" + ids[i] + "</ComputerID>";
    return (
      "<BESAPI><ClientQuery><ApplicabilityRelevance>true</ApplicabilityRelevance>" +
      "<QueryText>" +
      xmlEscape(query) +
      "</QueryText><Target>" +
      targets +
      "</Target></ClientQuery></BESAPI>"
    );
  }

  // onUpdate(rows, count, nextMs) after every check, with all results so far
  // (they are cumulative); done(error, rows, why) once. Waits the whole
  // timeout for computers that have not answered, unless ctx is cancelled.
  function evalFast(ctx, query, ids, timeoutMs, onUpdate, done) {
    var started = now();
    var timer = null;
    var delay = POLL_FIRST_MS;
    ctx.cancels.push(function () {
      clearTimeout(timer);
    });
    try {
      window.API.Post("clientquery", clientQueryXml(query, ids), function (error, status, body) {
        if (ctx.cancelled) return;
        fact("API.Post clientquery", "status " + status + (error ? ", error " + errText(error) : ""));
        var m = /<ID>\s*(\d+)\s*<\/ID>/.exec(String(body || ""));
        if (error || !m) {
          done("FastQuery submit failed (status " + status + "): " + (error ? errText(error) : String(body).slice(0, 300)));
          return;
        }
        log("FastQuery " + m[1] + " submitted to " + ids.length + " computer(s)");
        poll(m[1]);
      });
    } catch (e) {
      done("API.Post threw: " + errText(e));
      return;
    }

    function poll(queryId) {
      if (ctx.cancelled) return;
      try {
        window.API.Get("clientqueryresults/" + queryId + "?output=json", function (error, status, body) {
          if (ctx.cancelled) return;
          var rows;
          try {
            rows = JSON.parse(body).results || [];
          } catch (e) {
            fact("clientqueryresults body", "status " + status + ", " + String(body).slice(0, 200));
            done("could not read FastQuery results (status " + status + "): " + (error ? errText(error) : errText(e)));
            return;
          }
          var seen = {};
          var count = 0;
          for (var i = 0; i < rows.length; i++) {
            if (!seen[rows[i].computerID]) {
              seen[rows[i].computerID] = true;
              count++;
            }
          }
          if (count >= ids.length) return done(null, rows, "all " + count + " answered");
          var left = timeoutMs - (now() - started);
          if (left <= 0) {
            return done(null, rows, count + " of " + ids.length + " answered within " + Math.round(timeoutMs / 1000) + " s");
          }
          var wait = Math.min(delay, left);
          delay = Math.min(delay * POLL_GROWTH, POLL_MAX_MS);
          onUpdate(rows, count, wait);
          timer = setTimeout(function () {
            poll(queryId);
          }, wait);
        });
      } catch (e) {
        done("API.Get threw: " + errText(e));
      }
    }
  }

  // ---- dialect (console) --------------------------------------------------

  // The console has no analyzer (IE11), so Auto is a keyword guess.
  var SESSION_HINT = /\b(bes\s+[a-z]|current\s+console\s+user|in\s+web\s+reports\s+context|current\s+user\b|all\s+bes\s)/i;
  var CLIENT_HINT = /\b(operating\s+system|registry|files?\s|folders?\s|computer\s+name|running\s+application|services?\b|processes|active\s+device|ip\s+interfaces?)/i;

  function chooseDialects(text) {
    var mode = $("dialect").value;
    if (mode === "session") return { dialects: ["session"], why: "you picked session relevance" };
    if (mode === "client") return { dialects: ["client"], why: "you picked client relevance" };
    if (mode === "both") return { dialects: ["session", "client"], why: "you picked both" };
    var s = SESSION_HINT.test(text);
    var c = CLIENT_HINT.test(text);
    if (s && !c) return { dialects: ["session"], why: "it mentions session inspectors (a keyword guess)" };
    if (c && !s) return { dialects: ["client"], why: "it mentions client inspectors (a keyword guess)" };
    return { dialects: ["session", "client"], why: "the keywords don't settle it, so both run" };
  }

  // ---- results (console table) ---------------------------------------------

  function tbody() {
    return $("results").getElementsByTagName("tbody")[0];
  }

  function addRow(cells) {
    var tr = document.createElement("tr");
    for (var i = 0; i < cells.length; i++) {
      var td = document.createElement("td");
      if (i === 3) td.className = "answer";
      if (i === 4 && cells[i]) td.className = "error";
      td.appendChild(document.createTextNode(cells[i] === null || cells[i] === undefined ? "" : String(cells[i])));
      tr.appendChild(td);
    }
    tbody().appendChild(tr);
    return tr;
  }

  function answersCell(answers) {
    if (!answers.length) return "(no answers)";
    var shown = answers.slice(0, MAX_SHOWN).join("\n");
    if (answers.length > MAX_SHOWN) shown += "\n... " + (answers.length - MAX_SHOWN) + " more";
    return shown;
  }

  function clearResults() {
    var body = tbody();
    while (body.firstChild) body.removeChild(body.firstChild);
  }

  // ---- what can run here -----------------------------------------------

  function clientPaths() {
    var local = host.activeX && hostKind() === "console";
    var fast = host.api;
    var why = [];
    if (!local) why.push(host.activeX ? "this computer (qna) needs the console" : "this computer (qna) needs ActiveX, which this browser does not have");
    if (!fast) why.push("FastQuery needs the console's REST API");
    $("useLocal").disabled = !local;
    $("useFast").disabled = !fast;
    if (!local) $("useLocal").checked = false;
    if (!fast) $("useFast").checked = false;
    setText("clientWhy", why.length ? "Unavailable here: " + why.join("; ") + "." : "");
    return { local: local, fast: fast };
  }

  // A notice only when this build is somewhere it cannot do its job.
  function describeHost() {
    var kind = hostKind();
    var engine = document.documentMode ? "IE " + document.documentMode + " engine" : "modern engine";
    fact("host", kind + ", " + engine);
    var notice = "";
    if (target === "console") {
      if (kind === "none") notice = "Open this as a dashboard in the BigFix console to evaluate relevance.";
      else if (kind !== "console") notice = "This is the console dashboard; in Web Reports use the Web Reports version.";
      clientPaths();
    } else {
      if (!host.session) notice = "Open this as a Web Report to evaluate session relevance. Analysis still works here.";
      if (!analyzer) setText("analysis", "The analyzer is " + analyzerNote + ".", "hint");
    }
    setText("hostNotice", notice);
    setText("footer", (kind === "none" ? "Standalone page" : kind === "console" ? "BigFix console" : "BigFix Web Reports") + " - " + engine + " - analyzer " + analyzerNote + " - built " + (build.built || "?"));
  }

  // ---- evaluate ------------------------------------------------------------

  function getQuery() {
    return (editor ? editor.getText() : $("rel").value).replace(/^\s+|\s+$/g, "");
  }

  // Only the current run may finish the page's run state.
  function finishRun(ctx, message) {
    if (run !== ctx) return;
    run = null;
    if ($("cancel")) $("cancel").disabled = true;
    setText("status", message);
  }

  // Evaluate stays clickable while a run is going: a new query abandons it.
  function startRun() {
    if (run) stopRun("abandoned for a new query");
    run = { cancelled: false, cancels: [] };
    if ($("cancel")) $("cancel").disabled = false;
    setText("status", "Evaluating...");
    return run;
  }

  function stopRun(why) {
    var ctx = run;
    if (!ctx) return;
    ctx.cancelled = true;
    for (var i = 0; i < ctx.cancels.length; i++) {
      try {
        ctx.cancels[i]();
      } catch (e) {}
    }
    log("previous run " + why);
    finishRun(ctx, "Cancelled.");
  }

  // Web Reports: what the analyzer's dialect call means here. Session
  // relevance runs whatever it says; the note only sets expectations.
  function showDialect(choice) {
    var note = "";
    if (choice.dialects.length === 1 && choice.dialects[0] === "client") {
      note = "This looks like client relevance (" + choice.why + "), which Web Reports cannot evaluate. Evaluate tries it as session relevance anyway, in case that is wrong.";
    } else if (choice.dialects.length > 1) {
      note = "Evaluate runs it as session relevance: " + choice.why + ".";
    }
    if ($("dialectNote")) setText("dialectNote", note);
  }

  // Web Reports: analysis, then session relevance, always. Client relevance
  // cannot run here, but the dialect call can be wrong and a session error
  // comes back at once, so it is tried anyway after saying so.
  function evaluateWebReport() {
    var query = getQuery();
    if (!query) return;
    if (analyzer) {
      try {
        analyzer.analyze(query); // shows the dialect note too
      } catch (e) {
        log("analysis failed: " + errText(e));
      }
    }
    var out = $("wrResult");
    if (!host.session) {
      setText("wrResult", "Session relevance can only be evaluated in Web Reports.", "hint");
      return;
    }
    var ctx = startRun();
    log("session: evaluating");
    evalSession(query, function (err, answers, info) {
      if (ctx.cancelled) return;
      out.innerHTML = "";
      out.className = "";
      var summary = document.createElement("p");
      summary.className = "summary" + (err ? " error" : "");
      summary.appendChild(document.createTextNode(err ? "Error" : answers.length === 1 ? "1 answer" : answers.length + " answers"));
      var detail = document.createElement("span");
      detail.className = "hint";
      detail.appendChild(document.createTextNode("  -  " + info));
      summary.appendChild(detail);
      out.appendChild(summary);
      if (err) {
        var box = document.createElement("div");
        box.className = "errbox";
        box.appendChild(document.createTextNode(err));
        out.appendChild(box);
      } else if (answers.length) {
        var list = document.createElement("ol");
        list.className = "answers";
        for (var i = 0; i < answers.length && i < MAX_SHOWN; i++) {
          var li = document.createElement("li");
          li.appendChild(document.createTextNode(answers[i]));
          list.appendChild(li);
        }
        out.appendChild(list);
        if (answers.length > MAX_SHOWN) {
          var more = document.createElement("p");
          more.className = "hint";
          more.appendChild(document.createTextNode("... and " + (answers.length - MAX_SHOWN) + " more"));
          out.appendChild(more);
        }
      }
      log("session: " + (err ? "error" : answers.length + " answer(s)"));
      finishRun(ctx, "Done.");
    });
  }

  // FastQuery's rows in the console table, redrawn on every check: one per
  // computer that answered, then one per target still waiting.
  function fastQueryRows(ids, why) {
    var drawn = [];
    return function (rows, final) {
      for (var d = 0; d < drawn.length; d++) {
        if (drawn[d].parentNode) drawn[d].parentNode.removeChild(drawn[d]);
      }
      drawn = [];
      var byComputer = {};
      var order = [];
      for (var i = 0; i < rows.length; i++) {
        var r = rows[i];
        var key = String(r.computerID);
        if (!byComputer[key]) {
          byComputer[key] = { name: r.computerName, answers: [], errors: [], ms: r.ResponseTime };
          order.push(key);
        }
        (r.isFailure ? byComputer[key].errors : byComputer[key].answers).push(r.result);
      }
      for (var k = 0; k < order.length; k++) {
        var c = byComputer[order[k]];
        drawn.push(addRow(["client", "FastQuery", c.name + " (" + order[k] + ")", answersCell(c.answers), c.errors.join("; "), c.ms + " ms"]));
      }
      for (var n = 0; n < ids.length; n++) {
        if (!byComputer[ids[n]]) {
          drawn.push(addRow(["client", "FastQuery", ids[n], final ? "" : "waiting...", "", final ? "no answer" : why]));
        }
      }
    };
  }

  // Console: session and/or client relevance, as picked or guessed.
  function evaluateConsole() {
    var query = getQuery();
    if (!query) return;
    var choice = chooseDialects(query);
    var paths = clientPaths();
    var ctx = startRun();
    setText("dialectWhy", "Runs " + choice.dialects.join(" then ") + ": " + choice.why + ".");
    clearResults();
    var timeoutMs = Math.max(5, parseInt($("timeoutSec").value, 10) || 90) * 1000;
    var steps = [];

    for (var d = 0; d < choice.dialects.length; d++) {
      if (choice.dialects[d] === "session") {
        steps.push(function (next) {
          if (!host.session) {
            addRow(["session", "-", "", "", "Session relevance needs the BigFix console.", ""]);
            return next();
          }
          log("session: evaluating");
          evalSession(query, function (err, answers, info) {
            if (ctx.cancelled) return;
            addRow(["session", "this deployment", "", err ? "" : answersCell(answers), err, answers.length + " answer(s), " + info]);
            log("session: " + (err ? "error" : answers.length + " answer(s)"));
            next();
          });
        });
      } else {
        if (!$("useLocal").checked && !$("useFast").checked) {
          steps.push(function (next) {
            var why = paths.local || paths.fast ? "Tick This computer or FastQuery to run it." : $("clientWhy").textContent;
            addRow(["client", "-", "", "", "", "Not evaluated. " + why]);
            next();
          });
        }
        if ($("useLocal").checked) {
          steps.push(function (next) {
            log("client: qna on this computer");
            evalLocal(ctx, query, timeoutMs, function (err, answers, info) {
              if (ctx.cancelled) return;
              addRow(["client", "this computer (qna)", "", err && !answers ? "" : answersCell(answers || []), err, info || ""]);
              log("client qna: " + (err ? "error" : (answers || []).length + " answer(s)"));
              next();
            });
          });
        }
        if ($("useFast").checked) {
          steps.push(function (next) {
            var count = Math.max(1, parseInt($("fastCount").value, 10) || 5);
            pickTargets(count, function (err, ids, why) {
              if (ctx.cancelled) return;
              if (err) {
                addRow(["client", "FastQuery", "", "", err, ""]);
                return next();
              }
              log("FastQuery targets: " + ids.join(", ") + " (" + why + ")");
              var draw = fastQueryRows(ids, why);
              draw([], false);
              evalFast(
                ctx,
                query,
                ids,
                timeoutMs,
                function (rows, answered, nextMs) {
                  draw(rows, false);
                  setText("status", "FastQuery: " + answered + " of " + ids.length + " answered; checking again in " + Math.round(nextMs / 1000) + " s...");
                },
                function (err2, rows, why2) {
                  if (ctx.cancelled) return;
                  draw(rows || [], true);
                  if (err2) addRow(["client", "FastQuery", "", "", err2, why]);
                  log("FastQuery: " + (err2 || why2));
                  next();
                }
              );
            });
          });
        }
      }
    }

    var i = 0;
    function next() {
      if (ctx.cancelled) return;
      if (i >= steps.length) return finishRun(ctx, "Done.");
      steps[i++](next);
    }
    next();
  }

  function evaluate() {
    if (target === "console") evaluateConsole();
    else evaluateWebReport();
  }

  function cancel() {
    stopRun("cancelled");
  }

  function copyDiagnostics() {
    var box = $("diagText");
    box.focus();
    box.select();
    var ok = false;
    try {
      ok = document.execCommand("copy");
    } catch (e) {}
    if (!ok && window.clipboardData) {
      try {
        ok = window.clipboardData.setData("Text", box.value);
      } catch (e) {}
    }
    log(ok ? "diagnostics copied" : "select the diagnostics text and copy it by hand");
  }

  // ---- page setup ------------------------------------------------------------

  // Drop the other target's parts (data-only="console" / "webreport").
  function keepTarget() {
    var all = document.getElementById("rdbg").getElementsByTagName("*");
    var drop = [];
    for (var i = 0; i < all.length; i++) {
      var only = all[i].getAttribute("data-only");
      if (only && only !== target) drop.push(all[i]);
    }
    for (var j = 0; j < drop.length; j++) {
      if (drop[j].parentNode) drop[j].parentNode.removeChild(drop[j]);
    }
  }

  // IE11 has no <details>: show only the summary until it is clicked.
  function polyfillDetails() {
    if ("open" in document.createElement("details")) return;
    document.getElementById("rdbg").className += " no-details";
    var all = document.getElementsByTagName("details");
    for (var i = 0; i < all.length; i++) {
      (function (d) {
        var summary = d.getElementsByTagName("summary")[0];
        function show(open) {
          for (var c = d.firstChild; c; c = c.nextSibling) {
            if (c.nodeType === 1 && c !== summary) c.style.display = open ? "" : "none";
          }
          if (open) d.setAttribute("open", "open");
          else d.removeAttribute("open");
        }
        show(false);
        summary.onclick = function () {
          show(!d.getAttribute("open"));
        };
      })(all[i]);
    }
  }

  // ---- hooks for the analyzer layer (webreport) ---------------------------

  window.rdbg = {
    // api: {dialect(text) -> {dialects, why}, analyze(text), editor: {getText}}
    onAnalyzer: function (api, info) {
      fact("analyzer ready", seconds(sinceStart()) + " after the request started");
      analyzer = api;
      if (api.editor) {
        editor = api.editor;
        $("rel").style.display = "none";
      }
      analyzerNote = "loaded" + (info ? " (" + info + ")" : "");
      fact("analyzer", analyzerNote);
      describeHost();
      log("analyzer " + analyzerNote);
    },
    onAnalyzerFailed: function (reason) {
      analyzerNote = "unavailable: " + reason;
      fact("analyzer", analyzerNote);
      describeHost();
      log("analyzer " + analyzerNote);
    },
    initialText: function () {
      return $("rel").value;
    },
    evaluate: evaluate,
    showDialect: showDialect,
    log: log,
    fact: fact,
  };

  // ---- start -----------------------------------------------------------------

  // window.RDBG_BUILD is set by build_poc.py in a script before this one.
  var build = window.RDBG_BUILD || {};
  var target = build.target === "webreport" ? "webreport" : "console";
  keepTarget();
  polyfillDetails();

  fact("core ready (Evaluate usable)", seconds(sinceStart()) + " after the request started");
  host = detectHost();
  fact("build", target + ", built " + (build.built || "?"));
  fact("userAgent", navigator.userAgent);
  fact("documentMode", document.documentMode || "none");
  fact("WebAssembly", typeof window.WebAssembly);
  fact("DecompressionStream", typeof window.DecompressionStream);
  fact("ActiveXObject", host.activeX);
  fact("Relevance", hasGlobal("Relevance") ? typeof window.Relevance : "missing");
  fact("EvaluateRelevance", hasGlobal("EvaluateRelevance") ? typeof window.EvaluateRelevance : "missing");
  fact("API.Post/API.Get", host.api);
  fact("location", location.protocol + "//" + location.host);
  // Measured once the whole page has parsed, not just up to this script.
  var measure = function () {
    fact("page size (chars)", document.documentElement.outerHTML.length);
    // loadEventStart is only set once the load handlers are running.
    setTimeout(loadTimings, 0);
  };
  if (window.addEventListener) window.addEventListener("load", measure, false);
  else window.attachEvent("onload", measure);

  if (!build.analyzer) {
    analyzerNote = "not part of the console version";
  } else if (document.documentMode) {
    analyzerNote = "unavailable: this browser cannot run it (IE)";
  } else {
    analyzerNote = LOADING_NOTE;
    setTimeout(function () {
      if (!analyzer && analyzerNote === LOADING_NOTE) window.rdbg.onAnalyzerFailed("did not load within 5 minutes");
    }, 300000);
  }
  fact("analyzer", analyzerNote);
  describeHost();

  if (host.session) {
    evalSession(
      "in web reports context",
      function (err, answers) {
        host.webReports = err ? null : /^true$/i.test(answers[0]);
        fact("in web reports context", err ? "error: " + err : answers.join(", "));
        describeHost();
      },
      "web reports probe"
    );
  }

  $("evaluate").onclick = evaluate;
  if ($("cancel")) $("cancel").onclick = cancel;
  $("copyDiag").onclick = copyDiagnostics;
  // Ctrl+Enter in the plain textarea (the analyzer's editor has its own).
  $("rel").onkeydown = function (e) {
    e = e || window.event;
    if (e.keyCode === 13 && (e.ctrlKey || e.metaKey)) {
      evaluate();
      return false;
    }
  };
  log("core ready (" + target + ")");
})();
