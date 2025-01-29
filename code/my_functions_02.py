import sqlite3
from pathlib import Path
import pandas as pd
from ydata_profiling import ProfileReport


def read_playlist(file_path):
    """
    Reads a JSON file containing playlist data, processes it by removing unnecessary extensions from the filename,
    and adds new columns for the playlist name and region. It returns the DataFrame with these additional columns.

    Args:
        file_path (str): Path to the JSON file containing playlist data.

    Returns:
        pd.DataFrame: Processed DataFrame with 'Playlist' and 'Region' columns added.
    """
    df = pd.read_json(file_path)

    # Remove .json and extensions
    file_name = Path(file_path).stem
    file_name = file_name.replace("_tracks", "").replace("_features", "")

    # Add column for filename
    df["Playlist"] = file_name

    # Add column for region
    regions = ["UK", "USA", "Singapore"]
    region = [region for region in regions if region in file_name]
    df["Region"] = region[0] if region else "Global"

    return df


def inspect_dataframe(df, type):
    """
    Generates a profiling report for the DataFrame to provide an overview of the data,
    including data types, missing values, and other statistical details.

    Args:
        df (pd.DataFrame): The DataFrame to be profiled.
        type (str): A label for the type of data being inspected, used in the title of the report.

    Returns:
        None
    """

    print(f"---{type}---")

    # Generate profiling report
    profile = ProfileReport(df, title=f"{type} Profiling Report", explorative=True)
    profile.to_notebook_iframe()

    # Save as HTML
    profile.to_file(f"../reports/{type}_profiling_report.html")
    print(f"Profiling report saved as {type}_profiling_report.html")


def process_tracks(df):
    """
    Normalises the "items" column in the DataFrame containing track details, extracts relevant columns,
    and adds metadata columns for "Playlist" and "Region". It returns a cleaned and well-structured DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing playlist and track data.

    Returns:
        pd.DataFrame: Processed DataFrame containing track information with 'Track_Name', 'Track_ID',
                      'Popularity', 'Playlist', and 'Region' columns.
    """
    # Extract Playlist and Region information from DataFrame
    playlist = df["Playlist"]
    region = df["Region"]

    # Normalize JSON into DataFrame
    items = df["items"]

    df = pd.json_normalize(
        items, meta=[["track", "name"], ["track", "id"], ["track", "popularity"]]
    )

    # Reset index and add metadata columns
    df = df.reset_index(drop=True)

    # Select relevant columns and rename
    df = df[["track.name", "track.id", "track.popularity"]]
    df.columns = ["Track_Name", "Track_ID", "Popularity"]

    # Add metadata columns
    df["Playlist"] = playlist.values
    df["Region"] = region.values

    # Adjust index to start at 1
    df.index = range(1, len(df) + 1)

    return df


def process_features(df):
    """
    Processes the features of tracks by selecting and renaming the relevant columns, removing duplicates based on
    'Track_ID', and optimising the data for storage efficiency by rounding numerical values. The index is adjusted
    to start at 1 for consistency.

    Args:
        df (pd.DataFrame): The DataFrame containing feature data for tracks.

    Returns:
        pd.DataFrame: Cleaned and optimised DataFrame with rounded values and adjusted index.
    """

    # Select relevant columns and rename
    df = df[["id", "energy", "tempo", "danceability", "mode", "acousticness"]].rename(
        columns={
            "id": "Track_ID",
            "energy": "Energy",
            "tempo": "Tempo",
            "danceability": "Danceability",
            "mode": "Mode",
            "acousticness": "Acousticness",
        }
    )

    # Remove duplicates based on Track_ID
    df = df.drop_duplicates(subset="Track_ID")

    # Optimise for data efficiency
    columns_to_convert = [col for col in df.columns if col not in ["Track_ID", "Mode"]]
    for column in columns_to_convert:
        df[column] = df[column].round(3)

    # Adjust index to start at 1
    df.index = range(1, len(df) + 1)

    return df


def analyse_column_limits(df):
    """
    Analyses the DataFrame columns to determine their data type and the limits for numeric columns (min and max)
    or the maximum length for string columns. This helps in generating SQL data types with appropriate sizes.

    Args:
        df (pd.DataFrame): The DataFrame whose columns will be analysed.

    Returns:
        dict: A dictionary with column names as keys and their limits and data types as values.
    """
    column_analysis = {}

    # Iterate through each column to analyse data type and limits
    for col in df.columns:
        col_data = df[col]
        if col_data.dtype == "object":  # Strings
            max_length = col_data.astype(str).map(len).max()
            column_analysis[col] = {"type": "string", "max_length": max_length}
        elif pd.api.types.is_numeric_dtype(col_data):  # Numeric
            min_val, max_val = col_data.min(), col_data.max()
            column_analysis[col] = {"type": "numeric", "min": min_val, "max": max_val}
    return column_analysis


def create_table(table_name, col_limit, foreign_key=None):
    """
    Generates an SQL script to create a table with appropriate column types based on the provided column limits.
    It includes logic to determine the appropriate data type for each column based on its values and the possibility
    of adding a foreign key constraint.

    Args:
        table_name (str): The name of the table to be created.
        col_limit (dict): A dictionary containing column names and their data type limits.
        foreign_key (dict, optional): A dictionary containing details for a foreign key constraint (default is None).

    Returns:
        str: The generated SQL script to create the table.
    """
    sql_parts = [f"CREATE TABLE IF NOT EXISTS {table_name} ("]

    # Add Track_ID as primary key
    sql_parts.append("    Track_ID VARCHAR(50) PRIMARY KEY,")

    # Add columns based on limits
    for col, limits in col_limit.items():
        if col in ["Track_ID"]:
            continue

        # Determine SQL data type based on limits
        if limits["type"] == "string":
            length = limits["max_length"] + 5  # Add buffer
            sql_type = f"VARCHAR({length})" if length <= 255 else "TEXT"
        elif limits["type"] == "numeric":
            min_val, max_val = limits["min"], limits["max"]
            if -128 <= min_val and max_val <= 127:
                sql_type = "TINYINT"
            elif -32768 <= min_val and max_val <= 32767:
                sql_type = "SMALLINT"
            elif -2147483648 <= min_val and max_val <= 2147483647:
                sql_type = "INT"
            else:
                sql_type = "BIGINT"
        sql_parts.append(f"    {col} {sql_type},")

    # Add foreign key constraint if provided
    if foreign_key is None:
        sql_parts[-1] = sql_parts[-1].rstrip(",")
    else:
        sql_parts.append(
            f"    FOREIGN KEY ({foreign_key["column"]}) REFERENCES {foreign_key["table"]}({foreign_key["reference_column"]})"
        )

    sql_parts.append(");")

    return "\n".join(sql_parts)


def sql_database(df, type, foreign_key=None):
    """
    Creates an SQL table based on the structure and data types of the DataFrame and inserts the data into the table.
    It also profiles the DataFrame to determine column limits before generating the SQL table creation script.

    Args:
        df (pd.DataFrame): The DataFrame to be inserted into the database.
        type (str): The name of the table to be created and populated.
        foreign_key (dict, optional): Foreign key details if applicable (default is None).

    Returns:
        None
    """
    # Analyse column limits
    column_limits = analyse_column_limits(df)
    sql_table = create_table(type, column_limits, foreign_key)
    print(f"Generated table for {type}")

    # Connect to database
    conn = sqlite3.connect("../data/processed/spotify.db")
    conn.execute(sql_table)
    conn.commit()

    # Insert data into table
    df.to_sql(type, conn, if_exists="replace", index=False)
    print(f"Inserted data into {type}")
