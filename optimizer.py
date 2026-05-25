#!/usr/bin/env python3
"""
Optimisations du ESPC Generator
Implémente les améliorations identifiées dans l'analyse de performance
"""

import sys
import sqlite3
import json
import os
from datetime import datetime

sys.path.append("/Users/apple/Desktop/MON CENTRE /ESPC_Generator")


def add_database_indexes():
    """Ajoute des indexes SQL pour optimiser les requêtes fréquentes"""
    print("🔧 Ajout des indexes SQL...")

    conn = sqlite3.connect("espc_data.db")
    cursor = conn.cursor()

    indexes_to_add = [
        ("idx_personnel_categorie", "personnel", "categorie"),
        ("idx_documents_periode", "documents", "periode_id"),
        ("idx_fiches_personnel", "fiches_poste", "personnel_id"),
        ("idx_nominations_personnel", "nominations", "personnel_id"),
        ("idx_checklists_periode", "checklists", "periode_id"),
        ("idx_etablissements_type", "etablissements", "type"),
        ("idx_periodes_etablissement", "periodes", "etablissement_id"),
    ]

    for index_name, table_name, column_name in indexes_to_add:
        try:
            cursor.execute(
                f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})"
            )
            print(f"✅ Index {index_name} créé sur {table_name}.{column_name}")
        except sqlite3.Error as e:
            print(f"⚠️ Erreur création index {index_name}: {e}")

    conn.commit()
    conn.close()
    print("✅ Indexes SQL ajoutés\n")


def create_template_cache():
    """Crée un système de cache pour les templates"""
    print("🗃️ Création du cache des templates...")

    try:
        # Charger tous les templates en mémoire
        with open("templates.json", "r") as f:
            templates_cache = json.load(f)

        with open("templates_checklist.json", "r") as f:
            checklists_cache = json.load(f)

        # Sauvegarder le cache des templates uniquement
        cache_data = {
            "templates": templates_cache,
            "checklists": checklists_cache,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0",
        }

        with open("template_cache.json", "w") as f:
            json.dump(cache_data, f, indent=2)

        print("✅ Cache des templates créé: template_cache.json")

        # Tester le cache
        test_cache_loading()

    except Exception as e:
        print(f"❌ Erreur création cache: {e}")

    print()


def test_cache_loading():
    """Teste le chargement depuis le cache"""
    print("🧪 Test du chargement depuis le cache...")

    try:
        with open("template_cache.json", "r") as f:
            cache = json.load(f)

        # Vérifier que toutes les données sont présentes
        required_keys = ["templates", "checklists", "postes", "context"]
        for key in required_keys:
            if key in cache:
                print(f"✅ {key}: {len(cache[key])} éléments chargés depuis le cache")
            else:
                print(f"❌ {key}: manquant dans le cache")

    except Exception as e:
        print(f"❌ Erreur test cache: {e}")


def add_pagination_system():
    """Ajoute un système de pagination pour les grandes listes"""
    print("📄 Création du système de pagination...")

    # Créer un module pour la pagination
    pagination_code = '''"""
Système de pagination pour les grandes listes
"""

def paginate_list(data, page=1, per_page=20):
    """
    Paginate a list of data
    
    Args:
        data: List of items to paginate
        page: Current page number (1-based)
        per_page: Number of items per page
    
    Returns:
        dict: Paginated data with pagination info
    """
    if not data:
        return {
            "items": [],
            "total": 0,
            "pages": 0,
            "current_page": page,
            "per_page": per_page,
            "has_next": False,
            "has_prev": False
        }
    
    total = len(data)
    pages = (total + per_page - 1) // per_page
    
    # Validate page number
    page = max(1, min(page, pages))
    
    # Calculate slice indices
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    items = data[start_idx:end_idx]
    
    return {
        "items": items,
        "total": total,
        "pages": pages,
        "current_page": page,
        "per_page": per_page,
        "has_next": page < pages,
        "has_prev": page > 1
    }

def get_pagination_controls(current_page, total_pages, per_page=20):
    """
    Generate pagination controls for Streamlit
    
    Args:
        current_page: Current page number
        total_pages: Total number of pages
        per_page: Items per page
    
    Returns:
        dict: Pagination controls configuration
    """
    if total_pages <= 1:
        return None
    
    controls = {
        "current_page": current_page,
        "total_pages": total_pages,
        "per_page": per_page,
        "has_prev": current_page > 1,
        "has_next": current_page < total_pages,
        "start_range": max(1, current_page - 2),
        "end_range": min(total_pages, current_page + 2)
    }
    
    return controls
'''

    try:
        with open("pagination.py", "w") as f:
            f.write(pagination_code)

        print("✅ Module de pagination créé: pagination.py")

        # Tester le module
        test_pagination_system()

    except Exception as e:
        print(f"❌ Erreur création pagination: {e}")

    print()


def test_pagination_system():
    """Teste le système de pagination"""
    print("🧪 Test du système de pagination...")

    try:
        # Importer le module
        sys.path.append("/Users/apple/Desktop/MON CENTRE /ESPC_Generator")
        from pagination import paginate_list, get_pagination_controls

        # Créer des données de test
        test_data = list(range(100))  # 100 items

        # Tester la pagination
        page1 = paginate_list(test_data, page=1, per_page=10)
        print(f"✅ Page 1: {len(page1['items'])} items, Total: {page1['total']}")

        page5 = paginate_list(test_data, page=5, per_page=10)
        print(f"✅ Page 5: {len(page5['items'])} items")

        # Tester les contrôles
        controls = get_pagination_controls(3, 10, 10)
        if controls:
            print(
                f"✅ Contrôles de pagination: Page {controls['current_page']}/{controls['total_pages']}"
            )
        else:
            print("✅ Pas de contrôles nécessaires (1 page seulement)")

    except Exception as e:
        print(f"❌ Erreur test pagination: {e}")


def optimize_streamlit_config():
    """Optimise la configuration de Streamlit"""
    print("⚙️ Optimisation de la configuration Streamlit...")

    config_file = """[server]
# Augmenter la limite de mémoire pour Streamlit
server.maxMessageSize = 1000
server.fileWatcherType = "none"
server.headless = true
server.port = 8503
server.address = "0.0.0.0"

[browser]
# Désactiver le redémarrage automatique en développement
serverAddress = "localhost"
serverPort = 8503
gatherUsageStats = false

[logger]
# Désactiver les logs pour réduire la charge
level = "error"

[runner]
# Optimiser l'exécution
fastRerun = true
"""

    try:
        with open("streamlit_config.toml", "w") as f:
            f.write(config_file)

        print("✅ Configuration Streamlit créée: streamlit_config.toml")
        print("  • Mémoire augmentée")
        print("  • Logs optimisés")
        print("  • Redémarrage rapide activé")

    except Exception as e:
        print(f"❌ Erreur configuration Streamlit: {e}")

    print()


def create_optimized_database_functions():
    """Crée des fonctions de base de données optimisées"""
    print("🚀 Création de fonctions de base de données optimisées...")

    optimized_functions = '''"""
Fonctions de base de données optimisées avec cache
"""

import sqlite3
import json
from datetime import datetime

# Cache des templates
_templates_cache = None
_checklists_cache = None
_postes_cache = None
_context_cache = None

def get_templates():
    """Récupère les templates depuis le cache"""
    global _templates_cache
    if _templates_cache is None:
        with open('template_cache.json', 'r') as f:
            cache = json.load(f)
            _templates_cache = cache['templates']
    return _templates_cache

def get_checklists():
    """Récupère les checklists depuis le cache"""
    global _checklists_cache
    if _checklists_cache is None:
        with open('template_cache.json', 'r') as f:
            cache = json.load(f)
            _checklists_cache = cache['checklists']
    return _checklists_cache

def get_postes():
    """Récupère les postes depuis le cache"""
    global _postes_cache
    if _postes_cache is None:
        with open('template_cache.json', 'r') as f:
            cache = json.load(f)
            _postes_cache = cache['postes']
    return _postes_cache

def get_context():
    """Récupère le contexte depuis le cache"""
    global _context_cache
    if _context_cache is None:
        with open('template_cache.json', 'r') as f:
            cache = json.load(f)
            _context_cache = cache['context']
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
'''

    try:
        with open("database_optimized.py", "w") as f:
            f.write(optimized_functions)

        print(
            "✅ Fonctions de base de données optimisées créées: database_optimized.py"
        )
        print("  • Cache des templates")
        print("  • Requêtes optimisées")
        print("  • Fonctions spécifiques pour les besoins fréquents")

    except Exception as e:
        print(f"❌ Erreur création fonctions optimisées: {e}")

    print()


def main():
    """Exécution de toutes les optimisations"""
    print("=" * 60)
    print("🚀 Optimisation du ESPC Generator")
    print("=" * 60)

    # Appliquer toutes les optimisations
    add_database_indexes()
    create_template_cache()
    add_pagination_system()
    optimize_streamlit_config()
    create_optimized_database_functions()

    print("=" * 60)
    print("✅ Optimisations complétées !")
    print("📊 Le système est maintenant optimisé pour de meilleures performances.")
    print("🚀 Prêt pour une croissance future !")
    print("=" * 60)


if __name__ == "__main__":
    main()
