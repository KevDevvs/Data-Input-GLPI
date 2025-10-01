"""
Função para criar/atualizar Infocom de linha com data de início
"""
import requests
from helper.read_config import GLPI_URL, HEADERS
from helper.colors import c

def create_or_update_line_infocom(session_token, line_id, buy_date=None, use_date=None, entities_id=0):
    """
    Cria ou atualiza o Infocom (Management) de uma linha com datas
    
    Args:
        session_token: Token da sessão GLPI
        line_id: ID da linha
        buy_date: Data de compra/início (formato YYYY-MM-DD)
        use_date: Data de uso (formato YYYY-MM-DD)
        entities_id: ID da entidade
    
    Returns:
        bool: True se sucesso, False se erro
    """
    headers = {**HEADERS, "Session-Token": session_token}
    
    try:
        # Primeiro verifica se já existe Infocom para esta linha
        check_response = requests.get(f"{GLPI_URL}/Line/{line_id}/Infocom", headers=headers)
        
        existing_infocom_id = None
        
        if check_response.status_code == 200:
            infocom_data = check_response.json()
            
            # Verifica se já existe Infocom
            if isinstance(infocom_data, list) and len(infocom_data) > 0:
                existing_infocom_id = infocom_data[0].get('id')
            elif isinstance(infocom_data, dict) and infocom_data.get('id'):
                existing_infocom_id = infocom_data.get('id')
        
        # Prepara dados para atualização/criação
        infocom_data = {}
        if buy_date:
            infocom_data["buy_date"] = buy_date
        if use_date:
            infocom_data["use_date"] = use_date
        
        if existing_infocom_id:
            # Atualiza Infocom existente
            print(c(f"🔄 Atualizando Infocom {existing_infocom_id} da linha {line_id}", 'cyan'))
            
            update_response = requests.put(f"{GLPI_URL}/Infocom/{existing_infocom_id}", 
                                         headers=headers, 
                                         json={"input": infocom_data})
            
            if update_response.status_code == 200:
                print(c(f"✅ Infocom atualizado com data: {buy_date or use_date}", 'green'))
                return True
            else:
                print(c(f"❌ Falha ao atualizar Infocom: {update_response.status_code}", 'red'))
                return False
        else:
            # Cria novo Infocom
            print(c(f"🆕 Criando Infocom para linha {line_id}", 'cyan'))
            
            infocom_data.update({
                "items_id": line_id,
                "itemtype": "Line",
                "entities_id": entities_id
            })
            
            create_response = requests.post(f"{GLPI_URL}/Infocom", 
                                          headers=headers, 
                                          json={"input": infocom_data})
            
            if create_response.status_code in [200, 201]:
                result = create_response.json()
                new_infocom_id = result.get("id")
                print(c(f"✅ Infocom criado (ID: {new_infocom_id}) com data: {buy_date or use_date}", 'green'))
                return True
            else:
                print(c(f"❌ Falha ao criar Infocom: {create_response.status_code}", 'red'))
                print(c(f"Resposta: {create_response.text}", 'red'))
                return False
        
    except Exception as e:
        print(c(f"❌ Erro ao processar Infocom da linha {line_id}: {e}", 'red'))
        return False