import imaplib
import email
import re
from typing import List
import base64
import yaml
import pandas as pd
import os
from datetime import datetime

print(f'Time of run: {datetime.now()}')

# print("Current Working Directory:", os.getcwd())

# 0.1. Creation of lists for expense categories.
supermarkets_list = ['super', 'xtra', 'rey', 'pricesmart', 'metro', 'riba']
eating_out_list = {'siete granos' 'the raj', 'ay mi negra', 'casa santa', 'anti burger', 'tacos la neta', 'vitali',
                   'segundo muelle', 'souvlaki gr', 'golden unicorn', 'subway', 'esa flaca rica', 'food', 'sushi',
                   'tea', 'pizza', 'rest', 'pizzeria', 'tip', 'mo mo', 'ramen', 'rock and folk', 'bistro', 'coffee',
                   'cafe unido', 'xing fu tang',
                   'athanasiou', 'taphouse', 'wahaka', 'poke', 'popeyes', 'mcdonalds', 'taco bell', 'restaurant',
                   'bakery', 'patisserie', 'la rana dorada', 'legitima', 'brew'}
department_stores_list = ['bershka', 'old navy', 'bananarepublic', 'hm', 'zara', 'steven']
utilities_list = ['est multiplaza fideico', 'cwp', 'tigo', 'liberty', 'sura']
fuel_list = ['estacion', 'delta', 'texaco', 'puma']
subscriptions_list = ['apple.com/bill', 'spotify']
entertainment_list = ['burke bikes', 'cinepolis']
random_purchases_list = ['innovacion', 'relojin', 'amzn', 'apple store']
health = ['power club', 'orto']

# 0.2. Creation of budget dictionary and dataframe transformation
budget_2024 = {
    'Category':
        ['Internet', 'Electricity', 'Data', 'Car loan', 'Fuel', 'Loan 1', 'Loan 2', 'Subscriptions', 'Savings',
         'Groceries', 'Eating Out', 'Credit cards', 'Rent', 'Pets', 'Clothes', 'Entertainment'],
    'Amount': [34.74, 50, 22.42, 220.42, 50, 188, 92.31, 12, 200, 150, 100, 300, 500, 30, 50, 30]
}

budget_2024_df = pd.DataFrame(budget_2024)

category_mapping = {
    'Internet': 'Utilities',
    'Electricity': 'Utilities',
    'Data': 'Utilities',
    # Add more mappings as needed
}

# Apply the mapping to the 'Category' column
budget_2024_df['Category'] = budget_2024_df['Category'].map(category_mapping).fillna(budget_2024_df['Category'])

# Group by the new 'Category' and sum the 'Amount'
new_budget_df = budget_2024_df.groupby('Category', as_index=False)['Amount'].sum()

print(new_budget_df)

# Block 1.1. Email connection and loading of credentials
# print("opening yaml for credentials")
with open('/Users/victordona/Python/budget_automation_project/credentials.yml') as f:
    content = f.read()

my_credentials = yaml.load(content, Loader=yaml.FullLoader)
user, password = my_credentials["user"], my_credentials["password"]

imap_url = 'imap.gmail.com'
my_mail = imaplib.IMAP4_SSL(imap_url)
my_mail.login(user, password)

# The next three commented lines were used in the context of the previous code to extract mails from only one sender.
# I have migrated to the next model to include several senders at the same time.
# my_mail.select('inbox')
# key = 'FROM'
# value = 'credomatic-informa@pa.credomatic.com'

# Block 1.2. Selection of folder and addresses to receive messages from
my_mail.select('inbox')

# Selection of emails addresses to extract messages from
email_addresses_to_extract = ['credomatic-informa@pa.credomatic.com', 'notificaciones@pa.scotiabank.com']

# Block 1.3. Search of each email addresses
search_results_list = []
for email_address in email_addresses_to_extract:
    status, messages = my_mail.uid('search', None, f'FROM {email_address}')
    # print(f'Search status for {email_address}: {status}')
    # print(f'Messages for {email_address}: {messages}')
    if status == 'OK':
        search_results_list.extend(messages[0].split())

# Deduplicate the results if needed
search_results = list(set(search_results_list))
# print(search_results_list)
print(f'You have {len(search_results)} emails from these senders')
# print(email_addresses_to_extract[:])

bac_count = 0
scotia_count = 0
indexer = 0
other_email_cnt = 0
error_decoding_body_cnt = 0
unexpected_error_cnt = 0
cc_identifier = [4446, 2852]
cc_identifier_as_string = [str(num) for num in cc_identifier]
# print(f'Bac Count = {bac_count}')
# print(f'Scotia Count = {scotia_count}')
# print(f'Other Scotia Emails Count = {other_email_cnt}')

expenses_data = []

# Block 2.1. Data extraction from emails
for message in search_results:
    typ, msg_data = my_mail.uid('fetch', message, '(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)] BODY.PEEK[])')

    if typ == 'OK' and msg_data:
        email_message = email.message_from_bytes(msg_data[0][1])

        # Extract the sender's information
        from_address = email_message.get("From", "Unknown Sender")
        subject_header = email_message.get("Subject", "No Subject")

        # Decode subject using email.header.decode_header
        subject, encoding = email.header.decode_header(subject_header)[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or 'utf-8', errors='replace')

        indexer += 1
        # print(indexer)
        # print(f'From: {from_address}')
        # print(f'Subject: {subject}')

        # Block 2.2. Email extraction for BAC.
        # Definition of whether multipart or not as criterion 1 to know if it is from BAC or Scotiabank.
        if email_message.is_multipart() and 'credomatic-informa@pa.credomatic.com' in from_address:
            bac_count += 1
            # print('I am multipart')
            # print(f'Bac Count = {bac_count}')
            # print(f'Scotia Count = {scotia_count}')
            # print(f'Other email count: {other_email_cnt}')
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', 'replace')
                        # print('Printing body for BAC email')
                        # print(body)
                        bac_store_name_pattern = r'Monto\s*\r\n\r\n(.+)'
                        bac_usd_amount_pattern = r'USD\s*(.+)'
                        bac_date_pattern = r'hora\s*\r\n\r\n(.+)'

                        # Search for the pattern in the text
                        bac_store_name_match = re.search(bac_store_name_pattern, body)
                        bac_usd_amount_match = re.search(bac_usd_amount_pattern, body)
                        bac_transaction_date_match = re.search(bac_date_pattern, body)

                        # Check if there is a match and print the result
                        if bac_store_name_match and bac_usd_amount_match and bac_transaction_date_match:
                            store_name = bac_store_name_match.group(1).strip()
                            bac_usd_amount = bac_usd_amount_match.group(1).strip()
                            bac_transaction_date = datetime.strptime(bac_transaction_date_match.group(1).strip(),
                                                                     '%Y/%m/%d-%H:%M:%S')
                            # print(f'Store Name: {bac_store_name}')
                            # print(f'USD Amount: {bac_usd_amount}')
                            # print(f'Transaction Date: {bac_transaction_date.strftime("%Y-%m-%d")}')
                            expenses_data.append({'Store': store_name, 'USD Amount': bac_usd_amount,
                                                  'Transaction Date': bac_transaction_date.strftime("%Y-%m-%d")})
                        else:
                            # print(f'Unmatched BAC email - Subject: {subject}, Body: {body}')
                            pass
                        # print('Hola, soy de BAC, ciao.\n---')
                        # print(f'Body: {body}')
                    except UnicodeDecodeError as e:
                        print(f"Error decoding body: {e}")
                    break
        # Block 2.3. Email extraction for Scotiabank.
        elif ('notificaciones@pa.scotiabank.com' in from_address
              and re.search(r'autorización de débito en tarjeta principal', subject, re.IGNORECASE)):

            # print('I am NOT multipart')
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', 'replace')
                desired_text_pattern = re.compile(
                    fr'Gracias por su compra/retiro con su tarjeta de crédito titular de Scotiabank terminada en '
                    fr'{"|".join(cc_identifier_as_string)}')

                if desired_text_pattern.search(body):
                    # print(f'Printing body for Scotiabank email:\n {body}')
                    scotiabank_usd_amount_pattern = re.compile(r'por USD ([\d.,]+)')
                    scotiabank_store_name_pattern = re.compile('por USD [\d.,]+ en ([A-Z\s]+)')
                    scotiabank_date_pattern = re.compile(r'\b(\d{2}/\d{2}/\d{4})\b')

                    scotiabank_usd_amount_match = scotiabank_usd_amount_pattern.search(body)
                    scotiabank_store_name_match = scotiabank_store_name_pattern.search(body)
                    scotiabank_transaction_date_match = scotiabank_date_pattern.search(body)
                    if (scotiabank_usd_amount_match
                            and scotiabank_store_name_match
                            and scotiabank_transaction_date_match):
                        scotiabank_usd_amount = scotiabank_usd_amount_match.group(1)
                        store_name = scotiabank_store_name_match.group(1)
                        scotiabank_transaction_date = datetime.strptime(scotiabank_transaction_date_match.group(1),
                                                                        '%d/%m/%Y')
                        # print(f'Store Name: {scotiabank_store_name}')
                        # print(f'USD Amount: {scotiabank_usd_amount}')
                        # print(f'Transaction Date: {scotiabank_transaction_date.strftime("%Y-%m-%d")}')
                        expenses_data.append({'Store': store_name, 'USD Amount': scotiabank_usd_amount,
                                              'Transaction Date': scotiabank_transaction_date.strftime("%Y-%m-%d")})
                        scotia_count += 1
                    # print(f'Bac Count = {bac_count}')
                    # print(f'Scotia Count = {scotia_count}')
                    # print(f'Other email count: {other_email_cnt}')
                    else:
                        # print(f'Not a match - Subject: {subject}, Body: {body}')

                        # Try to extract information directly from the unmatched body
                        scotiabank_info_pattern = re.compile(
                            r'tarjeta de crédito titular de Scotiabank terminada en (\d{4}) por USD ([\d.,]+) en (\S+ \S+ \S+ \S+ \S+ \S+) el día (\d{2}/\d{2}/\d{4})'
                        )

                        scotiabank_info_match = scotiabank_info_pattern.search(body)

                        if scotiabank_info_match:
                            scotiabank_last_digits = scotiabank_info_match.group(1)
                            scotiabank_usd_amount = scotiabank_info_match.group(2)
                            scotiabank_store_name = scotiabank_info_match.group(3)
                            scotiabank_transaction_date = datetime.strptime(scotiabank_info_match.group(4), '%d/%m/%Y')

                            # print(f'Last Digits: {scotiabank_last_digits}')
                            # print(f'Store Name: {scotiabank_store_name}')
                            # print(f'USD Amount: {scotiabank_usd_amount}')
                            # print(f'Transaction Date: {scotiabank_transaction_date.strftime("%Y-%m-%d")}')
                else:
                    print('Not a match')
                    print(f'Body does not match the desired text: {body}')
                    other_email_cnt += 1
                    print(f'Bac Count = {bac_count}')
                    print(f'Scotia Count = {scotia_count}')
                    print(f'Other email count: {other_email_cnt}\n--')

            except UnicodeDecodeError as e:
                print(f"Error decoding body: {e}")
                error_decoding_body_cnt += 1
            except Exception as e:
                print(f"Unexpected error: {e}\n---")
                unexpected_error_cnt += 1
    else:
        print(f'Fuck it, I am unable to fetch message {message}')

# Block 3.1 Data recount, analysis and ordering by latest transaction date.
expenses_data_df = pd.DataFrame(expenses_data)
expenses_data_df['Transaction Date'] = pd.to_datetime(expenses_data_df['Transaction Date'])
expenses_data_df.sort_values(by='Transaction Date', inplace=True, ascending=False)


# print(expenses_data_df)
# print(expenses_data_df.dtypes)

# print(f'Bac Count = {bac_count}')
# print(f'Scotia Count = {scotia_count}')
# print(f'Other Scotia Emails Count = {other_email_cnt}')
# print(f'Error Decoding Body Count = {error_decoding_body_cnt}')
# print(f'Unexpected Error Count = {unexpected_error_cnt}')

# for sender in email_addresses_to_extract:
#     if sender == 'credomatic-informa@pa.credomatic.com':
#         print('It is I')
#     else:
#         print('It is not I')

# print(budget_2024_df)

# Block 3.2. Defining the categorize_expense
def categorize_expense(store_name):
    store_name = store_name.lower()

    # Check for supermarkets
    for keyword in supermarkets_list:
        if keyword in store_name:
            return 'Groceries'

    # Check for eating out
    for keyword in eating_out_list:
        if keyword in store_name:
            return 'Eating Out'

    # Check for department stores
    for keyword in department_stores_list:
        if keyword in store_name:
            return 'Clothes'

    # Check for utilities
    for keyword in utilities_list:
        if keyword in store_name:
            return 'Utilities'

    # Check for utilities
    for keyword in fuel_list:
        if keyword in store_name:
            return 'Fuel'

    # Check for subscriptions
    for keyword in subscriptions_list:
        if keyword in store_name:
            return 'Subscriptions'

    # Check for entertainment
    for keyword in entertainment_list:
        if keyword in store_name:
            return 'Entertainment'

    # Check for random purchases
    for keyword in random_purchases_list:
        if keyword in store_name:
            return 'Random purchases'

    # Check for health related purchases
    for keyword in health:
        if keyword in store_name:
            return 'Health'

    # Add more categories and checks as needed

    # If no match is found, return 'Uncategorized'
    return 'Uncategorized'


# Block 3.3. Adding the 'Category' column and applying the function categorize_expense
expenses_data_df['Category'] = expenses_data_df['Store'].apply(categorize_expense)

# Block 4. Filtering
# Block 4.1. Creation of today dynamic date reference
today = datetime.now().date()
# current_month = pd.Period(today.strftime('%Y-%m'))
current_month = today.strftime('%Y-%m')
# current_month2 = current_month + 1

# Printing all expenses
# print(expenses_data_df.to_string())

# Block 4.2. Filtering for current month expenses
# Printing current month expenses
current_month_expenses_df = expenses_data_df[
    expenses_data_df['Transaction Date'].dt.strftime('%Y-%m').str.startswith(current_month)].copy()
print(f'Printing expenses for {current_month}')
print(current_month_expenses_df.head(5))

# Block 4.3. Grouping current month expenses
current_month_expenses_df.loc[:, 'Transaction Date'] = pd.to_datetime(current_month_expenses_df['Transaction Date'])

current_month_expenses_df.loc[:, 'Transaction Month'] = current_month_expenses_df['Transaction Date'].dt.to_period(
    'M').copy()

# Convert 'USD Amount' to numeric, coercing errors to NaN for non-numeric values
current_month_expenses_df.loc[:, 'USD Amount'] = pd.to_numeric(current_month_expenses_df['USD Amount'], errors='coerce')

# Drop rows with NaN values in the 'USD Amount' column
current_month_expenses_df = current_month_expenses_df.dropna(subset=['USD Amount'])

# Group and sum the 'USD Amount' based on 'Category' and 'Transaction Month'
current_month_expenses_df = current_month_expenses_df.groupby(['Category', 'Transaction Month'], as_index=False)[
    'USD Amount'].sum()

# Print the result
print(f'Printing Monthly Aggregations for {current_month}')
print(current_month_expenses_df)

uncategorized_expenses = expenses_data_df[expenses_data_df['Category'] == 'Uncategorized']
# print(uncategorized_expenses.to_string())

remaining_balance_list = []

# Block 5.1. Subtracting current month expenses from budget to obtain the months remaining balance
for category in new_budget_df['Category']:
    if category in current_month_expenses_df['Category'].values:
        remaining_balance = (new_budget_df.loc[new_budget_df['Category'] == category, 'Amount'].values[0] -
                            current_month_expenses_df.loc[
                                current_month_expenses_df['Category'] == category, 'USD Amount'].values[0])
        remaining_balance_list.append({'Remaining Balance In': category, 'Amount': f'${remaining_balance:.2f}'})
        # print(f'Remaining balance for {category}: ${remaining_balance:.2f}')

        if remaining_balance < 0:
            pass
            # print(f"Warning: {category} budget exceeded!")
    else:
        pass
        # print(f'No expenses recorded for {category}')

remaining_balance_df = pd.DataFrame(remaining_balance_list)
print(remaining_balance_df)
