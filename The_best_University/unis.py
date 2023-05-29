"""
Produce a dataset of schools which satisfy all of Maria's criteria
Rank them from best to worst according to the same criteria.

Maria's schools must:
1.  be in an urban/metropolitan area.
2.  be in a city that ranks 75th percentile or higher on Kauffman's start-up rankings.
3.  be below 50th percentile in overall crime.
4.  offer a 2-year or 4-year degree in Information Technology/Science.
5.  Maria doesn't like the cold. Find and integrate temperature data. 
    Eliminate any schools located in cities/areas below the 25th percentile 
    in average temperature.
    

The plan:
1. Explore the data.
    1. Read the pdf data dictionaries or codebooks to figure out what 
    the variables mean and which ones you will need to use.
    2. Look for suitable columns to join the tables on.
    3. Load the data
    4. Explore the loaded data and eliminate the unneeded columns.
    5. Consider a metric for combined classification.
2. Data preprocessing.
    1. Perform any cleaning and standardization needed to facilitate 
       the joins & data congruency.
    2. Engineer a summary variable for school crime so that we can 
    compare schools by levels of crime overall.
3. Analysis.
    1. Eliminate from the data all the data points that fail to satisfy Maria's criteria.
    2. Engineer a summary parameter(equation) based on all the useful parameters.
"""




"""
1.1.-1.2. Reading of data pdf documentation. Finding potentialy useful columns.

The data(parameters) that I need:
    -Area character (Metropolian/Urban)
    -City name
    -Kaufman startups ranking, city
    -Crime rate (below 50th percentile)
    -Study subject (Information Technology/Science)
    -Subject lenght of studies/type of degree (2-year or 4-year degree)
    -Yearly average temperature data

Observation: the common parameter for all these data seems to be the City name.

The pontentially useful data I can find (to explore further):
*CollegeScoreboard:
    Root
    -ID
    -Currently Operating
    About the school
    -Name
    -Location
    -Degree Type
    Acedemics
    -Programs Offered by Type
*Crime:
    -City
    -Crime rates
*Kaufmann Index Entrepreneurship
    ent015u		entrepreneurship
    MSA Code (cities)

Observation: None of the current data sources has the temperature data. 
    I found online a publicly available dataset for 321 cities in the US
    (https://www.kaggle.com/datasets/sudalairajkumar/daily-temperature-of-major-cities)
! Please download the dataset 
*Daily Temperature of Major Cities
    -City
    -Country
    -AvgTemperature
"""

import numpy as np
import pandas as pd
import os
import opendatasets as od
import kaggle

current_directory = os.getcwd()

#Downloading the temperature & entrepreneurship dataset.
# Please note: You need kaggle API json file to download the temperature dataset this way.
# You can also download the dataset directly from the website with below link:
# https://www.kaggle.com/datasets/sudalairajkumar/daily-temperature-of-major-cities

# Setting the downoad addresses.
dataset_param_temp = 'sudalairajkumar/daily-temperature-of-major-cities'
dataset_url_entr = "https://www.kauffman.org/wp-content/uploads/2019/09/kieadata15.csv"

# Specify the directory path where to download the dataset
download_path_temp = os.path.join(current_directory, 'Data/Temperature')
download_path_entr = os.path.join(current_directory, 'Data/Entrepreneurship')

kaggle.api.dataset_download_files(dataset_param_temp, path=download_path_temp, unzip=True)
od.download(dataset_url_entr, data_dir=download_path_entr) 


for dirname, _, filenames in os.walk(current_directory):
    for filename in filenames:
        os.path.join(dirname, filename)


pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.expand_frame_repr', True)  # Disable column width wrapping

CollScoreboard_Raw = pd.read_csv("Data/CollegeScoreboard/CollegeScorecard.csv", low_memory=False)


CollScoreboard_Raw.sample(5)
CollScoreboard_Raw.shape        #(7804, 1729)!

CollScoreboard_Raw['INSTNM'].sample(5)
CollScoreboard_Raw['CITY'].sample(5)
CollScoreboard_Raw['STABBR'].sample(5)
CollScoreboard_Raw['UNITID'].sample(5)
CollScoreboard_Raw['SATMT75'].sample(5)


"""
"The second set (CIP[01-54][CERT1/CERT2/ASSOC/BACHL/CERT4]) 
identifies whether the institution offers the program, at what level, 
and whether the institution offers the program and level 
through an exclusively distance education program."

-This requires finding which The Classification of Instructional Programs (CIP) 
corresponds to the searched program(Information Technology/Science)

The internet search revealed that category 11 is corresponding to 
"COMPUTER AND INFORMATION SCIENCES AND SUPPORT SERVICES" 
which satisfies the condition.

-The programmes that satisfy the duration time are both ASSOC and BACHL type. 

The selected columns will be then 'CIP11ASSOC' and 'CIP11BACHL'.
"""

# Finding the "Currently Operating" column through the bool type.
boolean_columns = CollScoreboard_Raw.columns[
    CollScoreboard_Raw.dtypes == bool
    ] # No results

#Trying through the name search.
operating_column = CollScoreboard_Raw.columns[
    CollScoreboard_Raw.columns.str.contains('curr', case=False)
    ] # Found column named 'CURROPER


CollScoreboard_Raw['CURROPER'].sample(5) #exploring the column data



# Creating a filtered table only with the usefeul columns.
CollScoreboard_Filtered = CollScoreboard_Raw[[
    'INSTNM', 'CITY', 'SATMT25', 'CURROPER', 'CIP11ASSOC', 'CIP11BACHL']]

CollScoreboard_Filtered['CIP11ASSOC'].sample(5)
CollScoreboard_Filtered['CIP11BACHL'].sample(5)

# Filtering the rows for the examples where the Universities are currently open
# and they offer an Associate or a Bachelor degree.
CollScoreboard_Selected = CollScoreboard_Filtered[
    (CollScoreboard_Filtered['CURROPER'] == 1) &
    (
        (CollScoreboard_Filtered['CIP11ASSOC'] > 0) | 
        (CollScoreboard_Filtered['CIP11BACHL'] > 0)
    )
] # The Scoreboard data seems ready.



Crime_Raw = pd.read_csv("Data/Crime/Crime_2015.csv", low_memory=False)

Crime_Raw.sample(5)
Crime_Raw.shape     # (378, 12)

"""
This dataset is way more clearer than the previous one. 
It contains rate of crimes per 100.000 citizens for various crimes.
Not all crimes are alike (eg. Murder or Rape is much more dangerous crime than a Theft), 
thus engineering a weighted parameter for all the crimes will help to determine 
a fair assesment of the crime levels.

Below, I constructed a Dict with the ratio I apply to get the weighted paremeters.
"""

crime_weights = {
    'ViolentCrime':       5,
    'Murder':           300,
    'Rape':             150,
    'Robbery':            5,
    'AggravatedAssault': 10,
    'PropertyCrime':      1,
    'Burglary':           3,
    'Theft':            0.5,
    'MotorVehicleTheft':  3
}

Crime_Weighted = Crime_Raw.copy()
Crime_Weighted = Crime_Weighted.drop(['MSA', 'State'], axis=1)
Crime_Weighted.info()

#Converting all the data values to floats
Crime_Weighted['ViolentCrime'] = Crime_Weighted['ViolentCrime'].str.replace(',', '').astype(float)
Crime_Weighted['PropertyCrime'] = Crime_Weighted['PropertyCrime'].str.replace(',', '').astype(float)
Crime_Weighted['Burglary'] = Crime_Weighted['Burglary'].str.replace(',', '').astype(float)
Crime_Weighted['Theft'] = Crime_Weighted['Theft'].str.replace(',', '').astype(float)

# fixing the two times representation of city Washington.
washington_double = Crime_Weighted[Crime_Weighted['City'] == 'Washington']
wash_avg = washington_double.drop(['City'], axis=1).mean()
wash_averaged = pd.DataFrame(wash_avg).transpose()
wash_averaged['City'] = 'Washington'

Crime_Weighted = Crime_Weighted[Crime_Weighted['City'] != 'Washington']

Crime_Weighted = pd.concat([Crime_Weighted, wash_averaged], ignore_index=True)


#Creating a weighted crime table
for col, weight in crime_weights.items():
    if col in Crime_Weighted.columns:
        Crime_Weighted[col] = Crime_Weighted[col].mul(weight)

Crime_Weighted['Sum_Crime'] = Crime_Weighted.iloc[:, 1:9].sum(axis=1)

percentile_50 = np.percentile(Crime_Weighted['Sum_Crime'], 50)

#Filtering the data for only the positions with the lowest crime scores.
Crime_Filtered = Crime_Weighted[Crime_Weighted['Sum_Crime'] < percentile_50]

#Creating the final table with the only relevant data to join by.
Crime_Selected = Crime_Filtered[['City', 'Sum_Crime']]      #shape (189, 3)



"""
Based on the further exploration of the data, the following parameters 
will serve the best use to find the desired startups parameter per city.
indmaj2		major industry for main job = 4,7,8,9
class = 4 5 6 7
wgtat
msafp, 
msastat = 1, 2, 4
month, year
"""
Ent_Raw = pd.read_csv("Data/Entrepreneurship/kiedata15.csv", low_memory=False)

Ent_Raw.sample(5)
Ent_Raw.shape     # (636017, 37)

Ent_Raw['se15u'].sample(5)

# Changing MSA to City name will be required, as the names 
# don't match with the MSA Names found in the Crimes table.


MSAafter_may2004 = pd.read_excel(
    'Data/Entrepreneurship/kieacodebook_v7.xlsx', sheet_name='Appendix 3', header=2
    ).iloc[1:]
MSAafter_may2004 = MSAafter_may2004[['MSA Code', 'MSA Name']]


Ent_Merged = pd.merge(Ent_Raw, MSAafter_may2004, left_on='msafp', right_on='MSA Code')

# Filtering for metropolitan-only areas
Ent_Merged = Ent_Merged[Ent_Merged['MSA Code'] != 0]
Ent_Merged = Ent_Merged[Ent_Merged['msastat'].isin([1, 2, 4])]

# Filtering for the entrepreneurs-only
Ent_Merged = Ent_Merged[Ent_Merged['class'].isin([4, 5, 6, 7])]

# Filtering for the startup-type business areas
Ent_Merged = Ent_Merged[Ent_Merged['indmaj2'].isin([4, 7, 8, 9])]


# Preparation for modyfying the 'MSA Name' to the city name format.

#finding cities in the destination table containing '-'.
CollScoreboard_Selected['CITY'].str.contains('-').value_counts() #4

# Winston-Salem, Wilkes-Barre and Hampden-Sydney found.
CollScoreboard_Selected[CollScoreboard_Selected['CITY'].str.contains('-')]

#Converting the MSA Name to the only keep the CITY name.
Ent_Merged['CITY'] = Ent_Merged[
    'MSA Name'
    ].str.strip(
        "'"
        ).str.split(
            ','
            ).str[
                0].str.split(
                    '-'
                    ).str[0]

# update the rows with Winston-Salem, Wilkes-Barre and Hampden-Sydney. 
# These are the only rows in the future join table 'CollScoreboard_Selected' 
# that contain '-' in their name, thus were previosuly erroneously modified.

rows_to_update = Ent_Merged['CITY'].isin(['Winston', 'Wilkes', 'Hampden'])

Ent_Merged.loc[rows_to_update, 'CITY'] = Ent_Merged.loc[
    rows_to_update, 'CITY'
    ].str.replace(
        'Winston', 'Wilkes-Barre'
        ).str.replace(
            'Wilkes', 'Wilkes-Barre'
            ).str.replace(
                'Hampden', 'Hampden-Sydney'
                )

#group weight scores by the city
#using 'wgtat' score as an index of entrepreneurial activity.
Ent_Merged.info()
Ent_Grouped = Ent_Merged['CITY'].value_counts().reset_index()


#include only 75th percentile
Ent_Filtered = Ent_Grouped[
    Ent_Grouped['count'] > np.percentile(Ent_Grouped['count'], 75)
    ]

#The final table of top 25% Entrepreneurial cities is ready.
Ent_Filtered = Ent_Filtered.sort_values(
    ['count'], ascending=[False]).round() #shape (56,2)



# Time to find the Good Temperature cities.

Temp_Raw = pd.read_csv(
    "Data/city_temperature.csv", low_memory=False)

#Exploring the raw data.
Temp_Raw.shape      #(2906327, 8)
Temp_Raw.info()
Temp_Raw.sample(5)

#Filtering for only the US cities.
Temp_USA = Temp_Raw[Temp_Raw['Country'].isin(['US', 'USA'])]    #(1455337, 8)
Temp_USA['City'].drop_duplicates()  # 154 unique Cities

# Groupping cities by the average temperature.
Temp_Grouped = Temp_USA.groupby('City')['AvgTemperature'].mean().reset_index()

# Filtering out the bottom 25 percentile
Temp_Filtered = Temp_Grouped[
    Temp_Grouped['AvgTemperature'] > np.percentile(
        Temp_Grouped['AvgTemperature'], 25
        )
    ]  

#The final table of the upper 75% warm cities is ready.
Temp_Filtered = Temp_Filtered.sort_values(
    ['AvgTemperature'], ascending=[False]).round() #shape  (115, 2)


# Time to join all the results into one table.
# Tables to merge: 
    # CollScoreboard_Selected,  (2937, 6)
    # Crime_Selected,           (189, 3)
    # Ent_Filtered,             (56, 2)
    # Temp_Filtered.            (115, 2)
# We use 'City' Column to merge.

#Renaming the City column to match CITY to avoid duplicate columns.
Crime_Selected = Crime_Selected.rename(columns={'City': 'CITY'})
Temp_Filtered = Temp_Filtered.rename(columns={'City': 'CITY'})

Ent_Filtered = Ent_Filtered.rename(columns={'count': 'Entr_count'})


CollScoreboard_ToMerge = CollScoreboard_Selected[[
    'INSTNM', 'CITY', 'SATMT25']].drop_duplicates()

# First merge of first two tables.
Merged_All = pd.merge(
    CollScoreboard_ToMerge, 
    Crime_Selected, 
    on='CITY', 
    how='inner')    # (670, 4)

# Merging Entrepreuerial acitivity final table.
Merged_All = pd.merge(
    Merged_All, 
    Ent_Filtered, 
    on='CITY', 
    how='inner')    # (271, 5)

# Finally, Merging the Temperature data table.
Merged_All = pd.merge(
    Merged_All, 
    Temp_Filtered, 
    on='CITY', 
    how='inner')    # (217, 6)


# Engineering the final parameter for the final sorting. 

# The numerical value columns that will be used are : 
#   Sum_Crime, 
#   Entr_count, 
#   AvgTemperature
# First, the normalisation of the results will be useful. 
# We will use Min-Max Normalisation method to keep the values positive.

#Getting min and max values of the columns to normalise.
minV_Crime, maxV_Crime = Merged_All['Sum_Crime'].min(), Merged_All['Sum_Crime'].max()

minV_Ent, maxV_Ent = Merged_All['Entr_count'].min(), Merged_All['Entr_count'].max()

minV_Temp, maxV_Temp = Merged_All['AvgTemperature'].min(), Merged_All['AvgTemperature'].max()

# Conducting the normalisation into the new columns.
Merged_All['Crime_Norm'] = ((Merged_All['Sum_Crime'] - minV_Crime) / (maxV_Crime - minV_Crime)) +0.3
Merged_All['Entr_Norm'] = ((Merged_All['Entr_count'] - minV_Ent) / (maxV_Ent - minV_Ent)) +0.3
Merged_All['Temp_Norm'] = ((Merged_All['AvgTemperature'] - minV_Temp) / (maxV_Temp - minV_Temp)) +0.3

# Normalised values range from 0.3 to 1.3 to aviod the division problem and 
# to give points to the min values as well.
Merged_All.describe().round(3)


# Creating the engineered parameter. 
"""
The parameter assumes that:
a.) the Entrepreneurial activity would be the most important 
factor for Maria (multiplied by 4). 
b.) It promotes or degrades the score based on the crime, and 
c.) adds a small bonus for the good weather.
"""
Merged_All['Maria_Uni_Score'] = (
    Merged_All['Entr_Norm']*5 + Merged_All['Temp_Norm'] 
    ) / (Merged_All['Crime_Norm'] +0.7)
                                 
Merged_All = Merged_All.sort_values(
    ['Maria_Uni_Score', 'SATMT25'], ascending=[False, False])

Merged_All[[
    'INSTNM', 'CITY', 'Maria_Uni_Score', 'SATMT25', 
    'Entr_Norm', 'Temp_Norm', 'Crime_Norm'
    ]].head(30)


