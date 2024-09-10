import streamlit as st
from graphs import create_area_chart
from processing import count_values, read_data, filter_data, meets_requirements


def set_title(title: str = "Default"):
    """
    This function formats a string containing the title in html format.
    :return:
    """
    html_title = ("<h1 style='text-align: center; color: black;'>" +
                  f"{title}" +
                  "</h1>")

    st.markdown(html_title, unsafe_allow_html=True)


def set_dd_menu(options: list, title: str = "Seleccione una opción", index: int = None,
                placeholder: str = "Seleccione una opción", visibility: str = "visible"):
    """
    This function handles the creation of dropdown menus using the streamlit class "selectbox()".
    :param options: List of the elements to show in the dropdown menu.
    :param title: Header of the dropdown menu.
    :param index: Index of the element to show by default. Defaults to None.
    :param placeholder: Text of the dropdown menu when no option is selected.
    :param visibility: Boolean to specify if the title is to be seen or not.
    :return: variable chosen from the dropdown menu.
    """
    # Calling the selectbox method
    var = st.selectbox(
        label=title,
        options=options,
        index=index,
        placeholder=placeholder,
        label_visibility=visibility
    )

    return var


def set_filter_variables():
    """
    This function takes care of the available filters to apply. Three columns, with one checkbox each, are created
    A dictionary is also defined, it stores the available variables, their values and their comparison operation, as
    well as a flag to tell whether the filter corresponding to that variable is active.
    :return: Dictionary containing the variables used to filter and information about their status.
    """
    # Calling the columns method to retrieve three columns
    col1, col2, col3 = st.columns([1/3, 1/3, 1/3])
    # Setting a checkbox on each column
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
        "Minutos_min": {
            "name": "minutos_app",
            "value": 0,
            "flag": True,
            "operation": ">="
        },
        "Asistencias_min": {
            "name": "total_asist",
            "value": 0,
            "flag": True,
            "operation": ">="
        },
        "parameter": {
            "Key": "Minutos",
            "name": "minutos_app"
        },
        "operations": {
            "=": "eq",
            "<=": "le",
            "<": "lt",
            ">=": "ge",
            ">": "gt",
            "!=": "ne"
        }
    }

    return filter_vars


def set_sidebar():
    """
    This function takes charge of the sidebar configurations. It contains the checkboxes corresponding to the
    available filters, as well as drop down menus and input boxes to set the values and operations to filter by.
    :param df: Dataframe whose data will be used to feed the dropdown menus.
    :return: A dictionary containing updated information about the variables used to apply the filters.
    """
    # This command manipulates the width of the sidebar
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
        # Variables available to filter by
        variables = ["Entidad", "Minutos", "Asistencias"]
        # Available comparison operators
        operations = ["=", "<=", "<", ">=", ">", "!="]

        st.radio(label="Default", options=["2023", "2024"], index = 0,
                 label_visibility="hidden")
        df = read_data()[year]
        # Setting the header of the filters section in the sidebar
        st.write("Filtros generales:")
        # Obtaining the filter variables.
        filter_vars = set_filter_variables()

        # If the flag of the filter variable is set to true, activate the respective filter field
        if filter_vars["Entidad"]["flag"]:
            value = set_dd_menu(df["Entidad"].unique(),
                                "Seleccione la entidad que desea ver:",
                                index=0)
            # Appending the value of the Entidad filter
            filter_vars["Entidad"]["value"] = value

        if filter_vars["Minutos"]["flag"] or filter_vars["Asistencias"]["flag"]:
            # This list stores the variables whose flag is set to True
            quantitative_filters = [v for v in variables[1:] if filter_vars[v]["flag"]]
            col1, col2 = st.columns([0.5, 0.5])
            # Activating the corresponding filter field
            for q_filter in quantitative_filters:
                # The first column deploys a dropdown menu to select the comparison operator
                with col1:
                    operation = set_dd_menu(operations,
                                            title=f"Filtrar por {q_filter}:", index=4)
                    # Storing the comparison operator
                    filter_vars[q_filter]["operation"] = operation
                # The second column deploys an input box to enter the filter value
                with col2:
                    try:
                        value = int(st.text_input(label="Escriba", value=0,
                                                  label_visibility="hidden",
                                                  key=q_filter))
                    except ValueError:
                        value = 0
                    # Appending the value of the corresponding filter
                    filter_vars[q_filter]["value"] = value

        st.write("Requisitos Mínimos")
        # Creating two columns for the minimum requirements
        col1, col2 = st.columns([1/2, 1/2])

        for var in variables[1:]:
            # The first column deploys a dropdown menu to select the comparison operator
            with col1:
                operation = set_dd_menu([">", ">="],
                                        title=f"{var}:", index=0)
                # Appending the operation of the corresponding filter
                filter_vars[var + "_min"]["operation"] = operation
            # The second column deploys an input box to enter the filter value
            with col2:
                try:
                    value = int(st.text_input(label="Escriba", value=0,
                                              label_visibility="hidden",
                                              key=var + "_min"))
                except ValueError:
                    value = 0
                # Appending the operation of the corresponding filter
                filter_vars[var + "_min"]["value"] = value

    return filter_vars


def launch_dashboard():
    """
    This function deploys the streamlit dashboard in a navigator.
    :return:
    """
    st.set_page_config(layout="wide")
    set_title("PIBSE Salud")
    # Reading the data
    data = read_data()
    # Retrieving the selections chosen from the sidebar
    selections = set_sidebar()
    # Filtering the data if necessary
    filtered_df = filter_data(df, selections)
    # Creating requirement variables
    requirements_df = meets_requirements(filtered_df, selections) 

    # This dictionary stores the dataframes created
    dataframes = {
        "Cumple_Ambos": count_values(requirements_df, 
                                     "Fecha", "Cumple_Ambos"),
        "Cumple_Minutos": count_values(requirements_df, 
                                       "Fecha", "Cumple_Minutos"),
        "Cumple_Asistencias": count_values(requirements_df, 
                                           "Fecha", "Cumple_Asistencias")
    }

    # Creating a grid where the charts and tables will be included
    # Defining the number or columns and rows in the grid
    nrows = 3
    ncols = 2
    rows = {}

    # Inserting the charts and tables using a for loop
    for i in range(nrows):
        key = list(dataframes.keys())[i]
        rows[f"{i}"] = st.columns([2/3, 1/3])
        for j in range(ncols):
            # If j index is equal to 0, insert a graph
            if j == 0:
                tile = rows[f"{i}"][j].container()
                tile.plotly_chart(create_area_chart(dataframes[key],
                                                    "Participantes", key,
                                                    "Número de participantes"))
            # If the j index is equal to 1, write a table
            else:
                tile = rows[f"{i}"][j].container()
                tile.title("")
                tile.write("")
                tile.write(dataframes[key].set_index("Fecha"), 
                           use_container_width=True)

