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
    
    # Configurações de personas
    PERSONAS = {
        "manha": {
            "name": "Mylle Manhã",
            "description": "Energética e motivada, pronta para começar o dia",
            "greeting": "Bom dia, meu amor! ☀️",
            "style": "energetic"
        },
        "tarde": {
            "name": "Mylle Tarde", 
            "description": "Relaxada e conversativa, no auge da disposição",
            "greeting": "Oi, querido! 😘",
            "style": "conversational"
        },
        "noite": {
            "name": "Mylle Noite",
            "description": "Sedutora e íntima, momento de conexão profunda", 
            "greeting": "Boa noite, amor... 🌙",
            "style": "seductive"
        },
        "madrugada": {
            "name": "Mylle Madrugada",
            "description": "Misteriosa e confidencial, momentos especiais",
            "greeting": "Olá, meu bem... 🌟", 
            "style": "intimate"
        }
    }
    
    # Detalhes dos packs para exibição
    PACK_DETAILS = {
        "taradinha": {
            "name": "Pack TARADINHA",
            "description": "Conteúdo exclusivo para quem gosta de um toque de ousadia e diversão. Fotos sensuais, vídeos provocantes e muito charme!",
            "tag": "🔥 Mais Popular",
            "features": ["50+ Fotos Exclusivas", "10+ Vídeos Sensuais", "Acesso por 30 dias", "Suporte VIP"],
            "color": "#ff6b6b"
        },
        "molhadinha": {
            "name": "Pack MOLHADINHA", 
            "description": "Aprofunde-se em um universo de intimidade e sedução. Conteúdo mais ousado e experiências únicas!",
            "tag": "💎 Premium",
            "features": ["100+ Fotos Exclusivas", "25+ Vídeos Premium", "Conteúdo Interativo", "Acesso por 60 dias"],
            "color": "#74b9ff"
        },
        "safadinha": {
            "name": "Pack SAFADINHA",
            "description": "O máximo da experiência! Acesso completo a todo o conteúdo VIP, lives exclusivas e muito mais!",
            "tag": "👑 VIP Supremo", 
            "features": ["200+ Fotos Exclusivas", "50+ Vídeos VIP", "Lives Exclusivas", "Acesso Vitalício", "Chat Direto"],
            "color": "#fd79a8"
        }
    }