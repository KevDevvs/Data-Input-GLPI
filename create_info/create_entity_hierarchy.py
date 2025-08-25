
from create_info.get_or_create import get_or_create
import requests
from helper.read_config import GLPI_URL, APP_TOKEN, USER_TOKEN, HEADERS
from helper.colors import c


def create_entity_hierarchy(session_token, entidade_a, entidade_b=None, entidade_c=None, entidade_d=None):
    """
    Cria entidades em cascata (até 4 níveis) e retorna o ID da entidade mais profunda criada.
    """
    print(c("\n🏢 Processando hierarquia de entidades...", 'yellow'))
    eid_a = get_or_create(session_token, "Entity", "name", entidade_a)
    if eid_a is None:
        print(c(f"❌ [ERRO] Não foi possível criar ou encontrar a entidade A '{entidade_a}'. Hierarquia abortada.", 'red'))
        return None
    # Busca entidade B antes de criar, para evitar duplicidade
    eid_b = None
    if entidade_b:
        print(c(f"🔎 [BUSCA] Procurando/reativando Entity B '{entidade_b}' sob '{entidade_a}'...", 'cyan'))
        eid_b = get_or_create(session_token, "Entity", "name", entidade_b, {"entities_id": eid_a})
        if eid_b:
            print(c(f"♻️ [INFO] Entity B '{entidade_b}' será reutilizada para entidades C filhas.", 'yellow'))
        else:
            print(c(f"❌ [ERRO] Não foi possível criar ou encontrar a entidade B '{entidade_b}'. Hierarquia abortada.", 'red'))
            return eid_a
    # Cria entidade C como filha de B
    eid_c = None
    if entidade_c:
        print(c(f"🔎 [BUSCA] Procurando ou criando Entity C '{entidade_c}' sob Entity B '{entidade_b}' (ID: {eid_b})...", 'cyan'))
        # Busca manual por entidade C sob o parent correto
        headers = {**HEADERS, "Session-Token": session_token}
        params_c = {"criteria[0][field]": 1, "criteria[0][searchtype]": "equals", "criteria[0][value]": entidade_c,
                    "criteria[1][field]": 4, "criteria[1][searchtype]": "equals", "criteria[1][value]": eid_b}
        search_c = requests.get(f"{GLPI_URL}/search/Entity", headers=headers, params=params_c)
        resp_c = search_c.json()
        if resp_c.get("totalcount", 0) > 0:
            eid_c = int(resp_c["data"][0].get("id", resp_c["data"][0].get("2", 0)))
            print(c(f"♻️ [INFO] Entity C '{entidade_c}' já existe sob Entity B '{entidade_b}' (ID: {eid_c}). Reutilizando.", 'yellow'))
        else:
            eid_c = get_or_create(session_token, "Entity", "name", entidade_c, {"entities_id": eid_b})
            if eid_c:
                print(c(f"✅ [OK] Entity C '{entidade_c}' criada sob Entity B '{entidade_b}' (ID: {eid_b}).", 'green'))
            else:
                print(c(f"❌ [ERRO] Não foi possível criar ou encontrar a entidade C '{entidade_c}'. Hierarquia abortada.", 'red'))
                return eid_b if eid_b is not None else eid_a
    eid_d = None
    if entidade_d:
        print(c(f"🔎 [BUSCA] Criando Entity D '{entidade_d}' sob '{entidade_c}'...", 'cyan'))
        eid_d = get_or_create(session_token, "Entity", "name", entidade_d, {"entities_id": eid_c})
        if eid_d:
            print(c(f"✅ [OK] Entity D '{entidade_d}' criada/reutilizada sob '{entidade_c}'.", 'green'))
        else:
            print(c(f"❌ [ERRO] Não foi possível criar ou encontrar a entidade D '{entidade_d}'. Hierarquia abortada.", 'red'))
            return eid_c if eid_c is not None else (eid_b if eid_b is not None else eid_a)
    # Retorna o ID da entidade mais profunda criada
    return eid_d or eid_c or eid_b or eid_a

