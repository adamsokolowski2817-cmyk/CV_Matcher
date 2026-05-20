import os
import tempfile

import time
import hashlib

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from main import run_pipeline
from cv_reader import extract_text_from_pdf


app = FastAPI(title="CV Matcher API")

CACHE = {}
CACHE_TTL = 600


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "CV Matcher API działa"
    }


@app.post("/search")
async def search_offers(
    city: str = Form("Krakow"),
    query: str = Form("Python"),
    source: str = Form("all"),
    cv_file: UploadFile | None = File(None),
):
    cv_text = None

    if cv_file is not None:
        suffix = os.path.splitext(cv_file.filename)[1].lower()

        if suffix != ".pdf":
            return {
                "results": [],
                "advisor": {
                    "status": "error",
                    "message": "Obsługiwane są tylko pliki PDF.",
                    "suggestions": []
                }
            }

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await cv_file.read())
            tmp_path = tmp.name

        try:
            cv_text = extract_text_from_pdf(tmp_path)
        finally:
            os.remove(tmp_path)
            
    cv_hash = hashlib.md5((cv_text or "").encode("utf-8")).hexdigest()

    cache_key = f"{city}:{query}:{source}:{cv_hash}"
    now = time.time()

    if cache_key in CACHE:
        cached_time, cached_result = CACHE[cache_key]

        if now - cached_time < CACHE_TTL:
            return cached_result

    result = run_pipeline(
        city=city,
        query=query,
        source=source,
        cv_text=cv_text,
    )
    
    CACHE[cache_key] = (now, result)

    return result