"""
Fonctions de base de données optimisées avec cache
"""

import sqlite3
import json
from datetime import datetime

# Importer les fonctions de la base de données originale
from database import get_db_connection

# Cache des templates
_templates_cache = None
_checklists_cache = None
_postes_cache = None
_context_cache = None


def get_templates():
    """Récupère les templates depuis le cache"""
    global _templates_cache
    if _templates_cache is None:
        with open("template_cache.json", "r") as f:
            cache = json.load(f)
            _templates_cache = cache["templates"]
    return _templates_cache


def get_checklists():
    """Récupère les checklists depuis le cache"""
    global _checklists_cache
    if _checklists_cache is None:
        with open("template_cache.json", "r") as f:
            cache = json.load(f)
            _checklists_cache = cache["checklists"]
    return _checklists_cache


def get_postes():
    """Récupère les postes depuis le cache"""
    global _postes_cache
    if _postes_cache is None:
        with open("template_cache.json", "r") as f:
            cache = json.load(f)
            _postes_cache = cache["postes"]
    return _postes_cache


def get_context():
    """Récupère le contexte depuis le cache"""
    global _context_cache
    if _context_cache is None:
        with open("template_cache.json", "r") as f:
            cache = json.load(f)
            _context_cache = cache["context"]
    return _context_cache


def get_personnel_optimized(category=None, limit=None):
    """Fonction optimisée de récupération du personnel"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM personnel"
    params = []

    if category:
        query += " WHERE categorie = ?"
        params.append(category)

    if limit:
        query += f" LIMIT {limit}"

    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()

    return [dict(row) for row in result]


def get_documents_optimized(periode_id=None, limit=None):
    """Fonction optimisée de récupération des documents"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT d.*, e.nom as etablissement_nom, p.periode, p.trimestre, p.annee
        FROM documents d
        JOIN periodes p ON d.periode_id = p.id
        JOIN etablissements e ON p.etablissement_id = e.id
    """
    params = []

    if periode_id:
        query += " WHERE d.periode_id = ?"
        params.append(periode_id)

    if limit:
        query += f" LIMIT {limit}"

    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()

    return [dict(row) for row in result]
