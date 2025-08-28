# core.py - Core com detecção de modo filtro
import datetime
import time
import traceback
import atexit
import threading
import os
from .writer import LogWriter


class Logger:
    def __init__(self):
        self.writer = LogWriter()

        # Cache simples de tags (thread-safe básico)
        self.used_tags = set(["log", "info", "debug", "warning", "error", "exception"])
        self._tags_lock = threading.Lock()

        # Cache de timestamp simples
        self._last_timestamp = None
        self._last_timestamp_time = 0

        # Monitor de arquivo para detectar modo filtro
        self._last_filter_check = 0
        self._monitoring_enabled = True

        atexit.register(self.flush)

    def _check_filter_mode(self):
        """Verifica se o modo filtro foi ativado no HTML"""
        current_time = time.time()

        # Verifica apenas a cada 1 segundo para não impactar performance
        if current_time - self._last_filter_check < 1.0:
            return

        self._last_filter_check = current_time

        try:
            # Lê o arquivo HTML para verificar o estado do filtro
            if os.path.exists(self.writer.filename):
                with open(self.writer.filename, "r", encoding="utf-8") as f:
                    # Lê apenas os últimos 2000 bytes para encontrar o sinal
                    f.seek(0, 2)  # Vai para o final
                    file_size = f.tell()

                    read_size = min(2000, file_size)
                    f.seek(file_size - read_size)
                    tail_content = f.read()

                    # Procura pelo sinal do JavaScript
                    if 'data-filter-active="true"' in tail_content or 'FILTER_MODE:true:' in tail_content:
                        self.writer.activate_filter_mode()
                    elif 'data-filter-active="false"' in tail_content or 'FILTER_MODE:false:' in tail_content:
                        self.writer.deactivate_filter_mode()
        except:
            # Ignora erros para não impactar o logging
            pass

    def _get_timestamp(self):
        """Timestamp simples com cache mínimo"""
        current_time = time.time()

        # Cache apenas se for o mesmo milissegundo
        if (self._last_timestamp
                and abs(current_time - self._last_timestamp_time) < 0.001):
            return self._last_timestamp

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self._last_timestamp = timestamp
        self._last_timestamp_time = current_time
        return timestamp

    def _add_tag_safe(self, tag):
        """Adiciona tag thread-safe simples"""
        if not tag:
            return

        with self._tags_lock:
            if isinstance(tag, str):
                self.used_tags.add(tag)
            elif isinstance(tag, (list, tuple)):
                self.used_tags.update(str(t) for t in tag)

    def _format_message(self, message, tag=None):
        """Formata mensagem com timestamp e tags"""
        self._add_tag_safe(tag)

        # Timestamp
        ts = self._get_timestamp()

        # Monta mensagem final
        formatted_message = f"<br>{ts} - {str(message)}"

        return formatted_message

    def log(self, message, color="white", tag="log"):
        """Log direto usando o writer otimizado"""
        # Verifica modo filtro ocasionalmente
        if self._monitoring_enabled:
            self._check_filter_mode()

        formatted_message = self._format_message(message, tag)
        self.writer.write(formatted_message, color, tag)

    def info(self, message, color="white", tag="info"):
        """Info com formatação especial"""
        if self._monitoring_enabled:
            self._check_filter_mode()

        self._add_tag_safe(tag)
        ts = self._get_timestamp()
        formatted_message = f"<br>[INFO]<br>{ts} - {str(message)}<br>[INFO]"
        self.writer.write(formatted_message, color, tag)

    def debug(self, message, color="white", tag="debug"):
        if self._monitoring_enabled:
            self._check_filter_mode()

        formatted_message = self._format_message(f"## DEBUG: {str(message)}", tag)
        self.writer.write(formatted_message, color, tag)

    def warning(self, message, color="gold", tag="warning"):
        if self._monitoring_enabled:
            self._check_filter_mode()

        formatted_message = self._format_message(f"⚠️ {str(message)}", tag)
        self.writer.write(formatted_message, color, tag)

    def error(self, message, tag="error"):
        if self._monitoring_enabled:
            self._check_filter_mode()

        formatted_message = self._format_message(f"** {str(message)}", tag)
        self.writer.write(formatted_message, "red", tag)

    def report_exception(self, exc, timeout=None):
        """Reporta exceção"""
        if self._monitoring_enabled:
            self._check_filter_mode()

        err = traceback.format_exc()
        formatted_message = self._format_message(f"**** Exception: <code>{err}</code>", "exception")
        self.writer.write(formatted_message, "red", "exception")

        if timeout:
            time.sleep(timeout)

    def flush(self):
        """Flush simples"""
        self.writer.flush()

    def close(self):
        """Fecha logger e finaliza arquivo HTML"""
        self.writer.finalize_file()

    def get_used_tags(self):
        """Retorna tags usadas"""
        with self._tags_lock:
            return sorted(list(self.used_tags))

    def disable_filter_monitoring(self):
        """Desabilita monitoramento de filtros para máxima performance"""
        self._monitoring_enabled = False

    def enable_filter_monitoring(self):
        """Habilita monitoramento de filtros"""
        self._monitoring_enabled = True
