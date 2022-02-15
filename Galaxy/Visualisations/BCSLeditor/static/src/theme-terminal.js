define("ace/theme/terminal",["require","exports","module","ace/lib/dom"], function(require, exports, module) {

exports.isDark = false;
exports.cssClass = "ace-terminal-theme";
exports.cssText = ".ace-terminal-theme .ace_gutter {\
background: #ebebeb;\
color: #333;\
overflow : hidden;\
}\
.ace-terminal-theme .ace_print-margin {\
width: 1px;\
background: #e8e8e8;\
}\
.ace-terminal-theme {\
background-color: #FFFFFF;\
color: black;\
}\
.ace-terminal-theme .ace_cursor {\
color: black;\
}\
.ace-terminal-theme .ace_invisible {\
color: rgb(191, 191, 191);\
}\
.ace-terminal-theme .ace_constant.ace_buildin {\
color: rgb(88, 72, 246);\
}\
.ace-terminal-theme .ace_constant.ace_language {\
color: rgb(88, 92, 246);\
}\
.ace-terminal-theme .ace_constant.ace_library {\
color: rgb(6, 150, 14);\
}\
.ace-terminal-theme .ace_invalid {\
background-color: rgb(153, 0, 0);\
color: white;\
}\
.ace-terminal-theme .ace_fold {\
}\
.ace-terminal-theme .ace_support.ace_function {\
color: rgb(60, 76, 114);\
}\
.ace-terminal-theme .ace_support.ace_constant {\
color: rgb(6, 150, 14);\
}\
.ace-terminal-theme .ace_support.ace_type,\
.ace-terminal-theme .ace_support.ace_class\
.ace-terminal-theme .ace_support.ace_other {\
color: rgb(109, 121, 222);\
}\
.ace-terminal-theme .ace_variable.ace_parameter {\
font-style:italic;\
color:#FD971F;\
}\
.ace-terminal-theme .ace_keyword.ace_operator {\
color: deeppink;\
}\
.ace-terminal-theme .ace_comment {\
color: grey;\
}\
.ace-terminal-theme .ace_comment.ace_doc {\
color: #236e24;\
}\
.ace-terminal-theme .ace_comment.ace_doc.ace_tag {\
color: #236e24;\
}\
.ace-terminal-theme .ace_constant.ace_numeric {\
color: deeppink;\
}\
.ace-terminal-theme .ace_variable {\
color: rgb(49, 132, 149);\
}\
.ace-terminal-theme .ace_xml-pe {\
color: rgb(104, 104, 91);\
}\
.ace-terminal-theme .ace_entity.ace_name.ace_function {\
color: #0000A2;\
}\
.ace-terminal-theme .ace_heading {\
color: rgb(12, 7, 255);\
}\
.ace-terminal-theme .ace_list {\
color:rgb(185, 6, 144);\
}\
.ace-terminal-theme .ace_marker-layer .ace_selection {\
background: rgb(181, 213, 255);\
}\
.ace-terminal-theme .ace_marker-layer .ace_step {\
background: rgb(252, 255, 0);\
}\
.ace-terminal-theme .ace_marker-layer .ace_stack {\
background: rgb(164, 229, 101);\
}\
.ace-terminal-theme .ace_marker-layer .ace_bracket {\
margin: -1px 0 0 -1px;\
border: 1px solid rgb(192, 192, 192);\
}\
.ace-terminal-theme .ace_marker-layer .ace_active-line {\
background: rgba(0, 0, 0, 0.07);\
}\
.ace-terminal-theme .ace_gutter-active-line {\
background-color : #dcdcdc;\
}\
.ace-terminal-theme .ace_marker-layer .ace_selected-word {\
background: rgb(250, 250, 255);\
border: 1px solid rgb(200, 200, 250);\
}\
.ace-terminal-theme .ace_storage,\
.ace-terminal-theme .ace_keyword,\
.ace-terminal-theme .ace_meta.ace_tag {\
color: rgb(147, 15, 128);\
}\
.ace-terminal-theme .ace_string.ace_regex {\
color: rgb(255, 0, 0)\
}\
.ace-terminal-theme .ace_string {\
color: #1A1AA6;\
}\
.ace-terminal-theme .ace_entity.ace_other.ace_attribute-name {\
color: #994409;\
}\
.ace-terminal-theme .ace_part {\
color: green\
}\
.ace-terminal-theme .ace_roundbrackets {\
color: tomato\
}\
.ace-terminal-theme .ace_indent-guide {\
background: url(\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAACCAYAAACZgbYnAAAAE0lEQVQImWP4////f4bLly//BwAmVgd1/w11/gAAAABJRU5ErkJggg==\") right repeat-y;\
}\
";

var dom = require("../lib/dom");
dom.importCssString(exports.cssText, exports.cssClass);
});                (function() {
                    ace.require(["ace/theme/chrome"], function(m) {
                        if (typeof module == "object" && typeof exports == "object" && module) {
                            module.exports = m;
                        }
                    });
                })();
            
