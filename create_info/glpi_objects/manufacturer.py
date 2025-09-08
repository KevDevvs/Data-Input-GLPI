from helper.read_config import APP_TOKEN, USER_TOKEN, GLPI_URL
import requests
from helper.colors import c

def get_or_create_manufacturer(session_token, manufacturer_name):
    """
    Busca ou cria um fabricante no GLPI.
    
    Args:
        session_token: Token da sessão GLPI
        manufacturer_name: Nome do fabricante a ser buscado/criado
        
    Returns:
        int: ID do fabricante encontrado ou criado
        None: Se não foi possível encontrar ou criar o fabricante
    """
    print(c(f"🔍 [BUSCA] Procurando fabricante: '{manufacturer_name}'...", 'cyan'))
    headers = {
        "App-Token": APP_TOKEN,
        "Authorization": f"user_token {USER_TOKEN}",
        "Session-Token": session_token
    }
    
    try:
        # Primeiro tenta buscar diretamente todos os fabricantes
        response = requests.get(f"{GLPI_URL}/Manufacturer", headers=headers)
        items_list = response.json()
        
        # Procura na lista
        if isinstance(items_list, list):
            for item in items_list:
                if item.get("name") == manufacturer_name:
                    item_id = int(item["id"])
                    print(c(f"✅ [OK] Fabricante '{manufacturer_name}' encontrado (ID: {item_id})", 'green'))
                    return item_id
        
        # Se não encontrou, tenta via search
        search_params = {
            "criteria[0][field]": "name",
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": manufacturer_name
        }
        
        search = requests.get(f"{GLPI_URL}/search/Manufacturer", headers=headers, params=search_params)
        resp = search.json()
        
        if isinstance(resp, dict) and resp.get("totalcount", 0) > 0:
            item_id = int(resp["data"][0].get("2", 0))
            print(c(f"✅ [OK] Fabricante '{manufacturer_name}' encontrado via busca (ID: {item_id})", 'green'))
            return item_id
            
        # Se não encontrou, cria novo
        print(c(f"🆕 [CRIANDO] Novo fabricante: '{manufacturer_name}'...", 'blue'))
        payload = {
            "input": {
                "name": manufacturer_name
            }
        }
        
        r = requests.post(f"{GLPI_URL}/Manufacturer", headers=headers, json=payload)
        r.raise_for_status()
        
        response_data = r.json()
        if isinstance(response_data, dict):
            item_id = response_data.get("id")
            if item_id:
                print(c(f"✅ [OK] Fabricante '{manufacturer_name}' criado com sucesso (ID: {item_id})", 'green'))
                return item_id
        
        print(c(f"❌ [ERRO] Resposta inesperada ao criar fabricante: {r.text}", 'red'))
        return None
        
    except Exception as e:
        print(c(f"❌ [ERRO] Falha ao buscar/criar fabricante '{manufacturer_name}': {str(e)}", 'red'))
        return None
