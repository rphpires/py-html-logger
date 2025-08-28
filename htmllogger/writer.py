# writer.py - Append otimizado com marcador dinâmico
import os
import datetime
import glob
import time
import threading
import pkgutil
from . import config


class LogWriter:
    def __init__(self):
        self.filename = os.path.join(config.log_dir, config.main_filename)
        os.makedirs(config.log_dir, exist_ok=True)

        # Lock simples para thread safety
        self._file_lock = threading.Lock()
        self._file_handle = None
        self._last_color = None
        self._last_flush = 0

        # Estados do arquivo
        self._filter_mode_active = False
        self._end_marker = "<!-- LOG_END_MARKER -->"

        # Inicializa arquivo
        self._initialize_file()

    def _create_log_file(self):
        """Cria arquivo HTML usando template original + marcador"""
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                # Usa template original, mas modifica para adicionar nosso marcador
                template_content = pkgutil.get_data(__name__.split('.')[0], 'template.html').decode('utf-8')

                # Adiciona nosso marcador após o <!-- LOG_CONTENT -->
                modified_template = template_content.replace(
                    "<!-- LOG_CONTENT -->",
                    f"<!-- LOG_CONTENT -->\n{self._end_marker}"
                )
                f.write(modified_template)
        except Exception as e:
            print(f"Error creating log file: {e}")
            # Fallback - cria arquivo básico
            try:
                with open(self.filename, "w", encoding="utf-8") as f:
                    f.write("""<!DOCTYPE html>
<html>
<head><meta charset="utf-8" /></head>
<body style="color:white;background:black;font-family:monospace;">
<div id="logContainer">
<font color="white">
<!-- LOG_CONTENT -->
""" + self._end_marker + """
</font>
</div>
</body>
</html>""")
            except Exception as e2:
                print(f"Error creating fallback log file: {e2}")

    def _initialize_file(self):
        """Inicializa arquivo HTML se não existir"""
        if not os.path.exists(self.filename):
            self._create_log_file()

        # Garante que temos um handle válido
        with self._file_lock:
            if self._file_handle:
                try:
                    self._file_handle.close()
                except:
                    pass
                self._file_handle = None

            try:
                self._file_handle = open(self.filename, "a", encoding="utf-8", buffering=1)
            except Exception as e:
                print(f"Error opening log file: {e}")
                self._file_handle = None

    def write(self, message, color="white", tag=None):
        """Escrita direta com append otimizado"""
        current_time = time.time()

        # Verifica rotação apenas ocasionalmente
        if current_time - self._last_flush > 2.0:
            try:
                if (os.path.exists(self.filename)
                        and os.path.getsize(self.filename) >= config.max_size):
                    self._rotate_file()
            except:
                pass

        with self._file_lock:
            if not self._file_handle:
                self._initialize_file()

            try:
                # Prepara atributos de tag
                tag_attr = ""
                if tag:
                    if isinstance(tag, str):
                        tag_list = [tag]
                    else:
                        tag_list = [str(t) for t in tag] if tag else []

                    if tag_list:
                        tag_attr = f" data-tags='{','.join(tag_list)}'"

                # Se estamos em modo normal, usa append simples (MÁXIMA PERFORMANCE)
                if not self._filter_mode_active:
                    # Append direto como Trace.py - sem leitura de arquivo
                    if self._last_color != color:
                        prefix = ""
                        if self._last_color is not None:
                            prefix += '</font>'
                        prefix += f'<font color="{color}"{tag_attr}>\n'
                        content = prefix + message
                        self._last_color = color
                    else:
                        # Para mesma cor, mas com tags diferentes
                        if tag_attr:
                            prefix = f'</font><font color="{color}"{tag_attr}>\n'
                            content = prefix + message
                        else:
                            content = "\n" + message

                    # APPEND DIRETO - máxima performance
                    self._file_handle.write(content)

                else:
                    # Modo filtro ativo - precisa inserir no local correto
                    self._insert_with_marker(message, color, tag_attr)

                # Flush baseado no Trace.py
                if current_time - self._last_flush > 2.0:
                    self._file_handle.flush()
                    self._last_flush = current_time

            except Exception as e:
                print(f"Error writing log: {e}")
                try:
                    self._file_handle = None
                    self._initialize_file()
                except:
                    pass

    def _insert_with_marker(self, message, color, tag_attr):
        """Insere log respeitando o marcador (usado apenas quando filtros ativos)"""
        try:
            # Fecha arquivo temporariamente
            self._file_handle.close()

            # Lê arquivo
            with open(self.filename, "r", encoding="utf-8") as f:
                content = f.read()

            # Prepara nova linha
            if self._last_color != color:
                prefix = ""
                if self._last_color is not None:
                    prefix += '</font>'
                prefix += f'<font color="{color}"{tag_attr}>\n'
                new_line = prefix + message
                self._last_color = color
            else:
                if tag_attr:
                    prefix = f'</font><font color="{color}"{tag_attr}>\n'
                    new_line = prefix + message
                else:
                    new_line = "\n" + message

            # Insere antes do marcador
            if self._end_marker in content:
                new_content = content.replace(
                    self._end_marker,
                    new_line + "\n" + self._end_marker
                )
            else:
                # Fallback
                new_content = content + new_line

            # Reescreve arquivo
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write(new_content)

            # Reabre em modo append
            self._file_handle = open(self.filename, "a", encoding="utf-8", buffering=1)

        except Exception as e:
            print(f"Error in marker insertion: {e}")
            # Reabre arquivo em caso de erro
            self._file_handle = open(self.filename, "a", encoding="utf-8", buffering=1)

    def activate_filter_mode(self):
        """Ativa modo filtro - reorganiza arquivo para funcionar com filtros"""
        if self._filter_mode_active:
            return

        with self._file_lock:
            try:
                # Fecha handle atual
                if self._file_handle:
                    self._file_handle.close()
                    self._file_handle = None

                # Lê arquivo atual
                with open(self.filename, "r", encoding="utf-8") as f:
                    content = f.read()

                # Se o marcador não existe, adiciona
                if self._end_marker not in content:
                    # Encontra onde inserir o marcador
                    if "<!-- LOG_CONTENT -->" in content:
                        content = content.replace(
                            "<!-- LOG_CONTENT -->",
                            f"<!-- LOG_CONTENT -->\n{self._end_marker}"
                        )
                    else:
                        # Adiciona antes do fechamento
                        content = content.replace(
                            "</div>",
                            f"{self._end_marker}\n</div>"
                        )

                # Reescreve arquivo
                with open(self.filename, "w", encoding="utf-8") as f:
                    f.write(content)

                self._filter_mode_active = True

                # Reabre arquivo
                self._file_handle = open(self.filename, "a", encoding="utf-8", buffering=1)

            except Exception as e:
                print(f"Error activating filter mode: {e}")

    def deactivate_filter_mode(self):
        """Desativa modo filtro - volta para append direto máxima performance"""
        if not self._filter_mode_active:
            return

        with self._file_lock:
            try:
                # Fecha handle
                if self._file_handle:
                    self._file_handle.close()
                    self._file_handle = None

                # Remove marcador do arquivo
                with open(self.filename, "r", encoding="utf-8") as f:
                    content = f.read()

                # Remove marcador
                content = content.replace(self._end_marker, "")

                # Reescreve arquivo
                with open(self.filename, "w", encoding="utf-8") as f:
                    f.write(content)

                self._filter_mode_active = False

                # Reabre em modo append
                self._file_handle = open(self.filename, "a", encoding="utf-8", buffering=1)

            except Exception as e:
                print(f"Error deactivating filter mode: {e}")

    def _rotate_file(self):
        """Rotaciona arquivo quando atinge tamanho máximo"""
        with self._file_lock:
            # Fecha tags HTML antes de rotacionar
            if self._file_handle:
                try:
                    self._file_handle.write('</font>\n  </div>\n</body>\n</html>\n')
                    self._file_handle.flush()
                    self._file_handle.close()
                except:
                    pass
                self._file_handle = None

            # Remove marcador antes de rotacionar
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    content = f.read()
                content = content.replace(self._end_marker, "")
                with open(self.filename, "w", encoding="utf-8") as f:
                    f.write(content)
            except:
                pass

            # Rotaciona arquivo
            ts = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            new_filename = os.path.join(
                config.log_dir, f"{ts}_{config.main_filename}")

            try:
                os.rename(self.filename, new_filename)
            except:
                pass

            # Cria novo arquivo
            self._create_log_file()
            self._last_color = None
            self._filter_mode_active = False

            # Limpa arquivos antigos
            self._cleanup_old_files()

            # Reabre handle
            self._file_handle = open(self.filename, "a", encoding="utf-8", buffering=1)

    def _cleanup_old_files(self):
        """Remove arquivos antigos mantendo apenas os mais recentes"""
        try:
            files = sorted(glob.glob(os.path.join(
                config.log_dir, "*.html")), key=os.path.getctime, reverse=True)
            if len(files) > config.max_files:
                for old_file in files[config.max_files:]:
                    try:
                        os.remove(old_file)
                    except:
                        pass
        except:
            pass

    def flush(self):
        """Força flush imediato"""
        with self._file_lock:
            if self._file_handle:
                try:
                    self._file_handle.flush()
                    self._last_flush = time.time()
                except:
                    pass

    def close(self):
        """Fecha arquivo adequadamente"""
        with self._file_lock:
            if self._file_handle:
                try:
                    # Apenas fecha o handle - não tenta reescrever durante shutdown
                    self._file_handle.close()
                except:
                    pass
                finally:
                    self._file_handle = None

    def finalize_file(self):
        """Finaliza arquivo com tags HTML corretas - chame manualmente quando necessário"""
        with self._file_lock:
            try:
                # Fecha handle se aberto
                if self._file_handle:
                    self._file_handle.close()
                    self._file_handle = None

                # Só tenta finalizar se arquivo existe
                if not os.path.exists(self.filename):
                    return

                # Lê conteúdo atual
                content = ""
                try:
                    with open(self.filename, "r", encoding="utf-8") as f:
                        content = f.read()
                except:
                    return  # Se não conseguir ler, não faz nada

                # Remove marcador se existir
                content = content.replace(self._end_marker, "")

                # Adiciona fechamento HTML se necessário
                if not content.endswith('</html>'):
                    if not content.endswith('</font>'):
                        content += '</font>'
                    content += '\n  </div>\n</body>\n</html>\n'

                # Reescreve arquivo final
                try:
                    with open(self.filename, "w", encoding="utf-8") as f:
                        f.write(content)
                except:
                    pass  # Se não conseguir escrever, não trava

            except:
                pass  # Ignora todos os erros na finalização

    def __del__(self):
        """Cleanup simples - apenas fecha handle"""
        try:
            if hasattr(self, '_file_handle') and self._file_handle:
                self._file_handle.close()
        except:
            pass  # Ignora erros durante destruição
