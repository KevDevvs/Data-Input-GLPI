
import requests
from time import sleep
from helper.read_config import GLPI_URL, HEADERS
from helper.colors import c

def create_asset(session_token, asset_type, payload):
    """
    Cria ou atualiza um ativo (Line, Phone, Computer) vinculado à entidade e usuário.
    Retorna uma tupla (asset_id, error_message).
    """
    headers = {**HEADERS, "Session-Token": session_token}
    print(c(f"💻 Processando {asset_type}...", 'yellow'))
    
    # Log de debug para verificar o payload
    print(c(f"🔍 DEBUG - Payload para {asset_type}: {payload}", 'cyan'))
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
            # Verifica se data[0] é um dicionário ou uma lista
            data_item = resp["data"][0]
            if isinstance(data_item, dict):
                asset_id = int(data_item.get("id", data_item.get("2", 0)))
            elif isinstance(data_item, list) and len(data_item) > 2:
                # Se for lista, o ID geralmente está na posição 2
                asset_id = int(data_item[2]) if data_item[2] else 0
            else:
                # Fallback: busca qualquer valor numérico válido
                asset_id = None
                for item in (data_item if isinstance(data_item, list) else [data_item]):
                    if isinstance(item, (int, str)) and str(item).isdigit():
                        asset_id = int(item)
                        break
                if not asset_id:
                    asset_id = 0
            
            if asset_id > 0:
                requests.put(f"{GLPI_URL}/{asset_type}/{asset_id}", headers=headers, json={"input": payload})
                print(c(f"✅ {asset_type} atualizado", 'green'))
                return asset_id, None
            else:
                print(c(f"⚠️ ID inválido encontrado para {asset_type}, criando novo...", 'yellow'))
                # Continua para criação
        
        # Se não encontrou ou ID inválido, cria novo
        r = requests.post(f"{GLPI_URL}/{asset_type}", headers=headers, json={"input": payload})

        # verifica criação
        re_try = 3
        while re_try > 0:
            print(c(f"⏳ Verificando criação de {asset_type}, tentativa {4 - re_try}/3...", 'yellow'))
            response_data = r.json()
            
            # Verifica se a resposta é um dicionário ou lista
            asset_id = None
            if isinstance(response_data, dict):
                asset_id = response_data.get("id")
            elif isinstance(response_data, list) and len(response_data) > 0:
                # Se for lista, verifica se o primeiro item tem ID
                first_item = response_data[0]
                if isinstance(first_item, dict):
                    asset_id = first_item.get("id")
                elif len(response_data) >= 3:
                    # Se tem pelo menos 3 itens, o ID geralmente está na posição 2 (índice 2)
                    third_item = response_data[2]
                    if isinstance(third_item, (int, str)) and str(third_item).isdigit():
                        asset_id = int(third_item)
                elif isinstance(first_item, (int, str)) and str(first_item).isdigit():
                    asset_id = int(first_item)
            
            if asset_id:
                print(c(f"✅ {asset_type} criado", 'green'))
                return asset_id, None
            re_try -= 1
            sleep(1)

                
        return None, "Falha na criação após tentativas"
        
    except Exception as e:
        if "Duplicate entry" in str(e) or "already exists" in str(e):
            print(c(f"✅ {asset_type} processado", 'green'))
            return True, None
            
        print(c(f"❌ Erro ao processar {asset_type}", 'red'))
        return None, f"Erro: {str(e)}"
