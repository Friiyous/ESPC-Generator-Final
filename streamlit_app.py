"""Point d'entrée Streamlit Cloud - Délègue à app_simple.py"""
import os
import sys

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(__file__))

# Lancer l'application principale
from app_simple import main

if __name__ == "__main__":
    main()
