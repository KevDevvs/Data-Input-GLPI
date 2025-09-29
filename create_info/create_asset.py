
import requests
from time import sleep
from helper.read_config import GLPI_URL, HEADERS
from helper.colors import c

def create_asset(session_token, asset_type, payload):
    """
    Cria ou atualiza um ativo (Line, Phone, Computer) vinculado à entidade e usuário.
    Retorna o ID do ativo criado ou atualizado.
    """
    headers = {**HEADERS, "Session-Token": session_token}
    print(c(f"💻 Processando {asset_type}...", 'yellow'))
    search_value = payload.get("name")
    
    try:
        # Primeiro verifica se o ativo já existe
        users_id = payload.get("users_id", 0)
        search_params = {
            "criteria[0][field]": 1,
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": search_value
        }
        
        # Adiciona critério de usuário para Lines
        if asset_type == "Line":
            search_params.update({
                "criteria[1][link]": "AND",
                "criteria[1][field]": 70,
                "criteria[1][searchtype]": "equals",
                "criteria[1][value]": users_id
            })
        
        # Busca o ativo
        search = requests.get(f"{GLPI_URL}/search/{asset_type}", headers=headers, params=search_params)
        resp = search.json()
        
        # Se encontrou, atualiza
        if resp.get("totalcount", 0) > 0:
            asset_id = int(resp["data"][0].get("id", resp["data"][0].get("2", 0)))
            requests.put(f"{GLPI_URL}/{asset_type}/{asset_id}", headers=headers, json={"input": payload})
            print(c(f"✅ {asset_type} atualizado", 'green'))
            return asset_id
        
        # Se não encontrou, cria
        else:
            r = requests.post(f"{GLPI_URL}/{asset_type}", headers=headers, json={"input": payload})

            # verifica criação
            re_try = 3
            while re_try > 0:
                print(c(f"⏳ Verificando criação de {asset_type}, tentativa {4 - re_try}/3...", 'yellow'))
                sleep(3)
                asset_id = r.json().get("id")
                if asset_id:
                    print(c(f"✅ {asset_type} criado", 'green'))
                    return asset_id
                re_try -= 1
                
        return None
        
    except Exception as e:
        if "Duplicate entry" in str(e) or "already exists" in str(e):
            print(c(f"✅ {asset_type} processado", 'green'))
            return True
            
        print(c(f"❌ Erro ao processar {asset_type}", 'red'))
        return None
