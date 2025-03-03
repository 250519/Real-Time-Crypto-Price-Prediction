import requests
import psycopg2
from datetime import datetime
import time
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Replace with your CoinGecko API key
API_KEY = 'CG-9CgcfvpJyPBs9kH7YPep9tFL'

# CoinGecko API URL
API_URL = 'https://api.coingecko.com/api/v3/coins/{id}/market_chart/range'

# Database connection parameters
DB_PARAMS = {
    'dbname': 'Crypto_Data',
    'user': 'postgres',
    'password': 'harsh2505',
    'host': 'localhost',
    'port': '5432'
}

# Function to fetch data from CoinGecko

def fetch_data(coin_id, start_timestamp, end_timestamp):
    API_URL = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"

    headers = {
        'accept': 'application/json'  # Remove API Key
    }
    params = {
        'vs_currency': 'usd',
        'from': start_timestamp,
        'to': end_timestamp
    }

    logging.info(f"Fetching data for {coin_id} from {start_timestamp} to {end_timestamp}")
    logging.info(f"API URL: {API_URL}")
    logging.info(f"Params: {params}")

    response = requests.get(API_URL, headers=headers, params=params)

    if response.status_code == 200:
        logging.info("✅ Data fetched successfully!")
        return response.json()
    else:
        logging.error(f"❌ Error fetching data: {response.status_code} - {response.text}")
        return None


# Function to store data in PostgreSQL
def store_data(data, coin_id):
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        logging.info("✅ Connected to PostgreSQL successfully!")

        if not data or 'prices' not in data or 'market_caps' not in data or 'total_volumes' not in data:
            logging.error("❌ API response does not contain expected data fields!")
            return

        for price_entry in data['prices']:
            try:
                timestamp = datetime.utcfromtimestamp(price_entry[0] / 1000)
                price = price_entry[1]

                # Handle potential missing values (None)
                market_cap = next((item[1] for item in data['market_caps'] if item[0] == price_entry[0]), None)
                volume = next((item[1] for item in data['total_volumes'] if item[0] == price_entry[0]), None)

                if price is None or market_cap is None or volume is None:
                    logging.warning(f"⚠️ Skipping entry due to missing values -> Timestamp: {timestamp}, Price: {price}, Market Cap: {market_cap}, Volume: {volume}")
                    continue  # Skip this entry

                logging.info(f"Inserting Data -> Timestamp: {timestamp}, Price: {price}, Market Cap: {market_cap}, Volume: {volume}")

                cursor.execute("""
                    INSERT INTO crypto_prices (timestamp, coin_id, price_usd, market_cap, volume)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (timestamp, coin_id) DO NOTHING;
                """, (timestamp, coin_id, price, market_cap, volume))

            except Exception as e:
                logging.error(f"❌ Error processing entry {price_entry}: {e}")
                conn.rollback()  # Rollback only this entry, NOT the whole batch

        conn.commit()
        cursor.close()
        conn.close()
        logging.info("✅ Data successfully stored in PostgreSQL!")

    except Exception as e:
        logging.error(f"❌ Error storing data in PostgreSQL: {e}")

# Main function to fetch and store data
def main():
    coin_id = 'bitcoin'  # Example: 'bitcoin', 'ethereum'
    

    try:
        start_timestamp = int(time.mktime(datetime.strptime(start_date, '%Y-%m-%d').timetuple()))
        end_timestamp = int(time.mktime(datetime.strptime(end_date, '%Y-%m-%d').timetuple()))

        data = fetch_data(coin_id, start_timestamp, end_timestamp)
        if data:
            store_data(data, coin_id)
    except Exception as e:
        logging.error(f"❌ Error in main function: {e}")

if __name__ == '__main__':
    main()
