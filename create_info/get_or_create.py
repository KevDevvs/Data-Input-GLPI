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
    print(c(f"🔍 [BUSCA] Procurando modelo de {model_type}: '{model_name}'...", 'cyan'))
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
                    print(c(f"✅ [OK] Modelo '{model_name}' encontrado (ID: {item_id})", 'green'))
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
            print(c(f"✅ [OK] Modelo '{model_name}' encontrado via busca (ID: {item_id})", 'green'))
            return item_id
            
        # Se não encontrou, cria novo
        print(c(f"🆕 [CRIANDO] Novo modelo de {model_type}: '{model_name}'...", 'blue'))
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
                print(c(f"✅ [OK] Modelo '{model_name}' criado com sucesso (ID: {item_id})", 'green'))
                return item_id
        
        print(c(f"❌ [ERRO] Resposta inesperada ao criar modelo: {r.text}", 'red'))
        return None
        
    except Exception as e:
        print(c(f"❌ [ERRO] Falha ao buscar/criar modelo '{model_name}': {str(e)}", 'red'))
        return None

def get_or_create(session_token, endpoint, search_field, search_value, payload_extra=None):
    """
    Busca um item pelo campo especificado. Se não existir, cria o item.
    Retorna o ID do item encontrado ou criado.
    
    Args:
        session_token: Token da sessão GLPI
        endpoint: Endpoint da API (Entity, Group, User, etc)
        search_field: Campo a ser usado na busca
        search_value: Valor a ser buscado
        payload_extra: Dados adicionais para criação/busca (ex: entities_id)
    
    Returns:
        int: ID do item encontrado ou criado
        None: Se não foi possível encontrar ou criar o item
    """

    HEADERS = {
    "App-Token": APP_TOKEN,
    "Authorization": f"user_token {USER_TOKEN}"
}
    
    headers = {**HEADERS, "Session-Token": session_token}
        # Para grupos, tenta busca direta primeiro
    if endpoint == "Group":
        try:
            groups = requests.get(f"{GLPI_URL}/Group", headers=headers).json()
            if isinstance(groups, list):
                for group in groups:
                    if group.get("name") == search_value:
                        entity_id = group.get("entities_id")
                        if not payload_extra or not payload_extra.get("entities_id") or str(entity_id) == str(payload_extra.get("entities_id")):
                            found_id = int(group.get("id"))
                            print(c(f"✅ [OK] {endpoint} '{search_value}' encontrado (ID: {found_id})", 'green'))
                            return found_id
        except Exception as e:
            pass

    # Busca via API de busca
    params = {"criteria[0][field]": 1, "criteria[0][searchtype]": "equals", "criteria[0][value]": search_value}
    # Para entidades/grupos, busca também por entities_id se fornecido
    if endpoint in ["Entity", "Group"] and payload_extra and "entities_id" in payload_extra:
        params["criteria[1][field]"] = 4
        params["criteria[1][searchtype]"] = "equals"
        params["criteria[1][value]"] = payload_extra["entities_id"]
    search = requests.get(f"{GLPI_URL}/search/{endpoint}", headers=headers, params=params)
    resp = search.json()
    # Corrige caso a resposta seja uma lista inesperada
    if isinstance(resp, list):
        print(c(f"⚠️ [AVISO] Resposta inesperada da API (lista) ao buscar {endpoint} '{search_value}'. Buscando manualmente...", 'yellow'))
        for item in resp:
            if isinstance(item, dict):
                if (str(item.get("1", "")) == str(search_value)) or (item.get("name", "") == str(search_value)):
                    item_id = int(item.get("id", item.get("2", 0)))
                    print(f"✅ [OK] {endpoint} '{search_value}' encontrado (ID: {item_id})", 'green')
                    return item_id
        resp = {"totalcount": 0}
    if resp.get("totalcount", 0) > 0:
        item_id = int(resp["data"][0].get("id", resp["data"][0].get("2", 0)))
        print(f"✅ [OK] {endpoint} '{search_value}' encontrado (ID: {item_id})", 'green')
        return item_id
    # Para entidades, verifica se já existe via busca direta primeiro
    if endpoint == "Entity":
        try:
            entities_list = requests.get(f"{GLPI_URL}/Entity", headers=headers).json()
            if isinstance(entities_list, list):
                print(c(f"[DEBUG] Verificando na lista de {len(entities_list)} entidades antes de criar...", 'yellow'))
                for entity in entities_list:
                    if entity.get("name") == search_value:
                        parent_id = entity.get("entities_id", "") or entity.get("parent_id", "")
                        if not payload_extra or not payload_extra.get("entities_id") or str(parent_id) == str(payload_extra.get("entities_id")):
                            found_id = int(entity.get("id"))
                            print(c(f"✅ [OK] {endpoint} '{search_value}' já existe (ID: {found_id})", 'green'))
                            return found_id
        except Exception as e:
            print(c(f"[DEBUG] Erro na verificação prévia: {e}", 'yellow'))

    print(c(f"🆕 [CRIANDO] {endpoint} '{search_value}'...", 'blue'))
    payload = {"input": {search_field: search_value}}
    if payload_extra:
        payload["input"].update(payload_extra)
    r = requests.post(f"{GLPI_URL}/{endpoint}", headers=headers, json=payload)
    try:
        r.raise_for_status()
        item_id = r.json()["id"]
        print(c(f"✅ [OK] {endpoint} '{search_value}' criado (ID: {item_id})", 'green'))
        return item_id
    except Exception as e:
        print(c(f"❌ [ERRO] Não foi possível criar {endpoint} '{search_value}'. Resposta da API:", 'red'))
        print(r.text)
        # Se erro for de duplicidade, buscar novamente e retornar o ID
        if "já existe" in r.text or "already exists" in r.text or "Duplicate entry" in r.text:
            print(c(f"🔄 [BUSCA EXTRA] {endpoint} '{search_value}' já existe, buscando ID...", 'yellow'))
            # Busca manual considerando nome e parent (entities_id)
            search_params = {"criteria[0][field]": 1, "criteria[0][searchtype]": "equals", "criteria[0][value]": search_value}
            if endpoint in ["Entity", "Group"] and payload_extra and "entities_id" in payload_extra:
                search_params["criteria[1][field]"] = 4
                search_params["criteria[1][searchtype]"] = "equals"
                search_params["criteria[1][value]"] = payload_extra["entities_id"]
            search2 = requests.get(f"{GLPI_URL}/search/{endpoint}", headers=headers, params=search_params)
            print(c(f"[DEBUG] Resposta da busca por nome+parent: {search2.text}", 'yellow'))
            resp2 = search2.json()
            found_id = None
            if isinstance(resp2, list):
                for item in resp2:
                    if isinstance(item, dict):
                        nome_match = (str(item.get("1", "")) == str(search_value)) or (item.get("name", "") == str(search_value))
                        if not nome_match and "completename" in item:
                            nome_match = item["completename"].endswith(str(search_value))
                        if nome_match:
                            parent_id = item.get("entities_id") or item.get("4") or item.get("parent_id")
                            parent_match = True
                            if endpoint in ["Entity", "Group"] and payload_extra and "entities_id" in payload_extra:
                                parent_match = str(parent_id) == str(payload_extra["entities_id"])
                            if parent_match:
                                found_id = int(item.get("id", item.get("2", 0)))
                                break
                if found_id:
                    print(c(f"✅ [OK] {endpoint} '{search_value}' encontrado após erro (ID: {found_id})", 'green'))
                    return found_id
                print(c(f"❌ [ERRO] {endpoint} '{search_value}' não encontrado após erro de duplicidade.", 'red'))
                print(c(f"[DEBUG] Resposta da busca extra: {resp2}", 'yellow'))
                # Fallback: buscar todas entidades e filtrar manualmente por parent e nome
                if endpoint == "Entity" and payload_extra and "entities_id" in payload_extra:
                    print(c(f"[DEBUG] Fallback: buscando todas entidades e filtrando por parent ID {payload_extra['entities_id']} e nome '{search_value}'...", 'yellow'))
                    headers = {**HEADERS, "Session-Token": session_token}
                    resp_fallback = requests.get(f"{GLPI_URL}/search/Entity", headers=headers).json()
                    if resp_fallback.get("totalcount", 0) > 0:
                        for data in resp_fallback["data"]:
                            nome_match = (str(data.get("1", "")) == str(search_value)) or (data.get("name", "") == str(search_value))
                            parent_id = data.get("entities_id") or data.get("parent_id") or data.get("4")
                            parent_match = str(parent_id) == str(payload_extra["entities_id"])
                            if not nome_match and "completename" in data:
                                nome_match = data["completename"].endswith(str(search_value))
                            if nome_match and parent_match:
                                fallback_id = int(data.get("id", data.get("2", 0)))
                                print(c(f"✅ [OK] {endpoint} '{search_value}' encontrado via fallback (ID: {fallback_id})", 'green'))
                                return fallback_id
                    print(c(f"❌ [ERRO] {endpoint} '{search_value}' não encontrado via fallback.", 'red'))
            elif resp2.get("totalcount", 0) > 0:
                for data in resp2["data"]:
                    nome_match = (str(data.get("1", "")) == str(search_value)) or (data.get("name", "") == str(search_value))
                    if not nome_match and "completename" in data:
                        nome_match = data["completename"].endswith(str(search_value))
                    if nome_match:
                        parent_id = data.get("entities_id") or data.get("4") or data.get("parent_id")
                        parent_match = True
                        if endpoint in ["Entity", "Group"] and payload_extra and "entities_id" in payload_extra:
                            parent_match = str(parent_id) == str(payload_extra["entities_id"])
                        if parent_match:
                            found_id = int(data.get("id", data.get("2", 0)))
                            break
                if found_id:
                    print(c(f"✅ [OK] {endpoint} '{search_value}' encontrado após erro (ID: {found_id})", 'green'))
                    return found_id
                print(c(f"❌ [ERRO] {endpoint} '{search_value}' não encontrado após erro de duplicidade.", 'red'))
                print(c(f"[DEBUG] Resposta da busca extra: {resp2}", 'yellow'))
            # Busca direta na API
            print(c(f"[DEBUG] Tentando busca direta via API...", 'yellow'))
            if endpoint == "Entity":
                try:
                    all_entities = requests.get(f"{GLPI_URL}/Entity", headers=headers).json()
                    if isinstance(all_entities, list):
                                    # Primeiro procura por correspondência exata de nome e parent
                        for entity in all_entities:
                            nome = entity.get("name", "")
                            eid = entity.get("id", "")
                            parent = entity.get("entities_id", "") or entity.get("parent_id", "") or entity.get("4", "")
                            if nome == search_value:
                                if not payload_extra or not payload_extra.get("entities_id") or str(parent) == str(payload_extra.get("entities_id", "")):
                                    print(c(f"✅ [OK] Entity '{search_value}' encontrado via API direta (ID: {eid})", 'green'))
                                    return int(eid)
                        # Se não encontrou, imprime todas para debug
                                    # Debug listing removed for cleaner output
                except Exception as e:
                    print(c(f"[DEBUG] Erro na busca direta: {e}", 'yellow'))

            # Se busca direta falhar, tenta busca alternativa
            print(c(f"[DEBUG] Tentando busca alternativa com diferentes campos...", 'yellow'))
            for field in ["name", "1", "2", "completename"]:
                alt_search_params = {"criteria[0][field]": field, "criteria[0][searchtype]": "equals", "criteria[0][value]": search_value}
                if endpoint == "Entity" and payload_extra and "entities_id" in payload_extra:
                    alt_search_params.update({
                        "criteria[1][link]": "AND",
                        "criteria[1][field]": "entities_id",
                        "criteria[1][searchtype]": "equals",
                        "criteria[1][value]": payload_extra["entities_id"]
                    })
                alt_search_response = requests.get(f"{GLPI_URL}/search/{endpoint}", headers=headers, params=alt_search_params)
                print(c(f"[DEBUG] Resposta da busca alternativa (campo {field}): {alt_search_response.text}", 'yellow'))
            try:
                alt_resp = alt_search_response.json()
                if isinstance(alt_resp, list) and len(alt_resp) > 0:
                    for item in alt_resp:
                        if isinstance(item, dict):
                            nome = item.get("name", item.get("1", ""))
                            eid = item.get("id", item.get("2", ""))
                            parent = item.get("entities_id", "") or item.get("parent_id", "") or item.get("4", "")
                            if nome == search_value and str(parent) == str(payload_extra.get("entities_id", "")):
                                print(c(f"✅ [OK] {endpoint} '{search_value}' encontrado via busca alternativa (ID: {eid})", 'green'))
                                return int(eid)
                elif alt_resp.get("totalcount", 0) > 0:
                    for data in alt_resp["data"]:
                        nome = data.get("name", data.get("1", ""))
                        eid = data.get("2", data.get("id", ""))
                        parent = data.get("entities_id", "") or data.get("parent_id", "") or data.get("4", "")
                        if nome == search_value and str(parent) == str(payload_extra.get("entities_id", "")):
                            print(c(f"✅ [OK] {endpoint} '{search_value}' encontrado via busca alternativa (ID: {eid})", 'green'))
                            return int(eid)
                elif alt_resp.get("totalcount", 0) > 0:
                    print(c(f"[DEBUG] Itens retornados na busca alternativa:", 'yellow'))
                    for data in alt_resp["data"]:
                        nome = data.get("name", data.get("1", ""))
                        eid = data.get("id", data.get("2", ""))
                        parent = data.get("entities_id", data.get("parent_id", ""))
                        print(c(f"  - Nome: {nome} | ID: {eid} | Parent: {parent}", 'yellow'))
                        nome_match = (str(data.get("1", "")) == str(search_value)) or (nome == str(search_value))
                        if not nome_match and "completename" in data:
                            nome_match = data["completename"].endswith(str(search_value))
                        if nome_match:
                            alt_found_id = int(eid)
                    if alt_found_id:
                        print(c(f"✅ [OK] {endpoint} '{search_value}' encontrado (ID: {alt_found_id}) [busca alternativa]", 'green'))
                        return alt_found_id
            except Exception as e:
                print(c(f"[DEBUG] Erro ao processar resposta JSON alternativa: {e}", 'yellow'))
            print(c(f"❌ [ERRO] {endpoint} '{search_value}' não encontrado após erro de duplicidade.", 'red'))
            return None