import requests
from helper.read_config import GLPI_URL, HEADERS, APP_TOKEN, USER_TOKEN, HEADERS


def kill_session(session_token):
    """Encerra a sessão na API do GLPI."""
    requests.get(f"{GLPI_URL}/killSession", headers={**HEADERS, "Session-Token": session_token})

def init_session():
    """Inicia uma sessão na API do GLPI e retorna o token de sessão."""
    r = requests.get(f"{GLPI_URL}/initSession", headers=HEADERS)
    r.raise_for_status()
    return r.json()["session_token"]

