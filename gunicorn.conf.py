import multiprocessing

# Configurações do servidor
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 600

# Configurações de log
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Configurações de reload e debug
reload = False
reload_engine = "auto"

# Configurações de segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
