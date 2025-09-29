import sys
sys.path.append('.')
import requests
from glpi_session.glpi_session import init_session, kill_session
from helper.read_config import GLPI_URL, HEADERS

def debug_suppliers_items():
    """Debug para verificar se os itens aparecem nos suppliers"""
    try:
        session_token = init_session()
        session = requests.Session()
        session.headers.update({**HEADERS, "Session-Token": session_token})
        
        print("🔍 Verificando itens vinculados aos suppliers...")
        
        # Buscar todos os suppliers
        suppliers_response = session.get(f"{GLPI_URL}/Supplier")
        if suppliers_response.status_code == 200:
            suppliers = suppliers_response.json()
            print(f"\n🏢 Total de suppliers: {len(suppliers)}")
            
            for supplier in suppliers:
                supplier_id = supplier.get('id')
                supplier_name = supplier.get('name')
                
                print(f"\n🏭 Supplier: {supplier_name} (ID: {supplier_id})")
                
                # Verificar contratos vinculados
                contracts_response = session.get(f"{GLPI_URL}/Supplier/{supplier_id}/Contract_Supplier")
                if contracts_response.status_code == 200:
                    contracts = contracts_response.json()
                    print(f"   📄 Contratos: {len(contracts) if contracts else 0}")
                    if contracts:
                        for contract in contracts:
                            contract_id = contract.get('contracts_id')
                            print(f"     - Contrato ID: {contract_id}")
                            
                            # Para cada contrato, verificar itens vinculados
                            items_response = session.get(f"{GLPI_URL}/Contract/{contract_id}/Contract_Item")
                            if items_response.status_code == 200:
                                items = items_response.json()
                                if items:
                                    print(f"       📦 Itens no contrato: {len(items)}")
                                    for item in items:
                                        item_type = item.get('itemtype')
                                        item_id = item.get('items_id')
                                        print(f"         - {item_type} ID: {item_id}")
                                else:
                                    print(f"       📦 Nenhum item no contrato")
                
                # Tentar verificar se há endpoint direto para itens do supplier
                print(f"   🔍 Tentando buscar itens diretamente...")
                
                # Testar diferentes endpoints possíveis
                endpoints_to_try = [
                    f"Supplier/{supplier_id}/Computer",
                    f"Supplier/{supplier_id}/Line", 
                    f"Supplier/{supplier_id}/Item",
                    f"Supplier/{supplier_id}/SupplierItem"
                ]
                
                for endpoint in endpoints_to_try:
                    response = session.get(f"{GLPI_URL}/{endpoint}")
                    print(f"   📡 {endpoint}: Status {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        if data:
                            print(f"     ✅ Encontrados {len(data)} itens")
                        else:
                            print(f"     📭 Nenhum item encontrado")
        
        # Verificar se existe vinculação direta supplier->item no infocom
        print(f"\n\n🔍 Verificando vinculações via Infocom...")
        computers_response = session.get(f"{GLPI_URL}/Computer")
        if computers_response.status_code == 200:
            computers = computers_response.json()[:3]  # Pegar apenas os primeiros 3 para teste
            
            for computer in computers:
                comp_id = computer.get('id')
                print(f"\n💻 Computer {comp_id}:")
                
                # Verificar infocom
                infocom_response = session.get(f"{GLPI_URL}/Computer/{comp_id}/Infocom")
                if infocom_response.status_code == 200:
                    infocom_data = infocom_response.json()
                    if infocom_data:
                        infocom = infocom_data[0]
                        supplier_id_infocom = infocom.get('suppliers_id', 0)
                        print(f"   📋 Supplier ID no Infocom: {supplier_id_infocom}")
                        
                        if supplier_id_infocom > 0:
                            supplier_response = session.get(f"{GLPI_URL}/Supplier/{supplier_id_infocom}")
                            if supplier_response.status_code == 200:
                                supplier_info = supplier_response.json()
                                print(f"   🏭 Supplier: {supplier_info.get('name')}")
                    else:
                        print(f"   ❌ Nenhum Infocom")
        
        kill_session(session_token)
        
    except Exception as e:
        print(f"❌ Erro no debug: {e}")

if __name__ == "__main__":
    debug_suppliers_items()