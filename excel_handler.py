# excel_handler.py

import pandas as pd

# Paths to your Excel files
EXCEL_1 = './Excel-Sheets/contributor_Data.xlsx'
EXCEL_2 = './Excel-Sheets/CA.xlsx'
EXCEL_3 = './Excel-Sheets/MENTOR.xlsx'
EXCEL_4 = './Excel-Sheets/PA.xlsx'
EXCEL_5 = './Excel-Sheets/CA2.xlsx'  # Second sheet for Campus Ambassador

def load_excel_data():
    data = {}

    # Fetch email addresses only and combine multiple sources for the same role
    data['Contributor'] = pd.read_excel(EXCEL_1, usecols=["email"])['email'].values
    # Combine emails from both CA.xlsx and CA2.xlsx for Campus Ambassador role
    ca_emails = pd.read_excel(EXCEL_2, usecols=["email"])['email'].values
    ca_emails_extended = pd.read_excel(EXCEL_5, usecols=["email"])['email'].values
    data['Campus Ambassador'] = list(ca_emails) + list(ca_emails_extended)  # Merge the two lists

    data['Mentor'] = pd.read_excel(EXCEL_3, usecols=["email"])['email'].values
    data['Project Admin'] = pd.read_excel(EXCEL_4, usecols=["email"])['email'].values

    return data

# Function to find roles based on the preloaded data
def get_roles_for_email(email, excel_data):
    roles = []
    for role_name, emails in excel_data.items():
        if email in emails:
            roles.append(role_name)
    return roles
