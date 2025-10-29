import requests
import dotenv
import os

dotenv.load_dotenv()
# Using variables from .env file (DATABASE_URL and DATABASE_KEY)
SUPABASE_KEY = str(os.getenv("DATABASE_KEY"))
SUPABASE_URL = str(os.getenv("DATABASE_URL"))

# Setup headers for Supabase REST API
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def fetch_table(table_name):
    """
    Fetch all records from a Supabase table using direct REST API.
    Replaces supabase SDK to save ~10MB RAM and ~0.85s startup time.
    """
    try:
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/{table_name}?select=*',
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching table {table_name}: {e}")
        return []

#fetching functions
def searchTableByName(table_name, item_name):
    table_data = fetch_table(table_name)

    if table_name == 'outfits' or table_name == 'equipment':
        table_data = [item['data'] for item in table_data if 'data' in item]

    for item in table_data:
        if item.get("name", 'UNKNOWN').lower() == item_name.lower():
            return item
    return None

def searchTableById(table_name, item_id):
    table_data = fetch_table(table_name)
    for item in table_data:
        if item['id'] == item_id:
            return item
    return None