# Smart Graduate Job Application Assistant

An automated, local AI-driven pipeline designed to scrape graduate software engineering roles, analyze target company architectures, and generate highly tailored, humanized cover letters using local LLM inference.

## ️ Development Journey & Iterations

This project was developed locally across several structural iterations before deployment:

1. **Phase 1: Automated Scraper (Adzuna Integration)**
   - Implemented `search_pipeline.py` to extract raw payloads, managing pagination and network logging.
2. **Phase 2: Database Layer & Schema Protection**
   - Configured PostgreSQL inside Docker. Implemented a strict database `UniqueConstraint` on `(job_title, company)` to catch and drop duplicate listings safely via SQLAlchemy `IntegrityError` rollbacks.
3. **Phase 3: Local AI Inference (DeepSeek-R1:14B)**
   - Integrated Ollama to handle offline model processing. Tuned prompt constraints (`CRITICAL RULES`) to suppress generic corporate AI buzzwords (*"honed"*, *"dynamic"*) and anchor the persona to a junior software engineer.
4. **Phase 4: Full-Stack Integration**
   - Built a FastAPI server gateway with data validation layers (`Literal` typing constraints) and wired a vanilla JavaScript frontend using asynchronous native `fetch()` operations.

---

##  Initial Configuration & Setup

1. **Install Ollama** on your machine and pull the model:
   ```bash
   ollama pull deepseek-r1:14b
   ```


## Set up credentials: Create a `.env` file in the project root folder based on the template below:
```text
   ADZUNA_APP_ID=your_adzuna_id
   ADZUNA_APP_KEY=your_adzuna_key
   OLLAMA_MODEL=deepseek-r1:14b
   POSTGRES_DB_USER=postgres
   POSTGRES_DB_PASSWORD=password
```

## Set up CV: Create a `cv.txt` file in the project root folder.
- Copy and paste the raw text of your cv into here. The local LLM will customize the cover letter based on your qualifications.
- Note: For a specific prompt on how your LLM generated your cover letter. Go to `main.py` and to `prompt = {...` to configure.


## Create and activate your Python virtual environment:
   ```text
      # Windows
      py -m venv env
      .\env\Scripts\activate
      
      # macOS/Linux
      python3 -m venv env
      source env/bin/activate
   ```

## Start the FastAPI application gateway:
`uvicorn main:app --reload`

## Install application dependencies:
`pip install -r requirements.txt`


## Option A: Run the Automated Adzuna Market Scraper
`python search_pipeline.py`


## Option B: Manually Scrape a Specific Job URL
`python manual_url_pipeline.py`

## Docker Deployment
To containerize the application gateway:
   ```bash
   # Build the Docker image
   docker build -t job-assistant .
   
   # Run the container linked to your local environment file
   docker run -p 8000:8000 --env-file .env -e DB_HOST=host.docker.internal job-assistant
   ```

## The Frontend Dashboard (`index.html`)

To visualize the automated pipeline, this project includes a lightweight, custom-built web dashboard. 

* **Zero Dependencies:** Built entirely with native HTML, CSS, and Vanilla JavaScript. No heavy frameworks (like React or Angular) were used, keeping the footprint incredibly small.
* **Async Fetch API:** Communicates directly with the FastAPI backend (`http://localhost:8000`) using asynchronous `fetch()` calls to retrieve and display the AI-processed job payloads.
* **Dynamic DOM Rendering:** Automatically iterates through the PostgreSQL database rows and dynamically generates structured HTML cards containing the AI-generated company breakdown and cover letter snippets.
* **Direct Database Control:** Includes active UI event listeners (like the 'Delete' functionality) that trigger `DELETE` endpoint requests to instantly synchronize the PostgreSQL database and refresh the DOM without page reloads.

