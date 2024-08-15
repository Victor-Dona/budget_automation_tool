import pandas as pd
from datetime import date
from functions.bg_formatter import bg_df_formatter
from functions.bac_formatter import bac_df_formatter
from functions.categories import categorize

today = date.today()

# Handling the BG file formats with the function
# Calling function for both acounts
bg_df1 = bg_df_formatter(acc_extension='3286')
bg_df2 = bg_df_formatter(acc_extension='5620')

# Concatenate DataFrames 
bg_expenses = pd.concat([bg_df1, bg_df2], ignore_index=True)

# Handling the BAC file formats with the function
bac_df1 = bac_df_formatter(bac_file_date='2023_11')
bac_df2 = bac_df_formatter(bac_file_date='2023_12')
bac_df3 = bac_df_formatter(bac_file_date='2024_01')
bac_df4 = bac_df_formatter(bac_file_date='2024_02')
bac_df5 = bac_df_formatter(bac_file_date='2024_03')
bac_df6 = bac_df_formatter(bac_file_date='2024_04')
bac_df7 = bac_df_formatter(bac_file_date='2024_05')
bac_df8 = bac_df_formatter(bac_file_date='2024_06')
bac_df9 = bac_df_formatter(bac_file_date='2024_07')
bac_df10 = bac_df_formatter(bac_file_date='2024_08')
bac_df11 = bac_df_formatter(bac_file_date='2024_09')
bac_df12 = bac_df_formatter(bac_file_date='2024_10')

bac_expenses = pd.concat([bac_df1, bac_df2, bac_df3, bac_df4, bac_df5, bac_df6, bac_df7, bac_df8, bac_df9], ignore_index=True)

unified_expenses = pd.concat([bg_expenses, bac_expenses], ignore_index=True)

# Order unified expenses by date descending
unified_expenses = unified_expenses.sort_values(by='date')

# Reset index to maintain an index sequential order
unified_expenses = unified_expenses.reset_index(drop=True)

# Apply categorization functions
unified_expenses['category'] = unified_expenses['description'].apply(categorize)

# Extract uncategorized rows 
uncategorized_expenses = unified_expenses[unified_expenses['category'] == 'Uncategorized']

# Count values for each category
category_counts = unified_expenses['category'].value_counts()

# Print results
print(category_counts)
print(uncategorized_expenses)
#print(unified_expenses)

# Export uncategorized expenses
uncategorized_expenses = uncategorized_expenses.to_excel(f'./uncategorized_expenses_{today}.xlsx')

unified_expenses = unified_expenses.to_excel(f'./unified_expenses_{today}.xlsx')
