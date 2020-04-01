<%!
import collections
import json
import sys
from numpy import inf

#from routes import url_for
#prefix = url_for("/")
#path = os.getcwd()
%>

<%
def to_counter(state, ordering):
    """
    Transforms given state to Counter using given ordering

    :param state: str representation of state
    :param ordering: enumeration of agents
    :return: Counter representing the state
    """
    state = eval(state)
    if state[0] == inf:
        return inf
    return +collections.Counter({ordering[i]: state[i] for i in range(len(ordering))})


def node_to_string(node):
    """
    Creates string representation of Counter of agents.

    :param node: given Counter of agents.
    :return: string representation of Counter
    """
    if node == inf:
        return "inf"
    return "<br>".join([str(int(v)) + " " + str(k) for k, v in node.items()])


def side_to_string(side):
    """
    Another string representation of Counter, this time used as side in reaction
    :param side: given Counter
    :return: string representation of Counter
    """
    if side == inf:
        return "inf"
    return " + ".join([str(int(v)) + " " + str(k) for k, v in side.items()])


def create_sides(lhs, rhs):
    """
    From given substrates and products counters creates their mutual differences

    :param lhs: dict of substrates
    :param rhs: dict of products
    :return: two counters representing differences
    """
    if lhs == inf:
        return inf, inf
    if rhs == inf:
        return collections.Counter(), inf
    left = lhs - rhs
    right = rhs - lhs
    return left, right


def write_node(ID, label):
    """
    Creates string representation of a node

    :param ID: ID of given node
    :param label: enumeration of agents
    :return: string representation
    """
    return "\t{{id: {0}, label: '{0}', title: '{0}', text: '{1}'}},\n".format(ID, label)


def write_reaction(edge_id, left_index, right_index, substrates, products, rate):
    """
    Creates string representation of a reaction

    :param edge_id: ID of given reaction
    :param left_index: ID of FROM node
    :param right_index: ID of TO node
    :param substrates: enumeration of substrates
    :param products: enumeration of products
    :param rate: rate of the reaction (if any)
    :return: string representation
    """
    rate = " @ " + str(rate) if rate else ""
    return "\t{{id: {}, from: {}, to: {}, arrows: 'to', text: '{} => {}{}'}},\n".format(
        edge_id, left_index, right_index, side_to_string(substrates), side_to_string(products), rate)


def create_HTML_graph(filename): # just for testing, hda us used
def create_HTML_graph():
    output_file = firstpart

    # data = json.load(filename)

    data = ''.join(list(hda.datatype.dataprovider(
      hda, 
      'line', 
      strip_lines=True, 
      strip_newlines=True )))
    data = json.loads(data)

    ordering = data['ordering']
    nodes = {int(key): to_counter(data['nodes'][key], ordering) for key in data['nodes'].keys()}

    for id, state in nodes.items():
        output_file += write_node(id, node_to_string(state))

    output_file += "\t]);\n\n\t// create an array with edges\n\tvar edges = new vis.DataSet([\n"

    for edge_id, edge in enumerate(data['edges'], 1):
        substrates, products = create_sides(nodes[edge['s']], nodes[edge['t']])
        output_file += write_reaction(edge_id, edge['s'], edge['t'],
                                      substrates, products, edge.get('p', None))

    initial = data['initial']
    output_file += secondpart_1
    output_file += "\tvar fromNode = " + str(int(initial) + 1) + ";\n"
    output_file += secondpart_2
    return output_file


firstpart = \
'''<!doctype html>
<html>
<head>
    <title>Network | Interaction events</title>

   <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.css" rel="stylesheet" type="text/css"/>

    <style type="text/css">
        #mynetwork {
            width: 100%;
            height: 100%;
            border: 1px solid lightgray;
        }
        #rectangle {
            text-align: center;
            font-weight: bold;
        }
        #loadingBar {
            position:absolute;
            top:1px;
            left:1px;
            width: 100%;
            height: 93%;
            background-color:rgba(200,200,200,0.8);
            -webkit-transition: all 0.5s ease;
            -moz-transition: all 0.5s ease;
            -ms-transition: all 0.5s ease;
            -o-transition: all 0.5s ease;
            transition: all 0.5s ease;
            opacity:1;
        }
        #wrapper {
            position:relative;
            width:900px;
            height:900px;
        }
        #text {
            position:absolute;
            top:8px;
            left:530px;
            width:30px;
            height:50px;
            margin:auto auto auto auto;
            font-size:22px;
            color: #000000;
        }
        div.outerBorder {
            position:relative;
            top:400px;
            width:600px;
            height:44px;
            margin:auto auto auto auto;
            border:8px solid rgba(0,0,0,0.1);
            background: rgb(252,252,252); /* Old browsers */
            background: -moz-linear-gradient(top,  rgba(252,252,252,1) 0%, rgba(237,237,237,1) 100%); /* FF3.6+ */
            background: -webkit-gradient(linear, left top, left bottom, color-stop(0%,rgba(252,252,252,1)), color-stop(100%,rgba(237,237,237,1))); /* Chrome,Safari4+ */
            background: -webkit-linear-gradient(top,  rgba(252,252,252,1) 0%,rgba(237,237,237,1) 100%); /* Chrome10+,Safari5.1+ */
            background: -o-linear-gradient(top,  rgba(252,252,252,1) 0%,rgba(237,237,237,1) 100%); /* Opera 11.10+ */
            background: -ms-linear-gradient(top,  rgba(252,252,252,1) 0%,rgba(237,237,237,1) 100%); /* IE10+ */
            background: linear-gradient(to bottom,  rgba(252,252,252,1) 0%,rgba(237,237,237,1) 100%); /* W3C */
            filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#fcfcfc', endColorstr='#ededed',GradientType=0 ); /* IE6-9 */
            border-radius:72px;
            box-shadow: 0px 0px 10px rgba(0,0,0,0.2);
        }
        #border {
            position:absolute;
            top:10px;
            left:10px;
            width:500px;
            height:23px;
            margin:auto auto auto auto;
            box-shadow: 0px 0px 4px rgba(0,0,0,0.2);
            border-radius:10px;
        }
        #bar {
            position:absolute;
            top:0px;
            left:0px;
            width:20px;
            height:20px;
            margin:auto auto auto auto;
            border-radius:11px;
            border:2px solid rgba(30,30,30,0.05);
            background: rgb(0, 173, 246); /* Old browsers */
            box-shadow: 2px 0px 4px rgba(0,0,0,0.4);
        }
        html { 
            height: 100%;
        }
        body { 
            height: 90%;
            border:1px solid #000;
        }
    </style>
</head>
<body>

<div id="mynetwork"></div>
<div id="rectangle"style="width:100%;border:1px solid #000;"> </div>
<div id="loadingBar">
        <div class="outerBorder">
            <div id="text">0%</div>
            <div id="border">
                <div id="bar"></div>
            </div>
        </div>
</div>

<script type="text/javascript">
setTimeout(function () {
    // create an array with nodes
        var nodes = new vis.DataSet([
'''

secondpart_1 = '''
    ]);

    // create a network
    var container = document.getElementById('mynetwork');
    var data = {
        nodes: nodes,
        edges: edges
    };
    var options = {
        layout: {improvedLayout: true},
        physics: {
            enabled: true,
            barnesHut: {
                gravitationalConstant: -25000,
                centralGravity: 0.5,
                springConstant: 0.5,
                springLength: 200,
                damping: 0.15
            },
            maxVelocity: 50,
            minVelocity: 7.5,
            solver: 'barnesHut',
            timestep: 0.5,
            stabilization: {
                        enabled:true,
                        iterations:5000,
                    },
        },
        nodes: {
            size: 15,
            font: {
                size: 20
            },
            borderWidth: 2,
            borderWidthSelected: 4,
            color:{highlight:{border: '#B20F0F', background: 'red'}}
        },
        edges: {
            width: 4,
            selectionWidth: function (width) {return width*2.5;},
            color:{color:'#2B7CE9', hover:'#2B7CE9', highlight: 'red'}
        },
        interaction: {
        navigationButtons: true,
        keyboard: true,
        hover: true,
        tooltipDelay: 500,
        multiselect: true
        }
    };
    var network = new vis.Network(container, data, options);
    var stabil = true;
'''

secondpart_2 = '''
    network.on("click", function (params) {
        params.event = "[original event]";
        var tmp = " ";


        for (var i = 1; i <= nodes.length; i++) {
            if (nodes.get(i).id == params.nodes) {
                tmp = nodes.get(i).text;
            };
        };

        if(params.nodes.length === 0 && params.edges.length > 0) {
            for (var i = 1; i <= edges.length; i++) {
                if (edges.get(i).id == params.edges) {
                    tmp = edges.get(i).text;
                };
            };
        };

        document.getElementById('rectangle').innerHTML = '<div style="width:100%;height:100%;text-align:center;border:0px solid #000;">' + tmp + '</div>';
    });

    network.on("stabilized", function (params) {
    if(stabil) {
        network.fit();
        stabil = false;
    };
    });

    network.on("stabilizationProgress", function(params) {
                var maxWidth = 500;
                var minWidth = 20;
                var widthFactor = params.iterations/params.total*10;
                var width = Math.max(minWidth,maxWidth * widthFactor);

                document.getElementById('bar').style.width = width + 'px';
                document.getElementById('text').innerHTML = Math.round(widthFactor*100) + '%';
            });

    network.once("stabilizationIterationsDone", function() {
                document.getElementById('text').innerHTML = '100%';
                document.getElementById('bar').style.width = '496px';
                document.getElementById('loadingBar').style.opacity = 0;
                // really clean the dom element
                setTimeout(function () {document.getElementById('loadingBar').style.display = 'none';}, 0);
    });

    clickedNode = nodes.get(fromNode);
    clickedNode.color = {
            border: 'orange',
            background: 'orange',
            highlight: {
                border: 'orange',
                background: 'orange'
            }
        }
        nodes.update(clickedNode);

    network.on("doubleClick", function (params) {
        params.event = "[original event]";
        network.focus(params.nodes);
    });
}, 5);
</script>

</body>
</html>
'''
# for testing
# filename = open('bigger_pMC.json', "r")
# graph = create_HTML_graph(filename)

graph = create_HTML_graph()
%>

${graph}
