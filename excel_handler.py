import pandas as pd

# Paths to your Excel files
EXCEL_1 = './Excel-Sheets/contributor_Data.xlsx'
EXCEL_2 = './Excel-Sheets/CA.xlsx'
EXCEL_3 = './Excel-Sheets/MENTOR.xlsx'
EXCEL_4 = './Excel-Sheets/PA.xlsx'
EXCEL_5 = './Excel-Sheets/CA2.xlsx'  # Second sheet for Campus Ambassador

EXCEL_6 = './Excel-Sheets/CA_wob.xlsx'  
EXCEL_7 = './Excel-Sheets/MENTORS_wob.xlsx'  
EXCEL_8 = './Excel-Sheets/contributors_wob.xlsx'  
EXCEL_9 = './Excel-Sheets/PA_wob.xlsx'

def load_excel_data():
    data = {}

    ca_emails = pd.read_excel(EXCEL_2, usecols=["email"])['email'].str.lower().values
    ca_emails_extended = pd.read_excel(EXCEL_5, usecols=["email"])['email'].str.lower().values
    
    data['Campus Ambassador'] = list(ca_emails) + list(ca_emails_extended)  # Merge the two lists
    data['CA | Wob'] = pd.read_excel(EXCEL_6, usecols=["email"])['email'].str.lower().values

    
    data['Contributor'] = pd.read_excel(EXCEL_1, usecols=["email"])['email'].str.lower().values
    data['Contributor | Wob'] = pd.read_excel(EXCEL_8, usecols=["email"])['email'].str.lower().values

    data['Mentor'] = pd.read_excel(EXCEL_3, usecols=["email"])['email'].str.lower().values
    data['Mentor | Wob'] = pd.read_excel(EXCEL_7, usecols=["email"])['email'].str.lower().values
    
    data['Project Admin'] = pd.read_excel(EXCEL_4, usecols=["email"])['email'].str.lower().values
    data['PA | Wob'] = pd.read_excel(EXCEL_9, usecols=["email"])['email'].str.lower().values

    return data

# Function to find roles based on the preloaded data
def get_roles_for_email(email, excel_data):
    email = email.lower()  # Convert the passed email to lowercase for comparison
    roles = []
    for role_name, emails in excel_data.items():
        if email in emails:
            roles.append(role_name)
    return roles
