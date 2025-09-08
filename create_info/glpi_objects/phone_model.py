from helper.read_config import APP_TOKEN, USER_TOKEN, GLPI_URL
import requests
from helper.colors import c

def get_or_create_phone_model(session_token, model_name):
    """
    Busca ou cria um modelo de telefone no GLPI.
    
    Args:
        session_token: Token da sessão GLPI
        model_name: Nome do modelo a ser buscado/criado
        
    Returns:
        int: ID do modelo encontrado ou criado
        None: Se não foi possível encontrar ou criar o modelo
    """
    print(c(f"🔍 [BUSCA] Procurando modelo de telefone: '{model_name}'...", 'cyan'))
    headers = {
        "App-Token": APP_TOKEN,
        "Authorization": f"user_token {USER_TOKEN}",
        "Session-Token": session_token
    }
    
    try:
        # Primeiro tenta buscar diretamente todos os modelos
        models_response = requests.get(f"{GLPI_URL}/PhoneModel", headers=headers)
        models_list = models_response.json()
        
        # Procura na lista de modelos
        if isinstance(models_list, list):
            for model in models_list:
                if model.get("name") == model_name:
                    model_id = int(model["id"])
                    print(c(f"✅ [OK] Modelo '{model_name}' encontrado (ID: {model_id})", 'green'))
                    return model_id
        
        # Se não encontrou, tenta via search
        search_params = {
            "criteria[0][field]": "name",
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": model_name
        }
        
        search = requests.get(f"{GLPI_URL}/search/PhoneModel", headers=headers, params=search_params)
        resp = search.json()
        
        if isinstance(resp, dict) and resp.get("totalcount", 0) > 0:
            model_id = int(resp["data"][0].get("2", 0))
            print(c(f"✅ [OK] Modelo '{model_name}' encontrado via busca (ID: {model_id})", 'green'))
            return model_id
            
        # Se não encontrou, cria novo modelo
        print(c(f"🆕 [CRIANDO] Novo modelo de telefone: '{model_name}'...", 'blue'))
        payload = {
            "input": {
                "name": model_name
            }
        }
        
        r = requests.post(f"{GLPI_URL}/PhoneModel", headers=headers, json=payload)
        r.raise_for_status()
        
        response_data = r.json()
        if isinstance(response_data, dict):
            model_id = response_data.get("id")
            if model_id:
                print(c(f"✅ [OK] Modelo '{model_name}' criado com sucesso (ID: {model_id})", 'green'))
                return model_id
        
        print(c(f"❌ [ERRO] Resposta inesperada ao criar modelo: {r.text}", 'red'))
        return None
        
    except Exception as e:
        print(c(f"❌ [ERRO] Falha ao buscar/criar modelo '{model_name}': {str(e)}", 'red'))
        return None
