"""SAF SHIKAN — Authentication Module (Supabase Auth).

Provides company-grade login/logout and authentication gating for the AGRON Admin Portal.
All authentication is delegated to Supabase Auth (email + password).

Usage in app.py:
    from auth import require_auth, get_current_user_email, logout
    require_auth()   # Call early — halts execution and shows login if not authenticated.
"""

import streamlit as st
from supabase import create_client, Client


# ─── Supabase Client ─────────────────────────────────────────────────────────
def _get_supabase() -> "Client | None":
    """Create a Supabase client from Streamlit secrets (standalone, no app.py import)."""
    url = st.secrets.get("supabase_url", "")
    key = st.secrets.get("supabase_key", "")
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None


# ─── Session Helpers ─────────────────────────────────────────────────────────
def get_current_user() -> "dict | None":
    """Return the current authenticated user dict, or None if not logged in."""
    return st.session_state.get("auth_user", None)


def get_current_user_email() -> str:
    """Return the logged-in user's email, or 'anonymous' if unauthenticated."""
    user = get_current_user()
    return user.get("email", "anonymous") if user else "anonymous"


def logout() -> None:
    """Sign out current user via Supabase Auth and wipe all session state."""
    supabase = _get_supabase()
    if supabase:
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
    for key in [
        "auth_user", "auth_session",
        "audit_session_id", "audit_log", "portal_started"
    ]:
        st.session_state.pop(key, None)
    st.rerun()


# ─── Login Form ───────────────────────────────────────────────────────────────
def _render_login_screen() -> None:
    """Render the full-page branded SAF SHIKAN login screen."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif !important;
        background: linear-gradient(145deg, #071f10 0%, #0C3823 55%, #0e4a2c 100%) !important;
        min-height: 100vh;
    }
    .block-container {
        max-width: 460px !important;
        margin: 0 auto !important;
        padding-top: 5rem !important;
        padding-bottom: 2rem !important;
    }
    /* Card wrapper */
    .login-card {
        background: #FFFFFF;
        border-radius: 18px;
        padding: 40px 38px 32px 38px;
        box-shadow: 0 32px 64px rgba(0,0,0,0.30), 0 8px 24px rgba(0,0,0,0.12);
        margin-bottom: 18px;
    }
    .login-brand-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 6px;
    }
    .login-brand-dot {
        width: 28px; height: 28px;
        background: #0C3823;
        border-radius: 6px;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.7rem; color: white; font-weight: 800;
    }
    .login-brand-name {
        font-family: 'Outfit', sans-serif;
        font-size: 1.05rem; font-weight: 800;
        color: #0C3823; letter-spacing: 1px; text-transform: uppercase;
    }
    .login-tagline {
        font-size: 0.78rem; color: #64748B;
        letter-spacing: 0.2px; margin-bottom: 22px;
    }
    .login-divider {
        border: none; border-top: 1px solid #E2E8F0; margin-bottom: 22px;
    }
    .login-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.55rem; font-weight: 700;
        color: #0F172A; margin-bottom: 4px;
    }
    .login-sub {
        font-size: 0.83rem; color: #64748B; margin-bottom: 20px;
    }
    .login-footer-text {
        text-align: center; margin-top: 20px;
        font-size: 0.76rem; color: rgba(255,255,255,0.5);
    }
    /* Style Streamlit inputs within form */
    div[data-testid="stForm"] input {
        border-radius: 8px !important;
        border: 1.5px solid #E2E8F0 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.92rem !important;
    }
    div[data-testid="stForm"] input:focus {
        border-color: #0C3823 !important;
        box-shadow: 0 0 0 3px rgba(12,56,35,0.12) !important;
    }
    div[data-testid="stForm"] button[kind="primaryFormSubmit"],
    div[data-testid="stForm"] button[type="submit"] {
        background: #0C3823 !important;
        border-radius: 8px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.3px !important;
        height: 44px !important;
    }
    div[data-testid="stForm"] button:hover {
        background: #1a5c38 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Branded header card
    st.markdown("""
    <div class='login-card'>
        <div class='login-brand-row'>
            <div class='login-brand-dot'>SS</div>
            <div class='login-brand-name'>SAF SHIKAN</div>
        </div>
        <div class='login-tagline'>AGRON Admin Console &nbsp;·&nbsp; Customer Data &amp; Management Portal</div>
        <hr class='login-divider'>
        <div class='login-title'>Sign In to Continue</div>
        <div class='login-sub'>Enter your company credentials to access the portal.</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("saf_shikan_login", clear_on_submit=False):
        email = st.text_input(
            "Company Email Address",
            placeholder="you@company.com",
            help="Use the email address registered by your AGRON system administrator."
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="••••••••"
        )
        col_btn, col_space = st.columns([3, 1])
        with col_btn:
            submitted = st.form_submit_button(
                "Sign In →",
                use_container_width=True,
                type="primary"
            )

    if submitted:
        if not email.strip() or not password:
            st.error("⚠️ Both email and password are required.")
            return

        supabase = _get_supabase()
        if not supabase:
            st.error(
                "⚠️ Cannot connect to authentication server. "
                "Ensure `supabase_url` and `supabase_key` are set in Streamlit Secrets."
            )
            return

        with st.spinner("Authenticating..."):
            try:
                response = supabase.auth.sign_in_with_password({
                    "email": email.strip(),
                    "password": password
                })
                if response and response.user:
                    st.session_state["auth_user"] = {
                        "id":    response.user.id,
                        "email": response.user.email,
                        "role":  response.user.role or "authenticated",
                    }
                    if response.session:
                        st.session_state["auth_access_token"] = response.session.access_token
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password. Please try again.")
            except Exception as exc:
                msg = str(exc).lower()
                if any(kw in msg for kw in ("invalid", "credentials", "wrong", "not found", "email")):
                    st.error("❌ Invalid email or password.")
                else:
                    st.error(f"❌ Authentication error: {exc}")

    st.markdown("""
    <div class='login-footer-text'>
        Forgot your password? Contact your AGRON system administrator.<br>
        <span style='font-size:0.7rem;opacity:0.6;'>All sessions are logged and audited.</span>
    </div>
    """, unsafe_allow_html=True)


# ─── Gatekeeper ───────────────────────────────────────────────────────────────
def require_auth() -> None:
    """Call at the top of app.py — shows login screen and stops execution if not authenticated."""
    if not get_current_user():
        _render_login_screen()
        st.stop()
