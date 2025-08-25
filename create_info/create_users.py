
import requests
from helper.read_config import GLPI_URL, APP_TOKEN, USER_TOKEN, GROUP_ID, HEADERS
from helper.colors import c


def create_user(session_token, name, group, profile_id, entity_id):
    """
    Cria usuário e configura suas permissões.
    
    Args:
        session_token: Token da sessão GLPI
        name: Nome do usuário
        group: Nome do grupo ou email (se começar com @)
        profile_id: ID do perfil a ser associado
        entity_id: ID da entidade onde o usuário será criado
    
    Returns:
        int: ID do usuário criado/encontrado
        None: Se houve erro na criação
    """
    print(c("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", 'yellow'))
    print(c(f"👤 [ETAPA] Criando usuário '{name}'...", 'yellow'))

    # Validações iniciais
    if not profile_id:
        profile_id = 1  # Perfil Self-Service como fallback
        print(c(f"⚠️ [AVISO] Profile ID não fornecido para '{name}'. Usando perfil Self-Service (ID: {profile_id}).", 'yellow'))
    
    if not GROUP_ID:
        print(c(f"❌ [ERRO] GROUP_ID global não definido!", 'red'))
        return None

    headers = {**HEADERS, "Session-Token": session_token}

    # Processa o nome para firstname e realname
    name_parts = name.strip().split(' ')
    if not name_parts:
        print(c(f"❌ [ERRO] Nome do usuário inválido: {name}", 'red'))
        return None

    # Verifica se temos um email válido para usar como login
    if not group or not group.startswith("@"):
        print(c(f"❌ [ERRO] Email não fornecido para o usuário: {name}", 'red'))
        return None
    
    # Usa o email completo como login
    login = group.lstrip("@")
    if not login or '@' not in login:
        print(c(f"❌ [ERRO] Email inválido fornecido para o usuário: {name}", 'red'))
        return None
        
    print(c(f"🔑 [INFO] Login definido como email: {login}", 'cyan'))

    # Busca se o usuário já existe
    print(c(f"🔎 Verificando usuário: {login}", 'cyan'))
    search_params = {
        "criteria[0][field]": "1",  # campo name
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": login
    }
    search_response = requests.get(f"{GLPI_URL}/search/User", headers=headers, params=search_params)
    
    user_id = None
    if search_response.status_code in [200, 206]:
        try:
            search_data = search_response.json()
            if isinstance(search_data, dict) and search_data.get("totalcount", 0) > 0:
                user_id = int(search_data["data"][0].get("2", search_data["data"][0].get("id")))
                print(c(f"✅ [OK] Usuário encontrado (ID: {user_id})", 'green'))
        except Exception as e:
            print(c(f"⚠️ [AVISO] Erro ao processar resposta da busca: {e}", 'yellow'))
    
    if not user_id:
        # Prepara dados completos para criação
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
            "groups_id": GROUP_ID
        }

        # Cria o usuário primeiro sem o email
        try:
            print(c(f"🆕 Criando novo usuário...", 'blue'))
            
            # Primeira tentativa: criar usuário com dados básicos
            r = requests.post(f"{GLPI_URL}/User", headers=headers, json={"input": user_data})
                    # Verifica status da criação)
            
            # Se o usuário foi criado com sucesso e temos um email para adicionar
            if r.status_code in [200, 201] and group and group.startswith("@"):
                email = group.lstrip("@")
                if email and "@" in email:
                    user_id = r.json().get("id")
                    if user_id:
                        # Adiciona o email em uma requisição separada
                        email_data = {
                            "input": {
                                "users_id": user_id,
                                "email": email,
                                "is_default": 1
                            }
                        }
                        email_r = requests.post(f"{GLPI_URL}/UserEmail", headers=headers, json=email_data)
                        if email_r.status_code in [200, 201]:
                            print(c(f"📧 Email configurado: {email}", 'green'))
                        else:
                            print(c(f"⚠️ Não foi possível configurar o email", 'yellow'))
            
            if r.status_code in [200, 201]:
                try:
                    # Primeiro tenta pegar o ID da resposta direta
                    user_id = None
                    if r.text.strip():
                        try:
                            response_data = r.json()
                            if isinstance(response_data, dict) and "id" in response_data:
                                user_id = response_data["id"]
                                print(c(f"✅ [OK] ID obtido da resposta: {user_id}", 'green'))
                        except:
                            pass
                    
                    # Se não conseguiu o ID da resposta, tenta várias abordagens de busca
                    if not user_id:
                        users_response = requests.get(f"{GLPI_URL}/User", headers=headers)
                        if users_response.status_code == 200:
                            users = users_response.json()
                            if isinstance(users, list):
                                for user in users:
                                    if user.get("name") == login:
                                        user_id = int(user["id"])
                                        print(c(f"✅ [OK] Usuário encontrado (ID: {user_id})", 'green'))
                                        break
                        
                        # Método 2: Busca via endpoint de pesquisa
                        if not user_id:
                            print(c(f"[DEBUG] Método 2: Busca via search...", 'yellow'))
                            search_params = {
                                "criteria[0][field]": "1",
                                "criteria[0][searchtype]": "equals",
                                "criteria[0][value]": login
                            }
                            search_response = requests.get(
                                f"{GLPI_URL}/search/User",
                                headers=headers,
                                params=search_params
                            )
                            
                            if search_response.status_code in [200, 206]:
                                try:
                                    search_data = search_response.json()
                                    if isinstance(search_data, dict) and search_data.get("totalcount", 0) > 0:
                                        user_id = int(search_data["data"][0].get("2", search_data["data"][0].get("id")))
                                        print(c(f"✅ [OK] ID encontrado via search: {user_id}", 'green'))
                                except Exception as e:
                                    print(c(f"[DEBUG] Erro ao processar resposta search: {str(e)}", 'yellow'))
                        
                        # Método 3: Busca pelo nome completo
                        if not user_id:
                            print(c(f"[DEBUG] Método 3: Busca por nome completo...", 'yellow'))
                            search_params = {
                                "criteria[0][field]": "firstname",
                                "criteria[0][searchtype]": "equals",
                                "criteria[0][value]": user_data["firstname"],
                                "criteria[1][link]": "AND",
                                "criteria[1][field]": "realname",
                                "criteria[1][searchtype]": "equals",
                                "criteria[1][value]": user_data["realname"]
                            }
                            name_search = requests.get(
                                f"{GLPI_URL}/search/User",
                                headers=headers,
                                params=search_params
                            )
                            
                            if name_search.status_code in [200, 206]:
                                try:
                                    name_data = name_search.json()
                                    if isinstance(name_data, dict) and name_data.get("totalcount", 0) > 0:
                                        user_id = int(name_data["data"][0].get("2", name_data["data"][0].get("id")))
                                        print(c(f"✅ [OK] ID encontrado via nome completo: {user_id}", 'green'))
                                except Exception as e:
                                    print(c(f"[DEBUG] Erro ao processar resposta nome: {str(e)}", 'yellow'))
                    
                    if user_id:
                        print(c(f"✅ [OK] Usuário criado com sucesso (ID: {user_id})", 'green'))
                    else:
                        print(c(f"❌ [ERRO] Não foi possível obter o ID do usuário criado", 'red'))
                        return None
                except Exception as e:
                    print(c(f"❌ [ERRO] Falha ao processar resposta: {str(e)}", 'red'))
                    print(c(f"[DEBUG] Resposta completa: {r.text}", 'yellow'))
                    return None
            else:
                print(c(f"❌ [ERRO] Falha ao criar usuário: {r.text}", 'red'))
                return None
        except Exception as e:
            print(c(f"❌ [ERRO] Exceção ao criar usuário: {str(e)}", 'red'))
            print(c(f"[DEBUG] Tentando identificar o problema...", 'yellow'))
            try:
                print(c(f"[DEBUG] Status code: {r.status_code}", 'yellow'))
                print(c(f"[DEBUG] Resposta completa: {r.text}", 'yellow'))
            except:
                pass
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
        if r_profile.status_code in [200, 201]:
            print(c(f"✅ [OK] Perfil vinculado com sucesso!", 'green'))
        else:
            print(c(f"⚠️ [AVISO] Erro ao vincular perfil: {r_profile.text}", 'yellow'))

        # Vincula o usuário ao grupo
        group_payload = {
            "input": {
                "users_id": user_id,
                "groups_id": GROUP_ID,
                "entities_id": entity_id
            }
        }
        r_group = requests.post(f"{GLPI_URL}/Group_User", headers=headers, json=group_payload)
        if r_group.status_code in [200, 201]:
            print(c(f"✅ [OK] Grupo vinculado com sucesso!", 'green'))
        else:
            print(c(f"⚠️ [AVISO] Erro ao vincular grupo: {r_group.text}", 'yellow'))

        # Adiciona ou atualiza o email se necessário
        if group and group.startswith("@"):
            email = group.lstrip("@")
            if email and "@" in email:
                print(c(f"📧 [DEBUG] Iniciando processo de vinculação de email '{email}' para usuário {user_id}...", 'cyan'))
                
                # Tenta todas as abordagens possíveis
                
                # 1. Atualização direta no usuário
                print(c(f"🔄 [DEBUG] Tentativa 1: Atualização direta do usuário...", 'cyan'))
                email_update = {
                    "input": {
                        "id": user_id,
                        "email": email
                    }
                }
                r_email_direct = requests.put(f"{GLPI_URL}/User/{user_id}", headers=headers, json=email_update)
                # 2. Vinculação via UserEmail
                email_payload = {
                    "input": {
                        "users_id": user_id,
                        "email": email,
                        "is_default": 1
                    }
                }
                r_email = requests.post(f"{GLPI_URL}/UserEmail", headers=headers, json=email_payload)
                # 3. Atualização com array de emails se necessário
                email_array_update = {
                    "input": {
                        "id": user_id,
                        "_useremails": [{"email": email}]
                    }
                }
                r_email_array = requests.put(f"{GLPI_URL}/User/{user_id}", headers=headers, json=email_array_update)
                
                # Verifica o resultado
                if r_email_direct.status_code == 200 or r_email.status_code in [200, 201] or r_email_array.status_code == 200:
                    print(c(f"✅ [OK] Email vinculado com sucesso!", 'green'))
                elif "Duplicate entry" in str(r_email.text):
                    print(c(f"ℹ️ [INFO] Email já existe para este usuário", 'blue'))
                else:
                    print(c(f"⚠️ [AVISO] Todas as tentativas de vincular email falharam!", 'yellow'))

    return user_id

