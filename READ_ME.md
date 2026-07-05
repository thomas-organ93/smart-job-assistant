# Job Searcher
This project was developed locally across several structural iterations before deployment:

1. **Phase 1: Automated Scraper (Adzuna Integration)**
   - Implemented `search_pipeline.py` to extract raw payloads. Handles pagination and logging.
2. **Phase 2: Database Layer & Schema Protection**
   - Configured PostgreSQL inside Docker. Implemented a `UniqueConstraint` on `(job_title, company)` to catch and drop duplicate listings safely using SQLAlchemy's `IntegrityError`.
3. **Phase 3: Local AI Inference (DeepSeek-R1:14B)**
   - Integrated Ollama. Tuned prompt constraints (`CRITICAL LAWS`) to suppress generic AI buzzwords ("honed", "dynamic") and anchor the persona to a junior human software engineer.
4. **Phase 4: Full-Stack Integration**
   - Added a FastAPI gateway with validation layers and linked a vanilla JS frontend using native `fetch()` calls.


Install/Update the following 
* Install Ollama and download your selected deepseek model appropriate for your hardware.
* Local DeepSeek model into the .env file
* Adzuna id & key.
* Copy and paste your CV into the cv.txt file

## Requirement

* `python3 -m venv env` to create virtual environment.
* or `py -m venv env`

* `.\env\Scripts\activate` to activate environment.

* `pip install fastapi sqlalchemy psycopg2-binary uvicorn ollama dotenv` to install packages.

* `uvicorn main:app --reload` to run server.

* `Ctrl + C `to terminate server.

## Docker

* `docker build -t job-assistant .` to build the container.

* `docker run -p 8000:8000 --env-file .env -e DB_HOST=host.docker.internal job-assistant` to run the container.



## Run Adzuna Job Bot

* `uvicorn main:app --reload` to run server first.
* 
* `python search_pipeline.py` to run job search bot.