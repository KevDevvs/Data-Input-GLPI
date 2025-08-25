# Data-Input-GLPI
        Processa a planilha XLSX e realiza input dos dados no GLPI via API.
        
        Args:
            FILE_PATH: Caminho para o arquivo XLSX com os dados
            
        Returns:
            tuple: (total_processado, total_sucesso, total_erro) contagem de registros
            
        A planilha deve conter as seguintes colunas:
        - Nome do usuário
        - Entidade A (obrigatória)
        - Entidade B (opcional)
        - Entidade C (opcional)
        - Linha telefônica
        - Celular modelo
        - Celular IMEI
        - Notebook modelo
        - Notebook marca
        - Notebook serial
