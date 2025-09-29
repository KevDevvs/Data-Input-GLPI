import requests
from helper.read_config import GLPI_URL, HEADERS
from helper.colors import c

def get_or_create_supplier(session_token, supplier_name, entities_id=0):

    headers = {**HEADERS, "Session-Token": session_token}
    
    try:
        # Busca todos os suppliers
        get_all_response = requests.get(f"{GLPI_URL}/Supplier", headers=headers)
        
        if get_all_response.status_code == 200:
            all_suppliers = get_all_response.json()
            # Procura pelo nome exato
            if isinstance(all_suppliers, list):
                for supplier in all_suppliers:
                    if isinstance(supplier, dict) and supplier.get("name") == supplier_name:
                        supplier_id = supplier.get("id")
                        return supplier_id
        
        # Se não encontrou, cria um novo fornecedor na entidade raiz
        supplier_data = {
            "name": supplier_name,
            "entities_id": 0,  # Sempre entidade raiz
            "is_recursive": 1
        }
        
        create_response = requests.post(f"{GLPI_URL}/Supplier", headers=headers, json={"input": supplier_data})
        
        if create_response.status_code == 201:
            supplier_id = create_response.json().get("id")
            return supplier_id
        else:
            print(c(f"❌ Erro ao criar fornecedor '{supplier_name}'", 'red'))
            return None
            
    except Exception as e:
        print(c(f"❌ Erro ao processar fornecedor '{supplier_name}': {str(e)}", 'red'))
        return None

def get_or_create_contract(session_token, contract_name, entities_id=0, supplier_id=None):

    headers = {**HEADERS, "Session-Token": session_token}
    
    print(c(f"🔍 Função get_or_create_contract chamada para '{contract_name}' com supplier_id={supplier_id}", 'blue'))
    
    try:
        
        # Busca todos os contratos
        print(c(f"🔍 Buscando contrato '{contract_name}'...", 'blue'))
        get_all_response = requests.get(f"{GLPI_URL}/Contract", headers=headers)
        
        if get_all_response.status_code == 200:
            all_contracts = get_all_response.json()
            print(c(f"🔍 Encontrados {len(all_contracts) if isinstance(all_contracts, list) else 0} contratos no total", 'yellow'))
            
            # Procura pelo nome exato
            if isinstance(all_contracts, list):
                for contract in all_contracts:
                    if isinstance(contract, dict) and contract.get("name") == contract_name:
                        contract_id = contract.get("id")
                        print(c(f"✅ Contrato '{contract_name}' encontrado (ID: {contract_id})", 'green'))
                        
                        # Se foi fornecido um supplier_id, verificar se já está vinculado
                        if supplier_id:
                            # Verificar se o supplier já está vinculado
                            supplier_check = requests.get(f"{GLPI_URL}/Contract/{contract_id}/Contract_Supplier", headers=headers)
                            if supplier_check.status_code == 200:
                                existing_suppliers = supplier_check.json()
                                supplier_already_linked = False
                                if existing_suppliers:
                                    for sup in existing_suppliers:
                                        if sup.get('suppliers_id') == supplier_id:
                                            supplier_already_linked = True
                                            break
                                
                                if not supplier_already_linked:
                                    # Criar vinculação via Contract_Supplier
                                    link_data = {
                                        "contracts_id": contract_id,
                                        "suppliers_id": supplier_id
                                    }
                                    link_response = requests.post(f"{GLPI_URL}/Contract_Supplier", headers=headers, json={"input": link_data})
                                    if not link_response.status_code == 201:
                                        print(c(f"⚠️ Erro ao vincular supplier: {link_response.status_code}", 'yellow'))
                        
                        return contract_id
        
        # Se não encontrou, cria um novo contrato na entidade raiz
        print(c(f"🔍 Contrato '{contract_name}' não encontrado na lista", 'yellow'))
        print(c(f"⚠️ Contrato '{contract_name}' não encontrado, criando novo...", 'yellow'))
        contract_data = {
            "name": contract_name,
            "entities_id": 0,  # Sempre entidade raiz
            "is_recursive": 1
        }
        
        if supplier_id:
            print(c(f"📋 Criando contrato '{contract_name}' na entidade raiz (ID: 0) com supplier {supplier_id}", 'blue'))
        else:
            print(c(f"📋 Criando contrato '{contract_name}' na entidade raiz (ID: 0) sem supplier", 'blue'))
        
        create_response = requests.post(f"{GLPI_URL}/Contract", headers=headers, json={"input": contract_data})
        
        if create_response.status_code == 201:
            contract_id = create_response.json().get("id")
            
            # Se foi fornecido supplier_id, criar a vinculação após criar o contrato
            if supplier_id:
                link_data = {
                    "contracts_id": contract_id,
                    "suppliers_id": supplier_id
                }
                link_response = requests.post(f"{GLPI_URL}/Contract_Supplier", headers=headers, json={"input": link_data})
                if not link_response.status_code == 201:
                    print(c(f"⚠️ Erro ao vincular supplier ao novo contrato: {link_response.status_code}", 'yellow'))
            
            return contract_id
        else:
            print(c(f"❌ Erro ao criar contrato '{contract_name}'", 'red'))
            return None
            
    except Exception as e:
        print(c(f"❌ Erro ao processar contrato '{contract_name}': {str(e)}", 'red'))
        return None

def link_contract_to_asset(session_token, asset_type, asset_id, contract_id):
    """
    Vincula um contrato a um ativo.
    """
    headers = {**HEADERS, "Session-Token": session_token}
    
    try:
        # Define o endpoint correto baseado no tipo de ativo
        if asset_type in ["Computer", "Line"]:
            endpoint = "Contract_Item"
            item_data = {
                "contracts_id": contract_id,
                "items_id": asset_id,
                "itemtype": asset_type
            }
        else:
            print(c(f"⚠️ Tipo de ativo '{asset_type}' não suportado para contratos", 'yellow'))
            return False
        
        # Cria a vinculação diretamente (sem verificar se já existe)
        create_response = requests.post(f"{GLPI_URL}/{endpoint}", headers=headers, json={"input": item_data})
        
        if create_response.status_code == 201:
            return True
        elif create_response.status_code == 400:
            # Pode ser que já existe - vamos aceitar como sucesso
            response_text = create_response.text.lower()
            if "duplicate" in response_text or "already exists" in response_text:
                return True
            else:
                print(c(f"❌ Erro 400 ao vincular contrato: {create_response.text}", 'red'))
                return False
        else:
            print(c(f"❌ Erro ao vincular contrato ao {asset_type} - Status: {create_response.status_code}", 'red'))
            print(c(f"❌ Detalhes: {create_response.text}", 'red'))
            return False
            
    except Exception as e:
        print(c(f"❌ Erro ao vincular contrato: {str(e)}", 'red'))
        return False

def create_management_info(session_token, asset_type, asset_id, buy_date=None, value=None, supplier_id=None):
    headers = {**HEADERS, "Session-Token": session_token}
    
    try:
        # Define o endpoint correto baseado no tipo de ativo
        if asset_type == "Computer":
            endpoint = "Infocom"
            itemtype = "Computer"
        elif asset_type == "Line":
            endpoint = "Infocom"
            itemtype = "Line"
        else:
            print(c(f"⚠️ Tipo de ativo '{asset_type}' não suportado para informações de management", 'yellow'))
            return False
        
        # Verifica se já existe Infocom para este asset usando o endpoint direto
        try:
            check_url = f"{GLPI_URL}/{asset_type}/{asset_id}/Infocom"
            check_response = requests.get(check_url, headers=headers)
            
            if check_response.status_code == 200:
                existing_infocom = check_response.json()
                if isinstance(existing_infocom, list) and len(existing_infocom) > 0:
                    # Já existe Infocom, vamos atualizá-lo
                    infocom_id = existing_infocom[0].get("id")
                    
                    # Prepara dados para atualização
                    update_data = {}
                    
                    if buy_date:
                        date_str = str(buy_date).strip()
                        if ' ' in date_str:
                            date_str = date_str.split(' ')[0]
                        update_data["buy_date"] = date_str
                        
                    if value:
                        try:
                            value_float = float(str(value).strip().replace(',', '.'))
                            update_data["value"] = value_float
                        except ValueError:
                            print(c(f"⚠️ Valor '{value}' não é numérico válido", 'yellow'))
                    
                    # Adicionar supplier_id se fornecido
                    if supplier_id:
                        update_data["suppliers_id"] = supplier_id
                    
                    if update_data:
                        update_response = requests.put(f"{GLPI_URL}/Infocom/{infocom_id}", headers=headers, json={"input": update_data})
                        
                        if update_response.status_code == 200:
                            return True
                        else:
                            print(c(f"⚠️ Erro ao atualizar Infocom: {update_response.text}", 'yellow'))
                            return False
                    else:
                        return True
                        
        except Exception as e:
            print(c(f"🔍 Erro ao verificar Infocom existente: {str(e)}", 'yellow'))
        
        # Prepara os dados de management
        infocom_data = {
            "items_id": asset_id,
            "itemtype": itemtype
        }
        
        # Processa a data no formato correto do GLPI (YYYY-MM-DD)
        if buy_date:
            date_str = str(buy_date).strip()
            # Se a data tem formato datetime, extrai apenas a data
            if ' ' in date_str:
                date_str = date_str.split(' ')[0]
            infocom_data["buy_date"] = date_str
            
        if value:
            # Garante que o valor é numérico
            try:
                value_float = float(str(value).strip().replace(',', '.'))
                infocom_data["value"] = value_float
            except ValueError:
                print(c(f"⚠️ Valor '{value}' não é numérico válido", 'yellow'))
        
        # Adicionar supplier_id se fornecido
        if supplier_id:
            infocom_data["suppliers_id"] = supplier_id
        
        # Usa o endpoint Infocom que sabemos que funciona
        endpoint = "Infocom"
        
        # Prepara dados completos para criação
        infocom_data = {
            "items_id": asset_id,
            "itemtype": itemtype
        }
        
        # Processa a data no formato correto do GLPI (YYYY-MM-DD)
        if buy_date:
            date_str = str(buy_date).strip()
            # Se a data tem formato datetime, extrai apenas a data
            if ' ' in date_str:
                date_str = date_str.split(' ')[0]
            infocom_data["buy_date"] = date_str
            
        if value:
            # Garante que o valor é numérico
            try:
                value_float = float(str(value).strip().replace(',', '.'))
                infocom_data["value"] = value_float
            except ValueError:
                print(c(f"⚠️ Valor '{value}' não é numérico válido", 'yellow'))
        
        # Tenta criar o Infocom
        create_response = requests.post(f"{GLPI_URL}/{endpoint}", headers=headers, json={"input": infocom_data})
        
        if create_response.status_code == 201:
            infocom_id = create_response.json().get("id")
            return True
        elif create_response.status_code == 400:
            # Verifica se é erro de duplicata
            response_text = create_response.text.lower()
            if "duplicate" in response_text or "already exists" in response_text or "unicity" in response_text:
                return True
            else:
                print(c(f"❌ Erro 400 ao criar informações de management: {create_response.text}", 'red'))
                return False
        else:
            print(c(f"❌ Erro ao criar informações de management - Status: {create_response.status_code}", 'red'))
            return False

                
    except Exception as e:
        print(c(f"❌ Erro ao processar informações de management: {str(e)}", 'red'))
        return False