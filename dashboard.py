import streamlit as st
from st_aggrid import AgGrid
from graphs import create_time_series, create_area_chart
from processing import aggregate_data, read_data, filter_data, meets_requirements


def set_title(title: str = "Default"):
    """
    This function formats a string containing the title in html format.
    :return:
    """
    html_title = ("<h1 style='text-align: center; color: black;'>" +
                  f"{title}" +
                  "</h1>")

    st.markdown(html_title, unsafe_allow_html=True)


def set_dd_menu(options: list, header: str = "Seleccione una opción", index: int = None,
                placeholder: str = "Seleccione una opción", visibility: str = "visible"):
    """
    This function handles the creation of dropdown menus using the streamlit class "selectbox()".
    :param options: List of the elements to show in the dropdown menu.
    :param header: Header of the dropdown menu.
    :param index: Index of the element to show by default. Defaults to None.
    :param placeholder: Text of the dropdown menu when no option is selected.
    :param visibility:
    :return: variable chosen from the dropdown menu.
    """

    var = st.selectbox(
        label=header,
        options=options,
        index=index,
        placeholder=placeholder,
        label_visibility=visibility
    )

    return var


def set_filter_variables():
    """

    :return:
    """
    col1, col2, col3 = st.columns([1/3, 1/3, 1/3])

    with col1:
        entidad = st.checkbox(label="Entidad")
    with col2:
        asistencias = st.checkbox(label="Asistencias")
    with col3:
        minutos = st.checkbox(label="Minutos")

    filter_vars = {
        "Minutos": {
            "name": "minutos_app",
            "value": 0,
            "flag": minutos,
            "operation": ">"
        },
        "Asistencias": {
            "name": "total_asist",
            "value": 0,
            "flag": asistencias,
            "operation": ">"
        },
        "Entidad": {
            "name": "Entidad",
            "value": "Nuevo León",
            "flag": entidad,
            "operation": "="
        },
        "operations": {
            "=": "eq",
            "<=": "le",
            "<": "lt",
            ">=": "ge",
            ">": "gt",
            "!=": "ne"
        },
        "Minutos_min": {
            "name": "minutos_app",
            "value": 0,
            "flag": True,
            "operation": ">="
        },
        "Asistencias_min": {
            "name": "total_asist",
            "value": 0,
            "flag": False,
            "operation": ">="
        },
        "parameter": {
            "Key": "Minutos",
            "name": "minutos_app"
        }
    }

    return filter_vars


def set_sidebar(df):
    """
    This function takes charge of the sidebar configurations. For the dropdown menus, it takes the columns as the
    options in said menus.
    :param df:
    :return: Variables chosen in the dropdown menus.
    """

    # selected_options = {}

    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"] {
                width: 420px !important; # Set the width to your desired value
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:

        variables = ["Entidad", "Minutos", "Asistencias"]
        operations = ["=", "<=", "<", ">=", ">", "!="]
        st.write("Filtros generales:")
        filter_vars = set_filter_variables()

        if filter_vars["Entidad"]["flag"]:
            value = set_dd_menu(df["Entidad"].unique(),
                                "Seleccione la entidad que desea ver:",
                                index=0)
            filter_vars["Entidad"]["value"] = value
        if filter_vars["Minutos"]["flag"] or filter_vars["Asistencias"]["flag"]:
            quantitative_filters = [v for v in variables[1:] if filter_vars[v]["flag"]]
            col1, col2 = st.columns([0.5, 0.5])

            for q_filter in quantitative_filters:
                with col1:
                    operation = set_dd_menu(operations,
                                            header=f"Filtrar por {q_filter}:", index=4)
                    filter_vars[q_filter]["operation"] = operation
                with col2:
                    try:
                        value = int(st.text_input(label="Escriba", value=0,
                                                  label_visibility="hidden",
                                                  key=q_filter))
                    except ValueError:
                        value = 0

                    filter_vars[q_filter]["value"] = value

        st.write("Seleccione requerimiento a visualizar:")
        # parameter = st.radio(label="Seleccione requerimiento a visualizar",
        #                      options=["Minutos", "Asistencias"],
        #                      index=0, label_visibility="collapsed")

        # if parameter == "Minutos":
        #     filter_vars["Minutos_min"]["flag"] = True
        #     filter_vars["Asistencias_min"]["flag"] = False
        # else:
        #     filter_vars["Minutos_min"]["flag"] = False
        #     filter_vars["Asistencias_min"]["flag"] = True

        # filter_vars["parameter"]["name"] = filter_vars[parameter]["name"]
        # filter_vars["parameter"]["key"] = parameter

        st.write("Requerimientos Mínimos")

        col1, col2 = st.columns([1/2, 1/2])

        for var in variables[1:]:
            with col1:
                operation = set_dd_menu([">", ">="],
                                        header=f"{var}:", index=0)
                filter_vars[var + "_min"]["operation"] = operation
            with col2:
                try:
                    value = int(st.text_input(label="Escriba", value=0,
                                              label_visibility="hidden",
                                              key=var + "_min"))
                except ValueError:
                    value = 0

                filter_vars[var + "_min"]["value"] = value

    return filter_vars


def launch_dashboard():
    """
    This function deploys the streamlit dashboard in a navigator.
    :return:
    """
    st.set_page_config(layout="wide")
    set_title("PIBSE Salud")

    df = read_data()

    selections = set_sidebar(df)

    filtered_df = filter_data(df, selections)
    requirements_df = meets_requirements(filtered_df, selections)

    # chosen_parameter = selections["parameter"]["key"]
    # st.write(chosen_parameter)
    aggregated_data = aggregate_data(requirements_df, ["Fecha", f"Cumple_Ambos"],
                                     "Cumple_Ambos",
                                     operation="count")

    # st.write(aggregated_data)
    # st.plotly_chart(create_time_series(aggregated_data, selections["parameter"]))
    col1, col2 = st.columns([2/3, 1/3])
    with col1:
        title_asistencias = ""
        title_minutos = ""
        if selections["Minutos"]["flag"]:
            title_minutos = ", minutos " + selections["Minutos"]["operation"] \
                                + " " + str(selections["Minutos"]["value"])
        if selections["Asistencias"]["flag"]:
            title_asistencias = ", asistencias " + selections["Asistencias"]["operation"] \
                                + " " + str(selections["Asistencias"]["value"])
        if selections["Entidad"]["flag"]:
            selected_ent = selections["Entidad"]["value"]
            title = f"Gráfica de área en {selected_ent}" + title_asistencias + title_minutos
        else:
            title = "Gráfica de área general" + title_asistencias + title_minutos

        st.plotly_chart(create_area_chart(aggregated_data, "Conteo", "Cumple_Ambos", title))
    with col2:
        st.title("")
        st.write("")
        st.dataframe(aggregated_data, use_container_width=True)
    #
    # # st.plotly_chart(create_barchart(df, chosen_vars))
    # if options["graph_type"] == "Gráfica de Dona":
    #     st.pyplot(create_piechart(df, options["variables"]), clear_figure=True)
    # elif options["graph_type"] == "Gráfica de Barras":
    #     st.pyplot(create_barchart(df, options["variables"]), clear_figure=True)

# Hacer otra gráfica de los que cumplen con las asistencias y los minutos.
# Cambiar orden de las áreas.
# Hacer el ejecutable.
# Cambiar el  label del eje y por Número de participantes que cumplen con los requisitos.
# 


# Hacer otro similar para EPB. Tomar cualquiera de las bases. En este caso son más rubros
# Se tienen asistencias, no minutos_app, modulos en línea y 4 parámetros:
	Assitenicias (Hay trips y talleres introductorios, en cuanto a asistencias, son diferentes
			por ejemplo 4 en introductorio y 6 en trips.)
	Encuestas
	Trabajos
	Promedio de 3 módulos
	75% en cada módulo
	Ver aquí en los menus que se seleccione o por promedio o por módulos 