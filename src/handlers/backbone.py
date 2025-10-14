from supabase import create_client, Client
import dotenv
import os

dotenv.load_dotenv()
SUPABASE_KEY = str(os.getenv("DATABASE_KEY"))
SUPABASE_URL = str(os.getenv("DATABASE_URL"))

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_table(table_name):
    response = supabase.table(table_name).select("*").execute()
    return response.data

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