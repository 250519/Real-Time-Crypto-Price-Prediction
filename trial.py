import requests

api_key = 'PI0RRI0D70W6HCXZ'
ticker = 'CRYPTO:BTC'  # Correct format for crypto tickers

url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={api_key}'
response = requests.get(url)

print("code",response.status_code)
print("text",response.text)

if response.status_code == 200:
    data = response.json()
    feed = data.get('feed', [])
    if feed:
        for item in feed:
            title = item.get('title', 'No Title')
            sentiment_score = item.get('overall_sentiment_score', 'No Score')
            print(f'Title: {title}\nSentiment Score: {sentiment_score}\n')
    else:
        print("No news data available or invalid response structure.")
else:
    print(f"Request failed with status code {response.status_code}")
