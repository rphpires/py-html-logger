# HTML Logger

Uma biblioteca Python para geração de logs em HTML com suporte a cores, rotação de arquivos e filtros via JavaScript.

## Características

- ✅ Logs coloridos em formato HTML
- ✅ Rotaão automática de arquivos
- ✅ Interface limpa com filtros JavaScript integrados
- ✅ Thread-safe e de alta performance
- ✅ Suporte a exceções com traceback completo
- ✅ Configuração flexível de tamanho e quantidade de arquivos

## Instalação

```bash
pip install py-html-logger
```

## Uso Básico

```python
from htmllogger import log, error, report_exception

# Mensagens simples
log("Mensagem informativa normal")
log("Mensagem em azul", color="blue")

# Mensagens de erro
error("Esta é uma mensagem de erro")

# Registrar exceções
try:
    # Seu código aqui
    raise ValueError("Erro exemplo")
except Exception as e:
    report_exception(e)
```

## Configuração

```python
from htmllogger import config

# Personalize as configurações do logger
config(
    max_files=15,           # Número máximo de arquivos de log
    max_size=5000000,       # Tamanho máximo por arquivo (5MB)
    main_filename="log.html", # Nome do arquivo principal
    log_dir="logs"          # Diretório para os logs
)
```

## Estrutura de Arquivos

Os logs são armazenados no diretório especificado (padrão: `logs/`) com a seguinte estrutura:

```
logs/
└── log.html (arquivo atual)
└── 2023-10-05_12-30-45_log.html (arquivo rotacionado)
└── 2023-10-05_10-15-32_log.html (arquivo rotacionado)
```

## Filtros JavaScript Integrados

Os arquivos HTML gerados incluem recursos de filtro para facilitar a análise:

- Filtro por texto
- Filtro por nível (cor)
- Filtro por período

## Exemplo Completo

```python
from htmllogger import log, error, report_exception, config

# Configurar o logger
config(
    max_files=10,
    max_size=2000000,  # 2MB
    log_dir="my_logs"
)

# Registrar diferentes tipos de mensagens
log("Iniciando aplicação", color="green")
log("Processando dados...", color="blue")

for i in range(100):
    log(f"Processando item {i}")

try:
    # Código que pode gerar erro
    resultado = 10 / 0
except Exception as e:
    error("Divisão por zero detectada")
    report_exception(e)

log("Aplicação finalizada", color="green")
```

## API Reference

### log(message, color="white")
Registra uma mensagem com a cor especificada.

### error(message)
Registra uma mensagem de erro (em vermelho).

### report_exception(exc, timeout=None)
Registra uma exceção com seu traceback completo.

### config(**kwargs)
Configura as opções do logger:
- `max_files`: Número máximo de arquivos a manter
- `max_size`: Tamanho máximo em bytes por arquivo
- `main_filename`: Nome do arquivo de log principal
- `log_dir`: Diretório onde os logs serão armazenados

## Desenvolvimento

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Suporte

Se você encontrar problemas ou tiver dúvidas:

1. Consulte a [documentação](https://github.com/rphpires/py-html-logger)
2. Abra uma [issue](https://github.com/rphpires/py-html-logger/issues)
3. Entre em contato: rphspires@gmail.com

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Agradecimentos

- Desenvolvido por Raphael Pires
- Inspirado pela necessidade de logs visualmente ricos para debugging
- Contribuições são bem-vindas!