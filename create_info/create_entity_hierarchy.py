
from create_info.get_or_create import get_or_create
import requests
from helper.read_config import GLPI_URL, APP_TOKEN, USER_TOKEN, HEADERS
from helper.colors import c


def create_entity_hierarchy(session_token, entidade_a, entidade_b=None, entidade_c=None, entidade_d=None):
    """
    Cria entidades em cascata (até 4 níveis) e retorna o ID da entidade mais profunda criada.
    """
    print(c("🏢 Criando hierarquia de entidades", 'yellow'))

    eid_a = get_or_create(session_token, "Entity", "name", entidade_a)
    if eid_a is None:
        print(c(f"❌ Falha ao criar/encontrar '{entidade_a}'", 'red'))
        return None
    
    eid_b = None
    if entidade_b:
        eid_b = get_or_create(session_token, "Entity", "name", entidade_b, {"entities_id": eid_a})
        if not eid_b:
            print(c(f"❌ Falha ao criar/encontrar '{entidade_b}'", 'red'))
            return eid_a
    
    eid_c = None
    if entidade_c:
        eid_c = get_or_create(session_token, "Entity", "name", entidade_c, {"entities_id": eid_b})
        if not eid_c:
            print(c(f"❌ Falha ao criar/encontrar '{entidade_c}'", 'red'))
            return eid_b if eid_b is not None else eid_a
        
    eid_d = None
    if entidade_d:
        eid_d = get_or_create(session_token, "Entity", "name", entidade_d, {"entities_id": eid_c})
        if not eid_d:
            print(c(f"❌ Falha ao criar/encontrar '{entidade_d}'", 'red'))
            return eid_c if eid_c is not None else (eid_b if eid_b is not None else eid_a)

    # Retorna o ID da entidade mais profunda criada
    return eid_d or eid_c or eid_b or eid_a

