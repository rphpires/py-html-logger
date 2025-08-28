# config.py - Configurações otimizadas para tempo real

max_files = 15
max_size = 5_000_000    # 5 MB
main_filename = "log.html"
log_dir = "logs"

# Configurações otimizadas para tempo real com inserção correta
buffer_size = 5         # Buffer muito pequeno - 5 linhas para tempo real
flush_interval = 0.2    # Flush rápido - 200ms para tempo real
batch_processing = True  # Habilita processamento em lote pequeno

# Configurações para inserção no HTML
use_html_insertion = True   # Insere no local correto do HTML
preserve_javascript = True  # Mantém funcionalidade JavaScript completa
