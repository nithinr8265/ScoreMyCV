from flask import Blueprint, render_template, session, jsonify, redirect, url_for
from utils.supabase_client import get_supabase

admin_bp = Blueprint("admin", __name__)

def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = session.get("user")
        if not user or user.get("role") != "admin":
            return redirect(url_for("index"))
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route("/")
@admin_required
def admin_panel():
    return render_template("admin.html", user=session["user"])

@admin_bp.route("/stats", methods=["GET"])
@admin_required
def admin_stats():
    sb = get_supabase()
    users_count = sb.table("users").select("id", count="exact").execute()
    analyses_count = sb.table("analyses").select("id", count="exact").execute()
    recent_analyses = sb.table("analyses")\
        .select("id, ats_score, company_name, designation, created_at, users(name, email)")\
        .order("created_at", desc=True).limit(10).execute()
    top_designations = sb.table("analyses")\
        .select("designation").not_.is_("designation", "null").execute()
    top_companies = sb.table("analyses")\
        .select("company_name").not_.is_("company_name", "null").execute()

    # Count designations
    des_count = {}
    for row in (top_designations.data or []):
        d = row.get("designation")
        if d:
            des_count[d] = des_count.get(d, 0) + 1

    comp_count = {}
    for row in (top_companies.data or []):
        c = row.get("company_name")
        if c:
            comp_count[c] = comp_count.get(c, 0) + 1

    return jsonify({
        "total_users": users_count.count or 0,
        "total_analyses": analyses_count.count or 0,
        "recent_analyses": recent_analyses.data or [],
        "top_designations": sorted(des_count.items(), key=lambda x: -x[1])[:5],
        "top_companies": sorted(comp_count.items(), key=lambda x: -x[1])[:5],
    }), 200
