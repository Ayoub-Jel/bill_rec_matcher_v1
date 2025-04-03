import os
from pathlib import Path
import re
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta

from config import Config



class Utils:
    """Classe utilitaire avec des méthodes statiques"""
    
    @staticmethod
    def create_folders():
        """Création des dossiers nécessaires à l'application"""
        for folder in Config.UPLOAD_FOLDERS.values():
            Path(folder).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Nettoie un nom de fichier pour éviter les problèmes"""
        return re.sub(r'[\\/*?:"<>|]', "", filename)
    
    @staticmethod
    def extract_amount_from_string(text: str) -> float:
        """Extrait un montant d'une chaîne de caractères"""
        if not text:
            return None
        
        # Cherche des motifs qui ressemblent à des montants (avec ou sans devise)
        amount_patterns = [
            r'(\d+[,.]\d{2})\s*€',  # Format: 123,45 € ou 123.45 €
            r'€\s*(\d+[,.]\d{2})',  # Format: € 123,45 ou € 123.45
            r'(\d+[,.]\d{2})\s*EUR',  # Format: 123,45 EUR
            r'(\d+[,.]\d{2})',  # Format simple: 123,45 ou 123.45
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Prendre le premier montant trouvé
                amount_str = matches[0]
                # Normaliser la chaîne (remplacer la virgule par un point)
                amount_str = amount_str.replace(',', '.')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None
    
    @staticmethod
    def parse_date(date_string: str) -> Optional[datetime]:
        """Essaie de parser une date dans différents formats"""
        if not date_string:
            return None
            
        for date_format in Config.DATE_FORMATS:
            try:
                return datetime.strptime(date_string.strip(), date_format)
            except ValueError:
                continue
                
        # Essai d'extraction de date à partir de texte plus complexe
        date_patterns = [
            r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})', # Format: DD/MM/YYYY ou variations
            r'(\d{4})[/\-\.](\d{1,2})[/\-\.](\d{1,2})'   # Format: YYYY/MM/DD ou variations
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_string)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    try:
                        if len(groups[2]) == 4:  # YYYY est en dernier
                            date_str = f"{groups[0].zfill(2)}/{groups[1].zfill(2)}/{groups[2]}"
                            return datetime.strptime(date_str, "%d/%m/%Y")
                        elif len(groups[0]) == 4:  # YYYY est en premier
                            date_str = f"{groups[0]}/{groups[1].zfill(2)}/{groups[2].zfill(2)}"
                            return datetime.strptime(date_str, "%Y/%m/%d")
                    except ValueError:
                        continue
        
        return None