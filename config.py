from imports import *



class Config:
    """Configuration globale de l'application"""
    MISTRAL_API_KEY = "JbFjF3nMaTJcqcmTomUvcjfh4xbUw4el"  # À remplir au démarrage de l'application
    PIXTRAL_MODEL = "pixtral-12b-2409"
    UPLOAD_FOLDERS = {
        "images": "data/images/",
        "json_results": "data/json_results/",
        "bank_statements": "data/bank_statements/"
    }
    DATE_FORMATS = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y", "%m/%d/%Y"]