"""
Script de debug para verificar os valores de status que vêm da planilha
"""
import openpyxl
from helper.colors import c

def debug_status_values():
    """Carrega a planilha e mostra os valores de status"""
    print(c("🔍 Verificando valores de status na planilha...", 'yellow'))
    
    try:
        # Carrega a planilha
        wb = openpyxl.load_workbook("input_glpi.xlsx")
        sheet = wb.active
        
        print(c("\n📊 Valores de status encontrados:", 'cyan'))
        print(c("Linha | line_status | cel_status | nb_status", 'white'))
        print(c("-" * 45, 'white'))
        
        # Verifica as primeiras 10 linhas com dados
        for idx, row in enumerate(sheet.iter_rows(min_row=2, max_row=11, values_only=True), start=2):
            if len(row) >= 36:  # Verifica se tem colunas suficientes
                # Pega os índices corretos baseados na estrutura
                line_status = row[12] if len(row) > 12 else None  # Coluna 13 (índice 12)
                cel_status = row[21] if len(row) > 21 else None   # Coluna 22 (índice 21)
                nb_status = row[35] if len(row) > 35 else None    # Coluna 36 (índice 35)
                
                line_str = str(line_status) if line_status is not None else "None"
                cel_str = str(cel_status) if cel_status is not None else "None"
                nb_str = str(nb_status) if nb_status is not None else "None"
                
                print(f"{idx:4d} | {line_str:11} | {cel_str:10} | {nb_str}")
                
                # Mostra o tipo de dado
                if line_status is not None:
                    print(f"      line_status tipo: {type(line_status)} - valor: '{line_status}'")
                if cel_status is not None:
                    print(f"      cel_status tipo: {type(cel_status)} - valor: '{cel_status}'")
                if nb_status is not None:
                    print(f"      nb_status tipo: {type(nb_status)} - valor: '{nb_status}'")
                print()
                
    except Exception as e:
        print(c(f"❌ Erro ao analisar planilha: {e}", 'red'))

if __name__ == "__main__":
    debug_status_values()