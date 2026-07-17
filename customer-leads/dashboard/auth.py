"""SAF SHIKAN — Authentication Module (Supabase Auth).

Provides company-grade login/logout and authentication gating for the AGRON Admin Portal.
All authentication is delegated to Supabase Auth (email + password).

Usage in app.py:
    from auth import require_auth, get_current_user_email, logout
    require_auth()   # Call early — halts execution and shows login if not authenticated.
"""

import base64
import os
import streamlit as st
try:
    from supabase import create_client, Client
except Exception:
    create_client, Client = None, None


# ─── Logo Base64 Helper ──────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _get_logo_base64() -> str:
    """Return base64 encoded SAF SHIKAN green logo (`SS.png`) if available."""
    try:
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        paths_to_check = [
            os.path.join(curr_dir, "assets", "saf_shikan_logo.png"),
            os.path.join(os.path.dirname(os.path.dirname(curr_dir)), "Saf Shikan Logo - green without bg.png"),
            os.path.join(curr_dir, "saf_shikan_logo.png"),
        ]
        for p in paths_to_check:
            if os.path.exists(p):
                with open(p, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        pass
    return ""


# ─── Supabase Client ─────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
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
    return st.session_state.get("auth_user")


def get_current_user_email() -> str:
    """Return current user email string or 'anonymous' if unauthenticated."""
    user = get_current_user()
    return user["email"] if user else "anonymous"


def logout() -> None:
    """Sign out from Supabase (if client exists) and clear all session auth states."""
    supabase = _get_supabase()
    if supabase:
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
    for key in [
        "auth_user", "auth_access_token", "portal_unlocked",
        "audit_session_id", "audit_log", "portal_started", "_transitioning",
        "group_tab_viewed", "charts_tab_viewed", "sec_tab_viewed"
    ]:
        st.session_state.pop(key, None)
    st.rerun()


def _show_loader(status_text: str) -> None:
    """Show a beautiful full-screen overlay loading screen with custom status text matching SAF SHIKAN colors."""
    loader_html = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@700;800;900&display=swap');
    
    .premium-loader-overlay {{
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: radial-gradient(circle at center, #0C3823 0%, #05180c 100%) !important;
        z-index: 9999999 !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #FFFFFF !important;
    }}
    .loader-ring {{
        display: inline-block;
        position: relative;
        width: 80px;
        height: 80px;
        margin-bottom: 28px;
    }}
    .loader-ring div {{
        box-sizing: border-box;
        display: block;
        position: absolute;
        width: 64px;
        height: 64px;
        margin: 8px;
        border: 4px solid #10B981;
        border-radius: 50%;
        animation: loader-ring-anim 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
        border-color: #10B981 transparent transparent transparent;
    }}
    .loader-ring div:nth-child(1) {{
        animation-delay: -0.45s;
    }}
    .loader-ring div:nth-child(2) {{
        animation-delay: -0.3s;
    }}
    .loader-ring div:nth-child(3) {{
        animation-delay: -0.15s;
    }}
    @keyframes loader-ring-anim {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    .loader-title {{
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.65rem !important;
        font-weight: 800 !important;
        letter-spacing: 4px !important;
        color: #FFFFFF !important;
        margin-bottom: 6px !important;
        text-transform: uppercase !important;
    }}
    .loader-subtitle {{
        font-family: 'Inter', sans-serif !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: #4ADE80 !important;
        letter-spacing: 2px !important;
        margin-bottom: 24px !important;
        text-transform: uppercase !important;
    }}
    .loader-status {{
        font-family: 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
        color: #E2E8F0 !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 8px 18px !important;
        border-radius: 20px !important;
        letter-spacing: 0.5px !important;
        backdrop-filter: blur(4px) !important;
        animation: pulse 2s infinite ease-in-out !important;
    }}
    @keyframes pulse {{
        0% {{ opacity: 0.6; }}
        50% {{ opacity: 1; }}
        100% {{ opacity: 0.6; }}
    }}
    </style>
    <div class="premium-loader-overlay">
        <div class="loader-ring"><div></div><div></div><div></div><div></div></div>
        <div class="loader-title">AGRON</div>
        <div class="loader-subtitle">MANAGEMENT PORTAL</div>
        <div class="loader-status">{status_text}</div>
    </div>
    """
    st.markdown(loader_html, unsafe_allow_html=True)


# ─── Login Form ───────────────────────────────────────────────────────────────
def _render_login_screen() -> None:
    """Render the full-page branded SAF SHIKAN split-screen login screen."""
    login_placeholder = st.empty()
    with login_placeholder.container():
        st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800;900&display=swap');

    /* Hide standard streamlit header/sidebar/footer during login */
    header[data-testid="stHeader"], #MainMenu, footer, div[data-testid="stToolbar"] {
        display: none !important;
    }

    /* Remove standard block container margins and padding */
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100vw !important;
        overflow-x: hidden !important;
    }
    .stApp {
        background: #FFFFFF !important;
        overflow-x: hidden !important;
    }

    /* Horizontal block wrapper containing the 2 columns */
    div[data-testid="stHorizontalBlock"], div[data-testid="columns"] {
        gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100vw !important;
        min-height: 100vh !important;
        display: flex !important;
        align-items: stretch !important;
    }

    /* Column 1 (Left Column - White Form Area) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1),
    div[data-testid="stColumn"]:nth-of-type(1),
    div[data-testid="column"]:nth-of-type(1) {
        padding: 2.5rem 5vw !important;
        background: #FFFFFF !important;
        min-height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        border: none !important;
    }

    /* Column 2 (Right Column - Dark Green Hero Area) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2),
    div[data-testid="stColumn"]:nth-of-type(2),
    div[data-testid="column"]:nth-of-type(2) {
        padding: 0 !important;
        margin: 0 !important;
        background: linear-gradient(140deg, #05180c 0%, #0C3823 45%, #0e4e2f 100%) !important;
        min-height: 100vh !important;
        position: relative !important;
        overflow: hidden !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: none !important;
    }

    /* Responsive adjustment for screens narrower than 950px */
    @media (max-width: 950px) {
        div[data-testid="stHorizontalBlock"] > div:nth-child(1),
        div[data-testid="stColumn"]:nth-of-type(1),
        div[data-testid="column"]:nth-of-type(1) {
            padding: 3rem 2rem !important;
        }
        div[data-testid="stHorizontalBlock"] > div:nth-child(2),
        div[data-testid="stColumn"]:nth-of-type(2),
        div[data-testid="column"]:nth-of-type(2) {
            display: none !important;
        }
    }

    /* Form styling inside Left Column */
    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    /* Style form labels */
    div[data-testid="stForm"] label, div[data-testid="stForm"] p {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.76rem !important;
        font-weight: 700 !important;
        color: #64748B !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
        margin-bottom: 2px !important;
    }
    /* Style input boxes */
    div[data-testid="stForm"] input[type="text"],
    div[data-testid="stForm"] input[type="password"] {
        background-color: #EEF2F6 !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        height: 46px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        color: #0F172A !important;
        padding: 0 16px !important;
    }
    div[data-testid="stForm"] input[type="text"]:focus,
    div[data-testid="stForm"] input[type="password"]:focus {
        background-color: #FFFFFF !important;
        border-color: #0C3823 !important;
        box-shadow: 0 0 0 3px rgba(12,56,35,0.12) !important;
    }
    /* Style remember me checkbox container */
    div[data-testid="stForm"] div[data-testid="stCheckbox"] p {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        color: #64748B !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }
    /* Style Sign in button */
    div[data-testid="stForm"] button[kind="primaryFormSubmit"],
    div[data-testid="stForm"] button[type="submit"] {
        background: #0A3622 !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.02rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        height: 48px !important;
        margin-top: 10px !important;
        box-shadow: 0 6px 16px rgba(10,54,34,0.3) !important;
        letter-spacing: 0.4px !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover,
    div[data-testid="stForm"] button[type="submit"]:hover {
        background: #0E4B30 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 20px rgba(10,54,34,0.4) !important;
    }

    /* Right Hero Panel Concentric Circles & Elements */
    .radar-circle {
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 50%;
        pointer-events: none;
    }
    .circle-1 { width: 340px; height: 340px; }
    .circle-2 { width: 560px; height: 560px; }
    .circle-3 { width: 800px; height: 800px; border-color: rgba(255, 255, 255, 0.08); }
    .circle-4 { width: 1060px; height: 1060px; }

    .hero-content {
        position: relative;
        z-index: 5;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    .hero-logo-card {
        width: 240px; height: 240px;
        background: #FFFFFF;
        border-radius: 34px;
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 36px;
        position: relative;
    }
    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: 5px;
        margin-bottom: 6px;
        line-height: 1.1;
    }
    .hero-sub {
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        font-weight: 600;
        color: #4ADE80;
        letter-spacing: 4px;
        margin-bottom: 16px;
    }
    .hero-bar {
        width: 48px; height: 2.5px;
        background: #22C55E;
        border-radius: 2px;
    }
    .hero-footer {
        position: absolute;
        bottom: 1.8rem;
        left: 0; width: 100%;
        text-align: center;
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        color: rgba(255, 255, 255, 0.35);
        z-index: 5;
    }
    </style>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1.0, 1.35], gap="small")

    logo_b64 = _get_logo_base64()
    if logo_b64:
        logo_top_html = f'<img src="data:image/png;base64,{logo_b64}" style="width:26px; height:26px; object-fit:contain;" alt="SAF SHIKAN">'
        logo_card_html = f'<img src="data:image/png;base64,{logo_b64}" style="width:190px; height:190px; object-fit:contain;" alt="SAF SHIKAN Logo">'
    else:
        logo_top_html = '<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>'
        logo_card_html = '<svg viewBox="0 0 200 200" width="170" height="170"><circle cx="100" cy="100" r="90" fill="none" stroke="#0C3823" stroke-width="1.2" stroke-dasharray="4 3" opacity="0.4"/><circle cx="100" cy="100" r="80" fill="none" stroke="#0C3823" stroke-width="2"/><path d="M70,88 L130,88 L116,108 L84,108 Z" fill="#0C3823"/><path d="M54,78 C70,66 130,66 146,78" fill="none" stroke="#22c55e" stroke-width="3.2"/><ellipse cx="48" cy="78" rx="14" ry="4" fill="#0C3823"/><ellipse cx="152" cy="78" rx="14" ry="4" fill="#0C3823"/><ellipse cx="64" cy="118" rx="12" ry="3.5" fill="#0C3823"/><ellipse cx="136" cy="118" rx="12" ry="3.5" fill="#0C3823"/><line x1="61" y1="80" x2="80" y2="92" stroke="#0C3823" stroke-width="3.5"/><line x1="139" y1="80" x2="120" y2="92" stroke="#0C3823" stroke-width="3.5"/><text x="100" y="136" text-anchor="middle" font-family="\'Outfit\', sans-serif" font-weight="900" font-size="18" fill="#0C3823" letter-spacing="1">SAF SHIKAN</text><text x="100" y="152" text-anchor="middle" font-family="\'Inter\', sans-serif" font-weight="700" font-size="7.5" fill="#0C3823" letter-spacing="1.5">SUNDERING BARRIERS</text></svg>'

    with col_left:
        html_left_top = (
            '<div style="display:flex; align-items:center; gap:10px; margin-bottom:2.2rem;">'
            f'<div style="width:34px; height:34px; border-radius:50%; border:1.5px solid #0C3823; display:flex; align-items:center; justify-content:center; color:#0C3823; overflow:hidden;">{logo_top_html}</div>'
            '<span style="font-family:\'Outfit\',sans-serif; font-weight:800; font-size:1.25rem; color:#0C3823; letter-spacing:2px;">AGRON</span>'
            '</div>'
            '<div style="margin-bottom:1.5rem;">'
            '<h1 style="font-family:\'Outfit\',sans-serif; font-size:2.2rem; font-weight:800; color:#0F172A; margin:0 0 4px 0;">Welcome back</h1>'
            '<div style="font-size:0.92rem; color:#64748B; font-weight:500;">Log in to your account</div>'
            '</div>'
        )
        st.markdown(html_left_top, unsafe_allow_html=True)

        with st.form("saf_shikan_split_login", clear_on_submit=False):
            email = st.text_input(
                "LOGIN ID",
                placeholder="admin@safshikan.com",
                help="Use the email address registered by your AGRON system administrator."
            )
            password = st.text_input(
                "PASSWORD",
                type="password",
                placeholder="••••••••••••"
            )
            remember_me = st.checkbox("REMEMBER ME", value=False)
            submitted = st.form_submit_button(
                "Sign in",
                use_container_width=True,
                type="primary"
            )

        html_left_footer = (
            '<div style="margin-top:2.2rem; font-size:0.78rem; color:#94A3B8; font-weight:500; line-height:1.4;">'
            '© 2026 Saf Shikan Systems. Authorized personnel only.<br>'
            '<span style="font-size:0.74rem; color:#CBD5E1;">Forgot your password? Contact your AGRON system administrator.</span>'
            '</div>'
        )
        st.markdown(html_left_footer, unsafe_allow_html=True)

    with col_right:
        # Construct exact single-line unindented HTML string with full-bleed inline background to guarantee dark emerald hero panel
        html_right = (
            '<div style="width:100%; min-height:100vh; display:flex; align-items:center; justify-content:center; position:relative; overflow:hidden; background:linear-gradient(140deg, #05180c 0%, #0C3823 45%, #0e4e2f 100%); padding:2rem;">'
            '<div class="radar-circle circle-1"></div>'
            '<div class="radar-circle circle-2"></div>'
            '<div class="radar-circle circle-3"></div>'
            '<div class="radar-circle circle-4"></div>'
            '<div class="hero-content">'
            f'<div class="hero-logo-card">{logo_card_html}</div>'
            '<div class="hero-title">AGRON</div>'
            '<div class="hero-sub">MANAGEMENT PORTAL</div>'
            '<div class="hero-bar"></div>'
            '</div>'
            '<div class="hero-footer">© 2026 Saf Shikan Systems. Authorized personnel only.</div>'
            '</div>'
        )
        st.markdown(html_right, unsafe_allow_html=True)

    if submitted:
        if not email.strip() or not password:
            st.error("⚠️ Both LOGIN ID and PASSWORD are required.")
            return

        supabase = _get_supabase()
        if not supabase:
            st.error(
                "⚠️ Cannot connect to authentication server. "
                "Ensure `supabase_url` and `supabase_key` are set in Streamlit Secrets."
            )
            return

        status_placeholder = st.empty()
        with status_placeholder:
            _show_loader("Authenticating secure session...")

        try:
            response = supabase.auth.sign_in_with_password({
                "email": email.strip(),
                "password": password
            })
            if response and response.user:
                with status_placeholder:
                    _show_loader("Preparing database connections...")

                st.session_state["auth_user"] = {
                    "id":    response.user.id,
                    "email": response.user.email,
                    "role":  response.user.role or "authenticated",
                }
                if response.session:
                    st.session_state["auth_access_token"] = response.session.access_token
                st.session_state.pop("_transitioning", None)

                # Pre-warm cached data and audit logs inside the authentication spinner step
                try:
                    with status_placeholder:
                        _show_loader("Caching analytics & farmer registry...")
                    from data_loader import load_data
                    load_data()

                    with status_placeholder:
                        _show_loader("Synchronizing audit trail logs...")
                    from audit_logger import get_log_from_supabase
                    get_log_from_supabase(limit=200)
                except Exception:
                    pass

                with status_placeholder:
                    _show_loader("Opening AGRON dashboard...")
                st.rerun()
            else:
                status_placeholder.empty()
                st.error("❌ Invalid LOGIN ID or PASSWORD. Please try again.")
        except Exception as exc:
            status_placeholder.empty()
            msg = str(exc).lower()
            if any(kw in msg for kw in ("invalid", "credentials", "wrong", "not found", "email")):
                st.error("❌ Invalid LOGIN ID or PASSWORD.")
            else:
                st.error(f"❌ Authentication error: {exc}")

    st.markdown("""
    <div class='login-footer-text'>
        Forgot your password? Contact your AGRON system administrator.<br>
        <span style='font-size:0.7rem;opacity:0.6;'>All sessions are logged and audited.</span>
    </div>
    """, unsafe_allow_html=True)


# ─── Gatekeeper ──────────────────────────────────────────────────────────────
def require_auth() -> None:
    """Call at the top of app.py — shows login screen and stops execution if not authenticated."""
    if not get_current_user():
        _render_login_screen()
        st.stop()


