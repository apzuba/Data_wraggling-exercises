
import pandas as pd

from modules.exploring_data import explore
from modules.plots import plot_pivot
from modules.data_operations import (
    load_data, 
    get_auto_crime_filtered_data, 
    get_day_phases,
    create_pivot
)

# 1. Loading the data.
crime_data, offense_data = load_data()

# 2. Exploring the data.
explore(crime_data=crime_data)


#           TASK 1.
"""
Write a script that shows count of Auto Theft and Towed by 
Phase of Day(as index) vs Month(as column). 
Phase of day is defined as: 
    Morning = 6 a.m to 11 a.m
    Noon = 11.01 a.m to 5 p.m
    Evening = 5.01 p.m to 8 p.m
    Night = 8.01 p.m to 5.59 a.m 
    
Sample Output:
Jan Feb March.......Dec 
Morning 1 2 3………………2 
Noon 3 0 2………………3 
Evening 1 0 0………………4 
Night 0 1 1………………5

"""

# 3. Fitlering table for the auto-crime.
auto_code_filtered = get_auto_crime_filtered_data(crime_data)

# 4. Adding a new column value - Day Phase.
auto_code_filtered_phases = get_day_phases(auto_code_filtered)

# 5. Creating a pivot table.
pivot_auto_sorted, time_phase_order = create_pivot(auto_code_filtered_phases)

# 6. Plotting the data.
plot_pivot(pivot_auto_sorted, time_phase_order)


#           TASK 2.
"""
2. Write script to get offense 
(full offense name provided in offense_codes.csv file) 
per district which has maximum occurrence in respective district
"""

merged_table = pd.merge(
    crime_data, 
    offense_data, 
    left_on='OFFENSE_CODE', 
    right_on='CODE',
    how='left'
    )

selected_t = merged_table[['INCIDENT_NUMBER', 'DISTRICT', 'NAME']]

df2 = selected_t.groupby(['DISTRICT'])['NAME'].apply(
        lambda x: x.value_counts().index[0]
        ).reset_index()


#           TASK 3.
"""Add a column to data set which contains date of 
last incidents happened in respective district 

For Example: 
if a state has N incidents, a column should be added to dataset 
with (i+1)th incident 
having date of ith incident in that column.
"""

df3 = crime_data.copy()
df3.sort_values(['DISTRICT','OCCURRED_ON_DATE'], ascending=[True, True], inplace=True)
df3['PRE_OFF_DATE'] = df3.groupby(['DISTRICT'])['OCCURRED_ON_DATE'].shift(1)



#           TASK 4.
"""
Write a script to identify street having maximum 
number of incidents for every district.
"""

df4 = crime_data.copy()

df4_street = df4.groupby(['DISTRICT'])['STREET'].apply(
        lambda x: x.value_counts().index[0]
        ).reset_index()


#           TASK 5
"""
Create a subset of data, with only 10 recent incidents for each Street.
"""

df5 = crime_data.copy()
df5.sort_values(['STREET','OCCURRED_ON_DATE'], ascending=[True, False], inplace=True)

grouped = df5.groupby('STREET').head(10)
