"""
AI-Begleiter für die Solar-App
Schwebendes Fenster mit DeepSeek-Integration
"""

import streamlit as st
import requests
import json
from typing import Dict, List, Optional, Any
import time
from datetime import datetime

class DeepSeekCompanion:
    """AI-Begleiter mit DeepSeek-Integration"""
    
    def __init__(self):
        self.api_key = None
        self.api_base_url = "https://api.deepseek.com/v1"
        self.conversation_history = []
        self.is_visible = False
        
    def initialize_session_state(self):
        """Initialisiert Session State für den AI-Begleiter"""
        if 'ai_companion_visible' not in st.session_state:
            st.session_state.ai_companion_visible = False
        if 'ai_companion_history' not in st.session_state:
            st.session_state.ai_companion_history = []
        if 'ai_companion_api_key' not in st.session_state:
            st.session_state.ai_companion_api_key = ""
        if 'ai_companion_context' not in st.session_state:
            st.session_state.ai_companion_context = ""
            
    def set_api_key(self, api_key: str):
        """Setzt den DeepSeek API-Key"""
        self.api_key = api_key
        st.session_state.ai_companion_api_key = api_key
        
    def get_solar_context(self) -> str:
        """Erstellt Kontext über die aktuelle Solar-App Situation"""
        context = f"""
Du bist ein AI-Assistent für eine Solar-Angebotsapp. Die aktuelle Zeit ist {datetime.now().strftime('%d.%m.%Y %H:%M')}.

DEINE ROLLE:
- Hilf dem Nutzer bei Solar-/PV-Anlagen Fragen
- Unterstütze bei der Angebotserstellung
- Erkläre technische Begriffe einfach
- Gib praktische Tipps für Verkaufsgespräche

KONTEXT DER APP:
- Solar-Angebotsapp für PV-Anlagen
- Kann Multi-Firmen Angebote erstellen
- Unterstützt Kunden-Management (CRM)
- Berechnet Wirtschaftlichkeit und ROI
- Erstellt professionelle PDF-Angebote

ANTWORTE IMMER:
- Kurz und präzise (max. 3-4 Sätze)
- Hilfreich und praktisch
- Auf Deutsch
- Solar-/PV-fokussiert
"""
        return context
        
    def call_deepseek_api(self, message: str) -> Optional[str]:
        """Ruft die DeepSeek API auf"""
        if not self.api_key:
            return "❌ Bitte erst DeepSeek API-Key eingeben!"
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Conversation History mit Kontext aufbauen
            messages = [
                {"role": "system", "content": self.get_solar_context()}
            ]
            
            # Letzte 5 Nachrichten aus der History hinzufügen
            recent_history = st.session_state.ai_companion_history[-10:] if st.session_state.ai_companion_history else []
            for entry in recent_history:
                messages.append({"role": "user", "content": entry["user"]})
                messages.append({"role": "assistant", "content": entry["assistant"]})
                
            # Aktuelle Nachricht hinzufügen
            messages.append({"role": "user", "content": message})
            
            payload = {
                "model": "deepseek-chat", 
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7,
                "stream": False
            }
            
            response = requests.post(
                f"{self.api_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    ai_response = result['choices'][0]['message']['content']
                    
                    # Zur History hinzufügen
                    st.session_state.ai_companion_history.append({
                        "timestamp": datetime.now().strftime('%H:%M'),
                        "user": message,
                        "assistant": ai_response
                    })
                    
                    return ai_response
                else:
                    return "❌ Unerwartete API-Antwort"
            else:
                return f"❌ API-Fehler: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "⏱️ Timeout - DeepSeek antwortet nicht"
        except requests.exceptions.ConnectionError:
            return "🌐 Verbindungsfehler zu DeepSeek"
        except Exception as e:
            return f"❌ Fehler: {str(e)}"
            
    def render_floating_window(self):
        """Rendert das schwebende AI-Begleiter Fenster"""
        self.initialize_session_state()
        
        # Toggle Button für Sichtbarkeit
        col1, col2, col3 = st.columns([10, 1, 1])
        with col2:
            if st.button("🤖", help="AI-Begleiter ein/ausblenden", key="ai_toggle"):
                st.session_state.ai_companion_visible = not st.session_state.ai_companion_visible
                
        with col3:
            if st.session_state.ai_companion_visible:
                if st.button("❌", help="AI-Begleiter schließen", key="ai_close"):
                    st.session_state.ai_companion_visible = False
        
        # Schwebendes Fenster nur anzeigen wenn sichtbar
        if st.session_state.ai_companion_visible:
            self.render_companion_interface()
            
    def render_companion_interface(self):
        """Rendert die AI-Begleiter Benutzeroberfläche"""
        
        # Container für das schwebende Fenster
        with st.container():
            st.markdown("""
            <div style="
                position: fixed; 
                top: 100px; 
                right: 20px; 
                width: 350px; 
                max-height: 500px;
                background: white; 
                border: 2px solid #1B365D; 
                border-radius: 10px; 
                padding: 15px; 
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                z-index: 1000;
                overflow-y: auto;
            ">
            """, unsafe_allow_html=True)
            
            # Header
            st.markdown("### 🤖 Solar AI-Begleiter")
            st.markdown("*Powered by DeepSeek*")
            
            # API-Key Eingabe (falls nicht gesetzt)
            if not st.session_state.ai_companion_api_key:
                st.markdown("**🔑 DeepSeek API-Key eingeben:**")
                api_key_input = st.text_input(
                    "API-Key", 
                    type="password", 
                    placeholder="sk-...", 
                    key="api_key_input",
                    help="Ihren DeepSeek API-Key von https://platform.deepseek.com/"
                )
                if st.button("💾 Key speichern", key="save_api_key"):
                    if api_key_input:
                        self.set_api_key(api_key_input)
                        st.success("✅ API-Key gespeichert!")
                        st.rerun()
                    else:
                        st.error("❌ Bitte API-Key eingeben")
                        
                st.markdown("---")
                st.markdown("**💡 Beispiel-Fragen:**")
                st.markdown("• *Wie erkläre ich ROI bei PV-Anlagen?*")
                st.markdown("• *Was sind typische Einwände gegen Solar?*") 
                st.markdown("• *Speicher ja oder nein bei 8kWp?*")
                
            else:
                # Chat Interface
                self.render_chat_interface()
                
            st.markdown("</div>", unsafe_allow_html=True)
            
    def render_chat_interface(self):
        """Rendert das Chat-Interface"""
        
        # Chat History anzeigen
        if st.session_state.ai_companion_history:
            st.markdown("**💬 Gespräch:**")
            
            # Container für Chat-History mit begrenzter Höhe
            chat_container = st.container()
            with chat_container:
                # Nur die letzten 5 Nachrichten anzeigen
                recent_messages = st.session_state.ai_companion_history[-5:]
                
                for entry in recent_messages:
                    # User Message
                    st.markdown(f"""
                    <div style="background: #f0f0f0; padding: 8px; border-radius: 5px; margin: 5px 0;">
                        <strong>👤 Du ({entry['timestamp']}):</strong><br>
                        {entry['user']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # AI Response
                    st.markdown(f"""
                    <div style="background: #e8f4f8; padding: 8px; border-radius: 5px; margin: 5px 0;">
                        <strong>🤖 AI:</strong><br>
                        {entry['assistant']}
                    </div>
                    """, unsafe_allow_html=True)
                    
            # Clear History Button
            if st.button("🗑️ Verlauf löschen", key="clear_history"):
                st.session_state.ai_companion_history = []
                st.rerun()
                
        # Input für neue Nachricht
        st.markdown("---")
        
        # Quick Buttons für häufige Fragen
        st.markdown("**⚡ Quick-Fragen:**")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💰 ROI erklären", key="quick_roi"):
                self.process_message("Wie erkläre ich einem Kunden den ROI bei PV-Anlagen einfach?")
                
            if st.button("🔋 Speicher-Tipps", key="quick_storage"):
                self.process_message("Wann lohnt sich ein Batteriespeicher?")
                
        with col2:
            if st.button("🚫 Einwände", key="quick_objections"):                self.process_message("Was sind typische Kundeneinwände gegen Solar und wie antworte ich?")
                
            if st.button("📊 Angebotshilfe", key="quick_offer"):
                self.process_message("Tipps für ein überzeugendes PV-Angebot?")
                
        # Freie Nachrichteneingabe
        user_input = st.text_area(
            "Ihre Frage an den AI-Begleiter:", 
            placeholder="z.B. 'Wie berechne ich die optimale Anlagengröße?'",
            key="ai_user_input",
            height=80
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("📤 Senden", key="send_message"):
                if user_input.strip():
                    self.process_message(user_input)
                    st.rerun()
                else:
                    st.warning("⚠️ Bitte eine Frage eingeben")
        with col2:
            if st.button("⚙️ Settings", key="ai_settings"):
                # API-Key zurücksetzen
                if st.button("🔄 Key ändern", key="reset_api_key"):
                    st.session_state.ai_companion_api_key = ""
                    st.rerun()
                    
    def process_message(self, message: str):
        """Verarbeitet eine Nachricht"""
        with st.spinner("🤖 AI denkt nach..."):
            response = self.call_deepseek_api(message)
            
        if response:
            # Input wird beim nächsten Rerun automatisch geleert
            # Keine direkte Manipulation von st.session_state nötig
            pass
            
    def render_status_indicator(self):
        """Rendert Statusanzeige für den AI-Begleiter"""
        if st.session_state.get('ai_companion_api_key'):
            status = "🟢 AI Bereit"
        else:
            status = "🔴 API-Key fehlt"
            
        st.sidebar.markdown(f"**AI-Begleiter:** {status}")

# Global instance
ai_companion = DeepSeekCompanion()

def render_ai_companion():
    """Hauptfunktion zum Rendern des AI-Begleiters"""
    ai_companion.render_floating_window()
    
def render_ai_status():
    """Zeigt AI-Status in der Sidebar"""
    ai_companion.render_status_indicator()

def get_ai_companion_status() -> dict:
    """Gibt den Status des AI-Begleiters zurück"""
    return {
        "api_key_configured": bool(st.session_state.get('ai_companion_api_key')),
        "chat_history_count": len(st.session_state.get('ai_companion_history', [])),
        "window_visible": st.session_state.get('ai_companion_visible', False)
    }
