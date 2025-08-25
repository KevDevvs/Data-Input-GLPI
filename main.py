
from remove_data.remove_data import reset_glpi
from helper.colors import c
from create_info.create_entity_hierarchy import create_entity_hierarchy
from create_info.create_users import create_user
from glpi_session.glpi_session import init_session, kill_session
from create_info.create_asset import create_asset
from create_info.get_or_create import get_or_create_manufacturer, get_or_create_model
import openpyxl
import openpyxl
import os
from helper.read_config import FILE_PATH


def main():
    
    print(c("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", 'yellow'))
    print(c("🚀 [INICIANDO] Processamento da planilha XLSX...", 'yellow'))
    
    total_processado = 0
    total_sucesso = 0
    total_erro = 0
    session = None
    
    try:
        if not os.path.exists(FILE_PATH):
            print(c(f"❌ [ERRO] Arquivo '{FILE_PATH}' não encontrado!", 'red'))
            return total_processado, total_sucesso, total_erro
            
        wb = openpyxl.load_workbook(FILE_PATH)
        sheet = wb.active
        if sheet.max_row < 2:
            print(c("❌ [ERRO] Planilha vazia ou sem dados!", 'red'))
            return
        session = init_session()
    except Exception as e:
        print(c(f"❌ [ERRO] Falha ao processar arquivo: {str(e)}", 'red'))
        if session:
            kill_session(session)
        return


    for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        print(c(f"\n📄 [LINHA {idx}] Processando dados...", 'blue'))
        try:
            # Desempacota os campos da linha (nova ordem com email e marca do celular)
            nome, email, ent_a, ent_b, ent_c, linha, cel_marca, cel_modelo, cel_imei, nb_marca, nb_modelo, nb_serial = row

            # Validação de campos obrigatórios
            if not ent_a:
                print(c(f"❌ [ERRO] Entidade A obrigatória na linha {idx}. Pulando linha.", 'red'))
                continue

            # Cria entidades em cascata e pega o ID do último nível preenchido
            entidade_final_id = None
            if ent_c:  # Se tem entidade C, cria hierarquia completa
                entidade_final_id = create_entity_hierarchy(session, ent_a, ent_b, ent_c)
            elif ent_b:  # Se tem só até B, cria até segundo nível
                entidade_final_id = create_entity_hierarchy(session, ent_a, ent_b)
            else:  # Se tem só A, usa primeiro nível
                entidade_final_id = create_entity_hierarchy(session, ent_a)

            if not entidade_final_id:
                print(c(f"❌ [ERRO] Não foi possível criar/encontrar a hierarquia de entidades na linha {idx}.", 'red'))
                continue

            # Cria usuário e vincula sempre ao grupo 'User' e ao perfil Self-Service
            user_id = None
            if nome:
                perfil_id = 1  # ID do perfil Self-Service
                # Verifica se temos um email válido
                if email and '@' in email:
                    print(c(f"📧 [INFO] Email fornecido para '{nome}': {email}", 'cyan'))
                    email_param = f"@{email}"
                else:
                    print(c(f"ℹ️ [INFO] Nenhum email fornecido para '{nome}'", 'blue'))
                    email_param = 'User'
                user_id = create_user(session, nome, email_param, perfil_id, entidade_final_id)

            # Cria ativos vinculados à entidade/usuário (apenas se campo preenchido)
            if linha:
                create_asset(session, "Line", {
                    "name": linha, 
                    "entities_id": entidade_final_id,
                    "users_id": user_id if user_id else 0  # Usa 0 como fallback
                })

            if cel_modelo:
                # Format phone name to include brand and IMEI
                phone_name = cel_modelo
                if cel_marca and cel_imei and str(cel_imei).strip():
                    phone_name = f"Celular {str(cel_marca).strip()} - {str(cel_imei).strip()}"
                elif cel_imei and str(cel_imei).strip():
                    phone_name = f"Celular - {str(cel_imei).strip()}"
                
                # Prepara os dados do telefone
                phone_data = {
                    "name": phone_name,
                    "entities_id": entidade_final_id,
                    "users_id": user_id if user_id else 0,  # Usa 0 como fallback
                }

                # Busca ou cria o modelo
                if cel_modelo:
                    model_id = get_or_create_model(session, cel_modelo, "Phone")
                    if model_id:
                        phone_data["phonemodels_id"] = model_id
                    else:
                        print(c(f"⚠️ [AVISO] Não foi possível criar/encontrar o modelo '{cel_modelo}'", 'yellow'))

                # Busca ou cria o fabricante
                if cel_marca and str(cel_marca).strip():
                    manufacturer_id = get_or_create_manufacturer(session, str(cel_marca).strip())
                    if manufacturer_id:
                        phone_data["manufacturers_id"] = manufacturer_id
                    else:
                        print(c(f"⚠️ [AVISO] Não foi possível criar/encontrar o fabricante '{cel_marca}'", 'yellow'))

                # Adiciona IMEI como número serial
                if cel_imei and str(cel_imei).strip():
                    phone_data["serial"] = str(cel_imei).strip()

                create_asset(session, "Phone", phone_data)

            if nb_modelo:
                # Format computer name to include manufacturer and serial number
                computer_name = nb_modelo
                if nb_marca and nb_serial and str(nb_serial).strip():
                    computer_name = f"Notebook {str(nb_marca).strip()} - {str(nb_serial).strip()}"
                elif nb_serial and str(nb_serial).strip():
                    computer_name = f"Notebook - {str(nb_serial).strip()}"
                
                computer_data = {
                    "name": computer_name,
                    "entities_id": entidade_final_id,
                    "users_id": user_id if user_id else 0,  # Usa 0 como fallback
                    "is_dynamic": 0  # Garantir que não é um computador dinâmico
                }

                # Busca ou cria o modelo
                if nb_modelo:
                    model_id = get_or_create_model(session, nb_modelo, "Computer")
                    if model_id:
                        computer_data["computermodels_id"] = model_id
                    else:
                        print(c(f"⚠️ [AVISO] Não foi possível criar/encontrar o modelo '{nb_modelo}'", 'yellow'))

                # Busca ou cria o fabricante
                if nb_marca and str(nb_marca).strip():
                    manufacturer_id = get_or_create_manufacturer(session, str(nb_marca).strip())
                    if manufacturer_id:
                        computer_data["manufacturers_id"] = manufacturer_id
                    else:
                        print(c(f"⚠️ [AVISO] Não foi possível criar/encontrar o fabricante '{nb_marca}'", 'yellow'))

                # Adiciona serial se for válido
                if nb_serial and str(nb_serial).strip():
                    computer_data["serial"] = str(nb_serial).strip()

                create_asset(session, "Computer", computer_data)

            print(c(f"✅ [OK] Linha {idx} processada!", 'green'))
            total_processado += 1
            total_sucesso += 1
        except Exception as e:
            print(c(f"❌ [ERRO] Falha ao processar linha {idx}: {e}", 'red'))
            total_processado += 1
            total_erro += 1

    kill_session(session)
    print(c("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", 'yellow'))
    print(c("📊 [ESTATÍSTICAS]", 'yellow'))
    print(c(f"Total processado: {total_processado}", 'cyan'))
    print(c(f"Sucessos: {total_sucesso}", 'green'))
    print(c(f"Erros: {total_erro}", 'red'))
    print(c("\n🏁 [FINALIZADO] Sessão encerrada e processamento concluído! 🚀", 'yellow'))
    
    return total_processado, total_sucesso, total_erro


if __name__ == "__main__":
    try:
        print(c("\n🔄 Resetando ambiente GLPI...", 'yellow'))
        reset_glpi()
        print(c("✅ Reset concluído!", 'green'))
        
        total, sucessos, erros = main()
        
        if total > 0:
            taxa_sucesso = (sucessos / total) * 100
            print(c(f"\n📈 Taxa de sucesso: {taxa_sucesso:.1f}%", 'cyan'))
        
        if erros == 0:
            print(c("\n✅ Processamento concluído com sucesso! 🚀", 'green'))
        else:
            print(c(f"\n⚠️ Processamento concluído com {erros} erro(s)! 🚨", 'yellow'))
    except Exception as e:
        print(c(f"\n❌ Erro fatal durante execução: {e}", 'red'))