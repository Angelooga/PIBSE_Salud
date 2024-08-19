import pandas as pd
import operator
from datetime import datetime

def read_data(index_col: str = None, dtype=None):
    """
    This function reads a csv file and returns a pandas dataframe.
    :param index_col: Name of the column that will serve as the dataframe index
    :param dtype: Datatype or dictionary of datatypes in the dataframe.
    :return: A pandas dataframe containing the data
    """
    path = r"PIBSE 2024 Histórico (6 semanas).csv"
    # Reading the csv file
    df = pd.read_csv(path, index_col=index_col, dtype=dtype)
    # df["Fecha"] = pd.to_datetime(df["Fecha"])
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
    # This loop iterates over the available filters to check which filter has to be applied
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
    This function creates a new column in a dataframe that contains "Sí" or "No"
    depending on a previously defined requirement.
    :param df: Dataframe in which the new variable will be created.
    :param filter_vars: Dictionary that contains the requirements variables with their respective
    information.
    :return: Dataframe with the new variables created.
    """
    # Defining a dictionary that contains the comparison operators
    operators = {
        "=": operator.eq,
        "<=": operator.le,
        "<": operator.lt,
        ">=": operator.ge,
        ">": operator.gt,
        "!=": operator.ne
    }
    # Storing the requirements keys in a list
    requirements = ["Minutos_min", "Asistencias_min"]
    # Iterating over the requirements list to apply the corresponding comparison operations
    # and write the corresponding value in the new variable.
    for r in requirements:
        name = filter_vars[r]["name"]
        value = filter_vars[r]["value"]
        operation = operators[filter_vars[r]["operation"]]
        df["Cumple_" + r.strip("_min")] = df[name].apply(lambda x: 1 if operation(x, value) else 0)
    # Defining the Cumple_Ambos variables as the sum of the Cumple_Minutos and Cumple_Asistencias
    # column
    df["Cumple_Ambos"] = (df["Cumple_Minutos"] + df["Cumple_Asistencias"])//2
    # Changing the 1 by "Sí" and 0 by "No" in the new columns
    df["Cumple_Ambos"] = df["Cumple_Ambos"].apply(lambda x: "Sí" if x == 1 else "No")
    df["Cumple_Minutos"] = df["Cumple_Minutos"].apply(lambda x: "Sí" if x == 1 else "No")
    df["Cumple_Asistencias"] = df["Cumple_Asistencias"].apply(lambda x: "Sí" if x == 1 else "No")

    return df


def delete_redundancies(x, column: str):
    """
    This function takes care of the redundancies found in the Entidad and Sexo columns.
    It is used as an argument to the dataframe apply() method.
    :param x: Dataframe element to change.
    :param column: Column from which the redundancies will be eliminated.
    :return: Dataframe column with redundancies deleted.
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


def count_values(df, group_by: str, col: str):
    """
    This function counts the number of occurrences of unique values in a dataframe column.
    :param df: Dataframe from which the occurrences will be counted.
    :param group_by: Column to group the dataframe by.
    :param col: Dataframe column from which the occurrences will be counted.
    :return: Dataframe containing the number of occurrences of elements in the chosen column.
    """

    new_df = df.groupby(by=group_by)[col].value_counts().reset_index()
    new_df["Porcentaje"] = round(100 * new_df['count']/new_df.groupby('Fecha')["count"]\
                                                    .transform('sum'), 2)

    return new_df.rename(columns={"count": "Participantes"})

