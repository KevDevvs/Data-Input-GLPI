import sys
sys.path.append('.')
import requests
from glpi_session.glpi_session import init_session, kill_session
from helper.read_config import GLPI_URL, HEADERS

def debug_duplicate_contracts():
    """Debug para identificar contratos duplicados"""
    try:
        session_token = init_session()
        session = requests.Session()
        session.headers.update({**HEADERS, "Session-Token": session_token})
        
        print("🔍 Verificando contratos para identificar duplicatas...")
        
        # Buscar todos os contratos
        contracts_response = session.get(f"{GLPI_URL}/Contract")
        if contracts_response.status_code == 200:
            contracts = contracts_response.json()
            print(f"\n📄 Total de contratos: {len(contracts)}")
            
            # Agrupar contratos por nome para identificar duplicatas
            contract_names = {}
            for contract in contracts:
                contract_id = contract.get('id')
                contract_name = contract.get('name', '').strip()
                entity_id = contract.get('entities_id')
                
                if contract_name not in contract_names:
                    contract_names[contract_name] = []
                
                contract_names[contract_name].append({
                    'id': contract_id,
                    'entity_id': entity_id,
                    'name': contract_name
                })
            
            print(f"\n🔍 Análise de duplicatas:")
            duplicates_found = False
            
            for name, contracts_list in contract_names.items():
                if len(contracts_list) > 1:
                    duplicates_found = True
                    print(f"\n❌ DUPLICATA encontrada para '{name}':")
                    for contract in contracts_list:
                        print(f"   - ID: {contract['id']}, Entity: {contract['entity_id']}")
                else:
                    contract = contracts_list[0]
                    print(f"✅ '{name}' - ID: {contract['id']}, Entity: {contract['entity_id']}")
            
            if not duplicates_found:
                print(f"\n✅ Nenhuma duplicata encontrada!")
            
            # Verificar se a busca está funcionando corretamente
            print(f"\n\n🧪 Testando busca de contratos específicos:")
            test_contracts = ['1432131', '321421', '31873187']
            
            for test_name in test_contracts:
                print(f"\n🔍 Testando busca para '{test_name}':")
                
                # Método atual - buscar todos e filtrar
                found_contracts = []
                for contract in contracts:
                    if contract.get("name") == test_name:
                        found_contracts.append(contract)
                
                print(f"   📋 Contratos encontrados com nome '{test_name}': {len(found_contracts)}")
                for contract in found_contracts:
                    print(f"     - ID: {contract.get('id')}, Entity: {contract.get('entities_id')}")
        
        kill_session(session_token)
        
    except Exception as e:
        print(f"❌ Erro no debug: {e}")

if __name__ == "__main__":
    debug_duplicate_contracts()