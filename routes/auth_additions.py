# Add these routes to routes/auth.py

# ── Forgot Password Page ───────────────────────────────────────────────────────
# Add to routes/auth.py:

"""
@auth_bp.route("/forgot-password", methods=["GET"])
def forgot_password_page():
    from flask import render_template
    return render_template("forgot_password.html")

@auth_bp.route("/google/redirect", methods=["GET"])
def google_redirect():
    import os
    # Redirect to Supabase OAuth endpoint
    supabase_url = os.environ.get("SUPABASE_URL", "")
    redirect_url = f"{os.environ.get('APP_URL','http://localhost:5000')}/auth/google/callback-page"
    return redirect(f"{supabase_url}/auth/v1/authorize?provider=google&redirect_to={redirect_url}")

@auth_bp.route("/google/callback-page", methods=["GET"])
def google_callback_page():
    # After Supabase handles OAuth, it redirects here with access_token in fragment
    # The frontend JS picks it up and calls /auth/google/callback
    from flask import render_template
    return render_template("google_callback.html")
"""
