from helper.read_config import APP_TOKEN, USER_TOKEN, GLPI_URL
import requests
from helper.colors import c

def get_or_create(session_token, endpoint, search_field, search_value, payload_extra=None, search_options=None):
    """
    Busca um item pelo campo especificado. Se não existir, cria o item.
    Retorna o ID do item encontrado ou criado.
    
    Args:
        session_token: Token da sessão GLPI
        endpoint: Endpoint da API (Entity, Group, User, etc)
        search_field: Campo a ser usado na busca
        search_value: Valor a ser buscado
        payload_extra: Dados adicionais para criação/busca (ex: entities_id, is_recursive)
        search_options: Opções adicionais para busca (ex: is_recursive, parent_entities)
    
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
    
    # Adiciona parâmetros de busca recursiva se necessário
    if search_options and search_options.get("is_recursive"):
        params["is_recursive"] = 1
    
    # Para entidades/grupos/operadoras, busca também por entities_id se fornecido
    if endpoint in ["Entity", "Group", "LineOperator"] and payload_extra and "entities_id" in payload_extra:
        params["criteria[1][field]"] = 80  # entities_id
        params["criteria[1][searchtype]"] = "equals"
        params["criteria[1][value]"] = payload_extra["entities_id"]
        
    # Se necessário buscar em entidades pai
    if search_options and search_options.get("parent_entities"):
        params["criteria[2][link]"] = "OR"
        params["criteria[2][criteria][0][field]"] = 80  # entities_id
        params["criteria[2][criteria][0][searchtype]"] = "equals"
        params["criteria[2][criteria][0][value]"] = 0  # Root entity
    
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
            
            # Debug listing removed for cleaner output
        print(c(f"❌ [ERRO] {endpoint} '{search_value}' não encontrado após erro de duplicidade.", 'red'))
        return None
