#!/usr/bin/env python3
"""
Outil de mesure des performances du ESPC Generator
Identifie les goulots d'étranglement et optimise le système
"""

import sys
import time
import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

sys.path.append("/Users/apple/Desktop/MON CENTRE /ESPC_Generator")


@contextmanager
def timer(description):
    """Context manager pour mesurer le temps d'exécution"""
    start_time = time.time()
    yield
    end_time = time.time()
    print(f"⏱️  {description}: {end_time - start_time:.4f} secondes")


def measure_database_performance():
    """Mesure les performances de la base de données"""
    print("📊 Mesure des performances de la base de données...")

    # Test de connexion
    with timer("Connexion à la base de données"):
        conn = sqlite3.connect("espc_data.db")
        cursor = conn.cursor()

    # Test de requêtes simples
    with timer("Récupération du personnel"):
        cursor.execute("SELECT * FROM personnel")
        personnel = cursor.fetchall()
        print(f"  → {len(personnel)} enregistrements récupérés")

    with timer("Récupération des établissements"):
        cursor.execute("SELECT * FROM etablissements")
        etablissements = cursor.fetchall()
        print(f"  → {len(etablissements)} établissements")

    with timer("Récupération des périodes"):
        cursor.execute("SELECT * FROM periodes")
        periodes = cursor.fetchall()
        print(f"  → {len(periodes)} périodes")

    # Test de requêtes avec jointures
    with timer("Requête avec jointures (personnel + fiches)"):
        cursor.execute("""
            SELECT p.*, fp.template, fp.contenu
            FROM personnel p
            LEFT JOIN fiches_poste fp ON p.id = fp.personnel_id
            LIMIT 10
        """)
        jointures = cursor.fetchall()
        print(f"  → {len(jointures)} résultats avec jointures")

    # Test de recherche par catégorie
    with timer("Recherche par catégorie (IDE)"):
        cursor.execute("SELECT * FROM personnel WHERE categorie = ?", ("IDE",))
        ide_personnel = cursor.fetchall()
        print(f"  → {len(ide_personnel)} IDEs trouvés")

    # Test d'insertion
    with timer("Insertion de données test"):
        cursor.execute(
            """
            INSERT INTO personnel (nom, prenom, categorie, poste, date_embauche)
            VALUES (?, ?, ?, ?, ?)
        """,
            ("Performance Test", "User", "CIM", "Agent", "2024-01-01"),
        )
        conn.commit()
        inserted_id = cursor.lastrowid
        # Nettoyage
        cursor.execute("DELETE FROM personnel WHERE id = ?", (inserted_id,))
        conn.commit()
        print(f"  → Insertion et nettoyage réussis")

    conn.close()
    print("✅ Base de données testée\n")


def measure_file_io_performance():
    """Mesure les performances de lecture/écriture de fichiers"""
    print("📁 Mesure des performances de lecture/écriture de fichiers...")

    # Test de lecture de templates
    with timer("Lecture des templates principaux"):
        with open("templates.json", "r") as f:
            templates = json.load(f)
        print(f"  → {len(templates)} templates chargés")

    with timer("Lecture des checklists"):
        with open("templates_checklist.json", "r") as f:
            checklists = json.load(f)
        print(f"  → {len(checklists)} checklists chargées")

    # Test d'écriture
    with timer("Écriture de données test"):
        test_data = {"test": "performance", "timestamp": datetime.now().isoformat()}
        with open("test_performance.json", "w") as f:
            json.dump(test_data, f, indent=2)

        # Lecture et nettoyage
        with open("test_performance.json", "r") as f:
            read_data = json.load(f)
        os.remove("test_performance.json")
        print(f"  → Écriture/lecture/nettoyage réussis")

    print("✅ Fichiers testés\n")


def measure_application_startup():
    """Mesure le temps de démarrage de l'application"""
    print("🚀 Mesure du temps de démarrage de l'application...")

    # Test des imports principaux
    with timer("Import des modules principaux"):
        import database
        from chatbot import ChatbotAssistant
        from performance_manager import PerformanceManager

    print("✅ Imports testés\n")


def analyze_database_indexes():
    """Analyse des indexes existants et recommandations"""
    print("🔍 Analyse des indexes de la base de données...")

    conn = sqlite3.connect("espc_data.db")
    cursor = conn.cursor()

    # Vérifier les indexes existants
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    existing_indexes = cursor.fetchall()
    print(f"Indexes existants: {[idx[0] for idx in existing_indexes]}")

    # Analyser les tables et leurs tailles
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    recommendations = []

    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  → Table {table_name}: {count} enregistrements")

        # Recommandations d'index
        if table_name == "personnel" and count > 100:
            recommendations.append(
                f"  ⚠️  Ajouter un index sur 'categorie' pour {table_name}"
            )
        if table_name == "documents" and count > 50:
            recommendations.append(
                f"  ⚠️  Ajouter un index sur 'periode_id' pour {table_name}"
            )
        if table_name == "fiches_poste" and count > 25:
            recommendations.append(
                f"  ⚠️  Ajouter un index sur 'personnel_id' pour {table_name}"
            )

    conn.close()

    if recommendations:
        print("\n📝 Recommandations d'optimisation:")
        for rec in recommendations:
            print(rec)
    else:
        print("✅ Aucune recommandation d'index nécessaire pour le volume actuel")

    print()


def generate_optimization_report():
    """Génère un rapport d'optimisation"""
    print("📋 Génération du rapport d'optimisation...")

    report = {
        "timestamp": datetime.now().isoformat(),
        "performance_metrics": {},
        "recommendations": [],
        "next_steps": [],
    }

    # Mesurer les performances
    start_time = time.time()

    # Base de données
    conn = sqlite3.connect("espc_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM personnel")
    personnel_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM documents")
    documents_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM etablissements")
    etablissements_count = cursor.fetchone()[0]
    conn.close()

    end_time = time.time()

    # Collecter les métriques
    report["performance_metrics"] = {
        "total_records": personnel_count + documents_count + etablissements_count,
        "personnel_count": personnel_count,
        "documents_count": documents_count,
        "etablissements_count": etablissements_count,
        "measurement_time": end_time - start_time,
    }

    # Générer des recommandations basées sur les données
    if personnel_count > 50:
        report["recommendations"].append(
            "Ajouter pagination pour la liste du personnel"
        )
    if documents_count > 20:
        report["recommendations"].append("Optimiser la recherche de documents")
    if etablissements_count > 5:
        report["recommendations"].append("Ajouter un index sur la table établissements")

    # Prochaines étapes
    report["next_steps"] = [
        "Ajouter des indexes SQL pour les requêtes fréquentes",
        "Implémenter la pagination pour les grandes listes",
        "Optimiser le chargement des templates",
        "Ajuster la mémoire de Streamlit si nécessaire",
    ]

    # Sauvegarder le rapport
    with open("performance_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("📄 Rapport d'optimisation généré: performance_report.json")

    # Afficher un résumé
    print("\n📊 Résumé des performances:")
    print(
        f"  🔢 Total d'enregistrements: {report['performance_metrics']['total_records']}"
    )
    print(f"  👥 Personnel: {personnel_count}")
    print(f"  📄 Documents: {documents_count}")
    print(f"  🏢 Établissements: {etablissements_count}")

    print("\n🎯 Recommandations principales:")
    for rec in report["recommendations"]:
        print(f"  • {rec}")

    print("\n🚀 Prochaines étapes:")
    for step in report["next_steps"]:
        print(f"  • {step}")

    print()


def main():
    """Exécution complète de l'analyse de performance"""
    print("=" * 60)
    print("🔧 Analyse des Performances - ESPC Generator")
    print("=" * 60)

    # Mesurer toutes les performances
    measure_database_performance()
    measure_file_io_performance()
    measure_application_startup()
    analyze_database_indexes()
    generate_optimization_report()

    print("=" * 60)
    print("✅ Analyse de performance terminée !")
    print("📊 Consultez le fichier 'performance_report.json' pour les détails.")
    print("=" * 60)


if __name__ == "__main__":
    import os

    main()
