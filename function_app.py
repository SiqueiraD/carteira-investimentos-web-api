import azure.functions as func
import logging
from app.main import app
from opencensus.ext.azure.log_exporter import AzureLogHandler

# Configuração do Application Insights
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler())

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """
    Função principal que recebe todas as requisições HTTP
    """
    return func.AsgiMiddleware(app).handle(req, context)
