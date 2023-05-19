import pandas as pd

# Sample dataset in wide format
data = {
    'ID': [1, 2, 3],
    'Name': ['John', 'Alice', 'Bob'],
    'Age': [25, 30, 35],
    'Score1': [80, 90, 75],
    'Score2': [85, 95, 70]
}

df_wide = pd.DataFrame(data)
print("Original DataFrame (Wide Format):\n")
print(df_wide)

# Data Melting (Unpivoting)
df_melted = pd.melt(df_wide, id_vars=['ID', 'Name', 'Age'], var_name='Variable', value_name='Value')
print("\nMelted DataFrame:\n")
print(df_melted)

# Data Casting (Pivoting)
df_casted = df_melted.pivot(index=['ID', 'Name', 'Age'], columns='Variable', values='Value').reset_index()
print("\nCasted DataFrame (Wide Format):\n")
print(df_casted)
