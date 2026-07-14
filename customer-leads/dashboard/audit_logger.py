"""Audit Logger for SAF SHIKAN Farmer Portal.

Records all significant user actions (page views, filter applications, 
data exports) to a persistent audit trail stored in session state and 
optionally written to a log file.

Actions Tracked:
    - PAGE_VIEW   : Tab/page opened
    - FILTER_APPLY: Search or dropdown filter changed
    - DATA_EXPORT : CSV or Excel export triggered
    - SYSTEM      : App startup events
"""

import json
import os
import socket
from datetime import datetime, timezone
from typing import Literal

import streamlit as st

# Type alias for valid audit event categories
AuditEventType = Literal[
    "PAGE_VIEW",
    "FILTER_APPLY",
    "DATA_EXPORT",
    "SYSTEM"
]


def _session_id() -> str:
    """Return a stable session ID for the current browser session.
    
    Uses Streamlit session state to persist a generated ID across reruns.
    
    Returns:
        6-character hex session identifier string.
    """
    if "audit_session_id" not in st.session_state:
        import uuid
        st.session_state["audit_session_id"] = uuid.uuid4().hex[:8].upper()
    return st.session_state["audit_session_id"]


def _now_utc() -> str:
    """Return current UTC timestamp in ISO 8601 format.
    
    Returns:
        ISO 8601 UTC timestamp string (e.g. '2024-07-14T10:22:31Z').
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_display() -> str:
    """Return current UTC timestamp in human-readable display format.
    
    Returns:
        Human-readable timestamp string (e.g. '14 Jul 2024 · 10:22:31 UTC').
    """
    return datetime.now(timezone.utc).strftime("%d %b %Y · %H:%M:%S UTC")


def _ensure_log_list() -> None:
    """Ensure the audit log list exists in Streamlit session state."""
    if "audit_log" not in st.session_state:
        st.session_state["audit_log"] = []


def log_event(
    event_type: AuditEventType,
    description: str,
    details: dict | None = None
) -> None:
    """Record an audit event to the session-scoped audit trail.
    
    Args:
        event_type: Category of the event (PAGE_VIEW, FILTER_APPLY, DATA_EXPORT, SYSTEM).
        description: Human-readable one-line summary of the action.
        details: Optional dict of additional structured context (e.g. filter values, record counts).
    """
    _ensure_log_list()

    entry = {
        "id":          f"{_session_id()}-{len(st.session_state['audit_log']) + 1:04d}",
        "session":     _session_id(),
        "timestamp":   _now_utc(),
        "display_ts":  _now_display(),
        "event_type":  event_type,
        "description": description,
        "details":     details or {}
    }

    st.session_state["audit_log"].append(entry)


def get_log() -> list[dict]:
    """Return all audit log entries for the current session, newest first.
    
    Returns:
        Reversed list of audit log entry dicts.
    """
    _ensure_log_list()
    return list(reversed(st.session_state["audit_log"]))


def get_log_as_csv() -> str:
    """Serialise the current session audit log to CSV string format.
    
    Returns:
        CSV-formatted string of all audit events.
    """
    entries = get_log()
    if not entries:
        return "id,session,timestamp,event_type,description,details\n"
    
    rows = ["id,session,timestamp,event_type,description,details"]
    for e in entries:
        details_str = json.dumps(e["details"]).replace('"', '""')
        rows.append(
            f'{e["id"]},{e["session"]},{e["timestamp"]},{e["event_type"]},'
            f'"{e["description"]}","{details_str}"'
        )
    return "\n".join(rows)


def get_log_counts() -> dict[str, int]:
    """Return counts of events by type for the current session.
    
    Returns:
        Dict mapping event_type -> count.
    """
    _ensure_log_list()
    counts: dict[str, int] = {}
    for entry in st.session_state["audit_log"]:
        counts[entry["event_type"]] = counts.get(entry["event_type"], 0) + 1
    return counts


# ─── Event Type Styling Map ───────────────────────────────────────────────────
EVENT_CONFIG = {
    "PAGE_VIEW":    {"icon": "→",  "color": "#3B82F6", "bg": "#DBEAFE", "label": "Page View"},
    "FILTER_APPLY": {"icon": "≡",  "color": "#8B5CF6", "bg": "#EDE9FE", "label": "Filter"},
    "DATA_EXPORT":  {"icon": "↓",  "color": "#059669", "bg": "#D1FAE5", "label": "Export"},
    "SYSTEM":       {"icon": "◉",  "color": "#64748B", "bg": "#F1F5F9", "label": "System"},
}
