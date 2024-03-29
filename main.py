import bokeh.settings
from bokeh.client import push_session
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import (ColumnDataSource, Slider, TextInput, Select, Spinner, RangeSlider)
from bokeh.plotting import figure

bokeh.settings.settings.log_level = 'error'
bokeh.settings.settings.py_log_level = 'none'
bokeh.settings.settings.validation_level = 'none'

import numpy as np
from functools import reduce

DEFAULT_POLYNOMIAL_ORDER = 2

# define objects for layout
inputs = column()
# define graphing parameters
Graph = {
    "plot_layout": None,
    "options_layout": None,
    "new_option_layout": None,
    "current_type": "Polynomial",
    "type_options": ["log", "Polynomial", "Exp"],
    "x_min": 0,
    "x_max": 4,
    "y_min": 0,
    "y_max": 21,
    "x_absolute_min": 0,
    "x_absolute_max": 100,
    "y_absolute_min": 0,
    "y_absolute_max": 1000,
    # number of points used to graph the function. More points will result in a smoother, more accurate graph
    "graph_precision": 1000,
    "X": [x for x in range(4)],
    "Y": [y for y in range(4)],
    "polynomial_order": DEFAULT_POLYNOMIAL_ORDER,
    "polynomial_parameters": [],
}
source = ColumnDataSource(data=dict(x=Graph["X"], y=Graph["Y"]))

# Set up plot
plot = figure(height=900, width=1300,
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[Graph["x_min"], Graph["x_max"]], y_range=[Graph["y_min"], Graph["y_max"]])
plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)

# Set up Widgets
# These Widgets control the graph
x_slider = RangeSlider(title="X bounds", start=Graph["x_absolute_min"], end=Graph["x_absolute_max"], step=1,
                       value=(Graph["x_min"], Graph["x_max"]))
y_slider = RangeSlider(title="Y bounds", start=Graph["y_absolute_min"], end=Graph["y_absolute_max"], step=10,
                       value=(Graph["y_min"], Graph["y_max"]))
graph_precision_slider = Slider(title="Graph Precision", value=Graph["graph_precision"], start=100, end=1000, step=50)
# Controls what is plotted
plot_type_selector = Select(title="Option:", options=Graph["type_options"], value=Graph["current_type"])
# Specific parameters for the different types of plots
order_selector = Spinner(title="Polynomial Order", value=2, high=8, low=0, step=1)


# changes the precision of the graph for the nex update
def update_plot_precision(attrname, old, new):
    Graph["graph_precision"] = new
    update_graph("value", "", Graph["current_type"])


# Defines the parameters and variables for the different plots
def initialize_log_plot():
    pass


def initialize_polynomial_plot(order):
    temp_row = row()
    Graph["polynomial_parameters"].clear()
    for i in range(order+1):
        title_val = "a_" + str(i)
        widget = Spinner(title=title_val, value=1, high=100, low=-100, step=1)
        widget.on_change('value', update_graph)
        Graph["polynomial_parameters"].append(widget)
        temp_row.children.append(widget)
    Graph["options_layout"] = column(order_selector, temp_row, name="options_layout")
    update_graph("value", "", Graph["current_type"])


def initialize_exp_plot():
    pass


# create an initial plot for the selected option (default is Polynomial)
def initialize_plot(option):
    Graph["current_type"] = option
    match option:
        case "log":
            initialize_log_plot()
        case "Polynomial":
            initialize_polynomial_plot(DEFAULT_POLYNOMIAL_ORDER)
        case "Exp":
            initialize_exp_plot()

def update_polynomial_order(attname, old, new):
    Graph["polynomial_order"] = new
    initialize_polynomial_plot(Graph["polynomial_order"])

def update_polynomial():
    # sets up the X values for our graph. linspace creates an array of values from x_min to x_max. The third parameter is the number of points
    X = np.linspace(Graph["x_min"], Graph["x_max"], Graph["graph_precision"])
    parameter_values = list(map(lambda x: x.value, Graph["polynomial_parameters"]))
    Y = list(map(lambda x: reduce(lambda acc, val: acc + val[1] * pow(x, val[0]), enumerate(parameter_values), 0), X))
    source.data = dict(x=X, y=Y)


def update_domain(attrname, old, new):
    Graph["x_min"] = new[0]
    Graph["x_max"] = new[1]
    update_graph("value", "", Graph["current_type"])


def update_graph(attrname, old, new):
    curdoc().hold()
    model = curdoc().get_model_by_name("options_layout")
    if(model != None):
        curdoc().remove_root(model)
    curdoc().add_root(Graph["options_layout"])
    curdoc().unhold()
    match Graph["current_type"]:
        case "log":
            pass
        case "Polynomial":
            update_polynomial()
        case "Exp":
            pass


# set up links
x_slider.js_link("value", plot.x_range, "start", attr_selector=0)
x_slider.js_link("value", plot.x_range, "end", attr_selector=1)
y_slider.js_link("value", plot.y_range, "start", attr_selector=0)
y_slider.js_link("value", plot.y_range, "end", attr_selector=1)
# set up callbacks
x_slider.on_change("value", update_domain)
graph_precision_slider.on_change("value", update_plot_precision)
order_selector.on_change("value", update_polynomial_order)

Graph["plot_layout"] = column(plot_type_selector, plot, x_slider, y_slider,graph_precision_slider, width=1500, name="plot_layout")
curdoc().add_root(Graph["plot_layout"])
initialize_plot('Polynomial')
curdoc().title = "Plotting"
# session = push_session(curdoc())


# session.show()
