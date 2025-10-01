"""
Script para corrigir a criação de Infocom para linhas
"""
import requests
from helper.read_config import GLPI_URL, HEADERS
from glpi_session.glpi_session import init_session, kill_session
from helper.colors import c

def fix_infocom_creation():
    """Corrige a criação de Infocom"""
    print(c("🔧 Corrigindo criação de Infocom...", 'yellow'))
    
    try:
        session = init_session()
        if not session:
            return
        
        headers = {**HEADERS, "Session-Token": session}
        
        # Primeiro, vamos ver como é o Infocom existente (ID: 1)
        existing_infocom_response = requests.get(f"{GLPI_URL}/Infocom/1", headers=headers)
        
        if existing_infocom_response.status_code == 200:
            existing_data = existing_infocom_response.json()
            print(c("📋 Infocom existente como modelo:", 'cyan'))
            print(f"   items_id: {existing_data.get('items_id')}")
            print(f"   itemtype: {existing_data.get('itemtype')}")
            print(f"   entities_id: {existing_data.get('entities_id')}")
            print(f"   buy_date: {existing_data.get('buy_date')}")
        
        # Busca uma linha existente que ainda não tem Infocom
        lines_response = requests.get(f"{GLPI_URL}/Line", headers=headers)
        
        if lines_response.status_code in [200, 206]:
            lines_data = lines_response.json()
            
            # Tenta encontrar uma linha sem Infocom
            target_line_id = None
            for line in lines_data:
                line_id = line.get('id')
                if line_id:
                    # Verifica se já tem Infocom
                    check_infocom = requests.get(f"{GLPI_URL}/Line/{line_id}/Infocom", headers=headers)
                    if check_infocom.status_code == 200:
                        infocom_data = check_infocom.json()
                        if not infocom_data or (isinstance(infocom_data, list) and len(infocom_data) == 0):
                            target_line_id = line_id
                            print(c(f"🎯 Linha {line_id} sem Infocom encontrada", 'green'))
                            break
            
            if target_line_id:
                # Tenta diferentes estruturas de Infocom
                test_structures = [
                    # Estrutura 1: Básica
                    {
                        "items_id": target_line_id,
                        "itemtype": "Line",
                        "entities_id": 0,
                        "buy_date": "2024-03-11"
                    },
                    # Estrutura 2: Com mais campos obrigatórios
                    {
                        "items_id": target_line_id,
                        "itemtype": "Line",
                        "entities_id": 0,
                        "buy_date": "2024-03-11",
                        "value": 0.0,
                        "warranty_duration": 0
                    },
                    # Estrutura 3: Só com use_date
                    {
                        "items_id": target_line_id,
                        "itemtype": "Line",
                        "entities_id": 0,
                        "use_date": "2024-03-11"
                    }
                ]
                
                for i, test_data in enumerate(test_structures, 1):
                    print(c(f"\n🔍 Testando estrutura {i}: {test_data}", 'cyan'))
                    
                    infocom_response = requests.post(f"{GLPI_URL}/Infocom", headers=headers, json={"input": test_data})
                    
                    print(c(f"Status: {infocom_response.status_code}", 'yellow'))
                    print(c(f"Resposta: {infocom_response.text}", 'yellow'))
                    
                    if infocom_response.status_code in [200, 201]:
                        result = infocom_response.json()
                        infocom_id = result.get("id")
                        print(c(f"✅ Infocom criado com sucesso (ID: {infocom_id})", 'green'))
                        
                        # Verifica se foi salvo corretamente
                        check_response = requests.get(f"{GLPI_URL}/Infocom/{infocom_id}", headers=headers)
                        if check_response.status_code == 200:
                            saved_data = check_response.json()
                            print(c("✅ Dados salvos:", 'green'))
                            for key in test_data.keys():
                                if key in saved_data:
                                    print(f"   {key}: {saved_data[key]}")
                        break
                    else:
                        print(c(f"❌ Falha na estrutura {i}", 'red'))
            else:
                print(c("❌ Nenhuma linha sem Infocom encontrada", 'red'))
        
        kill_session(session)
        
    except Exception as e:
        print(c(f"❌ Erro: {e}", 'red'))

if __name__ == "__main__":
    fix_infocom_creation()