import imaplib
import email
import re
import yaml
import pandas as pd
from datetime import datetime

print("opening yaml for credentials")
with open('venv/credentials.yml') as f:
    content = f.read()

my_credentials = yaml.load(content, Loader=yaml.FullLoader)
user, password = my_credentials["user"], my_credentials["password"]

imap_url = 'imap.gmail.com'
my_mail = imaplib.IMAP4_SSL(imap_url)
my_mail.login(user, password)

my_mail.select('inbox')
key = 'FROM'
value = 'credomatic-informa@pa.credomatic.com'

_, data = my_mail.search(None, key, value)
mail_id_list = data[0].split()

# Creation of necessary lists
msgs = []
results = []  # List to store results

# Creation of category lists
supermarkets_list = ['super', 'xtra', 'rey', 'pricesmart', 'metro', 'riba']
eating_out_list = ['rest', 'pizzeria', 'tip', 'mo mo', 'ramen', 'rock and folk', 'bistro', 'coffee', 'cafe unido', 'xing fu tang',
                   'athanasiou', 'taphouse', 'wahaka', 'poke', 'popeyes', 'mcdonalds', 'taco bell', 'restaurant',
                   'bakery', 'patisserie', 'la rana dorada', 'legitima', 'brew']
department_stores_list = ['hm', 'zara', 'steven']
utilities_list = ['estacion', 'delta', 'texaco', 'cwp', 'tigo', 'liberty', 'sura']
subscriptions_list = ['apple', 'spotify']
entertainment_list = ['cinepolis']
random_purchases_list = ['innovacion', 'relojin']
health = ['power club', 'orto']

# Creating dictionary with budget values per category
budget_2024 = {
    'Categories':
        ['Internet', 'Electricity', 'Data', 'Car loan', 'Car gas', 'Loan 1', 'Loan 2', 'Subscriptions', 'Profuturo',
         'Groceries', 'Eating Out', 'Credit cards', 'Rent', 'Buns and plants'],
    'Amount': [34.74, 50, 22.42, 220.42, 50, 188, 92.31, 12, 30, 170, 25, 300, 500, 30]
}

print('Printing budget for the month')
budget_2024_df = pd.DataFrame(budget_2024)
print(budget_2024_df)

# Crossing the list expenses with the budgets dictionary to assign a budget to each category
print("Going through email loop to apply regex pattern")
for num in mail_id_list:
    typ, data = my_mail.fetch(num, '(RFC822)')
    msgs.append(data)

print('part in msg')
for msg in msgs[::-1]:
    for response_part in msg:
        if type(response_part) is tuple:
            my_msg = email.message_from_bytes(response_part[1])
            for part in my_msg.walk():
                if part.get_content_type() == 'text/plain':
                    content = part.get_payload(decode=True).decode('latin-1').replace('=20', ' ').replace('=09', '\t')
                    # print(content)
                    # print(repr(content))
                    # Define regex pattern
                    pattern_comercio = r'Monto\s*\r\n\r\n(.+)'
                    pattern_USD = r'USD\s*(.+)'
                    pattern_date = r'hora\s*\r\n\r\n(.+)'

                    # Search for the pattern in the text
                    match_comercio = re.search(pattern_comercio, content)
                    match_monto = re.search(pattern_USD, content)
                    match_date = re.search(pattern_date, content)

                    # Check if there is a match and print the result
                    if match_comercio and match_monto and match_date:
                        comercio = match_comercio.group(1).strip()
                        monto = match_monto.group(1).strip()
                        date = match_date.group(1).strip()
                        # print('Comercio:', comercio)
                        # print('Monto:', monto)
                        # print('Fecha y hora:', date)
                        results.append({'Comercio': comercio, 'Monto': monto, 'Fecha y hora': date})
                    else:
                        print('No match found for comercio, monto')

                    # print("---")

df = pd.DataFrame(results)

# Assuming your DataFrame is named 'expenses_df'
df['Category'] = 'Uncategorized'

print("Categorizing expenses")
def categorize_expense(comercio):
    comercio_lower = comercio.lower()

    # Check for supermarkets
    for keyword in supermarkets_list:
        if keyword in comercio_lower:
            return 'Supermarkets'

    # Check for eating out
    for keyword in eating_out_list:
        if keyword in comercio_lower:
            return 'Eating Out'

    # Check for department stores
    for keyword in department_stores_list:
        if keyword in comercio_lower:
            return 'Department Stores'

    # Check for utilities
    for keyword in utilities_list:
        if keyword in comercio_lower:
            return 'Utilities'

    # Check for subscriptions
    for keyword in subscriptions_list:
        if keyword in comercio_lower:
            return 'Subscriptions'

    # Check for entertainment
    for keyword in entertainment_list:
        if keyword in comercio_lower:
            return 'Entertainment'

    # Check for random purchases
    for keyword in random_purchases_list:
        if keyword in comercio_lower:
            return 'Random purchases'

    # Check for health related purchases
    for keyword in health:
        if keyword in comercio_lower:
            return 'Health'

    # Add more categories and checks as needed

    # If no match is found, return 'Uncategorized'
    return 'Uncategorized'


df['Category'] = df['Comercio'].apply(categorize_expense)

uncategorized_rows = df['Category'] == 'Uncategorized'
# print(df[uncategorized_rows].to_string())
# print(df.to_string())

# Up to this point, we have successfully added the category column and categorized each row accordingly

print("Date column formatting")
# Convert 'Fecha y hora' column to datetime format
df['Fecha y hora'] = pd.to_datetime(df['Fecha y hora'])

# Extract month and week columns
df['Date'] = df['Fecha y hora'].dt.to_period('M')

# Convert 'Monto' to numeric
df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce')

print(df.head())
# Group by 'Category', 'Month', and 'Week' and sum the 'Monto'
expenses_df = df.groupby(['Category', 'Date'], as_index=False)['Monto'].sum()

# Print the grouped data for expenses with no date constrictions
# print("Printing all expenses")
# print(expenses_df)

# Filter expenses for the current month
today = datetime.now().date()
# Extract month and year
month_and_year = today.strftime('%Y-%m')
# print(f"Month and Year: {month_and_year}")
current_month = pd.Period(month_and_year)  # Replace with your current month
expenses_df_current_month = expenses_df[expenses_df['Date'] == current_month]

# Print the grouped data for the current month
print("Printing expenses from current month")
print(expenses_df_current_month)

remaining_budgets_list = []

print("Subtracting budget-expenses for the current month")
for category in expenses_df['Category'].unique():
    if category in budget_2024_df['Categories'].values:
        for date in expenses_df['Date'].unique():
            # Filter expenses for the current category and month
            filtered_expenses = expenses_df[(expenses_df['Category'] == category) & (expenses_df['Date'] == date)]

            # Calculate remaining budget for the current category and month
            remaining_budget = budget_2024_df.loc[budget_2024_df['Categories'] == category, 'Amount'].iloc[0] - \
                               filtered_expenses['Monto'].sum()

            # Round the remaining budget to a desired precision
            remaining_budget = round(remaining_budget, 2)

            print(f"Remaining Budget for {category} in {date}: ${remaining_budget}")

            # Append the result to the remaining_budgets_list
            remaining_budgets_list.append({'Category': category, 'Date': date, 'Remaining Budget': remaining_budget})
    else:
        print(f"No budget information found for {category}")

# Create a DataFrame from the remaining_budgets_list
remaining_budgets_df = pd.DataFrame(remaining_budgets_list)
filtered_remaining_budgets_df = remaining_budgets_df.loc[remaining_budgets_df['Date'] == str(current_month), ['Category', 'Date', 'Remaining Budget']]

# Print the DataFrame with remaining budgets
print("Remaining Budgets DataFrame:")
print(remaining_budgets_df)
print("Filtered Remaining Budgets DataFrame:")
print(filtered_remaining_budgets_df)