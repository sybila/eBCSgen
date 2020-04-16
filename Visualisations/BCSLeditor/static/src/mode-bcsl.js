define("ace/mode/bcsl_highlight", ["require", "exports", "module", "ace/lib/oop", "ace/mode/text_highlight_rules"], function(require, exports, module)
{
    "use strict";

    var oop = require("../lib/oop");
    var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;

    var BcslHighlightRules = function()
    {
        this.$rules = {
            "start": [
            {
                token: "keyword.operator",
                regex: /<?=>/
            },
            {
                token: "keyword.operator",
                regex: /::/
            },
            {
                token: "keyword.operator",
                regex: / \+ /
            },
            {
                token: "constant.numeric",
                regex: /(^| )[0-9]+($| )/
            },
            {
                token: "variable.language",
                regex: /\?X/
            },
            {
                token: "keyword.operator",
                regex: /@/
            },
            {
                token: "part",
                regex: /\#.+$/
            },
            {
                token: "comment",
                regex: /\/\/.+$/
            }]
        };

        this.normalizeRules();
    };

    oop.inherits(BcslHighlightRules, TextHighlightRules);
    exports.BcslHighlightRules = BcslHighlightRules;
});

define("ace/mode/bcsl", ["require", "exports", "module", "ace/lib/oop", "ace/mode/text", "ace/mode/bcsl_highlight", "ace/worker/worker_client"], function(require, exports, module)
{
    "use strict";

    var oop = require("../lib/oop");
    var TextMode = require("./text").Mode;
    var BcslHighlightRules = require("./bcsl_highlight").BcslHighlightRules;
    var WorkerClient = require("ace/worker/worker_client").WorkerClient;

    var Mode = function(options)
    {
        this.fragmentContext = options && options.fragmentContext;
        this.HighlightRules = BcslHighlightRules;
    };
    oop.inherits(Mode, TextMode);

    (function()
    {
        this.getNextLineIndent = function(state, line, tab)
        {
            return this.$getIndent(line);
        };

        this.checkOutdent = function(state, line, input)
        {
            return false;
        };

        this.getCompletions = function(state, session, pos, prefix)
        {
            return this.$completer.getCompletions(state, session, pos, prefix);
        };

        this.createWorker = function(session)
        {
            if (this.constructor != Mode)
                return;

            var worker = new WorkerClient(["ace"], "ace/mode/bcsl_worker", "Worker");
            worker.attachToDocument(session.getDocument());

            worker.on("error", function(e)
            {
                session.setAnnotations(e.data);
                changeErrors(e.data);
            });

            worker.on("terminate", function()
            {
                session.clearAnnotations();
            });

            return worker;
        };

        this.$id = "ace/mode/bcsl";
    }).call(Mode.prototype);

    exports.Mode = Mode;
});
(function()
{
    window.require(["ace/mode/bcsl"], function(m)
    {
        if (typeof module == "object" && typeof exports == "object" && module)
        {
            module.exports = m;
        }
    });
})();

var changeErrors = function(e)
{
    con = document.getElementById('console')
    con.innerHTML = "";
    e.forEach( err => {
        con.innerHTML += err.msg_console + "<br>";
  });
    con.scrollTop = console.scrollHeight;
}
