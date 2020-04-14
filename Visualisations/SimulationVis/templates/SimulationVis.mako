<%!
import sys
import pandas

#from routes import url_for
#prefix = url_for("/")
#path = os.getcwd()
%>

<%
# def newSimulationGraph(filename): # just for testing, hda is used
def newSimulationGraph():
    html = firstpart
    # data = pandas.read_csv(filename)
    data = "\n".join(hda.datatype.dataprovider(hda, 'line', comment_char=none, provide_blank=True, strip_lines=False,
                                               strip_newlines=True))

    data = data.decode("utf-8")
    data = pandas.DataFrame([x.split(',') for x in data.split('\n')[1:]],
                            columns=[x for x in data.split('\n')[0].split(',')])

    html += "\tvar time = " + str(list(data.get("times"))) + ";\n"

    for i, col in enumerate(data.columns[1:]):
        html += "\tvar plot_{} = {{ x: time, y: {}, type: 'lines', name: '{}'}};\n".format(i, list(data.get(col)), str(col))

    html += "\tvar data = [{}];\n".format(",".join(["plot_" + str(i) for i in range(len(data.columns[1:]))]))
    html += lastpart
    return html


firstpart = \
'''
<head>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>

<body>
  <div id="simulation_graph"><!-- Plotly chart will be drawn inside this DIV --></div>
  <script>setTimeout(function(){
'''

lastpart = \
'''
var layout = { 
  title: 'Simulation',
  titlefont: {
      family: 'Courier New, monospace',
      size: 18,
      color: '#7f7f7f'
    },
  xaxis: {
    title: 'Time',
    titlefont: {
      family: 'Courier New, monospace',
      size: 18,
      color: '#7f7f7f'
    }
  },
  yaxis: {
    title: 'Concetration',
    titlefont: {
      family: 'Courier New, monospace',
      size: 18,
      color: '#7f7f7f'
    }
  }
};
var d3 = Plotly.d3;
var WIDTH_IN_PERCENT_OF_PARENT = 100,
    HEIGHT_IN_PERCENT_OF_PARENT = 95;
var gd3 = d3.select("div[id='simulation_graph']")
    .style({
        width: WIDTH_IN_PERCENT_OF_PARENT + '%',
        'margin-left': (100 - WIDTH_IN_PERCENT_OF_PARENT) / 2 + '%',
        height: HEIGHT_IN_PERCENT_OF_PARENT + 'vh',
        'margin-top': (100 - HEIGHT_IN_PERCENT_OF_PARENT) / 2 + 'vh'
    });
var res_graph = gd3.node();
    Plotly.newPlot(res_graph, data, layout);
    window.onresize = function() { Plotly.Plots.resize( res_graph ); };
    }, 50);
   
  </script>
  <style>
  .modebar-btn--logo {
    display: none
  }
  #simulation_graph {
    overflow: hiddne;
  }
  </style>
</body>
'''
# for testing
# filename = open('simple_out.csv', "r")
# graph = newSimulationGraph(filename)

graph = newSimulationGraph()

%>
${graph}