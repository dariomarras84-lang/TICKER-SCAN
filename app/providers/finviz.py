import requests

def get_finviz_data(ticker: str) -> dict:
    """
    Scrape basic data from FinViz for a given ticker.
    """
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {"error": f"FinViz request failed with status {response.status_code}"}

        html = response.text
        data = {}

        # Example scrape: look for Market Cap, Float, etc.
        if "Market Cap" in html:
            data["market_cap_found"] = True
        else:
            data["market_cap_found"] = False

        data["url"] = url
        return data
    except Exception as e:
        return {"error": str(e)}
