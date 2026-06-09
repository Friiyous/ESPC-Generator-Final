"""
Module de gestion simplifiée du personnel CSR NAGNENEFOUN
Base de données SQLite pour le suivi du personnel
"""

import sqlite3
import os
from datetime import datetime

# Chemin de la base de données
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "personnel.db")

def get_connection():
    """Obtenir une connexion à la base de données"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_personnel_db():
    """Initialiser la base de données du personnel"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table personnel
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personnel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenoms TEXT,
            fonction TEXT NOT NULL,
            telephone TEXT,
            date_ajout TEXT NOT NULL,
            statut TEXT DEFAULT 'actif'
        )
    """)
    
    # Table affectations/responsabilités
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responsabilites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personnel_id INTEGER NOT NULL,
            responsabilite TEXT NOT NULL,
            date_affectation TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (personnel_id) REFERENCES personnel(id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    return True

def ajouter_personnel(nom, fonction, prenoms="", telephone=""):
    """Ajouter un nouveau membre du personnel"""
    conn = get_connection()
    cursor = conn.cursor()
    
    date_ajout = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute("""
        INSERT INTO personnel (nom, prenoms, fonction, telephone, date_ajout)
        VALUES (?, ?, ?, ?, ?)
    """, (nom.upper(), prenoms, fonction, telephone, date_ajout))
    
    personnel_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return personnel_id

def get_tout_personnel():
    """Récupérer tous les membres du personnel"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.*, 
               (SELECT GROUP_CONCAT(r.responsabilite, ', ') 
                FROM responsabilites r 
                WHERE r.personnel_id = p.id) as responsabilites
        FROM personnel p
        ORDER BY p.nom ASC
    """)
    
    result = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in result]

def get_personnel_par_fonction(fonction):
    """Récupérer le personnel par fonction"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM personnel 
        WHERE fonction = ? 
        ORDER BY nom ASC
    """, (fonction,))
    
    result = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in result]

def ajouter_responsabilite(personnel_id, responsabilite, notes=""):
    """Ajouter une responsabilité à un membre du personnel"""
    conn = get_connection()
    cursor = conn.cursor()
    
    date_affectation = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute("""
        INSERT INTO responsabilites (personnel_id, responsabilite, date_affectation, notes)
        VALUES (?, ?, ?, ?)
    """, (personnel_id, responsabilite, date_affectation, notes))
    
    responsabilite_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return responsabilite_id

def get_responsabilites_personnel(personnel_id):
    """Récupérer les responsabilités d'un membre du personnel"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM responsabilites 
        WHERE personnel_id = ?
        ORDER BY date_affectation DESC
    """, (personnel_id,))
    
    result = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in result]

def modifier_personnel(personnel_id, nom=None, fonction=None, telephone=None):
    """Modifier les informations d'un membre du personnel"""
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if nom:
        updates.append("nom = ?")
        params.append(nom.upper())
    if fonction:
        updates.append("fonction = ?")
        params.append(fonction)
    if telephone:
        updates.append("telephone = ?")
        params.append(telephone)
    
    if updates:
        params.append(personnel_id)
        cursor.execute(f"""
            UPDATE personnel 
            SET {', '.join(updates)}
            WHERE id = ?
        """, params)
        
        conn.commit()
    
    conn.close()
    return True

def supprimer_personnel(personnel_id):
    """Supprimer un membre du personnel"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # D'abord supprimer les responsabilités
    cursor.execute("DELETE FROM responsabilites WHERE personnel_id = ?", (personnel_id,))
    
    # Ensuite supprimer le personnel
    cursor.execute("DELETE FROM personnel WHERE id = ?", (personnel_id,))
    
    conn.commit()
    conn.close()
    
    return True

def get_fonctions_disponibles():
    """Liste des fonctions disponibles dans le CSR"""
    return [
        "Chef de Centre",
        "Major / Sage-Femme",
        "Infirmier Diplômé d'État (IDE)",
        "Aide-Soignant(e)",
        "Secrétaire / Agent Administratif",
        "Agent d'Entretien / Fille de Salle",
        "Gardien / Planton",
        "Agent de Santé Communautaire (ASC)",
        "Pharmacien / Chargé Pharmacie",
        "Chargé PEV",
        "Chargé Paludisme",
        "Chargé VIH/PTME",
        "Autre"
    ]

def get_responsabilites_types():
    """Liste des types de responsabilités"""
    return [
        "Responsable de la Pharmacie",
        "Responsable de l'Hygiène",
        "Responsable des Déchets Biomédicaux",
        "Point Focal CMU",
        "Chargé PEV",
        "Chargé Paludisme",
        "Chargé VIH/PTME",
        "Chargé CPN",
        "Chargé Nutrition",
        "Secrétaire du COGES",
        "Trésorier du COGES",
        "Autre"
    ]

# Initialiser la base au chargement
init_personnel_db()
