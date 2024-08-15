import imaplib
import email
import yaml
import re
from datetime import datetime, date
import pandas as pd
from functions.categories import categorize
from typing import List


# Load credentials
with open('credentials.yml') as f:
    my_credentials = yaml.load(f, Loader=yaml.FullLoader)
user, password = my_credentials["user"], my_credentials["password"]

imap_url = 'imap.gmail.com'
my_mail = imaplib.IMAP4_SSL(imap_url)
my_mail.login(user, password)

# Select folder and addresses to extract messages from
my_mail.select('inbox')
email_addresses_to_extract = ['credomatic-informa@pa.credomatic.com', 'notificaciones@pa.scotiabank.com', 'notificaciones@yappy.com.pa']

# Search each email address
search_results_list = []
for email_address in email_addresses_to_extract:
    status, messages = my_mail.uid('search', None, f'FROM {email_address}')
    if status == 'OK':
        search_results_list.extend(messages[0].split())
search_results = list(set(search_results_list))
print(f'You have {len(search_results)} emails from these senders')

# Prepare a list to store email data
email_data = []
expenses_data = []

# Process emails
for email_uid in search_results:
    typ, msg_data = my_mail.uid('fetch', email_uid, '(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)] BODY.PEEK[])')

    if typ == 'OK' and msg_data:
        email_message = email.message_from_bytes(msg_data[0][1])

        from_address = email_message.get("From", "Unknown Sender")
        subject_header = email_message.get("Subject", "No Subject")
        date_header = email_message.get("Date", "No Date")

        subject, encoding = email.header.decode_header(subject_header)[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or 'utf-8', errors='replace')

        if email_message.is_multipart() and 'credomatic-informa@pa.credomatic.com' in from_address:
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', 'replace')
                        bac_store_name_pattern = r'Monto\s*\r\n\r\n(.+)'
                        bac_usd_amount_pattern = r'USD\s*(.+)'
                        bac_date_pattern = r'hora\s*\r\n\r\n(.+)'

                        bac_store_name_match = re.search(bac_store_name_pattern, body)
                        bac_usd_amount_match = re.search(bac_usd_amount_pattern, body)
                        bac_transaction_date_match = re.search(bac_date_pattern, body)

                        if bac_store_name_match and bac_usd_amount_match and bac_transaction_date_match:
                            store_name = bac_store_name_match.group(1).strip()
                            bac_usd_amount = bac_usd_amount_match.group(1).strip()
                            bac_transaction_date = datetime.strptime(bac_transaction_date_match.group(1).strip(), '%Y/%m/%d-%H:%M:%S')
                            expenses_data.append({'Store': store_name, 'USD Amount': bac_usd_amount, 'Transaction Date': bac_transaction_date.strftime("%Y-%m-%d")})
                    except UnicodeDecodeError as e:
                        print(f"Error decoding body: {e}")
                    break

        elif 'notificaciones@pa.scotiabank.com' in from_address and re.search(r'autorización de débito en tarjeta principal', subject, re.IGNORECASE):
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', 'replace')
                scotiabank_usd_amount_pattern = re.compile(r'por USD ([\d.,]+)')
                scotiabank_store_name_pattern = re.compile(r'por USD [\d.,]+ en ([A-Z\s]+)')
                scotiabank_date_pattern = re.compile(r'\b(\d{2}/\d{2}/\d{4})\b')

                scotiabank_usd_amount_match = scotiabank_usd_amount_pattern.search(body)
                scotiabank_store_name_match = scotiabank_store_name_pattern.search(body)
                scotiabank_transaction_date_match = scotiabank_date_pattern.search(body)

                if scotiabank_usd_amount_match and scotiabank_store_name_match and scotiabank_transaction_date_match:
                    scotiabank_usd_amount = scotiabank_usd_amount_match.group(1)
                    store_name = scotiabank_store_name_match.group(1)
                    scotiabank_transaction_date = datetime.strptime(scotiabank_transaction_date_match.group(1), '%d/%m/%Y')

                    expenses_data.append({'Store': store_name, 'USD Amount': scotiabank_usd_amount, 'Transaction Date': scotiabank_transaction_date.strftime("%Y-%m-%d")})
            except UnicodeDecodeError as e:
                print(f"Error decoding body: {e}")

# Create DataFrame from expenses data
df = pd.DataFrame(expenses_data)

df['Category'] = df['Store'].apply(categorize)

### OLD FUNCTION. DO NOT DELETE JUST YET ###
# # Function to categorize expenses
# def categorize_expense(store_name: str) -> str:
#     store_name_lower = store_name.lower()
#     for keyword, category in keyword_to_category.items():
#         if keyword.lower() in store_name_lower:
#             return category
#     return 'Other Expenses'

# # Apply categorization
# df['Category'] = df['Store'].apply(categorize_expense)

# # Reorder columns
df = df[['Transaction Date', 'Store', 'Category', 'USD Amount']]

# Transform to datetime to extract year-month and then group
df['Transaction Date'] = pd.to_datetime(df['Transaction Date'])
df['year_month'] = df['Transaction Date'].dt.to_period('M').astype(str)

# Convert year_month to YYYY-MonthName format
df['year_month_full'] = df['Transaction Date'].dt.strftime('%Y-%B')

df['USD Amount'] = pd.to_numeric(df['USD Amount'], errors='coerce')

# Group by 'Category' and 'year_month', then sum the 'USD Amount'
monthly_summary = df.groupby(['Category', 'year_month_full'])['USD Amount'].sum().reset_index()

# Current month
now = datetime.now()
current_month = now.strftime('%Y-%B')

# Filtering for the current month
monthly_summary = monthly_summary[monthly_summary['year_month_full'] == current_month]

#Filtering for current month detail
monthly_summary_detail = df[df['year_month_full'] == current_month]
monthly_summary_detail = monthly_summary_detail.sort_values(['Category', 'Transaction Date'])

# Print the result
print(f'\nMonthly Summary for {current_month}:')
print(monthly_summary)


print(f'\nMonthly Summary detail for {current_month}:')
print(monthly_summary_detail)
# Display DataFrame information
# print('\nDataFrame Info:')
# print(df.info())
