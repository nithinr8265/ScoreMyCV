import json
from flask import Blueprint, request, jsonify, session
from utils.supabase_client import get_supabase
from utils.groq_client import analyze_resume

analysis_bp = Blueprint("analysis", __name__)

def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return jsonify({"error": "Authentication required"}), 401
        return fn(*args, **kwargs)
    return wrapper


@analysis_bp.route("/analyze", methods=["POST"])
@login_required
def run_analysis():
    user = session["user"]
    data = request.get_json()
    resume_id = data.get("resume_id")
    company = data.get("company", "").strip() or None
    designation = data.get("designation", "").strip() or None

    if not resume_id:
        return jsonify({"error": "resume_id is required"}), 400

    sb = get_supabase()
    # Fetch resume
    resume_result = sb.table("resumes").select("*").eq("id", resume_id).eq("user_id", user["id"]).execute()
    if not resume_result.data:
        return jsonify({"error": "Resume not found"}), 404

    resume = resume_result.data[0]
    extracted_text = resume.get("extracted_text", "")
    if not extracted_text:
        return jsonify({"error": "No text found in resume"}), 422

    # Run AI analysis
    try:
        result = analyze_resume(extracted_text, company=company, designation=designation)
    except Exception as e:
        return jsonify({"error": f"AI analysis failed: {str(e)}"}), 500

    # Save analysis
    analysis_row = {
        "user_id": user["id"],
        "resume_id": resume_id,
        "ats_score": result.get("ats_score", 0),
        "letter_grade": result.get("letter_grade", "N/A"),
        "summary": result.get("summary", ""),
        "strengths": json.dumps(result.get("strengths", [])),
        "weaknesses": json.dumps(result.get("weaknesses", [])),
        "missing_keywords": json.dumps(result.get("missing_keywords", [])),
        "ats_improvements": json.dumps(result.get("ats_improvements", [])),
        "formatting_issues": json.dumps(result.get("formatting_issues", [])),
        "grammar_issues": json.dumps(result.get("grammar_issues", [])),
        "skill_gaps": json.dumps(result.get("skill_gaps", [])),
        "recommended_skills": json.dumps(result.get("recommended_skills", [])),
        "section_scores": json.dumps(result.get("section_scores", {})),
        "company_name": company,
        "designation": designation,
        "company_match_percentage": result.get("company_match_percentage"),
        "company_missing_skills": json.dumps(result.get("company_missing_skills", [])),
        "company_missing_keywords": json.dumps(result.get("company_missing_keywords", [])),
        "recommended_certifications": json.dumps(result.get("recommended_certifications", [])),
        "suggested_projects": json.dumps(result.get("suggested_projects", [])),
        "suggested_resume_changes": json.dumps(result.get("suggested_resume_changes", [])),
        "file_name": resume.get("file_name", ""),
    }

    save_result = sb.table("analyses").insert(analysis_row).execute()
    if not save_result.data:
        return jsonify({"error": "Failed to save analysis"}), 500

    analysis_id = save_result.data[0]["id"]
    return jsonify({"success": True, "analysis_id": analysis_id, "result": result}), 200


@analysis_bp.route("/history", methods=["GET"])
@login_required
def get_history():
    user = session["user"]
    sb = get_supabase()
    result = sb.table("analyses")\
        .select("id, ats_score, letter_grade, company_name, designation, file_name, created_at")\
        .eq("user_id", user["id"])\
        .order("created_at", desc=True)\
        .limit(50)\
        .execute()
    return jsonify({"success": True, "analyses": result.data or []}), 200


@analysis_bp.route("/<analysis_id>", methods=["GET"])
@login_required
def get_analysis(analysis_id):
    user = session["user"]
    sb = get_supabase()
    result = sb.table("analyses").select("*").eq("id", analysis_id).eq("user_id", user["id"]).execute()
    if not result.data:
        return jsonify({"error": "Analysis not found"}), 404

    row = result.data[0]
    # Parse JSON fields
    json_fields = ["strengths", "weaknesses", "missing_keywords", "ats_improvements",
                   "formatting_issues", "grammar_issues", "skill_gaps", "recommended_skills",
                   "section_scores", "company_missing_skills", "company_missing_keywords",
                   "recommended_certifications", "suggested_projects", "suggested_resume_changes"]
    for field in json_fields:
        if isinstance(row.get(field), str):
            try:
                row[field] = json.loads(row[field])
            except Exception:
                row[field] = []
    return jsonify({"success": True, "analysis": row}), 200


@analysis_bp.route("/<analysis_id>", methods=["DELETE"])
@login_required
def delete_analysis(analysis_id):
    user = session["user"]
    sb = get_supabase()
    result = sb.table("analyses").delete().eq("id", analysis_id).eq("user_id", user["id"]).execute()
    return jsonify({"success": True}), 200
