"""Leitura de ambiente e secrets da aplicação."""
import os
import logging
import streamlit as st

logger = logging.getLogger(__name__)

_PLACEHOLDER_MARKERS = (
    "cole_aqui",
    "cole_a_",
    "xxxxxxxx",
    "seu-projeto",
    "sua_chave",
    "your_",
    "change_me",
    "placeholder",
)


def is_development_environment() -> bool:
    """
    True quando ENVIRONMENT=development/dev ou [general].environment no secrets.toml.
    """
    env = os.getenv("ENVIRONMENT", "").lower().strip()
    if env in ("development", "dev"):
        return True
    if env in ("production", "prod"):
        return False

    try:
        if hasattr(st, "secrets") and "general" in st.secrets:
            env_config = str(st.secrets["general"].get("environment", "")).lower().strip()
            if env_config in ("development", "dev"):
                return True
            if env_config in ("production", "prod"):
                return False
    except Exception as e:
        logger.warning("Erro ao ler environment do secrets.toml: %s", e)

    return False


def _looks_placeholder(value) -> bool:
    if value is None:
        return True
    text = str(value).strip()
    if not text:
        return True
    lower = text.lower()
    return any(marker in lower for marker in _PLACEHOLDER_MARKERS)


def has_supabase_credentials() -> bool:
    """True se URL e chave do Supabase existem e não são placeholders."""
    try:
        cfg = st.secrets["connections"]["supabase"]
        url = cfg.get("SUPABASE_URL", "")
        key = cfg.get("SUPABASE_SERVICE_KEY") or cfg.get("SUPABASE_KEY", "")
        if _looks_placeholder(url) or _looks_placeholder(key):
            return False
        return bool(url) and bool(key)
    except Exception:
        return False


def has_google_credentials() -> bool:
    """True se a service account do BigQuery existe e não é placeholder."""
    try:
        google = st.secrets["google"]
        key = google.get("private_key", "")
        project = google.get("project_id", "")
        email = google.get("client_email", "")
        if _looks_placeholder(key) or _looks_placeholder(project) or _looks_placeholder(email):
            return False
        if "BEGIN PRIVATE KEY" not in str(key):
            return False
        return True
    except Exception:
        return False
