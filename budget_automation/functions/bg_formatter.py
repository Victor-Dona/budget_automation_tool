import pandas as pd # type: ignore
from datetime import date
print(pd.__version__)

today = date.today()

def bg_df_formatter(acc_extension):

    # Declare input file path
    input_file = f'./bg_data/{acc_extension}-{today}.xlsx'

    # Read Excel file
    bg_df = pd.read_excel(input_file, skiprows=7, header=0)

    # ARRANGEMENT AND FORMATTING
    # Select desired columns 
    bg_df = bg_df[['Fecha', 'Descripción', 'Débito', 'Crédito']] 

    # Rename columns
    bg_df.columns = ['date', 'description', 'debit', 'credit']

    # Add debit and credit into 'amount'
    bg_df['amount'] = bg_df['debit'].fillna(0)+bg_df['credit'].fillna(0)

    # Drop debit and credit
    bg_df = bg_df[['date', 'description', 'amount']]


    bg_df['category'] = 'uncategorized'

    bg_df = bg_df[['date', 'description', 'category', 'amount']]

    # Transform datetime to date
    bg_df['date'] = bg_df['date'].dt.date

    print(f'Transformation complete for {acc_extension}')
    #print(bg_df.head(5))
    #bg_df.info()

    return bg_df


# Calling function for both acounts
bg_df1 = bg_df_formatter(acc_extension='3286')
bg_df2 = bg_df_formatter(acc_extension='5620')

# Concatenate DataFrames 
bg_dfs = pd.concat([bg_df1, bg_df2], ignore_index=True)

# Order by date descending
bg_dfs = bg_dfs.sort_values(by='date')

# Reset index to maintain an index sequential order
bg_dfs = bg_dfs.reset_index(drop=True)

print(bg_dfs.head(10))


# Export BG expenses with today's date for track keeping later on
bg_epenses = bg_dfs.to_excel(f'./bg_data/bg_expenses_{today}.xlsx')
