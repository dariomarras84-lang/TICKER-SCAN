import requests

def get_yahoo_data(ticker: str) -> dict:
    """
    Get financial data from Yahoo Finance public API.
    """
    url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=financialData,defaultKeyStatistics,summaryDetail"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return {"error": f"Yahoo request failed: {response.status_code}"}
        data = response.json()
        return data
    except Exception as e:
        return {"error": str(e)}
