"""
Script para testar atualização de Infocom existente
"""
import requests
from helper.read_config import GLPI_URL, HEADERS
from glpi_session.glpi_session import init_session, kill_session
from helper.colors import c

def test_update_existing_infocom():
    """Testa atualização de Infocom existente"""
    print(c("🔧 Testando atualização de Infocom existente...", 'yellow'))
    
    try:
        session = init_session()
        if not session:
            return
        
        headers = {**HEADERS, "Session-Token": session}
        
        # Busca uma linha com Infocom
        lines_response = requests.get(f"{GLPI_URL}/Line", headers=headers)
        
        if lines_response.status_code in [200, 206]:
            lines_data = lines_response.json()
            
            for line in lines_data[:3]:  # Testa as primeiras 3 linhas
                line_id = line.get('id')
                if line_id:
                    print(c(f"\n🔍 Testando linha {line_id}...", 'cyan'))
                    
                    # Verifica se tem Infocom
                    infocom_response = requests.get(f"{GLPI_URL}/Line/{line_id}/Infocom", headers=headers)
                    
                    if infocom_response.status_code == 200:
                        infocom_data = infocom_response.json()
                        
                        if isinstance(infocom_data, list) and len(infocom_data) > 0:
                            infocom_item = infocom_data[0]
                            infocom_id = infocom_item.get('id')
                            
                            print(c(f"✅ Infocom encontrado (ID: {infocom_id})", 'green'))
                            print(f"   buy_date atual: {infocom_item.get('buy_date')}")
                            print(f"   use_date atual: {infocom_item.get('use_date')}")
                            
                            # Tenta atualizar com data
                            update_data = {
                                "buy_date": "2024-03-11",
                                "use_date": "2024-03-11"
                            }
                            
                            update_response = requests.put(f"{GLPI_URL}/Infocom/{infocom_id}", headers=headers, json={"input": update_data})
                            
                            print(c(f"Status atualização: {update_response.status_code}", 'yellow'))
                            
                            if update_response.status_code == 200:
                                print(c("✅ Infocom atualizado com sucesso", 'green'))
                                
                                # Verifica se salvou
                                check_response = requests.get(f"{GLPI_URL}/Infocom/{infocom_id}", headers=headers)
                                if check_response.status_code == 200:
                                    updated_data = check_response.json()
                                    print(c("📋 Dados após atualização:", 'cyan'))
                                    print(f"   buy_date: {updated_data.get('buy_date')}")
                                    print(f"   use_date: {updated_data.get('use_date')}")
                                    
                                    if updated_data.get('buy_date') == "2024-03-11":
                                        print(c("🎉 SUCESSO! Data foi salva corretamente!", 'green'))
                                        return True
                            else:
                                print(c(f"❌ Falha na atualização: {update_response.text}", 'red'))
                        
                        elif isinstance(infocom_data, dict):
                            # Se retornou um dict diretamente
                            infocom_id = infocom_data.get('id')
                            if infocom_id:
                                print(c(f"✅ Infocom encontrado (ID: {infocom_id})", 'green'))
                                
                                update_data = {"buy_date": "2024-03-11"}
                                update_response = requests.put(f"{GLPI_URL}/Infocom/{infocom_id}", headers=headers, json={"input": update_data})
                                
                                if update_response.status_code == 200:
                                    print(c("✅ Atualização bem-sucedida!", 'green'))
                                    return True
                        else:
                            print(c("❌ Nenhum Infocom encontrado para esta linha", 'red'))
        
        kill_session(session)
        return False
        
    except Exception as e:
        print(c(f"❌ Erro: {e}", 'red'))
        return False

if __name__ == "__main__":
    success = test_update_existing_infocom()
    if success:
        print(c("\n🎯 SOLUÇÃO ENCONTRADA! Podemos usar Infocom para salvar datas.", 'green'))
    else:
        print(c("\n❌ Ainda não conseguimos salvar a data.", 'red'))