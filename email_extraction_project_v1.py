import imaplib
import email
import re
import yaml
import pandas as pd

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

msgs = []
results = []  # List to store results

for num in mail_id_list:
    typ, data = my_mail.fetch(num, '(RFC822)')
    msgs.append(data)

for msg in msgs[::-1]:
    for response_part in msg:
        if type(response_part) is tuple:
            my_msg = email.message_from_bytes(response_part[1])
            for part in my_msg.walk():
                if part.get_content_type() == 'text/plain':
                    content = part.get_payload(decode=True).decode('latin-1').replace('=20', ' ').replace('=09', '\t')
                    #print(content)
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
                        print('Comercio:', comercio)
                        print('Monto:', monto)
                        print('Fecha y hora:', date)
                        results.append({'Comercio': comercio, 'Monto': monto, 'Fecha y hora': date})
                    else:
                        print('No match found for comercio, monto')

                    print("---")

df = pd.DataFrame(results)
print(df)