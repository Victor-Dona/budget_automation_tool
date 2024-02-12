import imaplib
import email
import re
from typing import List
import base64
import yaml
import pandas as pd
from datetime import datetime

# This one outputs all emails from three addresses properly
# Block 1.1. Email connection and loading of credentials
print("opening yaml for credentials")
with open('venv/credentials.yml') as f:
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
print(f'Bac Count = {bac_count}')
print(f'Scotia Count = {scotia_count}')
print(f'Other Scotia Emails Count = {other_email_cnt}')

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

        # Block 2.2. Body extraction.
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
                            bac_store_name = bac_store_name_match.group(1).strip()
                            bac_usd_amount = bac_usd_amount_match.group(1).strip()
                            bac_transaction_date = datetime.strptime(bac_transaction_date_match.group(1).strip(),
                                                                     '%Y/%m/%d-%H:%M:%S')
                            # print(f'Store Name: {bac_store_name}')
                            # print(f'USD Amount: {bac_usd_amount}')
                            # print(f'Transaction Date: {bac_transaction_date.strftime("%Y-%m-%d")}')
                            expenses_data.append({'Store': bac_store_name, 'USD Amount': bac_usd_amount,
                                   'Transaction Date': bac_transaction_date.strftime("%Y-%m-%d")})
                        else:
                            print(f'Unmatched BAC email - Subject: {subject}, Body: {body}')

                        # print('Hola, soy de BAC, ciao.\n---')
                        # print(f'Body: {body}')
                    except UnicodeDecodeError as e:
                        print(f"Error decoding body: {e}")
                    break

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
                        scotiabank_store_name = scotiabank_store_name_match.group(1)
                        scotiabank_transaction_date = datetime.strptime(scotiabank_transaction_date_match.group(1), '%d/%m/%Y')
                        # print(f'Store Name: {scotiabank_store_name}')
                        # print(f'USD Amount: {scotiabank_usd_amount}')
                        # print(f'Transaction Date: {scotiabank_transaction_date.strftime("%Y-%m-%d")}')
                        expenses_data.append({'Store': scotiabank_store_name, 'USD Amount': scotiabank_usd_amount,
                               'Transaction Date': scotiabank_transaction_date.strftime("%Y-%m-%d")})
                        scotia_count += 1
                    # print(f'Bac Count = {bac_count}')
                    # print(f'Scotia Count = {scotia_count}')
                    # print(f'Other email count: {other_email_cnt}')
                    else:
                        print(f'Not a match - Subject: {subject}, Body: {body}')

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

                            print(f'Last Digits: {scotiabank_last_digits}')
                            print(f'Store Name: {scotiabank_store_name}')
                            print(f'USD Amount: {scotiabank_usd_amount}')
                            print(f'Transaction Date: {scotiabank_transaction_date.strftime("%Y-%m-%d")}')
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

expenses_data_dt = pd.DataFrame(expenses_data)
print(expenses_data_dt)
print(f'Bac Count = {bac_count}')
print(f'Scotia Count = {scotia_count}')
print(f'Other Scotia Emails Count = {other_email_cnt}')
print(f'Error Decoding Body Count = {error_decoding_body_cnt}')
print(f'Unexpected Error Count = {unexpected_error_cnt}')

for sender in email_addresses_to_extract:
    if sender == 'credomatic-informa@pa.credomatic.com':
        print('It is I')
    else:
        print('It is not I')

    # Creation of category lists
    supermarkets_list = ['super', 'xtra', 'rey', 'pricesmart', 'metro', 'riba']
    eating_out_list = ['tea', 'pizza', 'rest', 'pizzeria', 'tip', 'mo mo', 'ramen', 'rock and folk', 'bistro', 'coffee',
                       'cafe unido', 'xing fu tang',
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
            ['Internet', 'Electricity', 'Data', 'Car loan', 'Car gas', 'Loan 1', 'Loan 2', 'Subscriptions', 'Savings',
             'Groceries', 'Eating Out', 'Credit cards', 'Rent', 'Pets', 'Clothes', 'Entertainment'],
        'Amount': [34.74, 50, 22.42, 220.42, 50, 188, 92.31, 12, 50, 170, 100, 300, 500, 30, 50, 30]
    }

    # print('Printing general budget in a dataframe')
    budget_2024_df = pd.DataFrame(budget_2024)
    # print(budget_2024_df)
