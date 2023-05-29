

import numpy as np
import pandas as pd
import os

for dirname, _, filenames in os.walk('/Users/apzuba/Documents/GitHub/data_wraggling exercises/Exercise 1/data'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

#change of the terminal output settings
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.expand_frame_repr', True)  # Disable column width wrapping

def explore(crime_data=None, offence_data=None):

    """
    This is a function that prints the sample instances of the table 
    and info on the columns.

    Parameters
    ----------
    crime_data : Pandas DataFrame

    offence_data : Pandas DataFrame 
    """
    # EXPLORING DATA 

    if crime_data is not None and not crime_data.empty:
        print(crime_data.sample(5))
        print(crime_data.info())

    if offence_data is not None and not offence_data.empty:
        print(offence_data.sample(5))
        print(offence_data.info())
    