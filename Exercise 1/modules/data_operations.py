import pandas as pd
import numpy as np
import re


def load_data():
    crime_data=pd.read_csv(
        "/Users/apzuba/Documents/GitHub/data_wraggling exercises/Exercise 1/data/crime.csv",encoding='windows-1252')
    
    offense_data=pd.read_csv(
        "/Users/apzuba/Documents/GitHub/data_wraggling exercises/Exercise 1/data/offense_codes.csv",encoding='windows-1252')

    # Change of the data to the Datetime format
    crime_data['OCCURRED_ON_DATE'] = pd.to_datetime(crime_data.OCCURRED_ON_DATE)

    return crime_data, offense_data


def get_auto_crime_filtered_data(crime_data):
    """This function filters the crime data table for only the vehicle-related crimes.

    Parameters
    ----------
    crime_data : Pandas DataFrame
    
    Returns
    ----------
    auto_code_filtered: Pandas DataFrame
    """
    # Search for Auto Theft and Towing data
    pattern = 'AUTO|TOWED'
    name_mask = crime_data['OFFENSE_DESCRIPTION'].str.contains(pattern, regex=True, flags=re.IGNORECASE)
    offense_codes = crime_data.loc[name_mask, 'OFFENSE_CODE'].values
    unique_codes = pd.Index(np.unique(offense_codes))

    # Filter the DataFrame based on the CODE values
    filtered_df = crime_data[crime_data['OFFENSE_CODE'].isin(unique_codes)]

    # Get the combination of found auto offence and code values
    auto_code = filtered_df[['OFFENSE_DESCRIPTION', 'OFFENSE_CODE', 'OCCURRED_ON_DATE', 'MONTH']]

    # Gettning unique values to find wrongly classified codes - codes 2900 and 735 
    unique = auto_code.drop_duplicates()
    # unique.info()

    # create a boolean mask for rows to keep
    mask = (auto_code['OFFENSE_CODE'] != 2900) & (auto_code['OFFENSE_CODE'] != 735)

    # Properly filtered data table
    auto_code_filtered = auto_code.loc[mask].reset_index(drop=True)

    return auto_code_filtered


def get_day_phases(auto_code_filtered):
    """Function creates a new column with day phases in a Pandas DataFrame.

    Parameters
    ----------
    auto_code_filtered : Pandas DataFrame

    Returns
    -------
    auto_code_filtered: Pandas DataFrame
    """
    time_bins = [0, 6, 11, 17, 20, 24]
    time_labels=['Night', 'Morning', 'Noon', 'Evening', 'Night']

    # Cut the Timestamp column into time phase categories
    auto_code_filtered['Time_Phase'] = pd.cut(
                            auto_code_filtered['OCCURRED_ON_DATE'].dt.hour, 
                            bins=time_bins, 
                            labels=time_labels, 
                            right=False,
                            ordered=False
                            )
    
    return auto_code_filtered


def create_pivot(auto_code_filtered_phases):
    """The function creates a pivot table from a Pandas DataFrame.

    Parameters
    ----------
    auto_code_filtered_phases : Pandas DataFrame

    Returns
    -------
    _type_
        _description_
    """
    pivot_auto = auto_code_filtered_phases.pivot_table(
        index='Time_Phase', 
        columns='MONTH', 
        values='OFFENSE_CODE', 
        aggfunc='count'
        )

    time_phase_order = ['Morning', 'Noon', 'Evening', 'Night']

    # Sort the pivot table rows based on the time_phase_order order
    pivot_auto_sorted = pivot_auto.reindex(time_phase_order)

    return pivot_auto_sorted, time_phase_order
    