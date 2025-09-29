
import requests
from helper.read_config import GLPI_URL, GROUP_ID, HEADERS
from helper.colors import c


def create_user(session_token, name, email, profile_id, entity_id, status_user, cpf=None):

    print(c(f"\n👤 Processando usuário '{name}'", 'yellow'))

    headers = {**HEADERS, "Session-Token": session_token}

    # Processa o nome para firstname e realname
    name_parts = name.strip().split(' ')
    if not name_parts:
        print(c("❌ Nome inválido", 'red'))
        return None

    if not email or not email.startswith("@"):
        print(c("❌ Email não fornecido", 'red'))
        return None
    
    # Usa o email completo como login
    login = email.lstrip("@")
    if not login or '@' not in login:
        print(c("❌ Email inválido", 'red'))
        return None

    # Busca se o usuário já existe
    search_params = {
        "criteria[0][field]": "1",  # campo name
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": login
    }
    search_response = requests.get(f"{GLPI_URL}/search/User", headers=headers, params=search_params)
    
    user_id = None
    if search_response.status_code in [200, 206]:
        search_data = search_response.json()
        if isinstance(search_data, dict) and search_data.get("totalcount", 0) > 0:
            user_id = int(search_data["data"][0].get("2", search_data["data"][0].get("id")))
            print(c(f"✅ [OK] Usuário encontrado (ID: {user_id})", 'green'))
    else:
        print(c(f"⚠️ [AVISO] Erro ao processar resposta da busca", 'yellow'))
    
    if not user_id:
        # Prepara os dados do usuário
        user_data = {
            "name": login,
            "firstname": name_parts[0],
            "realname": ' '.join(name_parts[1:]) if len(name_parts) > 1 else "",
            "password": "Ch@nge.me123",
            "password2": "Ch@nge.me123",
            "entities_id": entity_id,
            "profiles_id": profile_id,
            "is_active": 1,
            "authtype": 1,
            "groups_id": GROUP_ID,
            "usercategories_id": status_user,  # Categoria "Ativo"
            "registration_number": cpf if cpf else ""  # Campo Administrative Number
        }

        # Cria usuário com dados básicos
        r = requests.post(f"{GLPI_URL}/User", headers=headers, json={"input": user_data})
        
        # Tenta obter o ID do usuário criado
        if r.status_code in [200, 201]:
            response_data = r.json()
            user_id = response_data.get("id")
        else:
            print(c("❌ Falha ao criar usuário", 'red'))
            return None


    if user_id:
        # Vincula o usuário ao perfil
        profile_payload = {
            "input": {
                "users_id": user_id,
                "profiles_id": profile_id,
                "entities_id": entity_id,
                "is_recursive": 0
            }
        }

        r_profile = requests.post(f"{GLPI_URL}/Profile_User", headers=headers, json=profile_payload)
        if r_profile.status_code not in [200, 201]:
            print(c("⚠️ Erro ao vincular perfil", 'yellow'))

        # Vincula o usuário ao grupo
        group_payload = {
            "input": {
                "users_id": user_id,
                "groups_id": GROUP_ID,
                "entities_id": entity_id
            }
        }
        r_group = requests.post(f"{GLPI_URL}/Group_User", headers=headers, json=group_payload)
        if r_group.status_code not in [200, 201]:
            # Verifica se o erro é porque o usuário já está no grupo
            if "Duplicate entry" not in str(r_group.text) and "already exists" not in str(r_group.text):
                print(c("⚠️ Erro ao vincular grupo", 'yellow'))

        # Adiciona ou atualiza o email
        if email and email.startswith("@"):
            email = email.lstrip("@")
            if email and "@" in email:
                # Tenta os diferentes métodos de vinculação de email
                email_payload = {
                    "input": {
                        "users_id": user_id,
                        "email": email,
                        "is_default": 1
                    }
                }
                r_email = requests.post(f"{GLPI_URL}/UserEmail", headers=headers, json=email_payload)
                
                if r_email.status_code not in [200, 201]:
                    # Tenta atualização direta no usuário se o primeiro método falhar
                    email_update = {"input": {"id": user_id, "email": email}}
                    r_email_direct = requests.put(f"{GLPI_URL}/User/{user_id}", headers=headers, json=email_update)
                    
                    if r_email_direct.status_code not in [200, 201]:
                        print(c("⚠️ Erro ao vincular email", 'yellow'))

        print(c("✅ Usuário processado com sucesso", 'green'))
    return user_id

