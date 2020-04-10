def print_option(option, selected=False):
    return "\t\t<option value='{0}'{1}>{0}</option>\n".format(option, " selected" if selected else "")

def print_fixed_option(pos, option):
    return "\t\t<option value='{0}'>{1}</option>\n".format(pos, option)

HTML_start_2d = """
<html>
<head>
    <title>Select Image</title>

    <style>
        #combos {
            text-align: center;
            width: 620px;
        }

        #x_axis {
            margin: 0 50px 0 0;
        }

        body {
            font-size: 25px;
        }
    </style>

    <script type="text/javascript">
        function loadImage() {
            x_axis = document.getElementById("x_axis")
            y_axis = document.getElementById("y_axis")

            var svg_name = x_axis.value.concat("_", y_axis.value)

            fillImage(svg_name)
        }
    </script>

    <script type="text/javascript">
        function optionChanged(elem) {
            x_axis = document.getElementById("x_axis")
            y_axis = document.getElementById("y_axis")

            if (x_axis.value == y_axis.value){
                if (elem.id == "x_axis"){
                    var index = y_axis.selectedIndex;
                    if (index + 1 >= y_axis.options.length){
                        y_axis.value = y_axis.options.item(0).value;
                    } else {
                        y_axis.value = y_axis.options.item(index + 1).value;
                    }
                } else {
                    var index = x_axis.selectedIndex;
                    if (index + 1 >= x_axis.options.length){
                        x_axis.value = x_axis.options.item(0).value;
                    } else {
                        x_axis.value = x_axis.options.item(index + 1).value;
                    }
                }
            }

            var svg_name = x_axis.value.concat("_", y_axis.value)
            fillImage(svg_name)
        }
    </script>

    <script type="text/javascript">
        function fillImage(svg_name) {
            var image = document.getElementById("plot");
"""

HTML_start_more_d_1 = """
<head>
    <title>Select Image</title>

    <style>
        #combos {
            text-align: center;
            width: 620px;
        }

        #x_axis, #other {
            margin: 0 50px 0 0;
        }

        body {
            font-size: 20px;
        }
    </style>

    <script type="text/javascript">
        function loadImage() {
            x_axis = document.getElementById("x_axis")
            y_axis = document.getElementById("y_axis")

            var svg_name = x_axis.value.concat("_", y_axis.value);
            svg_name = svg_name.concat(getDimensionsName())

            fillImage(svg_name)
        }
    </script>

    <script type="text/javascript">
        function updateOtherDimensions() {
            x_axis = document.getElementById("x_axis")
            y_axis = document.getElementById("y_axis")

            var chosen = [x_axis.value, y_axis.value];
"""

HTML_start_more_d_2 = """
            var unused = [];

            //find dimensions
            for (const param of params){
                if (! chosen.includes(param)){
                    unused.push(param)
                }
            }

            for (i = 0; i < unused.length; i++){
                select_element = document.getElementById(dims[i])
                label = document.getElementById(dims[i].concat("_label"))

                // change label and name
                label.innerHTML = unused[i]
                select_element.name = unused[i]

                //change its options
                for (j = 0; j < select_element.options.length; j++){
                    select_element.options[j].innerHTML = eval(unused[i])[j]
                }
            }
        }
    </script>

    <script type="text/javascript">
        function getDimensionsName() {
"""

HTML_start_more_d_3 = """

            var svg_name = "";

            for (const dim of dims){
                dim_select = document.getElementById(dim)
                svg_name = svg_name.concat("_", dim_select.name, "_", dim_select.value);
            }
            return svg_name
        }
    </script>

    <script type="text/javascript">
        function optionChanged(elem) {
            x_axis = document.getElementById("x_axis")
            y_axis = document.getElementById("y_axis")

            if (x_axis.value == y_axis.value){
                if (elem.id == "x_axis"){
                    var index = y_axis.selectedIndex;
                    if (index + 1 >= y_axis.options.length){
                        y_axis.value = y_axis.options.item(0).value;
                    } else {
                        y_axis.value = y_axis.options.item(index + 1).value;
                    }
                } else {
                    var index = x_axis.selectedIndex;
                    if (index + 1 >= x_axis.options.length){
                        x_axis.value = x_axis.options.item(0).value;
                    } else {
                        x_axis.value = x_axis.options.item(index + 1).value;
                    }
                }
            }

            updateOtherDimensions()
            loadImage()
        }
    </script>

    <script type="text/javascript">
        function fillImage(svg_name) {
            var image = document.getElementById("plot");
"""

HTML_mid = """
            image.src = eval(svg_name);
        }
    </script>
</head>
<body onload="loadImage()">
    <div id="combos">"""

HTML_x_axis = """
    <label for="x_axis">X-axis</label>
    <select id="x_axis" onchange="optionChanged(this);">
"""

HTML_y_axis = \
"""    </select>

    <label for="y_axis">Y-axis</label>
    <select id="y_axis" onchange="optionChanged(this);">
"""

HTML_end_1 = \
"""    </select>
    </div>
"""

HTML_other_dim = """
    <div>
    <label id="other">Other dimensions: </label>
"""

HTML_dim_options = """
    <label id="dim_{0}_label">{1}</label>
    <select id="dim_{0}" name="{1}" onchange="loadImage();">
"""

HTML_dim_options_end = """
    </select>
    </div>
"""

HTML_end_2 = """
    <img id="plot">
</body>
</html>"""
