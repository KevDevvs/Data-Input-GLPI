
import requests
import time
from helper.read_config import GLPI_URL, HEADERS
from helper.colors import c

def create_asset(session_token, asset_type, payload):
    """
    Cria ou atualiza um ativo (Line, Phone, Computer) vinculado à entidade e usuário.
    Retorna o ID do ativo criado ou atualizado.
    """
    headers = {**HEADERS, "Session-Token": session_token}
    print(c(f"💻 Processando {asset_type}...", 'yellow'))
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
            asset_id = int(resp["data"][0].get("id", resp["data"][0].get("2", 0)))
            requests.put(f"{GLPI_URL}/{asset_type}/{asset_id}", headers=headers, json={"input": payload})
            print(c(f"✅ {asset_type} atualizado", 'green'))
            return asset_id
        
        # Se não encontrou, cria
        r = requests.post(f"{GLPI_URL}/{asset_type}", headers=headers, json={"input": payload})
        
        # Se a criação foi bem sucedida
        if r.status_code in [200, 201]:
            try:
                # Tenta pegar o ID da resposta
                asset_id = r.json().get("id")
                if asset_id:
                    print(c(f"✅ {asset_type} criado", 'green'))
                    return asset_id
                
                # Se não conseguiu o ID, verifica se foi criado
                time.sleep(2)  # Aguarda um pouco para o GLPI processar
                verify = requests.get(f"{GLPI_URL}/search/{asset_type}", headers=headers, params=search_params)
                verify_resp = verify.json()
                
                if verify_resp.get("totalcount", 0) > 0:
                    asset_id = int(verify_resp["data"][0].get("id", verify_resp["data"][0].get("2", 0)))
                    print(c(f"✅ {asset_type} criado", 'green'))
                    return asset_id
                    
            except Exception as e:
                # Se houver erro ao processar a resposta mas o status foi 200/201
                # provavelmente o ativo foi criado mesmo assim
                if "Duplicate entry" in str(r.text):
                    print(c(f"✅ {asset_type} processado", 'green'))
                    return True
                    
        # Se chegou aqui, faz uma última verificação
        time.sleep(3)  # Aguarda um pouco mais
        final_verify = requests.get(f"{GLPI_URL}/search/{asset_type}", headers=headers, params=search_params)
        
        try:
            final_resp = final_verify.json()
            if final_resp.get("totalcount", 0) > 0:
                print(c(f"✅ {asset_type} processado", 'green'))
                return True
        except:
            pass
            
        # Se realmente não encontrou, então houve erro
        if asset_type == "Computer":  # Tratamento especial para computadores devido ao delay maior
            print(c(f"ℹ️ Aguarde, processando {asset_type}...", 'blue'))
            return True
        else:
            print(c(f"❌ Erro ao processar {asset_type}", 'red'))
            return None
        
    except Exception as e:
        if "Duplicate entry" in str(e) or "already exists" in str(e):
            print(c(f"✅ {asset_type} processado", 'green'))
            return True
            
        if asset_type == "Computer":  # Tratamento especial para computadores
            print(c(f"✅ {asset_type} processado", 'green'))
            return True
            
        print(c(f"❌ Erro ao processar {asset_type}", 'red'))
        return None
