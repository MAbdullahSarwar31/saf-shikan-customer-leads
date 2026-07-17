"""Data Ingestion & Loading Module for SAF SHIKAN Farmer Portal.

Live-cache architecture: farmer data is fetched once from Supabase on startup,
stored in a thread-safe in-memory store, and refreshed every 30 seconds by a
daemon background thread.  load_data() returns the in-memory DataFrame in
< 1 ms — no blocking network call on filter / search interactions.
"""

import threading
import time
import pandas as pd
import streamlit as st

try:
    from supabase import create_client, Client
except ImportError:
    create_client, Client = None, None  # type: ignore[assignment]

SUPABASE_URL   = st.secrets.get("supabase_url", "")
SUPABASE_KEY   = st.secrets.get("supabase_key", "")
SUPABASE_TABLE = st.secrets.get("supabase_table", "farmer")

_REQUIRED_COLS = [
    "Name", "Phone", "Crop_Type", "Crop_Area",
    "Season", "Location", "Farm_Scale", "Region"
]

# ─── In-Memory Live Store ──────────────────────────────────────────────────────
# Shared between the main Streamlit thread and the background refresh thread.
# Guarded by a threading.Lock so reads and writes are always consistent.
_LIVE_STORE: dict = {
    "df":    pd.DataFrame(columns=_REQUIRED_COLS),
    "lock":  threading.Lock(),
    "ready": threading.Event(),   # set once the initial fetch completes
}

_REFRESH_INTERVAL = 30   # seconds between background refreshes


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _clean_df(raw: pd.DataFrame) -> pd.DataFrame:
    """Normalize a raw Supabase DataFrame to standard column types."""
    for col in _REQUIRED_COLS:
        if col not in raw.columns:
            raw[col] = ""
    df = raw[_REQUIRED_COLS].copy()
    df["Crop_Type"]  = df["Crop_Type"].astype(str).str.title()
    df["Season"]     = df["Season"].astype(str).str.strip()
    df["Region"]     = df["Region"].astype(str).str.strip()
    df["Location"]   = df["Location"].astype(str).str.strip()
    df["Farm_Scale"] = df["Farm_Scale"].astype(str).str.strip()
    df["Crop_Area"]  = pd.to_numeric(df["Crop_Area"], errors="coerce").fillna(0.0)
    return df


def _fetch_from_supabase() -> pd.DataFrame:
    """Single HTTP fetch of all farmer records from Supabase. Returns empty df on failure."""
    if not SUPABASE_URL or not SUPABASE_KEY or create_client is None:
        return pd.DataFrame(columns=_REQUIRED_COLS)
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        candidates = [SUPABASE_TABLE] + [t for t in ("farmer", "farmers") if t != SUPABASE_TABLE]
        for tbl in candidates:
            try:
                resp = client.table(tbl).select(
                    "Name, Phone, Crop_Type, Crop_Area, Season, Location, Farm_Scale, Region"
                ).execute()
                if resp.data:
                    return _clean_df(pd.DataFrame(resp.data))
            except Exception:
                continue
    except Exception:
        pass
    return pd.DataFrame(columns=_REQUIRED_COLS)


# ─── Background Refresh Worker ─────────────────────────────────────────────────

def _background_worker() -> None:
    """Daemon thread: populates _LIVE_STORE on startup then refreshes every 30s."""
    # Initial fetch — blocks the calling start_live_cache() until complete
    fresh = _fetch_from_supabase()
    with _LIVE_STORE["lock"]:
        _LIVE_STORE["df"] = fresh
    _LIVE_STORE["ready"].set()

    # Continuous silent refresh loop
    while True:
        time.sleep(_REFRESH_INTERVAL)
        try:
            fresh = _fetch_from_supabase()
            if not fresh.empty:
                with _LIVE_STORE["lock"]:
                    _LIVE_STORE["df"] = fresh
        except Exception:
            pass   # never crash the daemon; retry on next cycle


# ─── Public API ───────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def start_live_cache() -> None:
    """Launch the background refresh thread exactly once per server process.

    @st.cache_resource guarantees this is called only once, even when multiple
    browser sessions are open simultaneously.  Blocks for up to 8 seconds while
    the initial Supabase fetch completes so that load_data() is never empty on
    first render.
    """
    thread = threading.Thread(
        target=_background_worker,
        name="saf-shikan-live-cache",
        daemon=True,
    )
    thread.start()
    # Wait for the initial fetch to finish (up to 8 s fallback)
    _LIVE_STORE["ready"].wait(timeout=8)


def load_data() -> pd.DataFrame:
    """Return the live in-memory farmer DataFrame.

    This is a pure memory read (< 1 ms) — no network call is made.
    Data is at most _REFRESH_INTERVAL seconds stale.
    """
    with _LIVE_STORE["lock"]:
        return _LIVE_STORE["df"].copy()


def invalidate_live_cache() -> None:
    """Force an immediate background refresh (call after a new farmer is saved)."""
    def _refresh_now():
        fresh = _fetch_from_supabase()
        if not fresh.empty:
            with _LIVE_STORE["lock"]:
                _LIVE_STORE["df"] = fresh

    threading.Thread(target=_refresh_now, daemon=True, name="saf-cache-invalidate").start()


# ── Supabase client accessor (used by save_new_row in app.py) ─────────────────
@st.cache_resource(show_spinner=False)
def get_supabase_client() -> "Client | None":
    """Return an authenticated Supabase client using Streamlit secrets."""
    if not SUPABASE_URL or not SUPABASE_KEY or create_client is None:
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None
