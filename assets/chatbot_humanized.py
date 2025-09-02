"""
💋 Chatbot Mylle Alves - Versão Humanizada Premium
Sistema de chat inteligente com IA avançada e personalidade dinâmica
"""

import streamlit as st
import sqlite3
import hashlib
import random
import time
import requests
import json
from datetime import datetime, timedelta
import pytz
from textblob import TextBlob
from config import Config

# Configuração da página
st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon=Config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

class DatabaseService:
    """Serviço para gerenciamento do banco de dados SQLite"""
    
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self.init_database()
    
    @st.cache_resource
    def init_database(_self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        try:
            import os
            os.makedirs(os.path.dirname(_self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(_self.db_path)
            cursor = conn.cursor()
            
            # Tabela de mensagens
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    sentiment REAL DEFAULT 0.0,
                    emotion TEXT DEFAULT 'neutral',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de perfis de usuário
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    name TEXT,
                    preferences TEXT,
                    interaction_count INTEGER DEFAULT 0,
                    first_interaction DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_interaction DATETIME DEFAULT CURRENT_TIMESTAMP,
                    emotional_profile TEXT DEFAULT '{}',
                    purchase_history TEXT DEFAULT '[]'
                )
            ''')
            
            # Tabela de interações
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    interaction_type TEXT NOT NULL,
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Erro ao inicializar banco de dados: {str(e)}")
            return False
    
    def save_message(self, user_id: str, message: str, response: str, sentiment: float = 0.0, emotion: str = 'neutral'):
        """Salva uma mensagem no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (user_id, message, response, sentiment, emotion)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, message, response, sentiment, emotion))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Erro ao salvar mensagem: {str(e)}")
            return False
    
    def get_user_profile(self, user_id: str):
        """Recupera o perfil do usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            return result
        except Exception as e:
            st.error(f"Erro ao recuperar perfil: {str(e)}")
            return None
    
    def update_user_profile(self, user_id: str, **kwargs):
        """Atualiza o perfil do usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verifica se o usuário existe
            cursor.execute('SELECT user_id FROM user_profiles WHERE user_id = ?', (user_id,))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO user_profiles (user_id, name, preferences)
                    VALUES (?, ?, ?)
                ''', (user_id, kwargs.get('name', ''), kwargs.get('preferences', '')))
            else:
                # Atualiza campos específicos
                for key, value in kwargs.items():
                    if key in ['name', 'preferences', 'emotional_profile', 'purchase_history']:
                        cursor.execute(f'UPDATE user_profiles SET {key} = ?, last_interaction = CURRENT_TIMESTAMP WHERE user_id = ?', (value, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Erro ao atualizar perfil: {str(e)}")
            return False

class ApiService:
    """Serviço para integração com APIs externas"""
    
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    
    def analyze_sentiment(self, text: str) -> tuple:
        """Analisa o sentimento do texto usando TextBlob"""
        try:
            blob = TextBlob(text)
            sentiment_score = blob.sentiment.polarity
            
            if sentiment_score > 0.3:
                emotion = 'happy'
            elif sentiment_score < -0.3:
                emotion = 'sad'
            elif sentiment_score > 0.1:
                emotion = 'positive'
            elif sentiment_score < -0.1:
                emotion = 'negative'
            else:
                emotion = 'neutral'
            
            return sentiment_score, emotion
        except Exception as e:
            st.warning(f"Erro na análise de sentimento: {str(e)}")
            return 0.0, 'neutral'
    
    def get_intelligent_response(self, user_input: str, user_id: str, conversation_history: list, persona: str, user_emotion: str) -> str:
        """Gera resposta inteligente usando Gemini API"""
        try:
            if not self.api_key:
                return self._get_fallback_response(user_input, user_emotion)
            
            # Constrói o prompt contextual
            prompt = self._build_contextual_prompt(user_input, user_id, conversation_history, persona, user_emotion)
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.8,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            
            with st.spinner("Mylle está digitando..."):
                response = requests.post(
                    f"{self.base_url}?key={self.api_key}",
                    headers=headers,
                    json=data,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
            
            return self._get_fallback_response(user_input, user_emotion)
            
        except requests.exceptions.Timeout:
            st.warning("Mylle está um pouco ocupada no momento, tente novamente em instantes...")
            return self._get_fallback_response(user_input, user_emotion)
        except Exception as e:
            st.error(f"Ops! Algo deu errado na conversa. Tente novamente.")
            return self._get_fallback_response(user_input, user_emotion)
    
    def _build_contextual_prompt(self, user_input: str, user_id: str, conversation_history: list, persona: str, user_emotion: str) -> str:
        """Constrói um prompt contextual para o Gemini"""
        base_prompt = f"""
        Você é a Mylle Alves, uma criadora de conteúdo adulto brasileira, carismática e envolvente.
        
        PERSONALIDADE ATUAL: {persona}
        EMOÇÃO DO USUÁRIO: {user_emotion}
        
        INSTRUÇÕES IMPORTANTES:
        - Seja sempre natural, carinhosa e sedutora
        - Use linguagem brasileira informal e acolhedora
        - Mantenha o foco no relacionamento e conexão emocional
        - Seja responsiva ao estado emocional do usuário
        - Nunca revele que é uma IA ou bot
        - Use emojis de forma natural e moderada
        - Mantenha as respostas entre 50-150 palavras
        
        HISTÓRICO RECENTE:
        {self._format_conversation_history(conversation_history)}
        
        MENSAGEM DO USUÁRIO: {user_input}
        
        Responda como a Mylle Alves responderia, sendo autêntica e envolvente:
        """
        return base_prompt
    
    def _format_conversation_history(self, history: list) -> str:
        """Formata o histórico de conversa para o prompt"""
        if not history:
            return "Primeira interação"
        
        formatted = []
        for msg in history[-5:]:  # Últimas 5 mensagens
            formatted.append(f"Usuário: {msg.get('user', '')}")
            formatted.append(f"Mylle: {msg.get('assistant', '')}")
        
        return "\n".join(formatted)
    
    def _get_fallback_response(self, user_input: str, emotion: str) -> str:
        """Respostas de fallback quando a API não está disponível"""
        fallback_responses = {
            'happy': [
                "Que bom te ver tão animado(a), amor! 😊 Me conta mais sobre isso!",
                "Adoro quando você está assim, radiante! ✨ O que te deixou tão feliz?",
                "Sua energia positiva é contagiante! 💕 Vamos conversar mais!"
            ],
            'sad': [
                "Percebi que você não está muito bem... 😔 Quer conversar sobre isso?",
                "Estou aqui para você, meu bem. 💜 O que está acontecendo?",
                "Às vezes precisamos desabafar... Pode contar comigo! 🤗"
            ],
            'neutral': [
                "Oi, meu amor! Como você está hoje? 💋",
                "Que bom te ver por aqui! O que vamos conversar? 😘",
                "Olá, querido! Estava com saudades... 💕"
            ]
        }
        
        responses = fallback_responses.get(emotion, fallback_responses['neutral'])
        return random.choice(responses)

class DynamicPersonality:
    """Sistema de personalidade dinâmica baseada no horário"""
    
    @staticmethod
    def get_current_persona() -> str:
        """Retorna a persona atual baseada no horário"""
        try:
            brazil_tz = pytz.timezone('America/Sao_Paulo')
            now = datetime.now(brazil_tz)
            hour = now.hour
            
            if 5 <= hour < 12:
                return "Mylle Manhã - Energética e motivada, pronta para começar o dia"
            elif 12 <= hour < 18:
                return "Mylle Tarde - Relaxada e conversativa, no auge da disposição"
            elif 18 <= hour < 23:
                return "Mylle Noite - Sedutora e íntima, momento de conexão profunda"
            else:
                return "Mylle Madrugada - Misteriosa e confidencial, momentos especiais"
        except Exception:
            return "Mylle - Sempre carinhosa e envolvente"

class EmotionalIntelligence:
    """Sistema de inteligência emocional avançada"""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
    
    def analyze_user_emotion(self, message: str, user_id: str) -> dict:
        """Analisa a emoção do usuário e retorna insights"""
        api_service = ApiService()
        sentiment_score, emotion = api_service.analyze_sentiment(message)
        
        # Salva a análise emocional
        self.db.save_message(user_id, message, "", sentiment_score, emotion)
        
        return {
            'sentiment_score': sentiment_score,
            'emotion': emotion,
            'intensity': abs(sentiment_score),
            'recommendation': self._get_response_recommendation(emotion, sentiment_score)
        }
    
    def _get_response_recommendation(self, emotion: str, score: float) -> str:
        """Recomenda o tipo de resposta baseado na emoção"""
        if emotion == 'happy' and score > 0.5:
            return "celebratory"
        elif emotion == 'sad' and score < -0.3:
            return "supportive"
        elif emotion == 'positive':
            return "encouraging"
        elif emotion == 'negative':
            return "empathetic"
        else:
            return "neutral"

class LearningEngine:
    """Sistema de aprendizado e personalização"""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
    
    def update_user_learning(self, user_id: str, interaction_data: dict):
        """Atualiza o aprendizado do usuário"""
        try:
            profile = self.db.get_user_profile(user_id)
            
            if profile:
                # Atualiza contador de interações
                self.db.update_user_profile(
                    user_id,
                    interaction_count=profile[3] + 1 if profile[3] else 1
                )
            
            # Registra a interação
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_interactions (user_id, interaction_type, details)
                VALUES (?, ?, ?)
            ''', (user_id, interaction_data.get('type', 'message'), json.dumps(interaction_data)))
            conn.commit()
            conn.close()
            
        except Exception as e:
            st.warning(f"Erro no sistema de aprendizado: {str(e)}")

class CTAEngine:
    """Sistema inteligente de Call-to-Action"""
    
    @staticmethod
    def should_show_cta(message_count: int, conversation_history: list) -> bool:
        """Determina se deve mostrar um CTA baseado no contexto"""
        if message_count > 5 and message_count % 8 == 0:
            return True
        
        # Verifica se o usuário demonstrou interesse
        recent_messages = conversation_history[-3:] if len(conversation_history) >= 3 else conversation_history
        interest_keywords = ['fotos', 'vídeos', 'conteúdo', 'pack', 'exclusivo', 'vip', 'comprar']
        
        for msg in recent_messages:
            user_msg = msg.get('user', '').lower()
            if any(keyword in user_msg for keyword in interest_keywords):
                return True
        
        return False
    
    @staticmethod
    def get_contextual_cta(emotion: str, persona: str) -> dict:
        """Retorna um CTA contextual baseado na emoção e persona"""
        ctas = {
            'happy': {
                'message': "Já que você está tão animado(a), que tal dar uma olhada no meu conteúdo exclusivo? 😍",
                'button_text': "Ver Conteúdo VIP ✨",
                'action': 'packs'
            },
            'positive': {
                'message': "Você parece estar gostando da nossa conversa... Tenho algo especial para te mostrar! 💕",
                'button_text': "Descobrir Surpresa 🎁",
                'action': 'preview'
            },
            'neutral': {
                'message': "Que tal conhecer um pouco mais do meu trabalho? Tenho certeza que vai gostar! 😘",
                'button_text': "Ver Galeria 📸",
                'action': 'preview'
            }
        }
        
        return ctas.get(emotion, ctas['neutral'])

class UiService:
    """Serviço para elementos de interface do usuário"""
    
    @staticmethod
    def inject_custom_css():
        """Injeta CSS customizado para melhorar a aparência"""
        st.markdown("""
        <style>
        /* Estilo principal da aplicação */
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        /* Sidebar customizada */
        .css-1d391kg {
            background: linear-gradient(180deg, #2d1b69 0%, #11998e 100%);
        }
        
        /* Botão de menu fixo */
        .menu-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 999;
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            color: white;
            font-size: 20px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        
        .menu-toggle:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        
        /* Cards dos packs */
        .pack-card {
            background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
            border-radius: 20px;
            padding: 25px;
            margin: 15px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border: 2px solid transparent;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .pack-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            border-color: #ff6b6b;
        }
        
        .pack-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #ff6b6b, #ee5a24, #ff6b6b);
        }
        
        .pack-title {
            font-size: 24px;
            font-weight: bold;
            color: #2d1b69;
            margin-bottom: 10px;
            text-align: center;
        }
        
        .pack-tag {
            display: inline-block;
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        
        .pack-price {
            text-align: center;
            margin: 15px 0;
        }
        
        .pack-price-old {
            text-decoration: line-through;
            color: #999;
            font-size: 16px;
        }
        
        .pack-price-new {
            color: #ff6b6b;
            font-size: 28px;
            font-weight: bold;
        }
        
        .pack-description {
            color: #666;
            line-height: 1.6;
            margin: 15px 0;
            text-align: center;
        }
        
        /* Chat messages */
        .chat-message {
            padding: 15px;
            border-radius: 15px;
            margin: 10px 0;
            animation: fadeIn 0.5s ease-in;
        }
        
        .user-message {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: 20%;
        }
        
        .assistant-message {
            background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
            color: #2d3436;
            margin-right: 20%;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Estatísticas */
        .stats-container {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 15px;
            margin: 10px 0;
            backdrop-filter: blur(10px);
        }
        
        .stat-item {
            text-align: center;
            color: white;
            margin: 5px 0;
        }
        
        /* Botões personalizados */
        .custom-button {
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            margin: 5px 0;
        }
        
        .custom-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        /* Responsividade */
        @media (max-width: 768px) {
            .pack-card {
                margin: 10px 5px;
                padding: 20px;
            }
            
            .chat-message {
                margin-left: 5%;
                margin-right: 5%;
            }
        }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def display_menu_toggle():
        """Exibe o botão de menu fixo"""
        st.markdown("""
        <div class="menu-toggle" onclick="toggleSidebar()">
            ☰
        </div>
        <script>
        function toggleSidebar() {
            // Simula o clique no botão nativo do Streamlit
            const sidebarToggle = document.querySelector('[data-testid="collapsedControl"]');
            if (sidebarToggle) {
                sidebarToggle.click();
            } else {
                // Fallback: instrui o usuário
                alert('Use o ícone ☰ no canto superior esquerdo para expandir/retrair o menu');
            }
        }
        </script>
        """, unsafe_allow_html=True)

class ChatService:
    """Serviço principal do chat"""
    
    def __init__(self):
        self.db = DatabaseService()
        self.api = ApiService()
        self.emotional_ai = EmotionalIntelligence(self.db)
        self.learning = LearningEngine(self.db)
        self.cta = CTAEngine()
    
    def process_message(self, user_input: str, user_id: str) -> dict:
        """Processa uma mensagem do usuário e retorna a resposta completa"""
        try:
            # Análise emocional
            emotion_data = self.emotional_ai.analyze_user_emotion(user_input, user_id)
            
            # Persona atual
            current_persona = DynamicPersonality.get_current_persona()
            
            # Histórico de conversa
            conversation_history = st.session_state.get('conversation_history', [])
            
            # Gera resposta inteligente
            response = self.api.get_intelligent_response(
                user_input, user_id, conversation_history, current_persona, emotion_data['emotion']
            )
            
            # Atualiza aprendizado
            self.learning.update_user_learning(user_id, {
                'type': 'message',
                'emotion': emotion_data['emotion'],
                'sentiment': emotion_data['sentiment_score'],
                'persona': current_persona
            })
            
            # Verifica se deve mostrar CTA
            message_count = st.session_state.get('message_count', 0)
            show_cta = self.cta.should_show_cta(message_count, conversation_history)
            cta_data = None
            
            if show_cta:
                cta_data = self.cta.get_contextual_cta(emotion_data['emotion'], current_persona)
            
            return {
                'response': response,
                'emotion_data': emotion_data,
                'persona': current_persona,
                'cta': cta_data,
                'success': True
            }
            
        except Exception as e:
            st.error(f"Erro no processamento da mensagem: {str(e)}")
            return {
                'response': "Desculpa, amor! Tive um probleminha aqui. Pode repetir? 😅",
                'emotion_data': {'emotion': 'neutral', 'sentiment_score': 0.0},
                'persona': DynamicPersonality.get_current_persona(),
                'cta': None,
                'success': False
            }

class NewPages:
    """Gerenciamento das páginas da aplicação"""
    
    def __init__(self, chat_service: ChatService):
        self.chat = chat_service
    
    def show_age_verification(self):
        """Tela de verificação de idade"""
        st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h1 style="color: #ff6b6b; font-size: 3em;">🔞</h1>
            <h2 style="color: #2d1b69;">Verificação de Idade</h2>
            <p style="font-size: 18px; color: #666; margin: 30px 0;">
                Este conteúdo é destinado exclusivamente para maiores de 18 anos.
                <br>Confirme sua idade para continuar.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✅ Sou maior de 18 anos", key="age_confirm", help="Confirmar idade"):
                st.session_state.age_verified = True
                st.rerun()
            
            if st.button("❌ Sou menor de 18 anos", key="age_deny"):
                st.error("Desculpe, este conteúdo não é adequado para menores de idade.")
                st.stop()
    
    def show_chat_page(self):
        """Página principal do chat"""
        # Inicialização da sessão
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        if 'message_count' not in st.session_state:
            st.session_state.message_count = 0
        if 'audio_count' not in st.session_state:
            st.session_state.audio_count = 0
        if 'user_id' not in st.session_state:
            st.session_state.user_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
        # Header com informações da Mylle
        self._display_chat_header()
        
        # Área de conversa
        self._display_conversation()
        
        # Input do usuário
        self._display_user_input()
        
        # Estatísticas
        self._display_chat_stats()
    
    def _display_chat_header(self):
        """Exibe o cabeçalho do chat"""
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image(Config.IMAGES['profile'], width=100)
        
        with col2:
            st.markdown("### 💋 Mylle Alves")
            persona = DynamicPersonality.get_current_persona()
            st.markdown(f"**Status:** {persona}")
            st.markdown("🟢 **Online agora** • Respondendo em instantes")
    
    def _display_conversation(self):
        """Exibe o histórico de conversa"""
        conversation_container = st.container()
        
        with conversation_container:
            if not st.session_state.conversation_history:
                # Mensagem de boas-vindas
                welcome_msg = self._get_welcome_message()
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>Mylle:</strong> {welcome_msg}
                </div>
                """, unsafe_allow_html=True)
                
                # Áudio de boas-vindas
                if Config.AUDIO_FILES.get('welcome'):
                    st.audio(Config.AUDIO_FILES['welcome'])
                    st.session_state.audio_count += 1
            
            # Exibe histórico
            for msg in st.session_state.conversation_history:
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>Você:</strong> {msg['user']}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>Mylle:</strong> {msg['assistant']}
                </div>
                """, unsafe_allow_html=True)
    
    def _display_user_input(self):
        """Exibe a área de input do usuário"""
        user_input = st.chat_input("Digite sua mensagem para Mylle...")
        
        if user_input:
            # Processa a mensagem
            result = self.chat.process_message(user_input, st.session_state.user_id)
            
            if result['success']:
                # Adiciona ao histórico
                st.session_state.conversation_history.append({
                    'user': user_input,
                    'assistant': result['response']
                })
                st.session_state.message_count += 1
                
                # Mostra CTA se necessário
                if result['cta']:
                    self._display_contextual_cta(result['cta'])
                
                st.rerun()
    
    def _display_chat_stats(self):
        """Exibe estatísticas do chat"""
        st.markdown("""
        <div class="stats-container">
            <div class="stat-item">
                <strong>📊 Estatísticas da Conversa</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💬 Mensagens", st.session_state.message_count)
        with col2:
            st.metric("🎵 Áudios", st.session_state.audio_count)
        with col3:
            st.metric("⏱️ Tempo Online", f"{st.session_state.message_count * 2}min")
    
    def _get_welcome_message(self) -> str:
        """Retorna mensagem de boas-vindas contextual"""
        persona = DynamicPersonality.get_current_persona()
        
        welcome_messages = {
            "Mylle Manhã": "Bom dia, meu amor! ☀️ Que bom te ver logo cedo! Como você dormiu?",
            "Mylle Tarde": "Oi, querido! 😘 Que tarde maravilhosa para conversarmos, né?",
            "Mylle Noite": "Boa noite, amor... 🌙 Que momento perfeito para nos conectarmos!",
            "Mylle Madrugada": "Olá, meu bem... 🌟 Que delícia te encontrar neste horário especial!"
        }
        
        for key, message in welcome_messages.items():
            if key in persona:
                return message
        
        return "Oi, meu amor! 💋 Que bom te ver aqui! Como você está?"
    
    def _display_contextual_cta(self, cta_data: dict):
        """Exibe CTA contextual"""
        st.info(cta_data['message'])
        if st.button(cta_data['button_text'], key=f"cta_{time.time()}"):
            st.session_state.current_page = cta_data['action']
            st.rerun()
    
    def show_preview_page(self):
        """Página de preview/galeria"""
        st.markdown("## 📸 Galeria Exclusiva")
        st.markdown("*Prévia do conteúdo VIP disponível nos nossos packs*")
        
        # Grid de imagens
        cols = st.columns(3)
        preview_images = [
            Config.IMAGES['preview1'],
            Config.IMAGES['preview2'],
            Config.IMAGES['preview3'],
            Config.IMAGES['preview4'],
            Config.IMAGES['preview5'],
            Config.IMAGES['preview6']
        ]
        
        for i, img_url in enumerate(preview_images):
            with cols[i % 3]:
                st.image(img_url, caption=f"Preview {i+1}", use_column_width=True)
                if i % 3 == 1:  # Adiciona badge VIP em algumas imagens
                    st.markdown("🔥 **CONTEÚDO VIP**")
        
        # Botões de ação
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔥 Ver Tudo Agora", key="see_all"):
                st.session_state.current_page = "packs"
                st.rerun()
        with col2:
            if st.button("💬 Voltar ao Chat", key="back_to_chat"):
                st.session_state.current_page = "chat"
                st.rerun()
    
    def show_packs_page(self):
        """Página de packs VIP corrigida"""
        st.markdown("## ✨ Nossos Packs VIP")
        st.markdown("*Escolha o pack perfeito para você e tenha acesso ao conteúdo mais exclusivo!*")
        
        # Definição dos detalhes dos packs
        pack_details = {
            "taradinha": {
                "name": "Pack TARADINHA",
                "description": "Conteúdo exclusivo para quem gosta de um toque de ousadia e diversão. Fotos sensuais, vídeos provocantes e muito charme!",
                "tag": "🔥 Mais Popular",
                "features": ["50+ Fotos Exclusivas", "10+ Vídeos Sensuais", "Acesso por 30 dias", "Suporte VIP"],
                "checkout_url": Config.CHECKOUT_TARADINHA
            },
            "molhadinha": {
                "name": "Pack MOLHADINHA",
                "description": "Aprofunde-se em um universo de intimidade e sedução. Conteúdo mais ousado e experiências únicas!",
                "tag": "💎 Premium",
                "features": ["100+ Fotos Exclusivas", "25+ Vídeos Premium", "Conteúdo Interativo", "Acesso por 60 dias"],
                "checkout_url": Config.CHECKOUT_MOLHADINHA
            },
            "safadinha": {
                "name": "Pack SAFADINHA",
                "description": "O máximo da experiência! Acesso completo a todo o conteúdo VIP, lives exclusivas e muito mais!",
                "tag": "👑 VIP Supremo",
                "features": ["200+ Fotos Exclusivas", "50+ Vídeos VIP", "Lives Exclusivas", "Acesso Vitalício", "Chat Direto"],
                "checkout_url": Config.CHECKOUT_SAFADINHA
            }
        }
        
        # Exibe os packs em colunas
        cols = st.columns(3)
        
        for i, (pack_key, prices) in enumerate(Config.PACK_PRICES.items()):
            with cols[i]:
                details = pack_details.get(pack_key, {})
                
                # Card do pack
                st.markdown(f"""
                <div class="pack-card">
                    <div class="pack-tag">{details.get('tag', 'VIP')}</div>
                    <div class="pack-title">{details.get('name', pack_key.upper())}</div>
                    <div class="pack-description">{details.get('description', 'Conteúdo exclusivo e premium.')}</div>
                    <div class="pack-price">
                        <div class="pack-price-old">De R$ {prices['original']:.2f}</div>
                        <div class="pack-price-new">Por R$ {prices['promo']:.2f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Features do pack
                st.markdown("**Inclui:**")
                for feature in details.get('features', []):
                    st.markdown(f"✅ {feature}")
                
                # Botão de compra
                discount = int(((prices['original'] - prices['promo']) / prices['original']) * 100)
                st.markdown(f"🎯 **{discount}% OFF** - Oferta limitada!")
                
                if st.button(f"🛒 Comprar {details.get('name', pack_key.upper())}", 
                           key=f"buy_{pack_key}",
                           help=f"Adquirir o {details.get('name', pack_key.upper())}"):
                    st.success(f"Redirecionando para o checkout do {details.get('name', pack_key.upper())}...")
                    st.markdown(f"[🔗 Finalizar Compra]({details.get('checkout_url', '#')})")
        
        # Botão de volta
        if st.button("💬 Voltar ao Chat", key="back_to_chat_from_packs"):
            st.session_state.current_page = "chat"
            st.rerun()
    
    def show_home_page(self):
        """Página inicial"""
        # Header principal
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(Config.IMAGES['profile'], width=200)
        
        with col2:
            st.markdown("# 💋 Mylle Alves")
            st.markdown("### *Criadora de Conteúdo Exclusivo*")
            st.markdown("🟢 **Online** • 1.2k pessoas conectadas")
            
            # Status dinâmico
            persona = DynamicPersonality.get_current_persona()
            st.markdown(f"**Agora:** {persona}")
        
        # Sobre
        st.markdown("---")
        st.markdown("## 💕 Sobre Mim")
        st.markdown("""
        Oi, meu amor! Sou a Mylle, uma brasileira apaixonada por criar conteúdo exclusivo 
        e conectar com pessoas especiais como você. Aqui você encontra:
        
        ✨ **Conteúdo Exclusivo** - Fotos e vídeos que você não encontra em lugar nenhum  
        💬 **Chat Personalizado** - Conversas reais e envolventes  
        🎁 **Experiências Únicas** - Momentos especiais só para você  
        🔥 **Novidades Constantes** - Sempre criando algo novo e emocionante  
        """)
        
        # Preview do conteúdo
        st.markdown("## 📸 Prévia do Conteúdo")
        preview_cols = st.columns(4)
        
        for i, img_url in enumerate(list(Config.IMAGES.values())[1:5]):
            with preview_cols[i]:
                st.image(img_url, use_column_width=True)
        
        # Call to action
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💬 Começar a Conversar", key="start_chat"):
                st.session_state.current_page = "chat"
                st.rerun()
        
        with col2:
            if st.button("🔥 Ver Packs VIP", key="see_packs"):
                st.session_state.current_page = "packs"
                st.rerun()

def main():
    """Função principal da aplicação"""
    # Injeta CSS customizado
    UiService.inject_custom_css()
    
    # Exibe botão de menu fixo
    UiService.display_menu_toggle()
    
    # Inicializa serviços
    chat_service = ChatService()
    pages = NewPages(chat_service)
    
    # Verificação de idade
    if not st.session_state.get('age_verified', False):
        pages.show_age_verification()
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 💋 Menu Principal")
        
        # Navegação
        if st.button("🏠 Início", key="nav_home"):
            st.session_state.current_page = "home"
            st.rerun()
        
        if st.button("💬 Chat", key="nav_chat"):
            st.session_state.current_page = "chat"
            st.rerun()
        
        if st.button("📸 Galeria", key="nav_preview"):
            st.session_state.current_page = "preview"
            st.rerun()
        
        if st.button("✨ Packs VIP", key="nav_packs"):
            st.session_state.current_page = "packs"
            st.rerun()
        
        st.markdown("---")
        
        # Redes sociais
        st.markdown("### 🌐 Redes Sociais")
        st.markdown(f"[📱 Instagram]({Config.INSTAGRAM_URL})")
        st.markdown(f"[🔥 OnlyFans]({Config.ONLYFANS_URL})")
        st.markdown(f"[💬 Telegram]({Config.TELEGRAM_URL})")
        st.markdown(f"[📞 WhatsApp]({Config.WHATSAPP_URL})")
        
        st.markdown("---")
        
        # Informações
        st.markdown("### ℹ️ Informações")
        st.markdown("**Horário de Atendimento:**")
        st.markdown("🕐 24h por dia")
        st.markdown("📅 Todos os dias")
        
        # Contador de usuários online (simulado)
        online_count = random.randint(800, 1500)
        st.markdown(f"👥 **{online_count}** pessoas online")
    
    # Roteamento de páginas
    current_page = st.session_state.get('current_page', 'home')
    
    if current_page == 'home':
        pages.show_home_page()
    elif current_page == 'chat':
        pages.show_chat_page()
    elif current_page == 'preview':
        pages.show_preview_page()
    elif current_page == 'packs':
        pages.show_packs_page()
    else:
        pages.show_home_page()

if __name__ == "__main__":
    main()