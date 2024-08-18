import re
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots


def format_graphs_titles(key: str):
    """
    This function a string to the default title depending on the key chosen to make the plot
    :param key: Key chosen to make the plot.
    :return: String to attach to the default title.
    """

    str_to_attach = ""

    if key == "Cumple_Ambos":
        str_to_attach = " que cumplen ambos requerimientos"
    else:
        requirement = key.strip("Cumple_").lower()
        str_to_attach = f" que cumplen los requerimientos de {requirement}"
        
    return str_to_attach


def create_area_chart(df, y: str, color: str, title: str):
    """
    This function creates an area chart using plotly.
    :param df: Dataframe from which the data will be taken.
    :param y: Dataframe measured in the y-axis.
    :param color: Dataframe column used to segregate by color.
    :param title: Title of the chart.
    :return: Plotly figure.
    """
    # Defining a subplots instance
    fig = make_subplots()
    # Creating a figure corresponding to the No values.
    no_area = px.area(df[df[color] == "No"], "Fecha", y, color=color,
                      title=title, markers=True, groupnorm='fraction')
    # Creating a figure corresponding to the Sí values.
    si_area = px.area(df[df[color] == "Sí"], "Fecha", y, color=color,
                      title=title, markers=True, groupnorm='fraction')
    # If the Sí area chart is not empty, add it to the subplots figure
    if si_area.data:
        si_area.data[0]["line"]["color"] = "#6EE1FF"
        fig.add_trace(si_area.data[0],
                      secondary_y=False)
    # If the No area chart is not empty, add it to the subplots figure
    if no_area.data:
        no_area.data[0]["line"]["color"] = "#FF7373"
        fig.add_trace(no_area.data[0],
                      secondary_y=False)
    # Updating the figure layout with the desired parameters
    fig.update_layout(height=575, yaxis_title="Número de Participantes", title=title + format_graphs_titles(color),
                      yaxis_tickformat='.0%')

    return fig

