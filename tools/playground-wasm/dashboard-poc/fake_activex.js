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
  // What evalLocal hands cmd.exe, optionally creating a "finished" file
  // after qna; anything else is recorded as a bad command.
  var QNA_LINE = /^cmd\.exe \/c ""([^"]+)" -t -showtypes < "([^"]+)" > "([^"]+)" 2>&1(?: & type nul > "([^"]+)")?"$/;
  var NOT_FOUND = -2147217406; // wbemErrNotFound, 0x80041002, as JScript's e.number

  var ax = (window.__ax = {
    config: {
      // "ok", "blocked" (no WbemScripting), "connect" (ConnectServer throws),
      // "create" (ReturnValue 9, no process), "create-string" (ReturnValue
      // "0", a process), "create-odd" (ReturnValue 9 and a process)
      wmi: "ok",
      wmiQuery: "ok", // "throws": every lookup of a process fails (not wbemErrNotFound)
      runThrows: false, // WScript.Shell.Run throws (taskkill cannot run)
      delayMs: 300, // how long a fake qna runs; 0 finishes inside Create; null never finishes
    },
    wmiLookups: 0, // ExecQuery and Get("Win32_Process.Handle=...") calls
    terminated: [], // pids ended through WMI's Terminate()
    files: {}, // path -> text
    commands: [], // {via: "Exec" | "Run" | "WMI", line, ...}
    badCommands: [],
    deleted: [],
    written: {}, // path -> text, everything ever written (survives DeleteFile)
    processes: {}, // pid -> {alive, killed, created}, the process holding that pid now
    created: { startup: [] },
  });
  ax.files[QNA_DIR + "\\qna.exe"] = "";
  var nextPid = 4100;
  var nextTemp = 1;
  var nextCreated = 1;

  function creationDate() {
    return "20261020" + String(100000 + nextCreated++) + ".000000+000";
  }

  // The process exits on its own (crashes, say) without output, and Windows
  // gives its pid to an unrelated, long-running process.
  ax.reuse = function (pid) {
    var old = ax.processes[pid];
    old.alive = false;
    clearTimeout(old.timer);
    ax.processes[pid] = { pid: pid, alive: true, killed: false, created: creationDate(), line: "C:\\Windows\\notepad.exe" };
  };

  function answerFor(query) {
    if (/nonexistent/.test(query)) return "Q: E: Singular expression refers to nonexistent object.\r\nQ: T: 9\r\nQ: ";
    return "Q: A: qna says " + query + "\r\nQ: A: second\r\nQ: I: plural string\r\nQ: T: 12\r\nQ: ";
  }

  // A cmd.exe running qna with redirected stdin and stdout.
  function spawn(line) {
    var pid = nextPid++;
    var proc = { pid: pid, alive: true, killed: false, created: creationDate(), line: line };
    ax.processes[pid] = proc;
    var m = QNA_LINE.exec(line);
    if (!m) {
      ax.badCommands.push(line);
      proc.alive = false;
      return proc;
    }
    function finish() {
      if (!proc.alive) return;
      var input = ax.files[m[2]];
      var out = input === undefined ? "The system cannot find the file specified.\r\n" : answerFor(input.replace(/\r?\n$/, ""));
      ax.files[m[3]] = out;
      ax.written[m[3]] = out;
      if (m[4]) ax.files[m[4]] = ax.written[m[4]] = "";
      proc.alive = false;
    }
    if (ax.config.delayMs === 0) finish();
    else if (ax.config.delayMs !== null) proc.timer = setTimeout(finish, ax.config.delayMs);
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
    if (ax.config.runThrows) throw new Error("The system cannot find the file specified.");
    var m = /^taskkill \/F \/T \/PID (\d+)$/.exec(line);
    if (m) kill(+m[1]);
    return 0;
  };
  Shell.prototype.Exec = function (line) {
    var entry = { via: "Exec", line: line };
    ax.commands.push(entry);
    var proc = spawn(line);
    entry.pid = proc.pid;
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
  function lookupFailed() {
    var e = new Error("Generic failure");
    e.number = -2147217407; // wbemErrFailed
    return e;
  }

  Services.prototype.Get = function (cls) {
    var key = /^Win32_Process\.Handle='(\d+)'$/.exec(cls);
    if (key) {
      ax.wmiLookups++;
      if (ax.config.wmiQuery === "throws") throw lookupFailed();
      var proc = ax.processes[+key[1]];
      if (!proc || !proc.alive) {
        var e = new Error("Not found");
        e.number = NOT_FOUND;
        throw e;
      }
      return {
        ProcessId: proc.pid,
        CreationDate: proc.created,
        Terminate: function () {
          ax.terminated.push(proc.pid);
          kill(proc.pid);
          return 0;
        },
      };
    }
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
          var code = { "create-string": "0", "create-odd": 9 }[ax.config.wmi];
          return { ReturnValue: code === undefined ? 0 : code, ProcessId: proc.pid };
        },
      };
    }
    throw new Error("no class " + cls);
  };
  Services.prototype.ExecQuery = function (query) {
    ax.wmiLookups++;
    if (ax.config.wmiQuery === "throws") throw lookupFailed();
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
