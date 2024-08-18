import re
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots


def format_graphs_titles(variables: list):
    """
    This function gets a list of strings corresponding to the variables names and returns a string, in lower case, that
    enumerates them. For example, if the list is ["Plátano", "Uva",  "Queso"], the function will return the string
    "plátano, uva y queso", or, if the list is ["Plátano", "Uva", "Invierno"], the function will return the string
    "plátano, uva e invierno".
    :param variables: List containing the list of the variables.
    :return: String that enumerates the variables.
    """
    new_variables = [v for v in variables if v != ""]

    joined_vars = re.sub(r",([^,]*)$", r" y\1", ", ".join(new_variables).lower())

    return re.sub(r"y(?=\s+i)", "e", joined_vars)


def create_area_chart(df, y: str, color: str, title: str):
    """

    :param df:
    :param y:
    :param color:
    :param title:
    :return:
    """

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    no_area = px.area(df[df[color] == "No"], "Fecha", y, color=color,
                      title=title, markers=True,
                      range_y=None, groupnorm='fraction')

    si_area = px.area(df[df[color] == "Sí"], "Fecha", y, color=color,
                      title=title, markers=True,
                      range_y=None, groupnorm='fraction')

    if si_area.data:
        si_area.data[0]["line"]["color"] = "#6EE1FF"
        fig.add_trace(si_area.data[0],
                      secondary_y=False)
    # adata = area.data
    if no_area.data:
        no_area.data[0]["line"]["color"] = "#FF7373"
        fig.add_trace(no_area.data[0],
                      secondary_y=False)

    fig.update_layout(height=575, yaxis_title="Número de Participantes")

    fig.update_layout(yaxis_tickformat='.0%')

    return fig

