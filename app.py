import streamlit as st
st.write("Current Secrets:", st.secrets)

import streamlit as st
import pandas as pd
import datetime
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ===== CONFIGURATION =====
SHEET_ID = '1iFOkoeS02hq4QhzmWTvW1sEEh4QwDZPt'  # Only the Sheet ID, not the full URL
SHEET_NAME = 'Sheet1'
RECIPIENT_EMAIL = 'rolanda@rsmcduffiecpa.com'
SENDER_EMAIL = 'rolanda@rsmcduffiecpa.com'
SUBJECT_LINE = f"⬤ New Grants for Nonprofits – {datetime.date.today().strftime('%m/%d/%Y')}"

# ===== LOAD CREDENTIALS FROM STREAMLIT SECRETS =====
creds_dict = st.secrets["gcp_service_account"]
credentials = service_account.Credentials.from_service_account_info(
    creds_dict,
    scopes=[
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/gmail.send'
    ]
)

# ===== FUNCTION: SCRAPE SAMPLE GRANTS (Simulated Data) =====
def scrape_sample_grants():
    today = datetime.date.today().strftime('%m/%d/%Y')
    return pd.DataFrame([
        {
            'Grant Name': 'Community Empowerment Grant',
            'Amount': '$15,000',
            'Funder': 'ABC Foundation',
            'Eligibility': 'Nonprofits Nationwide',
            'Deadline': '07/31/2025',
            'Application Link': 'https://example.com/apply',
            'Date Found': today
        },
        {
            'Grant Name': 'Youth Education Grant',
            'Amount': '$5,000',
            'Funder': 'XYZ Trust',
            'Eligibility': '501(c)(3) Youth Orgs',
            'Deadline': '08/15/2025',
            'Application Link': 'https://example.org/youth-grant',
            'Date Found': today
        }
    ])

# ===== FUNCTION: SAVE TO GOOGLE SHEET =====
def save_to_google_sheet(df):
    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        values = [df.columns.tolist()] + df.values.tolist()
        body = {'values': values}
        sheet.values().append(
            spreadsheetId=SHEET_ID,
            range=f"{SHEET_NAME}!A1",
            valueInputOption="RAW",
            body=body
        ).execute()
    except Exception as e:
        st.error(f"Failed to save to Google Sheet: {e}")

# ===== FUNCTION: FORMAT HTML TABLE =====
def format_html_email(df):
    html = """
    <html><body>
    <h3>New Grant Opportunities:</h3>
    <table border="1" cellspacing="0" cellpadding="4">
    <tr>{}</tr>
    {}
    </table>
    </body></html>
    """.format(
        ''.join([f'<th>{col}</th>' for col in df.columns]),
        ''.join(['<tr>' + ''.join([f'<td>{cell}</td>' for cell in row]) + '</tr>' for row in df.values])
    )
    return html

# ===== FUNCTION: SEND EMAIL =====
def send_email(html_content):
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = SUBJECT_LINE
        message["From"] = SENDER_EMAIL
        message["To"] = RECIPIENT_EMAIL
        part = MIMEText(html_content, "html")
        message.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, st.secrets["gmail_app_password"])
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, message.as_string())
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# ===== STREAMLIT UI =====
st.title("Grant Finder AI Agent")

if st.button("Run Grant Search Now"):
    df = scrape_sample_grants()
    st.write("Grants Found:", df)

    save_to_google_sheet(df)
    html = format_html_email(df)
    send_email(html)
    st.success("✅ Daily grant summary saved and emailed!")

