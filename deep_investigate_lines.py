"""
Script para investigar mais profundamente a estrutura de linhas no GLPI
"""
import requests
from helper.read_config import GLPI_URL, HEADERS
from glpi_session.glpi_session import init_session, kill_session
from helper.colors import c

def deep_investigate_line_structure():
    """Investigação profunda da estrutura de linhas"""
    print(c("🔍 Investigação profunda da estrutura de linhas...", 'yellow'))
    
    try:
        session = init_session()
        if not session:
            return
        
        headers = {**HEADERS, "Session-Token": session}
        
        # Busca uma linha existente completa
        lines_response = requests.get(f"{GLPI_URL}/Line", headers=headers)
        
        if lines_response.status_code in [200, 206]:
            lines_data = lines_response.json()
            
            if isinstance(lines_data, list) and len(lines_data) > 0:
                first_line = lines_data[0]
                line_id = first_line.get('id')
                
                print(c(f"📋 Estrutura completa da linha ID {line_id}:", 'cyan'))
                print(c("=" * 60, 'white'))
                
                # Lista todos os campos
                for key, value in sorted(first_line.items()):
                    print(f"{key:25} : {value}")
                
                # Testa outros endpoints relacionados a linhas
                print(c(f"\n🔍 Testando endpoints relacionados:", 'cyan'))
                
                # Busca campos específicos da linha
                detail_response = requests.get(f"{GLPI_URL}/Line/{line_id}", headers=headers)
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    print(c(f"✅ Detalhes da linha {line_id}:", 'green'))
                    
                    # Procura por campos que podem ser de data de início
                    for key, value in detail_data.items():
                        if key not in first_line or first_line[key] != value:
                            print(f"   NOVO: {key} = {value}")
                
                # Verifica se há informações de Management (aba de Management)
                print(c(f"\n🔍 Verificando informações de Management:", 'cyan'))
                
                # No GLPI, informações de Management geralmente são salvas em InfoCom
                infocom_response = requests.get(f"{GLPI_URL}/Line/{line_id}/Infocom", headers=headers)
                if infocom_response.status_code == 200:
                    infocom_data = infocom_response.json()
                    if infocom_data:
                        print(c("✅ Informações de Management encontradas:", 'green'))
                        for key, value in infocom_data.items():
                            if 'date' in key.lower() or 'buy' in key.lower() or 'warranty' in key.lower():
                                print(f"   📅 {key}: {value}")
                else:
                    print(c("❌ Nenhuma informação de Management encontrada", 'red'))
                
        kill_session(session)
        
    except Exception as e:
        print(c(f"❌ Erro na investigação: {e}", 'red'))

def test_infocom_creation():
    """Testa criação de Infocom (Management) para linha"""
    print(c("\n🧪 Testando criação de informações de Management (Infocom)...", 'yellow'))
    
    try:
        session = init_session()
        if not session:
            return
        
        headers = {**HEADERS, "Session-Token": session}
        
        # Primeiro, cria uma linha simples
        line_data = {
            "name": "Linha Teste Management",
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
                
                # Agora tenta criar informações de Management (Infocom)
                infocom_data = {
                    "items_id": line_id,
                    "itemtype": "Line",
                    "buy_date": "2024-03-11",
                    "warranty_date": "2025-03-11",
                    "entities_id": 0
                }
                
                print(c(f"🔍 Tentando criar Infocom para linha {line_id}...", 'cyan'))
                
                infocom_response = requests.post(f"{GLPI_URL}/Infocom", headers=headers, json={"input": infocom_data})
                
                if infocom_response.status_code in [200, 201]:
                    infocom_result = infocom_response.json()
                    print(c(f"✅ Infocom criado: {infocom_result}", 'green'))
                    
                    # Verifica se foi salvo corretamente
                    check_response = requests.get(f"{GLPI_URL}/Line/{line_id}/Infocom", headers=headers)
                    if check_response.status_code == 200:
                        saved_data = check_response.json()
                        print(c(f"✅ Infocom salvo: {saved_data}", 'green'))
                else:
                    print(c(f"❌ Falha ao criar Infocom: {infocom_response.status_code}", 'red'))
                    print(c(f"Resposta: {infocom_response.text}", 'red'))
        
        kill_session(session)
        
    except Exception as e:
        print(c(f"❌ Erro no teste: {e}", 'red'))

if __name__ == "__main__":
    deep_investigate_line_structure()
    test_infocom_creation()