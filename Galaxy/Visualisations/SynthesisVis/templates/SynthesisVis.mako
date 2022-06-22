<%!
import sys, os
import itertools
import numpy as np
from pathlib import Path

sys.path.append('/home/xtrojak/eBCSgen/Galaxy/Visualisations/SynthesisVis/templates')

import libs
%>

<%
# def create_HTML(data):  # testing
def create_HTML():
    output = ""

    parser = libs.parsing.Parser()

    data = list(hda.datatype.dataprovider(hda, 'line', strip_lines=True, strip_newlines=True))

    parser.parse_file(data)

    # lin spaces of admissible values for all parameters
    spaced_dims = {key: np.linspace(parser.bounds[key][0], parser.bounds[key][1], 10) for key in parser.params}

    if len(parser.params) <= 2:
        output += libs.html.HTML_start_2d
    else:
        output += libs.html.HTML_start_more_d_1
        output += "\t\t\tvar dims = {}\n".format(["dim_{}".format(i) for i in range(len(parser.params) - 2)])
        output += "\t\t\tvar params = {}\n".format(parser.params)
        for param in spaced_dims:
            output += "\t\t\tvar {} = {}\n".format(param, list(spaced_dims[param]))
        output += libs.html.HTML_start_more_d_2
        output += "\t\t\tvar dims = {}".format(["dim_{}".format(i) for i in range(len(parser.params) - 2)])
        output += libs.html.HTML_start_more_d_3

    for (x, y) in itertools.permutations(parser.params, 2):
        bounds = parser.get_bounds(x, y)

        # extract all other dimensions
        other_dims = {param: parser.bounds[param] for param in parser.bounds.keys() - {x, y}}
        if other_dims:
            # ordered parameter names
            ordered_params = sorted(other_dims)

            # prepare possible positions for all params
            position_dims = {key: list(range(10)) for key in other_dims.keys()}

            # combinations of all positions of all params
            combinations = itertools.product(*(position_dims[name] for name in ordered_params))

            # values correspond to param names in  ordered_names
            for values in combinations:
                dims = {ordered_params[i]: values[i] for i in range(len(ordered_params))}
                dims_values = {param: spaced_dims[param][dims[param]] for param in ordered_params}

                dims_label = "_".join([param + "_" + str(dims[param]) for param in dims])

                pic = libs.svg.Picture(bounds)
                pic.load_rectangles(parser.regions, x, y, dims_values)
                # print vars
                output += '\t\t\tvar {}_{}_{} = "data:image/svg+xml;utf8,{}"\n'.format(x, y, dims_label, pic)
        else:
            pic = libs.svg.Picture(bounds)
            pic.load_rectangles(parser.regions, x, y, dict())
            # print vars
            output += '\t\t\tvar {}_{} = "data:image/svg+xml;utf8,{}"\n'.format(x, y, pic)

    # print mid
    output += libs.html.HTML_mid
    output += libs.html.HTML_x_axis

    # print x-axis options
    output += libs.html.print_option(parser.params[0], True)
    for param in parser.params[1:]:
        output += libs.html.print_option(param)

    output += libs.html.HTML_y_axis
    output += libs.html.print_option(parser.params[0])
    output += libs.html.print_option(parser.params[1], True)
    for param in parser.params[2:]:
        output += libs.html.print_option(param)

    # print end
    output += libs.html.HTML_end_1

    # print other dimensions
    if len(parser.params) > 2:
        output += libs.html.HTML_other_dim
        for i in range(len(parser.params) - 2):
            output += libs.html.HTML_dim_options.format(i, parser.params[i+2])
            values = spaced_dims[parser.params[i+2]]
            for j in range(len(values)):
                output += libs.html.print_fixed_option(j, values[j])
            output += libs.html.HTML_dim_options_end

    # print end
    output += libs.html.HTML_end_2
    return output

# for testing
# filename = open('SynthesisVis/templates/test.txt', "r")
# graph = create_HTML(filename.readlines())

graph = create_HTML()
%>

${graph}
