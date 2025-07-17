import pandas as pd
import requests
import time
import mysql.connector
from openpyxl import Workbook

# --- CONFIGURATION ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'pasig_business_analytics'
}

GEOCODE_URL = 'https://nominatim.openstreetmap.org/search'
USER_AGENT = 'PasigBusinessCapstone/1.0 (your_email@example.com)'

# --- FUNCTIONS ---
def geocode_address(address, barangay):
    full_address = f"{address}, {barangay}, Pasig City, Philippines"
    params = {
        'q': full_address,
        'format': 'json',
        'limit': 1
    }
    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get(GEOCODE_URL, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        else:
            return None, None
    except Exception as e:
        print(f"Geocoding error for '{full_address}': {e}")
        return None, None

def import_businesses_from_excel(filename):
    df = pd.read_excel(filename)
    # Standardize column names
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    required = ['business_trade_name', 'business_address', 'barangay', 'line_of_business']
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Connect to DB
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    insert_query = '''
        INSERT INTO businesses (business_trade_name, business_address, barangay, line_of_business, latitude, longitude)
        VALUES (%s, %s, %s, %s, %s, %s)
    '''

    for idx, row in df.iterrows():
        name = str(row['business_trade_name']).strip()
        address = str(row['business_address']).strip()
        barangay = str(row['barangay']).strip()
        line = str(row['line_of_business']).strip()
        lat, lon = geocode_address(address, barangay)
        print(f"{idx+1}. {name} | {address}, {barangay} | {lat}, {lon}")
        cursor.execute(insert_query, (name, address, barangay, line, lat, lon))
        conn.commit()
        time.sleep(1)  # Be polite to the geocoding API

    cursor.close()
    conn.close()
    print("Import complete!")

def generate_sample_excel(filename='sample_businesses.xlsx'):
    wb = Workbook()
    ws = wb.active
    ws.append(['BUSINESS TRADE NAME', 'BUSINESS ADDRESS', 'BARANGAY', 'LINE OF BUSINESS'])
    ws.append(['Jollibee', 'Ortigas Ave', 'Ugong', 'Fast Food'])
    ws.append(['SM Supermarket', 'F. Ortigas Jr. Rd', 'San Antonio', 'Supermarket'])
    ws.append(['Mercury Drug', 'Shaw Blvd', 'Kapitolyo', 'Pharmacy'])
    wb.save(filename)
    print(f"Sample Excel file saved as {filename}")

if __name__ == '__main__':
    # Uncomment to generate a sample Excel file
    # generate_sample_excel()

    # Change this to your actual Excel file
    excel_file = r'C:\xampp\htdocs\bploop\2020-2025 (Business Listing).xlsx'
    import_businesses_from_excel(excel_file) 