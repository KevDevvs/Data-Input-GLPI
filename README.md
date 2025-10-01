# Data-Input-GLPI

Script para input automatizado de dados no GLPI via API.

## Funcionalidades

- **Criação de Entidades**: Cria hierarquias de entidades em cascata
- **Criação de Usuários**: Registra usuários com perfis e grupos
- **Criação de Ativos**: Notebooks, celulares e linhas telefônicas
- **Criação de Componentes**: Armazenamento, processadores e memória RAM para notebooks
- **Vinculação Automática**: Associa componentes aos notebooks automaticamente

## Estrutura da Planilha

A planilha deve conter as seguintes colunas (ordem importa):

1. **Nome do User** - Nome completo do usuário
2. **email** - Email do usuário (obrigatório)
3. **CPF** - CPF do usuário
4. **Entidade A** - Primeira entidade (obrigatória)
5. **Entidade B** - Segunda entidade (opcional)
6. **Entidade C** - Terceira entidade (opcional)
7. **Entidade D** - Quarta entidade (opcional)
8. **Linha** - Número da linha telefônica
9. **Operadora** - Nome da operadora telefônica
10. **Marca do celular** - Fabricante do celular
11. **Modelo do Celular** - Modelo do celular
12. **IMEI do Celular** - IMEI do celular
13. **Fabricante Notebook** - Fabricante do notebook
14. **Modelo do Notebook** - Modelo do notebook
15. **Tipo de computador** - Tipo de computador (ID)
16. **Serial Number do Notebook** - Número de série
17. **Ativo Notebook** - Número do ativo
18. **Armazenamento Notebook** - Tipo de armazenamento (ex: "HDD 500GB", "SSD 256GB")
19. **Processador Notebook** - Processador (ex: "Intel i5", "AMD Ryzen 7")
20. **Memoria RAM Notebook** - Memória RAM (ex: "8GB", "16GB DDR4")

## Nova Funcionalidade: Componentes

O script agora cria automaticamente componentes de hardware para notebooks:

### Tipos de Componentes Criados:
- **Armazenamento**: HDDs, SSDs baseados no campo "Armazenamento Notebook"
- **Processador**: CPUs baseados no campo "Processador Notebook"  
- **Memória RAM**: Módulos de memória baseados no campo "Memoria RAM Notebook"

### Como Funciona:
1. O script cria o notebook no GLPI
2. Para cada componente preenchido na planilha:
   - Verifica se o tipo de componente existe (ex: "Armazenamento"), se não existe cria
   - Verifica se o componente específico existe (ex: "HDD 500GB"), se não existe cria
   - Vincula o componente ao notebook criado

### Exemplo de Dados:
```
Armazenamento Notebook: "SSD 256GB"
Processador Notebook: "Intel Core i7-8650U"  
Memoria RAM Notebook: "16GB DDR4"
```

Resultado no GLPI:
- Notebook criado com componentes vinculados
- Componentes reutilizáveis para outros notebooks
- Tipos de componente padronizados

## Como Executar

```bash
python main.py
```

## Retorno

O script retorna uma tupla com:
- `total_processado`: Total de linhas processadas
- `total_sucesso`: Sucessos
- `total_erro`: Erros encontrados
