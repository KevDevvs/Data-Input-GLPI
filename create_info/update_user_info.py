
import requests
from helper.read_config import APP_TOKEN, USER_TOKEN, GLPI_URL, GROUP_ID, HEADERS
from helper.colors import c


def update_user_info(session_token, user_id, user_data, entity_id, profile_id, email=None):
    """
    Função auxiliar para atualizar as informações do usuário após a criação
    """
    headers = {**HEADERS, "Session-Token": session_token}
    
    # 1. Atualiza dados básicos
    basic_update = {
        "input": {
            "id": user_id,
            "firstname": user_data.get("firstname"),
            "realname": user_data.get("realname"),
            "entities_id": entity_id,
            "is_active": 1
        }
    }
    
    if email:
        basic_update["input"]["email"] = email
    
    r_basic = requests.put(f"{GLPI_URL}/User/{user_id}", headers=headers, json=basic_update)
    # 2. Vincula o perfil
    profile_payload = {
        "input": {
            "users_id": user_id,
            "profiles_id": profile_id,
            "entities_id": entity_id,
            "is_recursive": 0
        }
    }
    r_profile = requests.post(f"{GLPI_URL}/Profile_User", headers=headers, json=profile_payload)
    
    # 3. Vincula o grupo
    if GROUP_ID:
        group_payload = {
            "input": {
                "users_id": user_id,
                "groups_id": GROUP_ID,
                "entities_id": entity_id
            }
        }
        r_group = requests.post(f"{GLPI_URL}/Group_User", headers=headers, json=group_payload)
        
    # 4. Adiciona email via UserEmail se fornecido
    if email:
        email_payload = {
            "input": {
                "users_id": user_id,
                "email": email,
                "is_default": 1
            }
        }
        r_email = requests.post(f"{GLPI_URL}/UserEmail", headers=headers, json=email_payload)
        if r_email.status_code in [200, 201]:
            print(c(f"✅ Email vinculado com sucesso: {email}", 'green'))
        
        # Se falhar, tenta atualizar email diretamente
        if r_email.status_code not in [200, 201]:
            email_update = {
                "input": {
                    "id": user_id,
                    "_useremails": [{"email": email}]
                }
            }
            r_email_alt = requests.put(f"{GLPI_URL}/User/{user_id}", headers=headers, json=email_update)
            if r_email_alt.status_code == 200:
                print(c(f"✅ Email atualizado com sucesso através do método alternativo", 'green'))
    
    return True

