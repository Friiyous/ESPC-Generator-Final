"""
Mobile Interface Module
"""

import streamlit as st
import os
import json
from datetime import datetime
from database import get_personnel, get_nominations, get_checklists
from performance_manager import performance_manager


class MobileInterface:
    def __init__(self):
        self.setup_mobile_layout()

    def setup_mobile_layout(self):
        """Setup mobile-optimized layout"""
        # Configure Streamlit for mobile
        st.set_page_config(
            page_title="ESPC Mobile",
            page_icon="📱",
            layout="wide",
            initial_sidebar_state="collapsed",
        )

        # Mobile navigation
        self.mobile_navigation()

    def mobile_navigation(self):
        """Mobile navigation bar"""
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

        with col1:
            if st.button("🏠", help="Accueil"):
                self.show_home()

        with col2:
            if st.button("📷", help="Scanner"):
                self.show_scanner()

        with col3:
            if st.button("💬", help="Chat"):
                self.show_chat()

        with col4:
            if st.button("📊", help="Performance"):
                self.show_performance()

        with col5:
            if st.button("⚙️", help="Paramètres"):
                self.show_settings()

    def show_home(self):
        """Mobile home screen"""
        st.title("📱 ESPC Mobile")

        # Quick stats
        personnel_count = len(get_personnel())
        active_nominations = len(
            [
                n
                for n in get_nominations()
                if n["date_nomination"] > datetime.now().strftime("%Y-%m-%d")
            ]
        )
        pending_checklists = len(
            [c for c in get_checklists() if c["statut"] == "en_cours"]
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Personnel", personnel_count)
        with col2:
            st.metric("Nominations", active_nominations)
        with col3:
            st.metric("Checklists", pending_checklists)

        # Quick actions
        st.subheader("🚀 Actions Rapides")

        if st.button("📄 Générer Rapport"):
            st.info("Formulaire de génération de rapport simplifié")

        if st.button("📅 Planifier Réunion"):
            st.info("Planification rapide de réunion")

        if st.button("📋 Vérifier Checklist"):
            st.info("Vérification rapide des checklists")

        # Recent activities
        st.subheader("📈 Activités Récentes")

        # Simulate recent activities
        activities = [
            "Nouvelle nomination: Koffi Kouassi - IDE",
            "Checklist T1 terminée",
            "Rapport mensuel généré",
            "Réunion COGES planifiée",
        ]

        for activity in activities:
            st.write(f"• {activity}")

    def show_scanner(self):
        """Mobile scanner interface"""
        st.title("📷 Scanner Rapide")

        st.info("Prenez une photo des documents pour analyse rapide")

        # File upload for mobile
        uploaded_file = st.file_uploader(
            "Télécharger une photo",
            type=["jpg", "jpeg", "png", "pdf"],
            help="Prenez en photo les documents pour analyse",
        )

        if uploaded_file is not None:
            st.success(f"Fichier téléchargé: {uploaded_file.name}")

            # Analyze the document (simulated)
            if st.button("🔍 Analyser Document"):
                with st.spinner("Analyse en cours..."):
                    # Simulated analysis
                    analysis_result = {
                        "type": "Document administratif",
                        "content": "Rapport d'activités mensuelles",
                        "actions": [
                            "Garder pour référence",
                            "Partager avec le district",
                        ],
                    }

                    st.subheader("Résultats de l'analyse")
                    st.json(analysis_result)

                    if st.button("💾 Sauvegarder"):
                        st.success("Document sauvegardé avec succès!")

    def show_chat(self):
        """Mobile chat interface"""
        st.title("💬 Assistant Intelligent")

        # Chat interface
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Chat input
        if prompt := st.chat_input("Posez votre question..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            # Get response
            with st.chat_message("assistant"):
                response = f"Je comprends votre question: '{prompt}'. Je vais vous aider avec cela."
                st.write(response)

                # Add to messages
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )

    def show_performance(self):
        """Mobile performance view"""
        st.title("📊 Performance Rapide")

        # Quick performance overview
        personnel_performance = performance_manager.get_personnel_performance()

        if personnel_performance:
            st.subheader("Performance du Personnel")

            # Simple list view for mobile
            for perf in personnel_performance[:5]:  # Show top 5
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"{perf['nom']} ({perf['categorie']})")

                with col2:
                    # Progress bar for mobile
                    progress = st.progress(perf["score"] / 100)
                    st.write(f"{perf['score']:.0f}%")

        # Quick stats
        st.subheader("Statistiques Rapides")

        col1, col2 = st.columns(2)

        with col1:
            avg_score = (
                sum(p["score"] for p in personnel_performance)
                / len(personnel_performance)
                if personnel_performance
                else 0
            )
            st.metric("Performance Moyenne", f"{avg_score:.1f}%")

        with col2:
            active_count = len(
                [p for p in personnel_performance if p["statut"] == "actif"]
            )
            st.metric("Personnel Actif", active_count)

    def show_settings(self):
        """Mobile settings"""
        st.title("⚙️ Paramètres")

        # Notification settings
        st.subheader("Notifications")

        notification_enabled = st.checkbox("Activer les notifications")
        email_notifications = st.checkbox("Notifications par email")
        whatsapp_notifications = st.checkbox("Notifications WhatsApp")

        # Theme settings
        st.subheader("Thème")

        theme = st.selectbox("Choisir le thème", ["Clair", "Sombre"])

        # Language settings
        st.subheader("Langue")

        language = st.selectbox("Langue", ["Français", "Anglais"])

        # Save settings
        if st.button("💾 Sauvegarder les paramètres"):
            st.success("Paramètres sauvegardés!")


# Global mobile interface instance
mobile_interface = MobileInterface()
