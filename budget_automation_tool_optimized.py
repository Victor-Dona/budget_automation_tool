import imaplib
import email
import re
from typing import List
import yaml
import pandas as pd
from datetime import datetime
#import matplotlib.pyplot as plt

# 0.1. Creation of lists for expense categories.
category_keywords = {
    'Groceries': ['gourmeats', 'arrocha', 'super', 'super xtra', 'rey', 'pricesmart', 'metro', 'riba'],
    'Eating Out': [ 'hotel el ejecutivo', 'tst', 'kokeshi', 'siete granos', 
                'zaz', 'arnazen do cafe', 'buena vista taphouse', 'michaels', 'hung s center',
                'gelarti', 'cakefit' ,'chicken', 'gongcha', 'pa que nelson', 'cerveceria central', 'casa de hampao', 'burger king', 'mentiritas blancas', 
                'beauty y the butcher', 'el huekito mexicano', 'gelato', 'dairy queen', 'la strega', 'perejil', 'miss cho', 'macdonalds', 'grand deli gourmet', 
                'izakaya', 'fratelli', 'the raj', 'ay mi negra', 'the wallace', 'queso chela', 'moocha', 'pedidosya', 'www.pidepaya.com', 'am pm',
                'casa santa', 'anti burger', 'tacos la neta', 'vitali', 'segundo muelle', 'souvlaki gr', 'golden unicorn', 'los tacos',
                'subway', 'esa flaca rica', 'food', 'sushi', 'tea', 'pizza', 'rest', 'pizzeria', 'tip', 'mo mo', 'ramen', 'CAFE BILAL', 'rock and folk',
                'rock and folk', 'bistro', 'coffee', 'cafe unido', 'xing fu tang', 'athanasiou', 'taphouse', 'wahaka', 'poke', 'cafe', 'los tarascos',
                'popeyes', 'brew', 'mcdonalds', 'taco bell', 'restaurante', 'bakery', 'patisserie', 'la rana dorada', 'legitima', 'onze'],
    'Clothes': ['bershka', 'old navy', 'bananarepublic', 'hm', 'zara', 'steven'],
    'Utilities': ['supera', 'super klin', 'est multiplaza fideico', 'estacion', '93137388TERPEL', 'delta', 'texaco', 'cwp', 'tigo','mi tigo' , 'liberty', 'sura', 'terpel', 'prontowash'],
    'Subscriptions': ['APPLE.COM', 'spotify', 'google'],
    'Entertainment': ['burke bikes', 'cinepolis'],
    'Transportation': ['uber', 'ubr'],
    'Other Expenses': ['discovery', 'innovacion', 'relojin', 'amzn', 'apple store', 'hatillo', 'xiaomi', 'panafoto', 'limpoint','mumuso', 'alcaldia', 
                       'cc scotiabank prom', 'permisos de trabajo', 'mona cell', 'WL *VUE*Testing Exam', 'FUND TECNOLOGICA DE PM'],
    'Health': ['power club', 'orto', 'farmas', 'javillo', 'revilla'],
    'Personal care': ['barber'],
    'Traveling': ['copa'],
    'Pets': ['melo', 'american pets'],
    'Cashback': ['cashback'],
    'Rent': ['rent'],
    'Education': ['Georgia Tech', 'the british council']

}

# Flatten the dictionary
keyword_to_category = {keyword: category for category, keywords in category_keywords.items() for keyword in keywords}

# 0.2. Creation of budget dictionary and dataframe transformation
budget = {
    'Categories':
        ['Internet', 'Electricity', 'Data', 'Car loan', 'Car gas', 'Loan 1', 'Loan 2', 'Subscriptions', 'Savings',
         'Groceries', 'Eating Out', 'Credit cards', 'Rent', 'Pets', 'Clothes', 'Entertainment'],
    'Amount': [30, 30, 22.42, 220.42, 50, 188, 92.31, 12, 250, 150, 120, 265, 500, 30, 50, 30]
}

budget_df = pd.DataFrame(budget)

# Block 1.1. Email connection and loading of credentials
with open('credentials.yml') as f:
    content = f.read()

my_credentials = yaml.load(content, Loader=yaml.FullLoader)
user, password = my_credentials["user"], my_credentials["password"]

imap_url = 'imap.gmail.com'
my_mail = imaplib.IMAP4_SSL(imap_url)
my_mail.login(user, password)

# Block 1.2. Selection of folder and addresses to receive messages from
my_mail.select('inbox')

# Selection of emails addresses to extract messages from
email_addresses_to_extract = ['credomatic-informa@pa.credomatic.com', 'notificaciones@pa.scotiabank.com']

# Block 1.3. Search of each email addresses
search_results_list = []
for email_address in email_addresses_to_extract:
    status, messages = my_mail.uid('search', None, f'FROM {email_address}')
    if status == 'OK':
        search_results_list.extend(messages[0].split())

# Deduplicate the results if needed
search_results = list(set(search_results_list))
print(f'You have {len(search_results)} emails from these senders')

bac_count = 0
scotia_count = 0
indexer = 0
other_email_cnt = 0
error_decoding_body_cnt = 0
unexpected_error_cnt = 0
cc_identifier = [4446, 2852, 6936]
cc_identifier_as_string = [str(num) for num in cc_identifier]

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

        # Block 2.2. Email extraction for BAC.
        # Definition of whether multipart or not as criterion 1 to know if it is from BAC or Scotiabank.
        if email_message.is_multipart() and 'credomatic-informa@pa.credomatic.com' in from_address:
            bac_count += 1
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', 'replace')
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
                            expenses_data.append({'Store': store_name, 'USD Amount': bac_usd_amount,
                                                  'Transaction Date': bac_transaction_date.strftime("%Y-%m-%d")})
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

                        expenses_data.append({'Store': store_name, 'USD Amount': scotiabank_usd_amount,
                                              'Transaction Date': scotiabank_transaction_date.strftime("%Y-%m-%d")})
                        scotia_count += 1

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

print(f'You have {bac_count} emails from BAC')
print(f'You have {scotia_count} emails from Scotiabank')
print(f'You have {other_email_cnt} other emails')
print(f'You have {error_decoding_body_cnt} emails with decoding errors')
print(f'You have {unexpected_error_cnt} emails with unexpected errors')

# Convert the expenses data to a DataFrame
expenses_data_df = pd.DataFrame(expenses_data)

# Ensure 'Transaction Date' is in datetime format and then convert to date
expenses_data_df['Transaction Date'] = pd.to_datetime(expenses_data_df['Transaction Date']).dt.date

# Categorize expenses with enhanced matching
expenses_data_df['Category'] = 'Uncategorized'
for keyword, category in keyword_to_category.items():
    pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
    expenses_data_df.loc[expenses_data_df['Store'].str.contains(pattern, na=False), 'Category'] = category

# Display uncategorized expenses to debug
uncategorized_expenses = expenses_data_df[expenses_data_df['Category'] == 'Uncategorized']
print("Uncategorized expenses:")
print(uncategorized_expenses)

expenses_data_df = expenses_data_df.sort_values(by='Transaction Date', ascending=True)


# Introduction of projected amount column
expenses_data_df['Projected Amount'] = None
# Reorder columns to fit excel format
new_order = ['Store', 'Category', 'Transaction Date', 'Projected Amount', 'USD Amount']
expenses_data_df = expenses_data_df[new_order]
print(expenses_data_df)

# Print uncategorized expenses
uncategorized_expenses = expenses_data_df[expenses_data_df['Category'] == 'Uncategorized']
print(uncategorized_expenses)

# Example of how to use 'current_month' to filter expenses
current_month = '2024-07'

# Filter for expenses in the current month
cm_expenses_df = expenses_data_df[expenses_data_df['Transaction Date'].apply(lambda x: x.strftime('%Y-%m')) == current_month]

# Grouping by 'Category' and summing 'USD Amount' within each category
cm_expenses_df['USD Amount'] = pd.to_numeric(cm_expenses_df['USD Amount'], errors='coerce')
cm_expenses_df = cm_expenses_df.groupby('Category')['USD Amount'].sum()

print(cm_expenses_df)

# Saving to an excel file
output_file_path = fr'C:\Users\vdonam\Documents\Python\budget_automation\files\expense_data.xlsx'
# print(output_file_path)

# Save the DataFrame to an Excel file
expenses_data_df.to_excel(output_file_path, index=False, header=True)
