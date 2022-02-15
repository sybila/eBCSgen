<%!
import os
from routes import url_for

prefix = url_for("/")
path = os.getcwd()

%>
<%
data = "\n".join(list(hda.datatype.dataprovider( hda, 'line', comment_char=none, provide_blank=True, strip_lines=False, strip_newlines=True )))
%>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <title>BCSL editor</title>

    <style type="text/css" media="screen">
    body {
        overflow: hidden;
    }

    #console {
        position: absolute;
        bottom: 0;
        height: 3%;
        float: left;
        left: 0%;
        width: 100%;
        overflow-y: auto;
        color: black;
        background: #e8e8e8;
        font-size: 1em;
        border-color: black;
        border-radius: 0px;
        border-style: solid;
        border-width: 1px;
        padding-left: 2px;
    }

    #actualPosition {
        position: absolute;
        float: right;
        right: 0;
        color: black;
        font-size: 12px;
        text-align:right;
        top: 0.5%;
        right: 0.5%;
    }

    #editor {
        margin: 0;
        position: absolute;
        top: 3.8%;
        bottom: 3%;
        left: 0;
        right: 0;
        height: 92.5%;
        font-size: 1em;
    }

    .button {
        background-color: #4CAF50; /* Green */
        border-color: #000;
        border-radius: 3px;
        border-style: solid;
        border-width: 1px;
        box-sizing: border-box;
        color: white;
        border: none;
        font-size: 12px;
        font-weight: 400;
        font-family: sans-serif;
        cursor: pointer;
        position: absolute;
        top: 0px;
        height: 3.5%;
    }

    .button:hover {
        background-color: #2c4330; /* #2c3143; */
    }

    #save_btn {
        left: 2px;
    }
    #undo_btn {
        left: 136px;
    }
    #redo_btn {
        left: 188px;
    }
    </style>
</head>
<body>
    <script type="application/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min.js"></script>
    <div id="editor" file-name=${hda.name} file-hid=${hda.hid} >${data}</div>
    <div id="console"></div>

    <script type="text/javascript" charset="utf-8">
        var hist_id = null;

        $(function() {
            var address = '${prefix}/history/current_history_json';
            $.get(address, function(resp) {
                if (resp && resp.id)
                    hist_id = resp.id;
            });
            $('#undo_btn').on('click', function() { ace.edit('editor').undo(); });
            $('#redo_btn').on('click', function() { ace.edit('editor').redo(); });
            $('#wrap_btn').on('click', function() { ace.edit('editor').getSession().setUseWrapMode(!ace.edit('editor').getSession().getUseWrapMode()); });

            $('#save_btn').on('click', function() {
                var cont = ace.edit('editor').getValue();
                var dInputs = {
                    dbkey: '?',
                    file_type: 'bcs',
                    'files_0|type': 'upload_dataset',
                    'files_0|space_to_tab': null,
                    'files_0|to_posix_lines': 'Yes'
                };

                var formData = new FormData();
                formData.append('tool_id', 'upload1');
                formData.append('history_id', hist_id);
                formData.append('inputs', JSON.stringify(dInputs));
                formData.append('files_0|file_data', new Blob([cont], {type: 'text/plain'}), 'BCS edit on data '+$('#editor').attr('file-hid'));

                $.ajax({
                    url: '${prefix}/api/tools',
                    data: formData,
                    processData: false,
                    contentType: false,
                    type: 'POST',
                    success: function (resp) {
                        window.setTimeout(function() {
                            window.parent.$('#history-refresh-button').trigger('click');
                        }, 3000);
                    }
                });
            });
        });
    </script>

    <input class="button" type="button" id="save_btn" value="Save modifications" />
    <input class="button" type="button" id="undo_btn" value="Undo" />
    <input class="button" type="button" id="redo_btn" value="Redo" />
    <div id="actualPosition">Row: 1, Column: 1</div>

    <script src="static/src/ace.js" type="text/javascript" charset="utf-8"></script>
    <script src="static/src/worker-bcsl.js" type="text/javascript"></script>

    <script>
        var editor = ace.edit("editor");
        editor.setTheme("ace/theme/terminal");
        editor.session.setMode("ace/mode/bcsl");
        editor.setOption("showPrintMargin", false);
        editor.getSession().setUseWrapMode(true);
        editor.resize();
        editor.session.selection.on('changeCursor', function(e) {
          document.getElementById("actualPosition").innerHTML = "Row: " + String(editor.getCursorPosition().row + 1) + ", Column: " + String(editor.getCursorPosition().column + 1);
        });
    </script>
</body>
</html>