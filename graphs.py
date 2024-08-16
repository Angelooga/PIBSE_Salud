import re
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from processing import aggregate_data


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


def create_time_series(data, option):
    """
    This function creates a time series given a dataframe.
    :param option:
    :param data: Dataframe from which the time series will be made.
    :return:
    """

    uniques = data["Entidad"].unique()

    if len(uniques) % 2 == 0:
        nrows = data["Entidad"].nunique() // 2
    else:
        nrows = data["Entidad"].nunique() // 2 + 1
    counter = 0
    last_index = 0

    fig = make_subplots(rows=nrows, cols=2,
                        subplot_titles=data["Entidad"].unique(),
                        shared_yaxes=True)

    for i in range(2):
        for j in range(nrows):
            if j == nrows - 1 and i == 0 and len(uniques) % 2 != 0:
                last_index = counter
                continue

            data_temp = data[data["Entidad"] == uniques[counter]]

            temp_fig = px.line(data_temp, x="Fecha", y=option,
                               color="Sexo",
                               color_discrete_map={"Hombre": "blue",
                                                   "Mujer": "red",
                                                   "Sin dato": "grey"}
                               )

            for d in temp_fig.data:
                if j == 0 and i == 0:
                    fig.add_trace((go.Scatter(x=d["x"], y=d["y"], name=d["name"],
                                              line=d["line"], legendgroup=d["legendgroup"]
                                              )
                                   ),
                                  row=j + 1, col=i + 1)
                else:
                    fig.add_trace((go.Scatter(x=d["x"], y=d["y"], name=d["name"],
                                              showlegend=False,
                                              line=d["line"], legendgroup=d["legendgroup"]
                                              )
                                   ),
                                  row=j + 1, col=i + 1)
            counter += 2
            if counter >= len(uniques):
                break

        counter = 1

        if i == 1 and len(uniques) % 2 != 0:
            data_temp = data[data["Entidad"] == uniques[last_index]]
            temp_fig = px.line(data_temp, x="Fecha", y=option,
                               color="Sexo",
                               color_discrete_map={"Hombre": "blue",
                                                   "Mujer": "red",
                                                   "Sin dato": "grey"})
            for d in temp_fig.data:
                fig.add_trace((go.Scatter(x=d["x"], y=d["y"], name=d["name"],
                                          showlegend=False,
                                          line=d["line"], legendgroup=d["legendgroup"]
                                          )),
                              row=nrows, col=i
                              )

    fig.update_layout(height=nrows * 600)

    return fig


def create_area_chart(df, y: str, color: str, title: str):
    """

    :param df:
    :param y:
    :param color:
    :param title:
    :return:
    """

    fig = px.area(df, "Fecha", y, color=color,
                  title=title, markers=True,
                  range_y=None)
    fig.update_layout(height=575, yaxis_title="Número de Participantes",
                      xaxis_title="Fecha")


    return fig

