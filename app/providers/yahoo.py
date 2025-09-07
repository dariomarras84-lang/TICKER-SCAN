import requests

def get_yahoo_data(ticker: str) -> dict:
    """
    Get financial data from Yahoo Finance public API with headers to reduce blocking.
    """
    url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=financialData,defaultKeyStatistics,summaryDetail"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"error": f"Yahoo request failed: {response.status_code}"}
        data = response.json()
        return data.get("quoteSummary", {}).get("result", [{}])[0]
    except Exception as e:
        return {"error": str(e)}
