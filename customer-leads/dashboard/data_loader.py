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
    create_client = None   # type: ignore[assignment]
    Client = None          # type: ignore[assignment]

# ─── Supabase Config (safe with defaults) ─────────────────────────────────────
try:
    SUPABASE_URL   = st.secrets.get("supabase_url", "")
    SUPABASE_KEY   = st.secrets.get("supabase_key", "")
    SUPABASE_TABLE = st.secrets.get("supabase_table", "farmer")
except Exception:
    SUPABASE_URL   = ""
    SUPABASE_KEY   = ""
    SUPABASE_TABLE = "farmer"

_REQUIRED_COLS = [
    "Name", "Phone", "Crop_Type", "Crop_Area",
    "Season", "Location", "Farm_Scale", "Region"
]

_REFRESH_INTERVAL = 30   # seconds between background refreshes

# ─── In-Memory Live Store (lazy-initialized on first access) ──────────────────
# Using a module-level dict with a Lock so the store is fully initialized
# before any thread can read or write it.
_store_lock  = threading.Lock()
_store_ready = threading.Event()
_store_df: pd.DataFrame = pd.DataFrame(columns=_REQUIRED_COLS)


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
        seen = {SUPABASE_TABLE}
        candidates = [SUPABASE_TABLE] + [t for t in ("farmer", "farmers") if t not in seen]
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
    """Daemon thread: populates the store on startup then refreshes every 30 s."""
    global _store_df

    # Initial fetch
    fresh = _fetch_from_supabase()
    with _store_lock:
        _store_df = fresh
    _store_ready.set()

    # Continuous silent refresh loop — never crashes the daemon
    while True:
        time.sleep(_REFRESH_INTERVAL)
        try:
            fresh = _fetch_from_supabase()
            if not fresh.empty:
                with _store_lock:
                    _store_df = fresh
        except Exception:
            pass


# ─── Public API ───────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def start_live_cache() -> None:
    """Launch the background refresh thread exactly once per server process.

    @st.cache_resource guarantees this runs only once, even with multiple
    concurrent browser sessions.  Blocks up to 8 s for the initial fetch.
    """
    t = threading.Thread(
        target=_background_worker,
        name="saf-shikan-live-cache",
        daemon=True,
    )
    t.start()
    _store_ready.wait(timeout=8)


def load_data() -> pd.DataFrame:
    """Return the live in-memory farmer DataFrame (< 1 ms, zero network calls).

    If start_live_cache() has not been called yet, returns whatever is currently
    in the store (empty DataFrame on first boot, populated after first call).
    """
    with _store_lock:
        return _store_df.copy()


def invalidate_live_cache() -> None:
    """Trigger an immediate background re-fetch (call after saving a new farmer)."""
    global _store_df

    def _refresh_now() -> None:
        global _store_df
        try:
            fresh = _fetch_from_supabase()
            if not fresh.empty:
                with _store_lock:
                    _store_df = fresh
        except Exception:
            pass

    threading.Thread(target=_refresh_now, daemon=True, name="saf-cache-invalidate").start()


# ── Supabase client accessor (used by save_new_row in app.py) ─────────────────
@st.cache_resource(show_spinner=False)
def get_supabase_client():
    """Return an authenticated Supabase client using Streamlit secrets."""
    if not SUPABASE_URL or not SUPABASE_KEY or create_client is None:
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None
