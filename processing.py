import pandas as pd
import operator
from datetime import datetime

def read_data(index_col: str = None, dtype=None):
    """
    This function reads a csv file and returns a pandas dataframe.
    :param index_col: Name of the column that will serve as the dataframe index
    :param dtype: Datatype or dictionary of datatypes in the dataframe.
    :param date_col: Name of the date column
    :return: A pandas dataframe containing the data
    """
    path = r"PIBSE 2024 Histórico (6 semanas).csv"
    # Reading the csv file
    df = pd.read_csv(path)
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    # Keeping the top six states with the highest number of participants
    states_to_keep = ["Sonora", "Oaxaca", "Querétaro", "Nuevo León", "Campeche", "Coahuila"]
    df = df[df["Entidad"].isin(states_to_keep)]
    # Deleting the redundancies from the Sexo column
    df["Sexo"] = df["Sexo"].apply(lambda x: delete_redundancies(x, "Sexo"))
    # Deleting "unnecessary" columns.
    cols_to_delete = ["Puesto", "total_encuestas"]
    cols_to_keep = [col for col in df.columns if col not in cols_to_delete]

    return df[cols_to_keep]


def filter_data(df, filter_vars: dict):
    """
    This function filters a data frame given a dictionary containing the name of the variables, the value used to
    filter and the comparison operator.
    :param df: Dataframe to filter.
    :param filter_vars: Dictionary containing the necessary information about the filter variables.
    :return: Filtered dataframe.
    """
    # Storing the operators in a dictionary. The key is the string representation of the operator, and the operator
    # is given by the operator class.
    available_filters = ["Entidad", "Minutos", "Asistencias"]
    operators = {
        "=": operator.eq,
        "<=": operator.le,
        "<": operator.lt,
        ">=": operator.ge,
        ">": operator.gt,
        "!=": operator.ne
    }
    # Making a copy of the dataframe
    new_df = df
    # This loops iterates over the available filters to check which filter has to be applied
    for f in available_filters:
        # If the flag of the available filter is set to true, apply the filter.
        if filter_vars[f]["flag"]:
            # Retrieving the operator class with its corresponding method.
            operation = filter_vars[f]["operation"]
            # Retrieving the name of the variable as it appears on the dataframe.
            name = filter_vars[f]["name"]
            # Value used to filter.
            value = filter_vars[f]["value"]
            new_df = new_df[operators[operation](new_df[name], value)]

    return new_df


def meets_requirements(df, filter_vars: dict):
    """

    :param df:
    :param filter_vars:
    :return:
    """
    operators = {
        "=": operator.eq,
        "<=": operator.le,
        "<": operator.lt,
        ">=": operator.ge,
        ">": operator.gt,
        "!=": operator.ne
    }
    requirements = ["Minutos_min", "Asistencias_min"]

    for r in requirements:
        name = filter_vars[r]["name"]
        value = filter_vars[r]["value"]
        operation = operators[filter_vars[r]["operation"]]
        df["Cumple_" + r.strip("_min")] = df[name].apply(lambda x: 1 if operation(x, value) else 0)

    df["Cumple_Ambos"] = (df["Cumple_Minutos"] + df["Cumple_Asistencias"])//2

    df["Cumple_Ambos"] = df["Cumple_Ambos"].apply(lambda x: "Sí" if x == 1 else "No")
    df["Cumple_Minutos"] = df["Cumple_Minutos"].apply(lambda x: "Sí" if x == 1 else "No")
    df["Cumple_Asistencias"] = df["Cumple_Asistencias"].apply(lambda x: "Sí" if x == 1 else "No")

    return df

# def count_uniques(df, variables: list):
#     """
#     This function counts the occurrence of unique values in a dataframe column, and orders the result un descending
#     order.
#     :param df: Dataframe from which the data will be collected.
#     :param variables: Dataframe columns to count the values from.
#     :return: A dataframe with the count of the unique values from the selected column.
#     """
#     # Filtering variables
#
#     filtered_variables = [v for v in variables if v != ""]
#
#     aggregated_df = df.groupby(by=filtered_variables)[[filtered_variables[0]]].aggregate("count")
#     sorted_df = aggregated_df.rename(columns={f"{filtered_variables[0]}": "Conteo"})
#
#     return sorted_df.reset_index()


def delete_redundancies(x, column: str):
    """
    :param x:
    :param column:
    :return:
    """
    if column == "Entidad":
        if x == "Ciudad De México":
            return "Ciudad de México"
        elif x == "Estado De México":
            return "Estado de México"
        else:
            return x
    elif column == "Sexo":
        if x == "femenino":
            return "Mujer"
        elif x == "Masculino":
            return "Hombre"
        elif x == "Otro" or x == "Prefiero No Contestar":
            return "Sin dato"
        else:
            return x
    else:
        return x


def aggregate_data(df, variables_to_group: list, variable_to_aggregate: str, operation: str = "sum"):
    """

    :param df:
    :param variables_to_group:
    :param variable_to_aggregate:
    :param operation:
    :return:
    """

    aggregated_df = df.groupby(variables_to_group)[[variable_to_aggregate]].aggregate(operation)
    sorted_df = aggregated_df.rename(columns={f"{variable_to_aggregate}": "Conteo"})

    return sorted_df.reset_index()


def count_values(df, group_by: str, col: str):
    """
    This function does something
    :param df:
    :param group_by:
    :param col:
    :return:
    """

    new_df = df.groupby(by=group_by)[col].value_counts().reset_index()

    return new_df.rename(columns={"count": "Conteo"})

