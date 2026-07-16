"""Audit Logger for SAF SHIKAN Farmer Portal — Supabase-Persistent Edition.

Records all significant user actions to:
  1. st.session_state["audit_log"]  — same-session fast display
  2. Supabase `audit_log` table     — cross-session, persistent, multi-user

Actions Tracked:
    PAGE_VIEW    — Tab/page opened
    FILTER_APPLY — Search or dropdown filter changed
    DATA_EXPORT  — CSV or Excel export triggered
    DATA_ENTRY   — New farmer record committed
    LOGIN        — Successful user authentication
    LOGOUT       — User signed out
    SYSTEM       — App startup / system events
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Literal

import streamlit as st

# ─── Type Alias ───────────────────────────────────────────────────────────────
AuditEventType = Literal[
    "PAGE_VIEW",
    "FILTER_APPLY",
    "DATA_EXPORT",
    "DATA_ENTRY",
    "LOGIN",
    "LOGOUT",
    "SYSTEM",
]


# ─── Internal Helpers ─────────────────────────────────────────────────────────
def _session_id() -> str:
    """Return a stable session ID for the current browser session."""
    if "audit_session_id" not in st.session_state:
        st.session_state["audit_session_id"] = uuid.uuid4().hex[:8].upper()
    return st.session_state["audit_session_id"]


def _now_utc() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_display() -> str:
    """Return current UTC timestamp in human-readable display format."""
    return datetime.now(timezone.utc).strftime("%d %b %Y · %H:%M:%S UTC")


def _current_user_email() -> str:
    """Return the logged-in user's email from session state, or 'anonymous'."""
    user = st.session_state.get("auth_user", {})
    return user.get("email", "anonymous") if user else "anonymous"


def _ensure_log_list() -> None:
    """Ensure the audit log list exists in Streamlit session state."""
    if "audit_log" not in st.session_state:
        st.session_state["audit_log"] = []


import threading

@st.cache_resource(show_spinner=False)
def _get_supabase_client():
    """Create and return a cached Supabase client from Streamlit secrets. Returns None on failure."""
    url = st.secrets.get("supabase_url", "")
    key = st.secrets.get("supabase_key", "")
    if not url or not key:
        return None
    try:
        from supabase import create_client
        return create_client(url, key)
    except Exception:
        return None


# ─── Supabase Write ───────────────────────────────────────────────────────────
def _write_to_supabase_worker(entry: dict) -> None:
    """Background thread worker to write audit entry to Supabase without blocking UI."""
    supabase = _get_supabase_client()
    if not supabase:
        return
    try:
        supabase.table("audit_log").insert({
            "session_id":  entry["session"],
            "user_email":  entry["user_email"],
            "event_type":  entry["event_type"],
            "description": entry["description"],
            "details":     entry["details"],
        }).execute()
    except Exception:
        pass


def _write_to_supabase(entry: dict) -> None:
    """Write a single audit entry to Supabase asynchronously in a background daemon thread."""
    threading.Thread(target=_write_to_supabase_worker, args=(entry,), daemon=True).start()


# ─── Public API ───────────────────────────────────────────────────────────────
def log_event(
    event_type: AuditEventType,
    description: str,
    details: "dict | None" = None
) -> None:
    """Record an audit event to session state AND Supabase (persistent cross-session log).

    Args:
        event_type:  Category of the event.
        description: Human-readable one-line summary of the action.
        details:     Optional dict of additional structured context.
    """
    _ensure_log_list()

    entry = {
        "id":          f"{_session_id()}-{len(st.session_state['audit_log']) + 1:04d}",
        "session":     _session_id(),
        "user_email":  _current_user_email(),
        "timestamp":   _now_utc(),
        "display_ts":  _now_display(),
        "event_type":  event_type,
        "description": description,
        "details":     details or {}
    }

    # 1. Local session state — instant UI display
    st.session_state["audit_log"].append(entry)

    # 2. Supabase persistent write — non-blocking background thread
    _write_to_supabase(entry)


def get_log() -> "list[dict]":
    """Return all audit log entries for the current session, newest first."""
    _ensure_log_list()
    return list(reversed(st.session_state["audit_log"]))


@st.cache_data(ttl=60, show_spinner=False)
def get_log_from_supabase(limit: int = 200) -> "list[dict]":
    """Fetch the last N audit entries from the Supabase audit_log table (all sessions/users).

    Returns:
        List of audit entry dicts, newest first. Empty list on failure.
    """
    supabase = _get_supabase_client()

    if not supabase:
        return []
    try:
        response = (
            supabase.table("audit_log")
            .select("id, session_id, user_email, event_type, description, details, created_at")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        if response.data:
            rows = []
            for row in response.data:
                # Normalise to match the same shape as session-state entries
                rows.append({
                    "id":          str(row.get("id", "")),
                    "session":     row.get("session_id", ""),
                    "user_email":  row.get("user_email", "anonymous"),
                    "timestamp":   row.get("created_at", ""),
                    "display_ts":  _format_supabase_ts(row.get("created_at", "")),
                    "event_type":  row.get("event_type", ""),
                    "description": row.get("description", ""),
                    "details":     row.get("details") or {}
                })
            return rows
        return []
    except Exception:
        return []


def _format_supabase_ts(ts_str: str) -> str:
    """Convert a Supabase ISO timestamp string to human-readable display format."""
    if not ts_str:
        return ""
    try:
        # Supabase returns: "2025-07-16T09:30:00+00:00" or "2025-07-16T09:30:00Z"
        ts_str = ts_str.replace("+00:00", "Z")
        if "." in ts_str:
            ts_str = ts_str.split(".")[0] + "Z"
        dt = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return dt.strftime("%d %b %Y · %H:%M:%S UTC")
    except Exception:
        return ts_str


def get_log_as_csv(use_supabase: bool = True) -> str:
    """Serialise the audit log to CSV format.

    Args:
        use_supabase: If True, exports from Supabase (cross-session); else session-only.

    Returns:
        CSV-formatted string of all audit events.
    """
    entries = get_log_from_supabase(limit=1000) if use_supabase else get_log()
    if not entries:
        return "id,session_id,user_email,timestamp,event_type,description,details\n"

    rows = ["id,session_id,user_email,timestamp,event_type,description,details"]
    for e in entries:
        details_str = json.dumps(e.get("details", {})).replace('"', '""')
        rows.append(
            f'{e["id"]},{e["session"]},{e["user_email"]},{e["timestamp"]},'
            f'{e["event_type"]},"{e["description"]}","{details_str}"'
        )
    return "\n".join(rows)


def get_log_counts() -> "dict[str, int]":
    """Return counts of events by type for the current session."""
    _ensure_log_list()
    counts: dict[str, int] = {}
    for entry in st.session_state["audit_log"]:
        counts[entry["event_type"]] = counts.get(entry["event_type"], 0) + 1
    return counts


# ─── Event Type Styling Map ───────────────────────────────────────────────────
EVENT_CONFIG = {
    "PAGE_VIEW":    {"icon": "👁️",  "color": "#3B82F6", "bg": "#DBEAFE", "label": "Page View"},
    "FILTER_APPLY": {"icon": "🔍",  "color": "#8B5CF6", "bg": "#EDE9FE", "label": "Filter"},
    "DATA_EXPORT":  {"icon": "📥",  "color": "#059669", "bg": "#D1FAE5", "label": "Export"},
    "DATA_ENTRY":   {"icon": "➕",  "color": "#10B981", "bg": "#D1FAE5", "label": "Data Entry"},
    "LOGIN":        {"icon": "🔐",  "color": "#0C3823", "bg": "#DCFCE7", "label": "Login"},
    "LOGOUT":       {"icon": "🚪",  "color": "#EF4444", "bg": "#FEE2E2", "label": "Logout"},
    "SYSTEM":       {"icon": "🛡️", "color": "#64748B", "bg": "#F1F5F9", "label": "System"},
}
