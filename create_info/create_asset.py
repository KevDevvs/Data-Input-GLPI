
import requests
from helper.read_config import GLPI_URL, HEADERS
from helper.colors import c

def create_asset(session_token, asset_type, payload):
    """
    Cria ou atualiza um ativo (Line, Phone, Computer) vinculado à entidade e usuário.
    Retorna o ID do ativo criado ou atualizado.
    """
    headers = {**HEADERS, "Session-Token": session_token}
    print(c("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", 'yellow'))
    print(c(f"💻 [ETAPA] Criando ativo do tipo {asset_type}...", 'yellow'))
    search_value = payload.get("name")
    
    # Parâmetros de busca específicos para Lines
    if asset_type == "Line":
        users_id = payload.get("users_id", 0)
        search_params = {
            "criteria[0][field]": 1,  # name
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": search_value,
            "criteria[1][link]": "AND",
            "criteria[1][field]": 70,  # users_id
            "criteria[1][searchtype]": "equals",
            "criteria[1][value]": users_id
        }
    else:
        search_params = {
            "criteria[0][field]": 1,
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": search_value
        }
    
    search = requests.get(f"{GLPI_URL}/search/{asset_type}", headers=headers, params=search_params)
    resp = search.json()
    if resp.get("totalcount", 0) > 0:
        asset_id = int(resp["data"][0].get("id", resp["data"][0].get("2", 0)))
        print(c(f"♻️ [OK] {asset_type} '{search_value}' já existe (ID: {asset_id}), atualizando...", 'green'))
        requests.put(f"{GLPI_URL}/{asset_type}/{asset_id}", headers=headers, json={"input": payload})
        return asset_id
    print(c(f"🆕 [CRIANDO] {asset_type} '{search_value}'...", 'blue'))
    r = requests.post(f"{GLPI_URL}/{asset_type}", headers=headers, json={"input": payload})
    try:
        r.raise_for_status()
        asset_id = r.json()["id"]
        print(c(f"✅ [OK] {asset_type} '{search_value}' criado (ID: {asset_id})", 'green'))
        return asset_id
    except Exception as e:
        print(c(f"❌ [ERRO] Não foi possível criar {asset_type} '{search_value}'. Resposta da API:", 'red'))
        print(r.text)
        raise
