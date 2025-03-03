import requests
import psycopg2
from datetime import datetime, timedelta

# Alpha Vantage API key and parameters
API_KEY = '95U7YEYJM5068K4V'
TICKER = 'CRYPTO:BTC'
API_URL = 'https://www.alphavantage.co/query'

# PostgreSQL database connection parameters
DB_PARAMS = {
    'dbname': 'Crypto_Data',
    'user': 'postgres',
    'password': 'harsh2505',
    'host': 'localhost',
    'port': '5432'
}

# Connect to the PostgreSQL database
conn = psycopg2.connect(**DB_PARAMS)
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS crypto_news (
    date DATE PRIMARY KEY,
    daily_sentiment_score FLOAT
);
''')
conn.commit()

# Function to fetch and store aggregated news sentiment data
def fetch_and_store_news_data(start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        time_from = current_date.strftime('%Y%m%dT0000')
        time_to = (current_date + timedelta(days=1)).strftime('%Y%m%dT0000')
        params = {
            'function': 'NEWS_SENTIMENT',
            'tickers': TICKER,
            'time_from': time_from,
            'time_to': time_to,
            'sort': 'RELEVANCE',
            'limit': 50,
            'apikey': API_KEY
        }
        response = requests.get(API_URL, params=params)
        data = response.json()
        feed = data.get('feed', [])
        if feed:
            sentiment_scores = [float(item.get('overall_sentiment_score', 0)) for item in feed]
            if sentiment_scores:
                daily_sentiment_score = sum(sentiment_scores) / len(sentiment_scores)
                cursor.execute(
                    'INSERT INTO crypto_news (date, daily_sentiment_score) VALUES (%s, %s) ON CONFLICT (date) DO UPDATE SET daily_sentiment_score = EXCLUDED.daily_sentiment_score',
                    (current_date, daily_sentiment_score)
                )
                conn.commit()
                print(f'Date: {current_date}, Sentiment Score: {daily_sentiment_score}')
        else:
            print(f'No news data for {current_date}')
        current_date += timedelta(days=1)

# Define the start and end dates for the news sentiment data
start_date = datetime(2025, 2, 25)
end_date = datetime(2025, 3, 3)

# Fetch and store the news data
fetch_and_store_news_data(start_date, end_date)

# Close the database connection
cursor.close()
conn.close()
