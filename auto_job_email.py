import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

# Configs
API_KEY = 'API_KEY' # Register google search api => https://console.cloud.google.com/
CSE_ID = 'GOOGLE_CUSTOM_SEARCH_KEY' # generate custom google search engine => https://programmablesearchengine.google.com/

SEARCH_QUERY = [
    'Informatiker Applikationsentwicklung (Luzern OR Solothurn OR Aarau) site:.ch',
    'Informatiker Applikationsentwicklung Praktikum (Luzern OR Solothurn OR Aarau) site:.ch',
    'Softwareentwickler (Luzern OR Solothurn OR Aarau) site:.ch',
    'Softwareentwickler Praktikum (Luzern OR Solothurn OR Aarau) site:.ch'
]

EXCLUDE_WORDS = [
    'ICT-Berufsbildung', 
    'berufsberatung.ch', 
    'Ausbildung', 
    'Lehre', 
    'Berufswahl-Portal', 
    'Dein Karriereschritt | IBZ', 
    'https://blog.bkd.lu.ch/informatikmittelschule/',
    'Informatikmittelschule - Kanton Luzern',
    'teko.ch',
    'TEKO Dipl. Informatiker',
    'Informatik NDS HF Applikationsentwicklung',
    'ICT-Berufe | ICT Berufsbildung Solothurn',
    'EFZ',
    'Hochschule Luzern'
]

#Email settings
EMAIL_SENDER = 'email'
EMAIL_SENDER_PASS = 'password'
EMAIL_SENDER_SERVER = 'servername'
EMAIL_PORT = 587
EMAIL_RECEIVER = 'to_email'

def google_search(search_query, api_key, cse_id, **kwargs):
    print(f"Start Google search for: {search_query}")
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'q': search_query,
        'key': api_key,
        'cx': cse_id,
    }
    params.update(kwargs)
    response = requests.get(url, params=params)
    print(f"Search completed for: {search_query}")
    return response.json()

def send_email(subject, body, sender, receiver, password):
    print("Start sending the e-mail...")
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP(EMAIL_SENDER_SERVER, EMAIL_PORT)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_SENDER_PASS)
    text = msg.as_string()
    server.sendmail(sender, receiver, text)
    server.quit()
    print("E-mail has been sent.")

def is_result_valid(item):
    title = item.get('title', '').lower()
    snippet = item.get('snippet', '').lower()
    for word in EXCLUDE_WORDS:
        if word.lower() in title or word.lower() in snippet:
            return False
    return True

def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        hours = mins // 60
        mins = mins % 60
        timeformat = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)
        print(timeformat, end='\r')
        time.sleep(1)
        t -= 1

while True:
    # E-Mail-content 
    email_body = 'New Jobs for... :\n\n'

    for query in SEARCH_QUERY:
        results = google_search(query, API_KEY, CSE_ID)

        email_body += f"Jobs for {query}:\n"
        for item in results.get('items', []):
            if is_result_valid(item):
                email_body += f"Titel: {item['title']}\nLink: {item['link']}\n\n"
        email_body += "\n"

    # E-Mail send
    send_email('Jobs for ...', email_body, EMAIL_SENDER, EMAIL_RECEIVER, EMAIL_SENDER_PASS)

    # Wait for 12 hours (43200 seconds)
    print("Script will be restarted in 12 hours...")
    countdown(43200)  # 12 Stunden Countdown (43200 Sekunden)
