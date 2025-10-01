
import requests
from helper.read_config import GLPI_URL, GROUP_ID, HEADERS
from helper.colors import c


def get_or_create_user_title(session_token, title_name):
    """
    Busca ou cria um UserTitle (cargo/posição) no GLPI
    
    Args:
        session_token: Token da sessão GLPI
        title_name: Nome do cargo/posição
        
    Returns:
        int: ID do UserTitle ou None em caso de erro
    """
    if not title_name or not str(title_name).strip():
        return None
        
    headers = {**HEADERS, "Session-Token": session_token}
    title_clean = str(title_name).strip()
    
    try:
        # Busca se o título já existe
        search_params = {
            "criteria[0][field]": "1",  # campo name
            "criteria[0][searchtype]": "equals",
            "criteria[0][value]": title_clean
        }
        
        search_response = requests.get(f"{GLPI_URL}/search/UserTitle", headers=headers, params=search_params)
        
        if search_response.status_code in [200, 206]:
            search_data = search_response.json()
            if isinstance(search_data, dict) and search_data.get("totalcount", 0) > 0:
                title_data = search_data["data"][0]
                title_id = title_data.get("2") or title_data.get("id")
                if title_id:
                    print(c(f"✅ Cargo '{title_clean}' encontrado (ID: {title_id})", 'green'))
                    return int(title_id)
        
        # Se não encontrou, cria novo
        title_payload = {
            "name": title_clean,
            "entities_id": 0  # Entidade raiz para ser compartilhado
        }
        
        create_response = requests.post(f"{GLPI_URL}/UserTitle", headers=headers, json={"input": title_payload})
        
        if create_response.status_code in [200, 201]:
            response_data = create_response.json()
            title_id = response_data.get("id")
            if title_id:
                print(c(f"✅ Cargo '{title_clean}' criado (ID: {title_id})", 'green'))
                return int(title_id)
                
        print(c(f"❌ Falha ao criar cargo '{title_clean}'", 'red'))
        return None
        
    except Exception as e:
        print(c(f"❌ Erro ao processar cargo '{title_clean}': {e}", 'red'))
        return None


def create_user(session_token, name, email, profile_id, entity_id, status_user, cpf=None, celular_pessoal=None, posicao=None, comentario=None):
    """
    Cria usuário no GLPI
    
    Args:
        session_token: Token da sessão GLPI
        name: Nome completo do usuário
        email: Email do usuário (será usado como login)
        profile_id: ID do perfil do usuário
        entity_id: ID da entidade
        status_user: Status do usuário (categoria)
        cpf: CPF do usuário (opcional)
        celular_pessoal: Celular pessoal do usuário (opcional)
        posicao: Posição/cargo do usuário (opcional)
        comentario: Comentário sobre o usuário (opcional)
    
    Returns:
        tuple: (user_id, error_message) onde user_id é None se houve erro
    """

    print(c(f"\n👤 Processando usuário '{name}'", 'yellow'))

    headers = {**HEADERS, "Session-Token": session_token}

    # Processa o nome para firstname e realname
    name_parts = name.strip().split(' ')
    if not name_parts:
        print(c("❌ Nome inválido", 'red'))
        return None, "Nome inválido"

    # Validação de email obrigatório
    if not email or not email.strip():
        print(c("❌ Email é obrigatório", 'red'))
        return None, "Email obrigatório ausente"
    
    email_clean = email.strip()
    
    # Verifica se o email tem formato válido
    if not email_clean.startswith("@"):
        print(c(f"❌ Email deve começar com @ (formato: @usuario@dominio.com). Recebido: '{email_clean}'", 'red'))
        return None, "Email formato inválido"
    
    # Remove o @ inicial e valida se tem @ no restante
    login = email_clean.lstrip("@")
    if not login or '@' not in login:
        print(c(f"❌ Email inválido - deve ter formato @usuario@dominio.com. Login: '{login}'", 'red'))
        return None, "Email malformado"

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
            user_data_result = search_data["data"][0]
            user_id_raw = user_data_result.get("2") or user_data_result.get("id")
            if user_id_raw:
                user_id = int(user_id_raw)
                print(c(f"✅ [OK] Usuário '{login}' encontrado (ID: {user_id})", 'green'))
                return user_id, None
        else:
            print(c(f"📝 Usuário '{login}' não encontrado, criando novo...", 'cyan'))
    else:
        print(c(f"⚠️ [AVISO] Erro ao buscar usuário (Status: {search_response.status_code})", 'yellow'))
    
    if not user_id:
        # Processa cargo/posição se fornecido
        title_id = None
        if posicao and str(posicao).strip():
            title_id = get_or_create_user_title(session_token, str(posicao).strip())
            if title_id:
                print(c(f"📋 Cargo/Posição vinculado: {str(posicao).strip()} (ID: {title_id})", 'cyan'))
            else:
                print(c(f"⚠️ Falha ao criar/vincular cargo: {str(posicao).strip()}", 'yellow'))
        
        # Gera senha temporária baseada no CPF
        senha_temp = "Ch@nge.me123"  # Senha padrão
        if cpf and str(cpf).strip():
            # Remove caracteres especiais do CPF e pega os 3 primeiros dígitos
            cpf_limpo = ''.join(filter(str.isdigit, str(cpf).strip()))
            if len(cpf_limpo) >= 3:
                primeiros_digitos = cpf_limpo[:3]
                senha_temp = f"senhatemp{primeiros_digitos}"
                print(c(f"🔑 Senha temporária gerada: senhatemp{primeiros_digitos}", 'cyan'))
            else:
                print(c(f"⚠️ CPF com menos de 3 dígitos, usando senha padrão", 'yellow'))
        else:
            print(c(f"🔑 CPF não fornecido, usando senha padrão", 'cyan'))
        
        # Prepara os dados do usuário
        user_data = {
            "name": login,
            "firstname": name_parts[0],
            "realname": ' '.join(name_parts[1:]) if len(name_parts) > 1 else "",
            "password": senha_temp,
            "password2": senha_temp,
            "entities_id": entity_id,
            "profiles_id": profile_id,
            "is_active": 1,
            "authtype": 1,
            "groups_id": GROUP_ID,
            "usercategories_id": status_user if status_user and str(status_user).strip() else 1,  # Padrão: 1 (Ativo)
        }
        
        # Adiciona CPF apenas se fornecido (campo opcional)
        if cpf and str(cpf).strip():
            user_data["registration_number"] = str(cpf).strip()
            print(c(f"📋 CPF adicionado: {str(cpf).strip()}", 'cyan'))
        else:
            print(c(f"📋 CPF não fornecido (campo opcional)", 'cyan'))
        
        # Adiciona celular pessoal se fornecido
        if celular_pessoal and str(celular_pessoal).strip():
            user_data["mobile"] = str(celular_pessoal).strip()
            print(c(f"📱 Celular pessoal adicionado: {str(celular_pessoal).strip()}", 'cyan'))
        
        # Adiciona cargo/posição se encontrado
        if title_id:
            user_data["usertitles_id"] = title_id
            
        # Adiciona comentário se fornecido
        if comentario and str(comentario).strip():
            user_data["comment"] = str(comentario).strip()
            print(c(f"💬 Comentário adicionado: {str(comentario).strip()[:50]}...", 'cyan'))

        # Cria usuário com dados básicos
        r = requests.post(f"{GLPI_URL}/User", headers=headers, json={"input": user_data})
        
        # Tenta obter o ID do usuário criado
        if r.status_code in [200, 201]:
            response_data = r.json()
            user_id = response_data.get("id")
        elif r.status_code == 400:
            # Erro 400 pode indicar usuário duplicado, tenta buscar novamente
            print(c("⚠️ Erro 400 - Tentando buscar usuário existente...", 'yellow'))
            
            # Aguarda um pouco para indexação
            import time
            time.sleep(1)
            
            # Tenta diferentes estratégias de busca
            search_strategies = [
                # Busca por nome (login)
                {
                    "criteria[0][field]": "1",  # campo name
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": login
                },
                # Busca por login
                {
                    "criteria[0][field]": "33",  # campo login
                    "criteria[0][searchtype]": "equals", 
                    "criteria[0][value]": login
                },
                # Busca por firstname + realname
                {
                    "criteria[0][field]": "9",   # firstname
                    "criteria[0][searchtype]": "equals",
                    "criteria[0][value]": name_parts[0],
                    "criteria[1][field]": "34",  # realname  
                    "criteria[1][searchtype]": "equals",
                    "criteria[1][value]": ' '.join(name_parts[1:]) if len(name_parts) > 1 else "",
                    "criteria[1][link]": "AND"
                }
            ]
            
            for strategy in search_strategies:
                search_response_retry = requests.get(f"{GLPI_URL}/search/User", headers=headers, params=strategy)
                if search_response_retry.status_code in [200, 206]:
                    retry_data = search_response_retry.json()
                    if isinstance(retry_data, dict) and retry_data.get("totalcount", 0) > 0:
                        user_data_result = retry_data["data"][0]
                        user_id_raw = user_data_result.get("2") or user_data_result.get("id")
                        if user_id_raw:
                            user_id = int(user_id_raw)
                            print(c(f"✅ [OK] Usuário '{login}' encontrado na segunda busca (ID: {user_id})", 'green'))
                            break
            
            if not user_id:
                print(c("❌ Usuário duplicado mas não encontrado na busca", 'red'))
                # Última tentativa: busca todos os usuários e filtra localmente
                try:
                    all_users_response = requests.get(f"{GLPI_URL}/User", headers=headers)
                    if all_users_response.status_code in [200, 206]:
                        all_users = all_users_response.json()
                        if isinstance(all_users, list):
                            for user in all_users:
                                user_name = user.get("name", "")
                                if user_name.lower() == login.lower():
                                    user_id = user.get("id")
                                    print(c(f"✅ [OK] Usuário encontrado na busca geral (ID: {user_id})", 'green'))
                                    break
                except Exception as e:
                    print(c(f"⚠️ Erro na busca geral: {e}", 'yellow'))
                
                if user_id:
                    return user_id, None
                else:
                    return None, "Usuário duplicado - não encontrado"
        else:
            print(c("❌ Falha ao criar usuário", 'red'))
            return None, f"Falha na criação no GLPI (Status: {r.status_code}) - {r.text}"


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
        return user_id, None
    else:
        return None, "Falha no processamento"

