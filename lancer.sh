#!/bin/bash

# Script de lancement de l'application ESPC Generator

cd "$(dirname "$0")"

# Vérifier si streamlit est installé
if ! command -v streamlit &> /dev/null; then
    echo "Streamlit non trouvé. Installation..."
    pip3 install streamlit groq python-docx
fi

# Lancer l'application
echo "Lancement de l'application ESPC Generator..."
streamlit run app_simple.py --server.port 8503 --server.headless true
