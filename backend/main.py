"""FastAPI backend application for Skillora (SkillBridge 2.0).

High-performance, explainable resume analysis and career intelligence service.
"""

import sys
import re
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pymupdf as fitz
from skill_matcher import match_skills, generate_7day_roadmap


app = FastAPI(
    title="Skillora API",
    description="Explainable AI-powered resume analysis and career intelligence engine",
    version="2.0.0"
)

# Enable CORS for local web interface & multi-origin integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def extract_text_from_pdf(content: bytes) -> tuple[str, int]:
    """
    Extract readable text from PDF bytes with column-order and table awareness.
    Returns (extracted_text, page_count).
    """
    try:
        pdf_document = fitz.open(stream=content, filetype="pdf")
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Could not read or parse this PDF file. The file may be corrupted."
        ) from exc

    if pdf_document.needs_pass:
        pdf_document.close()
        raise HTTPException(
            status_code=400,
            detail="Password-protected PDFs are not supported. Please upload an unlocked PDF."
        )

    page_count = len(pdf_document)
    if page_count == 0:
        pdf_document.close()
        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF document contains no pages."
        )

    all_text_parts = []

    for page_idx in range(page_count):
        page = pdf_document[page_idx]

        # Use sort=True to preserve natural reading order in multi-column layouts
        page_text = page.get_text("text", sort=True)

        # Fallback to block extraction if standard extraction is sparse
        if not page_text or len(page_text.strip()) < 20:
            blocks = page.get_text("blocks")
            # Sort blocks primarily by horizontal column threshold, then vertical y
            # blocks: (x0, y0, x1, y1, text, block_no, block_type)
            sorted_blocks = sorted(blocks, key=lambda b: (b[0] > (page.rect.width * 0.45), b[1]))
            page_text = "\n".join(b[4] for b in sorted_blocks if b[4].strip())

        # Clean excessive duplicate whitespace while preserving line structure
        cleaned = re.sub(r"[ \t]+", " ", page_text)
        all_text_parts.append(cleaned)

    pdf_document.close()
    full_text = "\n\n".join(all_text_parts).strip()
    return full_text, page_count


# Backward compatibility wrapper for learning plan
def generate_learning_plan(missing_skills):
    return generate_7day_roadmap(missing_skills, [])


@app.get("/")
def home():
    """Service health & metadata."""
    return {
        "service": "Skillora API",
        "version": "2.0.0",
        "message": "Welcome to Skillora API! AI-powered resume intelligence is running.",
        "status": "running"
    }


@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Analyze uploaded resume PDF against target job description.
    Performs skill extraction, normalization, contextual matching, priority ranking,
    and returns a structured explainable report.
    """
    # 1. Validate file extension
    if not resume.filename or not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload a PDF document (.pdf)."
        )

    # 2. Validate job description input
    clean_jd = job_description.strip()
    if not clean_jd:
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty. Please provide the target role requirements."
        )

    if len(clean_jd) < 15:
        raise HTTPException(
            status_code=400,
            detail="Job description is too short. Please provide a detailed description for accurate matching."
        )

    # 3. Read content with size limit (max 5 MB)
    max_bytes = 5 * 1024 * 1024
    content = await resume.read(max_bytes + 1)

    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail="Resume exceeds the 5 MB maximum file size limit."
        )

    # 4. Check PDF magic header
    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file content. The uploaded file is not a valid PDF document."
        )

    # 5. Extract text with layout awareness
    extracted_text, page_count = extract_text_from_pdf(content)

    if not extracted_text or len(extracted_text.strip()) < 30:
        raise HTTPException(
            status_code=400,
            detail="No readable text found in this PDF. The document may be a scanned image or photograph. Please upload a PDF with selectable text."
        )

    # 6. Execute Intelligence Matching
    analysis = match_skills(extracted_text, clean_jd)

    return {
        "success": True,
        "message": "Resume analyzed successfully!",
        "filename": resume.filename,
        "page_count": page_count,
        "analysis": analysis
    }
