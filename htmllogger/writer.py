# writer.py
import os
import datetime
import glob
import time
from . import config, html_template


class LogWriter:
    def __init__(self):
        self.filename = os.path.join(config.log_dir, config.main_filename)
        os.makedirs(config.log_dir, exist_ok=True)
        if not os.path.exists(self.filename):
            self._create_log_file()

        # Buffer para armazenar múltiplas linhas antes de escrever
        self.buffer = []
        self.buffer_size = 50  # Número de linhas para bufferizar
        self.last_write_time = time.time()
        self.write_interval = 0.1  # Escrever a cada 0.1 segundos no mínimo

    def _create_log_file(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(html_template.html_header)

    def _rotate_file(self):
        ts = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        new_filename = os.path.join(
            config.log_dir, f"{ts}_{config.main_filename}")
        os.rename(self.filename, new_filename)
        self._create_log_file()

        # mantém apenas os N arquivos mais recentes
        files = sorted(glob.glob(os.path.join(
            config.log_dir, "*.html")), key=os.path.getctime, reverse=True)
        if len(files) > config.max_files:
            for old_file in files[config.max_files:]:
                os.remove(old_file)

    def write(self, line: str):
        current_time = time.time()

        # Adiciona linha ao buffer
        self.buffer.append(line)

        # Verifica se deve escrever no arquivo
        if (len(self.buffer) >= self.buffer_size
                or current_time - self.last_write_time >= self.write_interval):
            self._flush_buffer()

    def _flush_buffer(self):
        if not self.buffer:
            return

        if os.path.exists(self.filename) and os.path.getsize(self.filename) >= config.max_size:
            self._rotate_file()

        # Abre o arquivo uma vez para todas as linhas do buffer
        with open(self.filename, "r+", encoding="utf-8") as f:
            content = f.read()
            new_content = content.replace(
                "<!-- LOG_CONTENT -->",
                "\n" + "\n".join(self.buffer) + "<!-- LOG_CONTENT -->"
            )
            f.seek(0)
            f.write(new_content)
            f.truncate()

        # Limpa o buffer e atualiza o tempo
        self.buffer = []
        self.last_write_time = time.time()

    def flush(self):
        """Força a escrita do buffer restante"""
        self._flush_buffer()
