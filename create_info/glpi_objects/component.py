from helper.read_config import HEADERS, GLPI_URL
import requests
from helper.colors import c
from time import sleep

def link_component(computer_id, nb_armazenamento, nb_processador, nb_memoria, session):
    
    headers = {**HEADERS, "Session-Token": session}
        
    # Processa armazenamento (HDD/SSD)
    if nb_armazenamento and str(nb_armazenamento).strip():
        try:
            hd_name = str(nb_armazenamento).strip()
            
            # Primeiro procura se já existe
            search_params = {
                "criteria[0][field]": 1,  # campo 1 = name
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": hd_name,
                "reset": "reset"
            }
            search_response = requests.get(f"{GLPI_URL}/search/DeviceHardDrive", 
                                        headers=headers, 
                                        params=search_params)
            
            hd_id = None
            if search_response.status_code == 200:
                result = search_response.json()
                if result.get("totalcount", 0) > 0:
                    hd_id = int(result["data"][0].get("2", 0))
            
            # Se não encontrou, cria
            if not hd_id:
                hd_data = {
                    "name": hd_name,
                    "designation": hd_name,
                    "comment": "Criado automaticamente",
                    "entities_id": 0,
                    "is_recursive": 1
                }
                hd_response = requests.post(f"{GLPI_URL}/DeviceHardDrive", 
                                            headers=headers, 
                                            json={"input": hd_data})
                
                if hd_response.status_code == 201:
                    hd_id = hd_response.json().get("id")
            
            # Vincula ao computador se tiver ID
            if hd_id:
                link_data = {
                    "items_id": computer_id,
                    "itemtype": "Computer",
                    "deviceharddrives_id": hd_id
                }
                link_response = requests.post(f"{GLPI_URL}/Item_DeviceHardDrive", 
                            headers=headers, 
                            json={"input": link_data})
                
                if not link_response.status_code in [200, 201]:
                    print(c(f"❌ Erro ao vincular HD: {link_response.text}", 'red'))
        except Exception as e:
            print(c(f"❌ Erro ao processar HD: {str(e)}", 'red'))
    
    # Processa processador
    if nb_processador and str(nb_processador).strip():
        try:
            cpu_name = str(nb_processador).strip()
            
            # Primeiro procura se já existe
            search_params = {
                "criteria[0][field]": 1,  # campo 1 = name
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": cpu_name,
                "reset": "reset"
            }
            search_response = requests.get(f"{GLPI_URL}/search/DeviceProcessor", 
                                        headers=headers, 
                                        params=search_params)
            
            cpu_id = None
            if search_response.status_code == 200:
                result = search_response.json()
                if result.get("totalcount", 0) > 0:
                    cpu_id = int(result["data"][0].get("2", 0))
                    print(c(f"✅ Processador '{cpu_name}' encontrado (ID: {cpu_id})", 'green'))
            
            # Se não encontrou, cria
            if not cpu_id:
                cpu_data = {
                    "name": cpu_name,
                    "designation": cpu_name,
                    "comment": "Criado automaticamente",
                    "entities_id": 0,
                    "is_recursive": 1
                }
                cpu_response = requests.post(f"{GLPI_URL}/DeviceProcessor", 
                                            headers=headers, 
                                            json={"input": cpu_data})
                
                if cpu_response.status_code == 201:
                    cpu_id = cpu_response.json().get("id")
            
            # Vincula ao computador se tiver ID
            if cpu_id:
                link_data = {
                    "items_id": computer_id,
                    "itemtype": "Computer",
                    "deviceprocessors_id": cpu_id
                }
                link_response = requests.post(f"{GLPI_URL}/Item_DeviceProcessor", 
                            headers=headers, 
                            json={"input": link_data})
                
                if not link_response.status_code in [200, 201]:
                    print(c(f"❌ Erro ao vincular processador: {link_response.text}", 'red'))
        except Exception as e:
            print(c(f"❌ Erro ao processar processador: {str(e)}", 'red'))
    
    # Processa memória RAM
    if nb_memoria and str(nb_memoria).strip():
        try:
            ram_name = str(nb_memoria).strip()
            
            # Primeiro procura se já existe
            search_params = {
                "criteria[0][field]": 1,  # campo 1 = name
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": ram_name,
                "reset": "reset"
            }
            search_response = requests.get(f"{GLPI_URL}/search/DeviceMemory", 
                                        headers=headers, 
                                        params=search_params)
            
            ram_id = None
            if search_response.status_code == 200:
                result = search_response.json()
                if result.get("totalcount", 0) > 0:
                    ram_id = int(result["data"][0].get("2", 0))
            
            # Se não encontrou, cria
            if not ram_id:
                ram_data = {
                    "name": ram_name,
                    "designation": ram_name,
                    "comment": "Criada automaticamente",
                    "entities_id": 0,
                    "is_recursive": 1
                }
                ram_response = requests.post(f"{GLPI_URL}/DeviceMemory", 
                                            headers=headers, 
                                            json={"input": ram_data})
                
                if ram_response.status_code == 201:
                    ram_id = ram_response.json().get("id")
            
            # Vincula ao computador se tiver ID
            if ram_id:
                link_data = {
                    "items_id": computer_id,
                    "itemtype": "Computer",
                    "devicememories_id": ram_id,
                    "size": str(ram_name).replace("GB", "").strip()
                }
                link_response = requests.post(f"{GLPI_URL}/Item_DeviceMemory", 
                            headers=headers, 
                            json={"input": link_data})
                
                if not link_response.status_code in [200, 201]:
                    print(c(f"❌ Erro ao vincular memória: {link_response.text}", 'red'))
        except Exception as e:
            print(c(f"❌ Erro ao processar memória: {str(e)}", 'red'))
    
  