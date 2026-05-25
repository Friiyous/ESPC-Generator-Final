"""
Chatbot Intelligence Module
"""

import streamlit as st
import os
import json
from datetime import datetime
from groq import Groq


class ChatbotAssistant:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
        api_key = os.environ.get("GROQ_API_KEY", "")
        if api_key:
            self.client = Groq(api_key=api_key)
        else:
            self.client = None
        self.chat_history = []

    def get_system_prompt(self):
        """Get the system prompt for the chatbot"""
        return """
Tu es un assistant intelligent pour le responsable de centre de santé en Côte d'Ivoire.

RÈGLES:
1. Sois concis et utile
2. Réponds en français professionnel
3. Fais des suggestions pratiques basées sur le contexte
4. Ne donne pas de conseils médicaux, seulement administratifs
5. Utilise les données du centre si disponibles

DOMAINES:
- Gestion du personnel
- Organisation des réunions
- Rapports et documents
- Planification des activités
- Gestion des stocks
- Communication avec le district
- Formation du personnel
- Évaluations qualité

FORMAT:
- Réponse courte et directe
- Si nécessaire, propose des actions
- Ne te répète pas
        """

    def get_chat_response(self, user_message, context=None):
        """Get response from Groq chatbot"""
        try:
            # Build conversation history
            messages = [{"role": "system", "content": self.get_system_prompt()}]

            # Add context if available
            if context:
                messages.append(
                    {"role": "system", "content": f"Contexte du centre: {context}"}
                )

            # Add chat history
            for msg in self.chat_history[-5:]:  # Last 5 messages
                messages.append(msg)

            # Add current message
            messages.append({"role": "user", "content": user_message})

            # Get response from Groq
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.3,
                max_tokens=1000,
            )

            response_text = response.choices[0].message.content

            # Add to chat history
            self.chat_history.append({"role": "user", "content": user_message})
            self.chat_history.append({"role": "assistant", "content": response_text})

            return response_text

        except Exception as e:
            return f"Je suis désolé, je ne peux pas répondre pour le moment: {str(e)}"

    def get_quick_actions(self):
        """Get quick action suggestions"""
        return [
            "📊 Générer rapport mensuel",
            "📅 Planifier réunion COGES",
            "👥 Voir planning personnel",
            "📋 Consulter checklist",
            "📈 Voir indicateurs",
            "📧 Envoyer notification",
            "🔍 Rechercher document",
            "⚙️ Paramètres application",
        ]

    def clear_chat_history(self):
        """Clear chat history"""
        self.chat_history = []


# Global chatbot instance
chatbot = ChatbotAssistant()
