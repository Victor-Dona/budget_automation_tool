import pandas as pd
from datetime import date

def bac_df_formatter(bac_file_date):
    try:
        bac_df = pd.read_csv(f'./{bac_file_date}_Últimos_movimientos.csv', skiprows=[1, 2, 3, 4])

        # Rename columns
        bac_df.columns = ['date', 'description', 'empty1', 'amount', 'empty2', 'empty3', 'empty4', 'empty5', 'empty6']

        # Select desired columns
        bac_df = bac_df[['date', 'description', 'amount']]

        # Transform amount to numeric to multiply by -1
        bac_df['amount'] = pd.to_numeric(bac_df['amount'], errors='coerce')
        bac_df['amount'] = bac_df['amount'] * (-1.00)

        # Transform to datetime to filter not wanted rows by NaN and amount of 0
        bac_df['date'] = pd.to_datetime(bac_df['date'], format='%d/%m/%Y', errors='coerce')
        bac_df = bac_df[~((bac_df['date'].isna()) & (bac_df['amount'].isna() | (bac_df['amount'] == 0)))]

        # Strip any spaces in the 0.00 str to filter the row
        bac_df['description'] = bac_df['description'].astype(str).str.strip()
        bac_df = bac_df[bac_df['description'] != '0.00' ]

        # Transform datetime to date
        bac_df['date'] = bac_df['date'].dt.date

        # Forward fill missing dates
        bac_df['date'] = bac_df['date'].fillna(method='ffill')

        bac_df['category'] = 'uncategorized'

        bac_df = bac_df[['date', 'description', 'category', 'amount']]

        print(f'Transformation complete for {bac_file_date}')
        #print(bac_df.head())
        return bac_df
    
    except FileNotFoundError:
        pass
        #print(f'File not found: {bac_file_date}')

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

bac_dfs = pd.concat([bac_df1, bac_df2, bac_df3, bac_df4, bac_df5, bac_df6, bac_df7, bac_df8, bac_df9], ignore_index=True)

# Order by date descending
#bac_dfs = bac_dfs.sort_values(by='date')

# Reset index to maintain an index sequential order
#bac_dfs = bac_dfs.reset_index(drop=True)
print(bac_dfs)

today = date.today()

# Export BG expenses with today's date for track keeping later on
bac_expenses = bac_dfs.to_excel(f'./bac_expenses_{today}.xlsx')
