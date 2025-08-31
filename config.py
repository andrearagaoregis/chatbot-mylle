"""
Configurações centralizadas do Chatbot Mylle Alves
"""
import os
from typing import Dict, List

class Config:
    # Configurações da aplicação
    APP_TITLE = "💋 Mylle Alves - Chat Exclusivo"
    APP_ICON = "💋"
    
    # URLs e Links
    INSTAGRAM_URL = "https://instagram.com/myllealves"
    ONLYFANS_URL = "https://onlyfans.com/myllealves"
    TELEGRAM_URL = "https://t.me/myllealves"
    WHATSAPP_URL = "https://wa.me/5511999999999"
    
    # Links de Checkout (substitua pelos seus links reais)
    CHECKOUT_TARADINHA = "https://pay.hotmart.com/taradinha"
    CHECKOUT_MOLHADINHA = "https://pay.hotmart.com/molhadinha"
    CHECKOUT_SAFADINHA = "https://pay.hotmart.com/safadinha"
    
    # Configurações de IA
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    MAX_REQUESTS_PER_SESSION = 50
    
    # Configurações de áudio
    AUDIO_FILES = {
        "welcome": "assets/audio/Oi meu amor tudo bem.mp3",
        "seductive": "assets/audio/seductive.mp3",
        "playful": "assets/audio/playful.mp3",
        "intimate": "assets/audio/intimate.mp3"
    }
    
    # Imagens do projeto
    IMAGES = {
        "profile": "https://images.pexels.com/photos/1239291/pexels-photo-1239291.jpeg",
        "preview1": "https://images.pexels.com/photos/1040881/pexels-photo-1040881.jpeg",
        "preview2": "https://images.pexels.com/photos/1043471/pexels-photo-1043471.jpeg",
        "preview3": "https://images.pexels.com/photos/1382731/pexels-photo-1382731.jpeg",
        "preview4": "https://images.pexels.com/photos/1758144/pexels-photo-1758144.jpeg",
        "preview5": "https://images.pexels.com/photos/1758146/pexels-photo-1758146.jpeg",
        "preview6": "https://images.pexels.com/photos/1758148/pexels-photo-1758148.jpeg"
    }
    
    # Preços dos packs
    PACK_PRICES = {
        "taradinha": {"original": 97, "promo": 47},
        "molhadinha": {"original": 197, "promo": 97},
        "safadinha": {"original": 297, "promo": 147}
    }
    
    # Configurações de timing
    RESPONSE_DELAYS = {
        "min": 1,
        "max": 4,
        "typing_speed": 0.05
    }
    
    # Configurações de banco de dados
    DATABASE_PATH = "database/chatbot.db"
    
    # Configurações de segurança
    RATE_LIMIT_MESSAGES = 100
    RATE_LIMIT_WINDOW = 3600  # 1 hora