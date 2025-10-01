"""
Script para descobrir a estrutura correta do Infocom
"""
import requests
from helper.read_config import GLPI_URL, HEADERS
from glpi_session.glpi_session import init_session, kill_session
from helper.colors import c

def investigate_infocom_structure():
    """Investiga a estrutura correta do Infocom"""
    print(c("🔍 Investigando estrutura do Infocom...", 'yellow'))
    
    try:
        session = init_session()
        if not session:
            return
        
        headers = {**HEADERS, "Session-Token": session}
        
        # Busca Infocoms existentes para ver a estrutura
        infocom_response = requests.get(f"{GLPI_URL}/Infocom", headers=headers)
        
        if infocom_response.status_code in [200, 206]:
            infocom_data = infocom_response.json()
            
            if isinstance(infocom_data, list) and len(infocom_data) > 0:
                first_infocom = infocom_data[0]
                
                print(c("📋 Estrutura de um Infocom existente:", 'cyan'))
                print(c("=" * 50, 'white'))
                
                for key, value in sorted(first_infocom.items()):
                    print(f"{key:25} : {value}")
                
                # Verifica campos de data
                print(c(f"\n📅 Campos de data encontrados:", 'green'))
                for key, value in first_infocom.items():
                    if 'date' in key.lower() or 'buy' in key.lower() or 'warranty' in key.lower():
                        print(f"   {key}: {value}")
            else:
                print(c("❌ Nenhum Infocom encontrado", 'red'))
        else:
            print(c(f"❌ Erro ao buscar Infocom: {infocom_response.status_code}", 'red'))
        
        kill_session(session)
        
    except Exception as e:
        print(c(f"❌ Erro na investigação: {e}", 'red'))

def test_alternative_date_approach():
    """Testa abordagens alternativas para salvar data"""
    print(c("\n🧪 Testando abordagens alternativas...", 'yellow'))
    
    try:
        session = init_session()
        if not session:
            return
        
        headers = {**HEADERS, "Session-Token": session}
        
        # Primeiro, cria uma linha
        line_data = {
            "name": "Linha Teste Data Alt",
            "entities_id": 0,
            "users_id": 0,
            "lineoperators_id": 1,
            "linetypes_id": 1,
            "states_id": 8
        }
        
        create_response = requests.post(f"{GLPI_URL}/Line", headers=headers, json={"input": line_data})
        
        if create_response.status_code in [200, 201]:
            response_data = create_response.json()
            line_id = response_data.get("id")
            
            if line_id:
                print(c(f"✅ Linha criada (ID: {line_id})", 'green'))
                
                # Abordagem 1: Tentar atualizar a linha com campos de data diretamente
                print(c("🔍 Tentativa 1: Atualizar linha com campos de data...", 'cyan'))
                
                update_data = {
                    "buy_date": "2024-03-11",
                    "warranty_date": "2025-03-11",
                    "use_date": "2024-03-11",
                    "delivery_date": "2024-03-11"
                }
                
                update_response = requests.put(f"{GLPI_URL}/Line/{line_id}", headers=headers, json={"input": update_data})
                
                if update_response.status_code == 200:
                    print(c("✅ Linha atualizada", 'green'))
                    
                    # Verifica se salvou
                    check_response = requests.get(f"{GLPI_URL}/Line/{line_id}", headers=headers)
                    if check_response.status_code == 200:
                        updated_line = check_response.json()
                        print(c("📋 Campos após atualização:", 'cyan'))
                        for field in update_data.keys():
                            if field in updated_line:
                                print(c(f"   ✅ {field}: {updated_line[field]}", 'green'))
                            else:
                                print(c(f"   ❌ {field}: Não encontrado", 'red'))
                else:
                    print(c(f"❌ Falha na atualização: {update_response.status_code}", 'red'))
                
                # Abordagem 2: Tentar criar Infocom com estrutura simples
                print(c("\n🔍 Tentativa 2: Criar Infocom simples...", 'cyan'))
                
                simple_infocom = {
                    "items_id": line_id,
                    "itemtype": "Line",
                    "buy_date": "2024-03-11"
                }
                
                infocom_response = requests.post(f"{GLPI_URL}/Infocom", headers=headers, json={"input": simple_infocom})
                print(c(f"Resultado: {infocom_response.status_code} - {infocom_response.text}", 'yellow'))
        
        kill_session(session)
        
    except Exception as e:
        print(c(f"❌ Erro no teste: {e}", 'red'))

if __name__ == "__main__":
    investigate_infocom_structure()
    test_alternative_date_approach()