"""
Module de gestion de la base de données SQLite
"""

import sqlite3
import os
from datetime import datetime

DATABASE_PATH = "espc_data.db"


def get_db_connection():
    """Établit la connexion à la base de données"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialise les tables de la base de données"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table des établissements
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS etablissements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            type TEXT,
            region TEXT,
            district TEXT,
            population INTEGER,
            telephone TEXT,
            responsable TEXT,
            date_creation TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table des périodes d'évaluation
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS periodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            etablissement_id INTEGER,
            periode TEXT,
            trimestre TEXT,
            annee INTEGER,
            date_debut TEXT,
            date_fin TEXT,
            FOREIGN KEY (etablissement_id) REFERENCES etablissements(id)
        )
    """)

    # Table des données d'évaluation (clé-valeur par établissement/période)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donnees_evaluation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            periode_id INTEGER,
            categorie TEXT,
            sous_categorie TEXT,
            indicateur TEXT,
            valeur TEXT,
            score REAL,
            observations TEXT,
            FOREIGN KEY (periode_id) REFERENCES periodes(id)
        )
    """)

    # Table des documents générés
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            periode_id INTEGER,
            type_document TEXT,
            titre TEXT,
            contenu TEXT,
            date_generation TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (periode_id) REFERENCES periodes(id)
        )
    """)

    # Table du personnel
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personnel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            categorie TEXT NOT NULL,
            poste TEXT NOT NULL,
            telephone TEXT DEFAULT '',
            date_embauche TEXT,
            statut TEXT DEFAULT 'actif',
            date_creation TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Migration : ajouter colonne telephone si elle n'existe pas
    try:
        cursor.execute("ALTER TABLE personnel ADD COLUMN telephone TEXT DEFAULT ''")
    except Exception:
        pass

    # Table des fiches de poste
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fiches_poste (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personnel_id INTEGER,
            template TEXT,
            contenu TEXT,
            date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (personnel_id) REFERENCES personnel(id)
        )
    """)

    # Table des nominations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nominations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personnel_id INTEGER,
            poste TEXT NOT NULL,
            date_nomination TEXT,
            session TEXT,
            duree TEXT,
            motif TEXT,
            date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (personnel_id) REFERENCES personnel(id)
        )
    """)

    # Table des checklists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checklists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            periode_id INTEGER,
            type_checklist TEXT,
            items TEXT,
            statut TEXT DEFAULT 'en_cours',
            date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (periode_id) REFERENCES periodes(id)
        )
    """)

    conn.commit()
    conn.close()


def ajouter_etablissement(
    nom, type_, region, district, population, telephone, responsable
):
    """Ajoute un nouvel établissement"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO etablissements (nom, type, region, district, population, telephone, responsable)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (nom, type_, region, district, population, telephone, responsable),
    )
    conn.commit()
    id_etablissement = cursor.lastrowid
    conn.close()
    return id_etablissement


def get_etablissements():
    """Récupère tous les établissements"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM etablissements ORDER BY nom")
    result = cursor.fetchall()
    conn.close()
    return [dict(row) for row in result]


def get_etablissement_by_id(id_):
    """Récupère un établissement par son ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM etablissements WHERE id = ?", (id_,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None


def ajouter_periode(etablissement_id, periode, trimestre, annee, date_debut, date_fin):
    """Ajoute une nouvelle période d'évaluation"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO periodes (etablissement_id, periode, trimestre, annee, date_debut, date_fin)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (etablissement_id, periode, trimestre, annee, date_debut, date_fin),
    )
    conn.commit()
    id_periode = cursor.lastrowid
    conn.close()
    return id_periode


def get_periodes(etablissement_id):
    """Récupère les périodes d'évaluation d'un établissement"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM periodes
        WHERE etablissement_id = ?
        ORDER BY annee DESC, trimestre DESC
    """,
        (etablissement_id,),
    )
    result = cursor.fetchall()
    conn.close()
    return [dict(row) for row in result]


def ajouter_donnee(
    periode_id, categorie, sous_categorie, indicateur, valeur, score, observations
):
    """Ajoute une donnée d'évaluation"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO donnees_evaluation (periode_id, categorie, sous_categorie, indicateur, valeur, score, observations)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            periode_id,
            categorie,
            sous_categorie,
            indicateur,
            valeur,
            score,
            observations,
        ),
    )
    conn.commit()
    conn.close()


def get_donnees_periode(periode_id):
    """Récupère toutes les données d'une période"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM donnees_evaluation
        WHERE periode_id = ?
    """,
        (periode_id,),
    )
    result = cursor.fetchall()
    conn.close()
    return [dict(row) for row in result]


def sauvegarder_document(periode_id, type_document, titre, contenu):
    """Sauvegarde un document généré"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO documents (periode_id, type_document, titre, contenu)
        VALUES (?, ?, ?, ?)
    """,
        (periode_id, type_document, titre, contenu),
    )
    document_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return document_id


def get_documents(periode_id):
    """Récupère les documents d'une période"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM documents
        WHERE periode_id = ?
        ORDER BY date_generation DESC
    """,
        (periode_id,),
    )
    result = cursor.fetchall()
    conn.close()
    return [dict(row) for row in result]


# =================================================================
# FONCTIONS PERSONNEL
# =================================================================


def ajouter_personnel(nom, prenom, categorie, poste, telephone, date_embauche):
    """Ajoute un nouveau membre du personnel"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO personnel (nom, prenom, categorie, poste, telephone, date_embauche)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (nom, prenom, categorie, poste, telephone, date_embauche),
    )
    conn.commit()
    id_personnel = cursor.lastrowid
    conn.close()
    return id_personnel


def get_personnel():
    """Récupère tout le personnel"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personnel ORDER BY categorie, nom")
    result = cursor.fetchall()
    conn.close()
    return [dict(row) for row in result]


def get_personnel_by_id(id_):
    """Récupère un membre du personnel par son ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM personnel WHERE id = ?", (id_,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None


def verifier_doublon_personnel(nom, prenom, categorie, exclude_id=None):
    """Vérifie si un employé avec le même nom/prénom/catégorie existe déjà"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if exclude_id:
        cursor.execute(
            "SELECT id FROM personnel WHERE nom = ? AND prenom = ? AND categorie = ? AND id != ?",
            (nom, prenom, categorie, exclude_id),
        )
    else:
        cursor.execute(
            "SELECT id FROM personnel WHERE nom = ? AND prenom = ? AND categorie = ?",
            (nom, prenom, categorie),
        )
    result = cursor.fetchone()
    conn.close()
    return result is not None


def get_personnel_par_categorie(categorie):
    """Récupère le personnel par catégorie"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM personnel 
        WHERE categorie = ? 
        ORDER BY nom
    """,
        (categorie,),
    )
    result = cursor.fetchall()
    conn.close()
    return [dict(row) for row in result]


def modifier_personnel(id_, nom, prenom, categorie, poste, telephone, date_embauche, statut):
    """Modifie les informations d'un membre du personnel"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE personnel 
        SET nom = ?, prenom = ?, categorie = ?, poste = ?, telephone = ?, date_embauche = ?, statut = ?
        WHERE id = ?
    """,
        (nom, prenom, categorie, poste, telephone, date_embauche, statut, id_),
    )
    conn.commit()
    conn.close()


def supprimer_personnel(id_):
    """Supprime un membre du personnel"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM personnel WHERE id = ?", (id_,))
    conn.commit()
    conn.close()


# =================================================================
# FONCTIONS FICHES DE POSTE
# =================================================================


def ajouter_fiche_poste(personnel_id, template, contenu):
    """Ajoute une fiche de poste"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO fiches_poste (personnel_id, template, contenu)
        VALUES (?, ?, ?)
    """,
        (personnel_id, template, contenu),
    )
    id_fiche = cursor.lastrowid
    conn.commit()
    conn.close()
    return id_fiche


def get_fiches_poste(personnel_id=None):
    """Récupère les fiches de poste"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if personnel_id:
        cursor.execute(
            """
            SELECT fp.*, p.nom, p.prenom, p.categorie
            FROM fiches_poste fp
            JOIN personnel p ON fp.personnel_id = p.id
            WHERE fp.personnel_id = ?
            ORDER BY fp.date_creation DESC
        """,
            (personnel_id,),
        )
    else:
        cursor.execute("""
            SELECT fp.*, p.nom, p.prenom, p.categorie
            FROM fiches_poste fp
            JOIN personnel p ON fp.personnel_id = p.id
            ORDER BY fp.date_creation DESC
        """)
    result = cursor.fetchall()
    conn.close()
    return [dict(row) for row in result]


# =================================================================
# FONCTIONS NOMINATIONS
# =================================================================


def ajouter_nomination(personnel_id, poste, date_nomination, session, duree, motif):
    """Ajoute une nomination"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO nominations (personnel_id, poste, date_nomination, session, duree, motif)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (personnel_id, poste, date_nomination, session, duree, motif),
    )
    conn.commit()
    conn.close()


def get_nominations(personnel_id=None):
    """Récupère les nominations"""
    conn = get_db_connection()
    cursor = conn.cursor()
    if personnel_id:
        cursor.execute(
            """
            SELECT n.*, p.nom, p.prenom, p.categorie
            FROM nominations n
            JOIN personnel p ON n.personnel_id = p.id
            WHERE n.personnel_id = ?
            ORDER BY n.date_creation DESC
        """,
            (personnel_id,),
        )
    else:
        cursor.execute("""
            SELECT n.*, p.nom, p.prenom, p.categorie
            FROM nominations n
            JOIN personnel p ON n.personnel_id = p.id
            ORDER BY n.date_creation DESC
        """)
    result = cursor.fetchall()
    conn.close()
    return [dict(row) for row in result]


# =================================================================
# FONCTIONS CHECKLISTS
# =================================================================


def ajouter_checklist(periode_id, type_checklist, items, statut="en_cours"):
    """Ajoute une checklist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO checklists (periode_id, type_checklist, items, statut)
        VALUES (?, ?, ?, ?)
    """,
        (periode_id, type_checklist, items, statut),
    )
    conn.commit()
    conn.close()


def get_checklists(periode_id=None, statut=None):
    """Récupère les checklists"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT c.*, e.nom as etablissement, p.periode
        FROM checklists c
        JOIN periodes p ON c.periode_id = p.id
        JOIN etablissements e ON p.etablissement_id = e.id
        WHERE 1=1
    """
    params = []

    if periode_id:
        query += " AND c.periode_id = ?"
        params.append(periode_id)

    if statut:
        query += " AND c.statut = ?"
        params.append(statut)

    query += " ORDER BY c.date_creation DESC"

    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return [dict(row) for row in result]


def maj_statut_checklist(id_, statut):
    """Met à jour le statut d'une checklist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE checklists SET statut = ? WHERE id = ?", (statut, id_))
    conn.commit()
    conn.close()
