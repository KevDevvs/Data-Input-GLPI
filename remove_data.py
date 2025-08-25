import mysql.connector

# Configuração da conexão com o banco
config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "glpi"
}

# Script SQL para limpeza (mantém configs e usuários padrão)
reset_sql = """
SET FOREIGN_KEY_CHECKS = 0;
DELETE FROM glpi_tickets;
DELETE FROM glpi_tickets_users;
DELETE FROM glpi_tickets_groups;
DELETE FROM glpi_tickets_tickets;
DELETE FROM glpi_tickets_items;
DELETE FROM glpi_ticketsatisfactions;
DELETE FROM glpi_ticketfollowups;
DELETE FROM glpi_tickettasks;
DELETE FROM glpi_ticketvalidations;

DELETE FROM glpi_computers;
DELETE FROM glpi_monitors;
DELETE FROM glpi_printers;
DELETE FROM glpi_networkequipments;
DELETE FROM glpi_phones;
DELETE FROM glpi_peripherals;
DELETE FROM glpi_softwarelicenses;
DELETE FROM glpi_softwareversions;
DELETE FROM glpi_softwares;
DELETE FROM glpi_consumables;
DELETE FROM glpi_cartridges;

DELETE FROM glpi_documents;
DELETE FROM glpi_documents_items;

DELETE FROM glpi_logs;
DELETE FROM glpi_events;
DELETE FROM glpi_notepads;

DELETE FROM glpi_users WHERE name NOT IN ('glpi', 'tech', 'normal', 'post-only', 'GLPI Bot');

DELETE FROM glpi_groups_users WHERE users_id IN (SELECT id FROM glpi_users WHERE name NOT IN ('glpi', 'tech', 'normal', 'post-only', 'GLPI Bot'));
DELETE FROM glpi_users_profiles WHERE users_id IN (SELECT id FROM glpi_users WHERE name NOT IN ('glpi', 'tech', 'normal', 'post-only', 'GLPI Bot'));
DELETE FROM glpi_entities_users WHERE users_id IN (SELECT id FROM glpi_users WHERE name NOT IN ('glpi', 'tech', 'normal', 'post-only', 'GLPI Bot'));
DELETE FROM glpi_useremails WHERE users_id IN (SELECT id FROM glpi_users WHERE name NOT IN ('glpi', 'tech', 'normal', 'post-only', 'GLPI Bot'));
DELETE FROM glpi_userphones WHERE users_id IN (SELECT id FROM glpi_users WHERE name NOT IN ('glpi', 'tech', 'normal', 'post-only', 'GLPI Bot'));
DELETE FROM glpi_usercategories_users WHERE users_id IN (SELECT id FROM glpi_users WHERE name NOT IN ('glpi', 'tech', 'normal', 'post-only', 'GLPI Bot'));
DELETE FROM glpi_users_infos WHERE users_id IN (SELECT id FROM glpi_users WHERE name NOT IN ('glpi', 'tech', 'normal', 'post-only'));
DELETE FROM glpi_entities WHERE name <> 'GI Group';

DELETE FROM glpi_contacts;
DELETE FROM glpi_contacttypes;
DELETE FROM glpi_locations;
DELETE FROM glpi_domains;

DELETE FROM glpi_reminders;
DELETE FROM glpi_alerts;
DELETE FROM glpi_knowbaseitems;

ALTER TABLE glpi_tickets AUTO_INCREMENT = 1;
ALTER TABLE glpi_computers AUTO_INCREMENT = 1;
ALTER TABLE glpi_users AUTO_INCREMENT = 1;
ALTER TABLE glpi_entities AUTO_INCREMENT = 1;
"""

def reset_glpi():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # Executa múltiplos comandos SQL, ignorando comentários, comandos vazios e comandos para tabelas inexistentes
        for command in reset_sql.split(";"):
            cmd = command.strip()
            # Ignora comentários e comandos vazios
            if not cmd or cmd.startswith("--"):
                continue
            # Se for TRUNCATE, DELETE ou ALTER TABLE, verifica se a tabela existe
            import re
            match = re.match(r"(TRUNCATE|ALTER TABLE|DELETE FROM) ([a-zA-Z0-9_]+)", cmd)
            if match:
                table = match.group(2)
                cursor.execute(f"SHOW TABLES LIKE '{table}'")
                if cursor.fetchone() is None:
                    print(f"⚠️ Tabela '{table}' não existe. Comando ignorado.")
                    continue
            cursor.execute(cmd + ";")
        # Reativa restrições de chave estrangeira
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        conn.commit()
        print("✅ Reset do GLPI concluído com sucesso!")
    
    except mysql.connector.Error as err:
        print(f"❌ Erro: {err}")
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# if __name__ == "__main__":
#     reset_glpi()
