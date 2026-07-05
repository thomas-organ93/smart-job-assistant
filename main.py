import os
from typing import Literal
from fastapi import FastAPI, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import ollama
from dotenv import load_dotenv
import models
from database import SessionLocal, engine
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

LOCAL_MODEL = os.environ.get("LOCAL_DEEPSEEK_MODEL")

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="Smart Local Graduate Job Assistant")

# Allows frontend to fetch calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
CV_PATH = BASE_DIR / "cv.txt"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/jobs/enrich")
def process_and_track_job(
        job_description: str,
        source_url: str = None,
        db: Session = Depends(get_db)
):
    try:
        user_cv_content = ""
        if CV_PATH.exists():
            with open(CV_PATH, "r", encoding="utf-8") as cv_file:
                user_cv_content = cv_file.read()
        else:
            print("[Warning] cv.txt not found. Proceeding without personalised CV content.")

        prompt = f"""
            You are an expert career assistant. Analyze the following raw job description text and the candidate's actual CV.

            Candidate's Real CV:
            {user_cv_content}

            Target Job Description Data:
            {job_description}

            Provide your response strictly in four parts separated ONLY by '---'. 
            CRITICAL: Do NOT write headers, labels, or titles like "Section 1:", "Part 1:", or markdown bold tags for the sections. Just write the raw extracted content for each part directly.

            Part 1: The completely normalized and clean Job Title (e.g., "Graduate Software Engineer"). Strip away all internal tracking codes, department names, years, or parenthesis blocks.
            ---
            Part 2: The clean company name string (e.g., "Suade").
            ---
            Part 3: A brief 2-sentence breakdown of what this company does and if they seem to have data/ML infrastructure.
            ---
            Section 4: A highly tailored 3-paragraph cover letter snippet.
            CRITICAL TONE RULES FOR SECTION 4:
            1. Write in a clean, factual, and professional tone. Avoid generic filler.
            2. NEVER use buzzwords like "motivated", "cutting-edge", "technology-led transformation", "honed", "passionate", or "enthusiasm".
            3. Do not hide retail experience behind corporate phrasing like "outside of academia". Call it what it is (e.g., "part-time work at Asda") to show reliability, or don't mention it at all.
            4. Focus entirely on concrete evidence: names of modules, the specific tech stack, and what was actually built in the university projects.
            5. Forbidden Words: Do not use "dynamic", "expert", "expertise", "analytical mindset", "optimize", "cutting-edge", "leverage", or "honed".
            6. Always start with 'Dear Hiring Team,' or similar, and end with my name.
        """

        # Using Ollama / local DeepSeek configuration block here
        # (or switch back to ai_client.models.generate_content if using Gemini)
        response = ollama.chat(
            model=LOCAL_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        ai_output = response["message"]["content"]

        # Clean local DeepSeek reasoning traces out if present
        if "</think>" in ai_output:
            ai_output = ai_output.split("</think>")[-1].strip()

        # Parse distinct sections dynamically
        if "---" in ai_output:
            sections = ai_output.split("---")

            # Helper function to strip out accidental "Section X:" text if the AI forgets instructions
            def clean_section_text(text_block: str) -> str:
                lines = text_block.strip().split("\n")
                filtered_lines = []
                for line in lines:
                    lowered = line.lower().strip()
                    # Skip lines that are just repeating instruction headings
                    if lowered.startswith("section") or lowered.startswith("part") or not lowered:
                        if ":" in lowered or "**" in lowered:
                            continue
                    filtered_lines.append(line)
                return "\n".join(filtered_lines).strip().replace("**", "")

            extracted_title = clean_section_text(sections[0])
            extracted_company = clean_section_text(sections[1])
            breakdown = clean_section_text(sections[2])
            cover_letter = clean_section_text(sections[3])
        else:
            raise ValueError("Local model failed to split content into sections cleanly using '---'")

        # Log the cleaned data into Postgres
        new_job = models.GraduateJob(
            job_title=extracted_title,
            company=extracted_company,
            company_breakdown=breakdown,
            cover_letter_snippet=cover_letter,
            has_ml_team="machine learning" in job_description.lower() or "data" in job_description.lower(),
            status="Not Applied",
            source_url=source_url
        )

        try:
            db.add(new_job)
            db.commit()
            db.refresh(new_job)
            return {"status": "Success", "tracked_data": new_job}

        except IntegrityError:
            db.rollback()
            print(f"[Pipeline Notice] Blocked duplicate entry: {extracted_title} at {extracted_company}")
            return {
                "status": "Skipped",
                "message": f"A listing for {extracted_title} at {extracted_company} is already tracked."
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Enrichment failed: {str(e)}")


@app.get("/jobs")
def get_all_tracked_jobs(db: Session = Depends(get_db)):
    return db.query(models.GraduateJob).all()


@app.patch("/jobs/{job_id}/status")
def update_job_status(
        job_id: int,
        status: Literal["Not Applied", "Applied"] = Body(..., embed=True),
        db: Session = Depends(get_db)
):
    job = db.query(models.GraduateJob).filter(models.GraduateJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job record not found")

    job.status = status
    db.commit()
    db.refresh(job)
    return {"status": "Updated", "tracked_data": job}