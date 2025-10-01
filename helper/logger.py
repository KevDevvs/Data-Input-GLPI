import os
import logging
from datetime import datetime
from helper.colors import c

class GLPILogger:
    """
    Classe para gerenciar logs do sistema GLPI
    Salva logs em arquivo TXT e opcionalmente exibe no terminal
    """
    
    def __init__(self, log_dir="logs", log_file=None):
        """
        Inicializa o logger
        
        Args:
            log_dir (str): Diretório onde salvar os logs
            log_file (str): Nome do arquivo de log (opcional, usa timestamp se não fornecido)
        """
        self.log_dir = log_dir
        
        # Cria diretório de logs se não existir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Define nome do arquivo se não fornecido
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"glpi_input_{timestamp}.log"
        
        self.log_file_path = os.path.join(log_dir, log_file)
        
        # Configura o logger
        self.logger = logging.getLogger('GLPI_Logger')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove handlers existentes para evitar duplicação
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Configura handler para arquivo
        file_handler = logging.FileHandler(self.log_file_path, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Formato personalizado para o arquivo
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Adiciona handler ao logger
        self.logger.addHandler(file_handler)
        
        # Log inicial
        self.info("=" * 60)
        self.info("INÍCIO DO LOG - GLPI Data Input System")
        self.info("=" * 60)
    
    def _log_and_print(self, level, message, color=None, show_terminal=True):
        """
        Método interno para logar e exibir mensagem
        
        Args:
            level (str): Nível do log (INFO, ERROR, WARNING, etc.)
            message (str): Mensagem a ser logada
            color (str): Cor para exibição no terminal
            show_terminal (bool): Se deve exibir no terminal
        """
        # Remove códigos de cores para o arquivo de log
        clean_message = self._remove_color_codes(message)
        
        # Loga no arquivo
        if level.upper() == 'DEBUG':
            self.logger.debug(clean_message)
        elif level.upper() == 'INFO':
            self.logger.info(clean_message)
        elif level.upper() == 'WARNING':
            self.logger.warning(clean_message)
        elif level.upper() == 'ERROR':
            self.logger.error(clean_message)
        elif level.upper() == 'CRITICAL':
            self.logger.critical(clean_message)
        
        # Exibe no terminal se solicitado
        if show_terminal:
            if color:
                print(c(message, color))
            else:
                print(message)
    
    def _remove_color_codes(self, text):
        """Remove códigos de cores da mensagem para salvar no arquivo"""
        import re
        # Remove códigos ANSI de cores
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', str(text))
    
    def info(self, message, show_terminal=True):
        """Log de informação (azul no terminal)"""
        self._log_and_print('INFO', message, 'blue', show_terminal)
    
    def success(self, message, show_terminal=True):
        """Log de sucesso (verde no terminal)"""
        self._log_and_print('INFO', f"✅ {message}", 'green', show_terminal)
    
    def warning(self, message, show_terminal=True):
        """Log de aviso (amarelo no terminal)"""
        self._log_and_print('WARNING', f"⚠️ {message}", 'yellow', show_terminal)
    
    def error(self, message, show_terminal=True):
        """Log de erro (vermelho no terminal)"""
        self._log_and_print('ERROR', f"❌ {message}", 'red', show_terminal)
    
    def debug(self, message, show_terminal=False):
        """Log de debug (cyan no terminal, não exibe por padrão)"""
        self._log_and_print('DEBUG', f"🔍 {message}", 'cyan', show_terminal)
    
    def critical(self, message, show_terminal=True):
        """Log crítico (vermelho no terminal)"""
        self._log_and_print('CRITICAL', f"🚨 {message}", 'red', show_terminal)
    
    def separator(self, title="", show_terminal=True):
        """Adiciona separador visual no log"""
        if title:
            sep = f"--- {title} ---"
        else:
            sep = "-" * 50
        self._log_and_print('INFO', sep, 'yellow', show_terminal)
    
    def process_start(self, description, show_terminal=True):
        """Log de início de processo"""
        self._log_and_print('INFO', f"🚀 INICIANDO: {description}", 'yellow', show_terminal)
    
    def process_end(self, description, show_terminal=True):
        """Log de fim de processo"""
        self._log_and_print('INFO', f"🏁 CONCLUÍDO: {description}", 'green', show_terminal)
    
    def line_processing(self, line_number, show_terminal=True):
        """Log de processamento de linha específica"""
        self._log_and_print('INFO', f"📄 Processando linha {line_number}...", 'blue', show_terminal)
    
    def item_created(self, item_type, item_id, item_name="", show_terminal=True):
        """Log de criação de item bem-sucedida"""
        name_part = f" - {item_name}" if item_name else ""
        self._log_and_print('INFO', f"✅ {item_type} criado (ID: {item_id}){name_part}", 'green', show_terminal)
    
    def item_failed(self, item_type, reason="", show_terminal=True):
        """Log de falha na criação de item"""
        reason_part = f" - {reason}" if reason else ""
        self._log_and_print('ERROR', f"❌ Falha ao criar {item_type}{reason_part}", 'red', show_terminal)
    
    def status_update(self, column_name, status, show_terminal=True):
        """Log de atualização de status na planilha"""
        emoji = "✅" if status == "OK" else "❌" if status == "ERRO" else "⚪"
        self._log_and_print('INFO', f"{emoji} Status {column_name}: {status}", 'cyan', show_terminal)
    
    def statistics(self, total, success, errors, show_terminal=True):
        """Log de estatísticas finais"""
        self.separator("ESTATÍSTICAS FINAIS", show_terminal)
        self._log_and_print('INFO', f"📊 Total processado: {total}", 'cyan', show_terminal)
        self._log_and_print('INFO', f"✅ Sucessos: {success}", 'green', show_terminal)
        self._log_and_print('INFO', f"❌ Erros: {errors}", 'red', show_terminal)
        
        if total > 0:
            success_rate = (success / total) * 100
            self._log_and_print('INFO', f"📈 Taxa de sucesso: {success_rate:.1f}%", 'cyan', show_terminal)
    
    def close(self):
        """Fecha o logger e salva informações finais"""
        self.separator("FIM DO LOG", True)
        self.info(f"Log salvo em: {self.log_file_path}")
        
        # Remove handlers para evitar problemas
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)
    
    def get_log_file_path(self):
        """Retorna o caminho completo do arquivo de log"""
        return os.path.abspath(self.log_file_path)


# Instância global do logger (será inicializada quando necessário)
_global_logger = None

def get_logger(log_dir="logs", log_file=None):
    """
    Função para obter uma instância global do logger
    
    Args:
        log_dir (str): Diretório dos logs
        log_file (str): Nome do arquivo de log
    
    Returns:
        GLPILogger: Instância do logger
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = GLPILogger(log_dir, log_file)
    return _global_logger

def close_logger():
    """Fecha o logger global"""
    global _global_logger
    if _global_logger is not None:
        _global_logger.close()
        _global_logger = None