import requests
from bs4 import BeautifulSoup

# FastAPI server endpoint
FASTAPI_URL = "http://localhost:8000/jobs/enrich"

def url_job_entry():
    print("=== URL Job Ingestion Pipeline ===")
    url = input("Enter the Job Posting URL: ").strip()

    if not url:
        return

    print(f"\n[Scraper] Fetching text from: {url}...")

    try:
        # Standard browser header so websites don't immediately block
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        page_response = requests.get(url, headers=headers, timeout=10)
        page_response.raise_for_status()

        # Parse the HTML and extract only the visible text
        soup = BeautifulSoup(page_response.text, "html.parser")

        # Target main body to avoid navigation data
        main_content = soup.find('main') or soup.find('body') or soup
        raw_text = main_content.get_text(separator=' ', strip=True)

        print(f"[Scraper] Successfully extracted {len(raw_text)} characters of text.")

    except Exception as e:
        print(f"[Error] Could not scrape that URL: {e}")
        print("Note: If this is LinkedIn or Handshake, their anti-bot walls blocked the request.")
        return

    # Cap the text to 1500 characters
    short_description = raw_text[:1500]

    # Bundle the scraped text and send it to local DeepSeek model
    full_text_payload = f"Source URL: {url}. Raw Page Text: {short_description}"

    try:
        print(" -> Forwarding to FastAPI container for DeepSeek processing...")
        api_response = requests.post(
            FASTAPI_URL,
            params={
                "job_description": full_text_payload,
                "source_url": url
            }
        )

        if api_response.status_code == 200:
            data = api_response.json()
            print(f" -> [Success] Stored securely to PostgreSQL table via FastAPI.")
            print(f" -> [Status] {data.get('message', data.get('status', 'Completed'))}")
        else:
            print(f" -> [Fail] Container backend status error: {api_response.status_code}")
            print(f"    Server Message: {api_response.text}")

    except Exception as backend_error:
        print(f" -> [Error] Couldn't map stream to pipeline port: {backend_error}")


if __name__ == "__main__":
    while True:
        url_job_entry()

        cont = input("\nWould you like to enter another URL? (y/n): ").strip().lower()
        if cont != 'y':
            print("Exiting URL pipeline. Good luck!")
            break
        print("\n" + "=" * 40 + "\n")