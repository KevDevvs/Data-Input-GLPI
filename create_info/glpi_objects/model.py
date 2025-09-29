from helper.read_config import APP_TOKEN, USER_TOKEN, GLPI_URL
import requests
from helper.colors import c

def get_or_create_model(session_token, model_name, model_type):
    """
    Busca ou cria um modelo no GLPI.
    
    Args:
        session_token: Token da sessão GLPI
        model_name: Nome do modelo a ser buscado/criado
        model_type: Tipo do modelo ('Phone' ou 'Computer')
        
    Returns:
        int: ID do modelo encontrado ou criado
        None: Se não foi possível encontrar ou criar o modelo
    """
    model_endpoint = f"{model_type}Model"  # PhoneModel ou ComputerModel
    headers = {
        "App-Token": APP_TOKEN,
        "Authorization": f"user_token {USER_TOKEN}",
        "Session-Token": session_token
    }
    
    try:
        # Primeiro tenta buscar diretamente todos os modelos
        response = requests.get(f"{GLPI_URL}/{model_endpoint}", headers=headers)
        items_list = response.json()
        
        # Procura na lista
        if isinstance(items_list, list):
            for item in items_list:
                if item.get("name") == model_name:
                    item_id = int(item["id"])
                    return item_id
        
        # Se não encontrou, tenta via search
        search_params = {
            "criteria[0][field]": "name",
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": model_name
        }
        
        search = requests.get(f"{GLPI_URL}/search/{model_endpoint}", headers=headers, params=search_params)
        resp = search.json()
        
        if isinstance(resp, dict) and resp.get("totalcount", 0) > 0:
            item_id = int(resp["data"][0].get("2", 0))
            return item_id
            
        # Se não encontrou, cria novo
        payload = {
            "input": {
                "name": model_name
            }
        }
        
        r = requests.post(f"{GLPI_URL}/{model_endpoint}", headers=headers, json=payload)
        r.raise_for_status()
        
        response_data = r.json()
        if isinstance(response_data, dict):
            item_id = response_data.get("id")
            if item_id:
                return item_id
        
        print(c(f"❌ [ERRO] Resposta inesperada ao criar modelo: {r.text}", 'red'))
        return None
        
    except Exception as e:
        print(c(f"❌ [ERRO] Falha ao buscar/criar modelo '{model_name}': {str(e)}", 'red'))
        return None
