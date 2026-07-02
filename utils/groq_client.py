import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()  # Must be here so GROQ_API_KEY is set before client init

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an expert ATS (Applicant Tracking System) and resume analyst with 15+ years of HR and recruitment experience. 
Analyze resumes objectively and return ONLY valid JSON with no extra text, markdown, or explanation."""

def analyze_resume(resume_text: str, company: str = None, designation: str = None) -> dict:
    """Send resume text to Groq and return structured analysis."""
    
    extra = ""
    if company or designation:
        extra = f"""
Also provide company/designation-specific analysis:
- Company: {company or 'Not specified'}
- Designation: {designation or 'Not specified'}
- company_match_percentage: integer 0-100
- company_missing_skills: list of strings
- company_missing_keywords: list of strings
- recommended_certifications: list of strings
- suggested_projects: list of strings
- suggested_resume_changes: list of strings
"""

    extra_field = (",\n  " + extra.strip()) if extra else ""

    prompt = f"""Analyze the following resume as an ATS system and hiring expert. Return ONLY a JSON object with these exact keys:

{{
  "ats_score": <integer 0-100>,
  "letter_grade": <"A+"|"A"|"B+"|"B"|"C"|"D"|"F">,
  "summary": <string, 2-3 sentence professional summary>,
  "strengths": [<string>, ...],
  "weaknesses": [<string>, ...],
  "missing_keywords": [<string>, ...],
  "ats_improvements": [<string>, ...],
  "formatting_issues": [<string>, ...],
  "grammar_issues": [<string>, ...],
  "skill_gaps": [<string>, ...],
  "recommended_skills": [<string>, ...],
  "section_scores": {{
    "contact_info": <integer 0-100>,
    "work_experience": <integer 0-100>,
    "education": <integer 0-100>,
    "skills": <integer 0-100>,
    "projects": <integer 0-100>,
    "certifications": <integer 0-100>
  }}{extra_field}
}}

RESUME TEXT:
{resume_text}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000,
    )
    
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip().rstrip("```").strip()
    
    return json.loads(raw)