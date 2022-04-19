import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser
import os
from pathlib import Path

BASE_DIR = Path(__file__).parents[1]
OUTPUT_DIR = BASE_DIR / "output"

def redact_small_numbers(df, n, numerator, denominator, rate_column):
    """Takes counts df as input and suppresses low numbers.  Sequentially redacts
    low numbers from numerator and denominator until count of redcted values >=n.
    Rates corresponding to redacted values are also redacted.
    
    Args:
        df: measures dataframe
        n: threshold for low number suppression
        numerator: column name for numerator
        denominator: column name for denominator
        rate_column: column name for rate
    
    Returns:
        Input dataframe with low numbers suppressed
    """
    
    def suppress_column(column):    
        suppressed_count = column[column<=n].sum()
        
        #if 0 dont need to suppress anything
        if suppressed_count == 0:
            pass
        
        else:
            column = column.replace([0, 1, 2, 3, 4, 5],np.nan)
            

            while suppressed_count <=n:
                suppressed_count += column.min()
                column.iloc[column.idxmin()] = np.nan   
        return column
    
    
    for column in [numerator, denominator]:
        df[column] = suppress_column(df[column])
    
    df.loc[(df[numerator].isna())| (df[denominator].isna()), rate_column] = np.nan
    
    return df    

def convert_ethnicity(df):
    """Converts the ethnicity of a dataframe from int to an understandable string.
    
    Args:
        df: dataframe with ethnicity column
    
    Returns:
        Input dataframe with converted ethnicity column
    """
    ethnicity_codes = {1.0: "White", 2.0: "Mixed", 3.0: "Asian", 4.0: "Black", 5.0:"Other", np.nan: "unknown", 0: "unknown"}
    df = df.replace({"ethnicity": ethnicity_codes})

    return df

def convert_binary(df, binary_column, positive, negative):
    """Converts a column with binary variable codes as 0 and 1 to understandable strings.

    Args:
        df: dataframe with binary column
        binary_column: column name of binary variable
        positive: string to encode 1 as
        negative: string to encode 0 as

    Returns:
        Input dataframe with converted binary column
    """
    replace_dict = {0: negative, 1: positive}
    df[binary_column] = df[binary_column].replace(replace_dict)
    return df

def drop_missing_demographics(df, demographic):
    """Drops any rows with missing values for a given demographic variable.

    Args: 
        df: measures dataframe
        demographic: column name of demographic variable

    Returns:
        Dataframe with no rows missing demographic variable.
    """
    return df.loc[df[demographic].notnull(),:]

def calculate_rate(df, numerator, denominator, rate_per=100):
    """Creates a rate column for a dataframe with a numerator and denominator column.
    
    Args:
        df: measures dataframe
        numerator: numerator for rate
        denominator: denominator for rate
        rate_per: unit for calculated rate
    
    Returns:
        Input dataframe with additional rate column
    """

    rate = df[numerator]/(df[denominator]/rate_per)
    df['rate'] = rate
    
    return df
        
def drop_irrelevant_practices(df, practice_col):
    """Drops irrelevant practices from the given measure table.
    An irrelevant practice has zero events during the study period.
    Args:
        df: A measure table.
        practice_col: column name of practice column
    Returns:
        A copy of the given measure table with irrelevant practices dropped.
    """
    is_relevant = df.groupby(practice_col).value.any()
    return df[df[practice_col].isin(is_relevant[is_relevant == True].index)]


def create_child_table(
    df, code_df, code_column, term_column, nrows=5
):

    """
    Args:
        df: A measure table.
        code_df: A codelist table.
        code_column: The name of the code column in the codelist table.
        term_column: The name of the term column in the codelist table.
        measure: The measure ID.
        nrows: The number of rows to display.
    Returns:
        A table of the top `nrows` codes.
    """
 
    event_counts = (
        df.groupby("event_code")["ast_population"]
        .sum()  # We can't use .count() because the measure column contains zeros.
        .rename_axis(code_column)
        .rename("Events")
        .reset_index()
        .sort_values("Events", ascending=False)
    )

    
    event_counts["Events (thousands)"] = event_counts["Events"] / 1000
       
    # Gets the human-friendly description of the code for the given row
    # e.g. "Systolic blood pressure".
    code_df = code_df.set_index(code_column).rename(
        columns={term_column: "Description"}
    )
    event_counts = (
        event_counts.set_index(code_column).join(code_df).reset_index()
    )

    
    # Cast the code to an integer.
    event_counts[code_column] = event_counts[code_column].astype(int)
    
    # return top n rows
    
    return event_counts.iloc[:nrows, :]

def get_number_practices(df):
    """Gets the number of practices in the given measure table.
    Args:
        df: A measure table.
    """
    return len(df.practice.unique())


def get_percentage_practices(measure_table):
    """Gets the percentage of practices in the given measure table.
    Args:
        measure_table: A measure table.
    """

    # Read in all input practice count files and get num unique
    practice_df_list = []
    for file in os.listdir(OUTPUT_DIR):
        if file.startswith("input_practice_count"):
            df = pd.read_csv(os.path.join(OUTPUT_DIR, file))
            practice_df_list.append(df)

    total_practices_df = pd.concat(practice_df_list, axis=0)
    num_practices_total= get_number_practices(total_practices_df)

    # Get number of practices in measure
    num_practices_in_study = get_number_practices(measure_table)

    return np.round((num_practices_in_study / num_practices_total) * 100, 2)

def add_date_lines(plt, vlines):
    # TODO: Check that it is within the range?
    for date in vlines:
        try:
            plt.vlines(
                x=[pd.to_datetime(date)],
                ymin=0,
                ymax=100,
                colors="orange",
                ls="--",
            )
        except parser._parser.ParserError:
            # TODO: add logger and print warning on exception
            # Skip any dates not in the correct format
            continue


def plot_measures(
    df,
    filename,
    title,
    column_to_plot,
    category=False,
    y_label=None,
    vlines=[]
):
    """Produce time series plot from measures table.  One line is plotted for each sub
    category within the category column.

    Args:
        df: A measure table
        title: Plot title string
        column_to_plot: Name of column to plot
        category: Name of column indicating different categories
        y_label: String indicating y axis text
    """
    plt.figure(figsize=(15, 8))
    if category:
        for unique_category in df[category].unique():

            df_subset = df[df[category] == unique_category]

            plt.plot(df_subset["date"], df_subset[column_to_plot], marker="o")
    else:
        plt.plot(df["date"], df[column_to_plot], marker="o")

    plt.ylabel(y_label)
    plt.xlabel(None)
    # plt.xticks(rotation="horizontal")

    plt.title(title)

    plt.rc("font", size=14)
    plt.rc("axes", titlesize=14)
    plt.rc("axes", labelsize=14)
    plt.rc("xtick", labelsize=14)
    plt.rc("ytick", labelsize=14)
    plt.rc("legend", fontsize=14)
    plt.rc("figure", titlesize=14)

    # yticks = np.arange(5)
    # plt.set_yticks(yticks)
    plt.ylim(bottom=0, top=20)

    plt.gca().set_yticklabels(
        ["{:.1f}%".format(x) for x in plt.gca().get_yticks()]
    )

    myFmt = mdates.DateFormatter('%b-%Y')
    plt.gca().xaxis.set_major_formatter(myFmt)
    
    plt.xticks(rotation = 45)
   
    add_date_lines(plt, vlines)

    if category:
        plt.legend(df[category].unique(), loc="upper right")

    else:
        pass

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename)
    plt.clf()

