import os
from dotenv import load_dotenv
import urllib.parse
import requests

load_dotenv()

ADZUNA_APP_ID = os.environ.get("ADZUNA_ID")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_KEY")

# FastAPI server endpoint
FASTAPI_URL = "http://localhost:8000/jobs/enrich"

def auto_search_and_pipeline(keywords="graduate software engineer", location="london", radius_miles=25):
    # Convert miles to matching integer Kilometers format
    radius_km = int(radius_miles * 1.609)

    print(
        f"[Search Engine] Querying API for '{keywords}' in '{location}' (+{radius_miles}mi / {radius_km}km radius)...")

    # 1. Manually format clean URL queries to avoid Nginx syntax faults
    clean_keywords = urllib.parse.quote(keywords)
    clean_location = urllib.parse.quote(location)

    # Constructing standard query string with exact parameters
    api_url = (
        f"https://api.adzuna.com/v1/api/jobs/gb/search/1"
        f"?app_id={ADZUNA_APP_ID}"
        f"&app_key={ADZUNA_APP_KEY}"
        f"&what={clean_keywords}"
        f"&where={clean_location}"
        f"&distance={radius_km}"
        f"&results_per_page=5"
        f"&content-type=application/json"
    )

    try:
        # Requesting without passing params dictionary to let raw encoded values clear the gate
        response = requests.get(api_url)

        if response.status_code != 200:
            print(f"[Error] Gateway threw code {response.status_code}. Response text summary:")
            print(response.text[:500])
            return

        jobs_list = response.json().get("results", [])
        print(f"[Search Engine] Successfully authorized! Discovered {len(jobs_list)} live matching listings.")

    except Exception as e:
        print(f"[Error] Connection to Adzuna engine broken: {e}")
        return

    # 2. Iterate through results and stream pipelines
    for i, job in enumerate(jobs_list):
        title = job.get("title", "Unknown Title")
        company = job.get("company", {}).get("display_name", "Unknown Company")
        job_location = job.get("location", {}).get("display_name", "Unknown Location")
        raw_description = job.get("description", "")
        redirect_url = job.get("redirect_url", "")

        print(f"\n[{i + 1}/{len(jobs_list)}] Processing: '{title}' at {company} ({job_location})")

        # Limit characters
        short_description = raw_description[:1000]
        full_text_payload = f"Title: {title}. Company: {company}. Location: {job_location}. Details: {short_description}"

        # Change this to pass it as a query parameter (params=) instead of json=
        try:
            print(" -> Forwarding to FastAPI container for DeepSeek processing...")
            api_response = requests.post(
                FASTAPI_URL,
                # Changed from json= to params=
                params={
                    "job_description": full_text_payload,
                    "source_url": redirect_url
                }
            )

            if api_response.status_code == 200:
                print(f" -> [Success] Stored securely to PostgreSQL table via FastAPI.")
            else:
                print(f" -> [Fail] Container backend status error: {api_response.status_code}")
                # This debug line will show you EXACTLY what field FastAPI is complaining about:
                print(f"    Server Message: {api_response.text}")

        except Exception as backend_error:
            print(f" -> [Error] Couldn't map stream to pipeline port: {backend_error}")

if __name__ == "__main__":
    auto_search_and_pipeline()