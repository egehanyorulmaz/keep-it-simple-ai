import pandas as pd

def drop_columns_to_rows(df, column_names):
    """
    This function takes a dataframe and a list of column names and drops the columns from the dataframe
    and adds the column names as rows to the dataframe.
    :param df: Pandas dataframe
    :param column_names: List of column names
    :return: Pandas dataframe
    """
    temp_df = pd.DataFrame(data=[df.columns.tolist()], columns=column_names)
    df.columns = column_names
    df = pd.concat([temp_df, df], ignore_index=True)
    return df

def drop_columns_with_nan(df, threshold):
    # calculate the number of NaN values in each column
    num_nans = df.isna().sum()

    # calculate the percentage of NaN values in each column
    pct_nans = num_nans / len(df)

    # get the list of column names to drop
    columns_to_drop = list(pct_nans[pct_nans >= threshold].index)

    # drop the columns with the threshold or more NaN values
    df_dropped = df.drop(columns=columns_to_drop)

    return df_dropped