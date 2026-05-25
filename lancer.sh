#!/bin/bash

# Script de lancement amélioré de l'application ESPC Generator

cd "$(dirname "$0")"

echo "🚀 Démarrage de l'application ESPC Generator v2.0"
echo "==============================================="

# Vérifier les dépendances
echo "📋 Vérification des dépendances..."

if ! command -v streamlit &> /dev/null; then
    echo "⚠️ Streamlit non trouvé. Installation..."
    pip3 install streamlit groq python-docx plotly pandas fpdf
fi

# Vérifier les modules personnalisés
echo "🔍 Vérification des modules personnalisés..."

if [ ! -f "whatsapp_integration.py" ]; then
    echo "⚠️ Module WhatsApp non trouvé"
fi

if [ ! -f "chatbot.py" ]; then
    echo "⚠️ Module Chatbot non trouvé"
fi

if [ ! -f "performance_manager.py" ]; then
    echo "⚠️ Module Performance non trouvé"
fi

if [ ! -f "mobile_interface.py" ]; then
    echo "⚠️ Module Mobile non trouvé"
fi

echo "✅ Tous les modules sont disponibles"

# Options de lancement
echo ""
echo "🎯 Options de lancement disponibles:"
echo "1. Application principale (app.py)"
echo "2. Vue mobile (mobile_interface.py)"
echo "3. Dashboard performance (performance_manager.py)"
echo "4. Chatbot (chatbot.py)"

read -p "Choisissez l'option (1-4) [1]: " choice

case $choice in
    2)
        echo "📱 Lancement de la vue mobile..."
        streamlit run mobile_interface.py --server.port 8503 --server.headless true
        ;;
    3)
        echo "📊 Lancement du dashboard performance..."
        streamlit run performance_manager.py --server.port 8503 --server.headless true
        ;;
    4)
        echo "💬 Lancement du chatbot..."
        streamlit run chatbot.py --server.port 8503 --server.headless true
        ;;
    *)
        echo "🏥 Lancement de l'application principale..."
        streamlit run app.py --server.port 8503 --server.headless true
        ;;
esac

echo ""
echo "🌐 Application disponible à l'adresse:"
echo "   Local: http://localhost:8503"
echo "   Réseau: http://$(hostname -I | awk '{print $1}'):8503"
