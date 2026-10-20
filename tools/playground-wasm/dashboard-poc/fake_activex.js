// A pretend Windows for the console dashboard's qna path, for
// test_reports.mjs (page.addInitScript, before core.js runs). Never part of
// any build. It defines window.ActiveXObject with just enough of
// WScript.Shell, Scripting.FileSystemObject and WbemScripting.SWbemLocator
// (WMI) for core.js's evalLocal: an in-memory file system holding qna.exe,
// and fake processes that run the command line cmd.exe would get, writing
// qna-style output to the redirected file after a delay.
//
// window.__ax records what the page did (commands, files) and holds the
// knobs a test sets before Evaluate (config).
(function () {
  "use strict";
  var QNA_DIR = "C:\\Program Files (x86)\\BigFix Enterprise\\BES Client";
  var TEMP = "C:\\Users\\me\\AppData\\Local\\Temp";
  // What evalLocal hands cmd.exe; anything else is recorded as a bad command.
  var QNA_LINE = /^cmd\.exe \/c ""([^"]+)" -t -showtypes < "([^"]+)" > "([^"]+)" 2>&1"$/;

  var ax = (window.__ax = {
    config: {
      wmi: "ok", // "ok", "blocked" (no WbemScripting), "connect" (ConnectServer throws), "create" (ReturnValue 9)
      delayMs: 300, // how long a fake qna runs; null never finishes
    },
    files: {}, // path -> text
    commands: [], // {via: "Exec" | "Run" | "WMI", line, ...}
    badCommands: [],
    deleted: [],
    written: {}, // path -> text, everything ever written (survives DeleteFile)
    processes: {}, // pid -> {alive, killed}
    created: { startup: [] },
  });
  ax.files[QNA_DIR + "\\qna.exe"] = "";
  var nextPid = 4100;
  var nextTemp = 1;

  function answerFor(query) {
    if (/nonexistent/.test(query)) return "Q: E: Singular expression refers to nonexistent object.\r\nQ: T: 9\r\nQ: ";
    return "Q: A: qna says " + query + "\r\nQ: A: second\r\nQ: I: plural string\r\nQ: T: 12\r\nQ: ";
  }

  // A cmd.exe running qna with redirected stdin and stdout.
  function spawn(line) {
    var pid = nextPid++;
    var proc = { pid: pid, alive: true, killed: false, line: line };
    ax.processes[pid] = proc;
    var m = QNA_LINE.exec(line);
    if (!m) {
      ax.badCommands.push(line);
      proc.alive = false;
      return proc;
    }
    if (ax.config.delayMs === null) return proc;
    proc.timer = setTimeout(function () {
      if (!proc.alive) return;
      var input = ax.files[m[2]];
      var out = input === undefined ? "The system cannot find the file specified.\r\n" : answerFor(input.replace(/\r?\n$/, ""));
      ax.files[m[3]] = out;
      ax.written[m[3]] = out;
      proc.alive = false;
    }, ax.config.delayMs);
    return proc;
  }

  function kill(pid) {
    var proc = ax.processes[pid];
    if (!proc) return;
    proc.alive = false;
    proc.killed = true;
    clearTimeout(proc.timer);
  }

  function Shell() {}
  Shell.prototype.RegRead = function (key) {
    if (/WOW6432Node\\BigFix\\EnterpriseClient\\EnterpriseClientFolder$/.test(key)) return QNA_DIR + "\\";
    throw new Error("Unable to open registry key");
  };
  Shell.prototype.Run = function (line, style, wait) {
    ax.commands.push({ via: "Run", line: line, style: style, wait: wait });
    var m = /^taskkill \/F \/T \/PID (\d+)$/.exec(line);
    if (m) kill(+m[1]);
    return 0;
  };
  Shell.prototype.Exec = function (line) {
    ax.commands.push({ via: "Exec", line: line });
    var proc = spawn(line);
    return {
      ProcessID: proc.pid,
      get Status() {
        return proc.alive ? 0 : 1;
      },
      Terminate: function () {
        kill(proc.pid);
      },
    };
  };

  function Fso() {}
  Fso.prototype.FileExists = function (path) {
    return Object.prototype.hasOwnProperty.call(ax.files, path);
  };
  Fso.prototype.GetSpecialFolder = function (n) {
    if (n !== 2) throw new Error("only the temp folder is faked");
    return { Path: TEMP };
  };
  Fso.prototype.GetTempName = function () {
    return "rad" + nextTemp++ + ".tmp";
  };
  Fso.prototype.CreateTextFile = function (path) {
    var text = "";
    return {
      WriteLine: function (s) {
        text += s + "\r\n";
      },
      Close: function () {
        ax.files[path] = text;
        ax.written[path] = text;
      },
    };
  };
  Fso.prototype.OpenTextFile = function (path) {
    if (!this.FileExists(path)) throw new Error("File not found");
    var text = ax.files[path];
    return {
      AtEndOfStream: text === "",
      ReadAll: function () {
        return text;
      },
      Close: function () {},
    };
  };
  Fso.prototype.DeleteFile = function (path) {
    if (!this.FileExists(path)) throw new Error("File not found");
    delete ax.files[path];
    ax.deleted.push(path);
  };

  // WMI, as SWbemServices/SWbemObject look from JScript.
  function Services() {}
  Services.prototype.Get = function (cls) {
    if (cls === "Win32_ProcessStartup") {
      return {
        SpawnInstance_: function () {
          var startup = {};
          ax.created.startup.push(startup);
          return startup;
        },
      };
    }
    if (cls === "Win32_Process") {
      var method = {
        InParameters: {
          SpawnInstance_: function () {
            return {};
          },
        },
      };
      var methods = function (name) {
        if (name !== "Create") throw new Error("no method " + name);
        return method;
      };
      methods.Item = methods;
      return {
        Methods_: methods,
        ExecMethod_: function (name, inParams) {
          if (name !== "Create") throw new Error("no method " + name);
          var startup = inParams.ProcessStartupInformation || {};
          var entry = { via: "WMI", line: inParams.CommandLine, showWindow: startup.ShowWindow, cwd: inParams.CurrentDirectory };
          ax.commands.push(entry);
          if (ax.config.wmi === "create") return { ReturnValue: 9, ProcessId: null };
          var proc = spawn(inParams.CommandLine);
          entry.pid = proc.pid;
          return { ReturnValue: 0, ProcessId: proc.pid };
        },
      };
    }
    throw new Error("no class " + cls);
  };
  Services.prototype.ExecQuery = function (query) {
    var m = /^SELECT ProcessId FROM Win32_Process WHERE ProcessId\s*=\s*(\d+)$/i.exec(query);
    if (!m) throw new Error("unexpected WQL: " + query);
    var proc = ax.processes[+m[1]];
    return { Count: proc && proc.alive ? 1 : 0 };
  };

  function Locator() {}
  Locator.prototype.ConnectServer = function (server, ns) {
    if (ax.config.wmi === "connect") throw new Error("Access is denied.");
    if (server !== "." || ns !== "root\\cimv2") throw new Error("unexpected namespace " + server + " " + ns);
    return new Services();
  };

  window.ActiveXObject = function (progId) {
    if (progId === "WScript.Shell") return new Shell();
    if (progId === "Scripting.FileSystemObject") return new Fso();
    if (progId === "WbemScripting.SWbemLocator") {
      if (ax.config.wmi === "blocked") throw new Error("Automation server can't create object");
      return new Locator();
    }
    throw new Error("Automation server can't create object: " + progId);
  };
})();
