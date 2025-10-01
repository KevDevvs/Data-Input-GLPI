"""
Script para investigar os campos corretos de data para linhas no GLPI
"""
import requests
from helper.read_config import GLPI_URL, HEADERS
from glpi_session.glpi_session import init_session, kill_session
from helper.colors import c

def investigate_line_date_fields():
    """Investiga quais campos de data estão disponíveis para linhas"""
    print(c("🔍 Investigando campos de data para linhas...", 'yellow'))
    
    try:
        # Inicia sessão GLPI
        session = init_session()
        if not session:
            print(c("❌ Falha ao conectar com GLPI", 'red'))
            return
        
        headers = {**HEADERS, "Session-Token": session}
        
        # Busca uma linha existente para ver sua estrutura
        lines_response = requests.get(f"{GLPI_URL}/Line", headers=headers)
        
        if lines_response.status_code in [200, 206]:
            lines_data = lines_response.json()
            
            if isinstance(lines_data, list) and len(lines_data) > 0:
                # Pega a primeira linha para análise
                first_line = lines_data[0]
                
                print(c("📊 Estrutura de uma linha existente:", 'cyan'))
                print(c("=" * 50, 'white'))
                
                # Procura por campos relacionados a data
                date_fields = []
                for key, value in first_line.items():
                    if any(word in key.lower() for word in ['date', 'data', 'start', 'begin', 'init', 'warranty', 'buy', 'purchase']):
                        date_fields.append((key, value))
                        print(c(f"🗓️  {key}: {value}", 'green'))
                
                if not date_fields:
                    print(c("⚠️ Nenhum campo de data encontrado nos campos óbvios", 'yellow'))
                    print(c("\n📋 Todos os campos da linha:", 'cyan'))
                    for key, value in first_line.items():
                        print(f"   {key}: {value}")
                
                # Verifica se existe um campo mais específico
                possible_start_fields = [
                    'begin_date', 'start_date', 'activation_date', 'installation_date',
                    'warranty_date', 'buy_date', 'purchase_date', 'creation_date'
                ]
                
                print(c(f"\n🎯 Campos testados para data de início:", 'cyan'))
                for field in possible_start_fields:
                    if field in first_line:
                        print(c(f"✅ {field}: {first_line[field]}", 'green'))
                    else:
                        print(c(f"❌ {field}: Não encontrado", 'red'))
                        
            else:
                print(c("❌ Nenhuma linha encontrada para análise", 'red'))
        else:
            print(c(f"❌ Erro ao buscar linhas: {lines_response.status_code}", 'red'))
        
        # Encerra sessão
        kill_session(session)
        
    except Exception as e:
        print(c(f"❌ Erro na investigação: {e}", 'red'))

def test_line_creation_with_different_date_fields():
    """Testa criação de linha com diferentes campos de data"""
    print(c("\n🧪 Testando criação de linha com diferentes campos de data...", 'yellow'))
    
    try:
        session = init_session()
        if not session:
            return
        
        headers = {**HEADERS, "Session-Token": session}
        
        # Dados base para teste
        test_data_base = {
            "name": "Teste Data Linha",
            "entities_id": 0,
            "users_id": 0,
            "lineoperators_id": 1,
            "linetypes_id": 1,
            "states_id": 8
        }
        
        # Testa diferentes campos de data
        date_fields_to_test = [
            'buy_date',
            'begin_date', 
            'start_date',
            'activation_date',
            'installation_date',
            'warranty_date'
        ]
        
        test_date = "2024-03-11"
        
        for date_field in date_fields_to_test:
            print(c(f"\n🔍 Testando campo: {date_field}", 'cyan'))
            
            test_data = test_data_base.copy()
            test_data[date_field] = test_date
            
            # Tenta criar a linha
            create_response = requests.post(f"{GLPI_URL}/Line", headers=headers, json={"input": test_data})
            
            if create_response.status_code in [200, 201]:
                response_data = create_response.json()
                line_id = response_data.get("id")
                if line_id:
                    print(c(f"✅ Linha criada com {date_field} (ID: {line_id})", 'green'))
                    
                    # Busca a linha criada para verificar se o campo foi salvo
                    get_response = requests.get(f"{GLPI_URL}/Line/{line_id}", headers=headers)
                    if get_response.status_code == 200:
                        line_data = get_response.json()
                        if date_field in line_data and line_data[date_field]:
                            print(c(f"✅ Campo {date_field} salvo: {line_data[date_field]}", 'green'))
                        else:
                            print(c(f"❌ Campo {date_field} não foi salvo", 'red'))
                else:
                    print(c(f"❌ Falha ao criar linha com {date_field}", 'red'))
            else:
                print(c(f"❌ Erro HTTP {create_response.status_code} para {date_field}", 'red'))
        
        kill_session(session)
        
    except Exception as e:
        print(c(f"❌ Erro no teste: {e}", 'red'))

if __name__ == "__main__":
    investigate_line_date_fields()
    test_line_creation_with_different_date_fields()