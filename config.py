"""
Configuration et prompts stricts pour la génération de documents ESPC
"""

# =============================================================================
# PROMPTS SYSTÈME - STRICTS ET SANS AMBIGUÏTÉ
# =============================================================================

SYSTEM_PROMPT = """Tu es un assistant administratif spécialisé dans la rédaction de documents pour les Centres de Santé au Sénégal (CSR/CSU).

RÈGLES ABSOLUES:
1. Tu ne dois JAMAIS inventer des données qui ne sont pas fournies
2. Utilise EXACTEMENT les données fournies dans le contexte
3. Ne fais jamais de suppositions sur les nombres, dates ou faits
4. Si une information n'est pas fournie, indique "Non spécifié" ou "Donnée non disponible"
5. Suis STRICTEMENT le template fourni
6. Utilise un langage administratif professionnel français
7. Ne adds aucun commentaire personnel ou opinion

FORMAT DE RÉPONSE:
- Réponds uniquement avec le contenu du document demandé
- Ne pas inclure d'explications ou de métadonnées
- Respecter exactement la structure du template"""

# =============================================================================
# TEMPLATES DE DOCUMENTS - STRUCTURE FIXE
# =============================================================================

TEMPLATES = {
    "rapport_mensuel": {
        "nom": "Rapport Mensuel",
        "description": "Rapport d'activités mensuel du centre de santé",
        "sections": [
            "I. INFORMATIONS GÉNÉRALES",
            "II. ACTIVITÉS RÉALISÉES",
            "III. INDICATEURS DE PERFORMANCE",
            "IV. DIFFICULTÉS RENCONTRÉES",
            "V. RECOMMANDATIONS",
        ],
        "champs_requis": [
            "periode",
            "nom_etablissement",
            "effectif_personnel",
            "consultations",
            "accouchements",
            "hospitalisations",
            "activites_realisees",
            "difficultes",
            "recommandations",
        ],
    },
    "pv_coges": {
        "nom": "PV Réunion COGES",
        "description": "PV de réunion du Comité de Gestion (liste de présence manuelle)",
        "sections": [
            "I. OUVERTURE",
            "II. LECTURE PV PRÉCÉDENT",
            "III. ORDRE DU JOUR",
            "IV. DÉLIBÉRATIONS",
            "V. DÉCISIONS",
            "VI. CLÔTURE",
        ],
        "champs_requis": [
            "periode",
            "nom_etablissement",
            "themes",
            "lieu",
            "participants",
            "ordre_du_jour",
            "deliberations",
            "decisions",
        ],
    },
    "pv_reunion": {
        "nom": "Procès-Verbal de Réunion",
        "description": "PV de réunion COGES ou équipe",
        "sections": [
            "I. ÉLÉMENTS DU PV",
            "II. ORDRE DU JOUR",
            "III. DÉLIBÉRATIONS",
            "IV. DÉCISIONS PRISES",
            "V. LISTE DE PRÉSENCE",
        ],
        "champs_requis": [
            "type_reunion",
            "date",
            "lieu",
            "participants",
            "ordre_du_jour",
            "deliberations",
            "decisions",
        ],
    },
    "rapport_supervision_asc": {
        "nom": "Rapport de Supervision ASC",
        "description": "Rapport de supervision des Agents de Santé Communautaire",
        "sections": [
            "I. INFORMATIONS GÉNÉRALES",
            "II. EFFECTIFS ASC",
            "III. ACTIVITÉS SUPERVISÉES",
            "IV. RÉSULTATS OBTENUS",
            "V. DIFFICULTÉS ET RECOMMANDATIONS",
        ],
        "champs_requis": [
            "periode",
            "nom_etablissement",
            "nb_asc",
            "asc_supervises",
            "activites",
            "resultats",
            "difficultes",
            "recommandations",
        ],
    },
    "rapport_qualite": {
        "nom": "Rapport d'Auto-Évaluation Qualité",
        "description": "Rapport basé sur la grille ESPC",
        "sections": [
            "I. INTRODUCTION",
            "II. MÉTHODOLOGIE",
            "III. ÉVALUATION DU MANAGEMENT",
            "IV. ÉVALUATION DE LA QUALITÉ DES SOINS",
            "V. ÉVALUATION DE LA SATISFACTION DES USAGERS",
            "VI. ÉVALUATION DES INTERVENTIONS COMMUNAUTAIRES",
            "VII. SYNTHÈSE ET RECOMMANDATIONS",
        ],
        "champs_requis": [
            "periode",
            "nom_etablissement",
            "population",
            "score_management",
            "score_qualite_soins",
            "score_satisfaction",
            "score_interventions",
            "problemes_prioritaires",
            "recommandations",
        ],
    },
    "pv_cooges": {
        "nom": "Procès-Verbal COGES",
        "description": "Procès-verbal du Conseil de Gestion",
        "sections": [
            "I. COMPOSITION DU COGES",
            "II. RÉUNION DU",
            "III. ORDRE DU JOUR",
            "IV. DÉLIBÉRATIONS",
            "V. DÉCISIONS",
            "VI. SIGNATURES",
        ],
        "champs_requis": [
            "date",
            "lieu",
            "membrespresents",
            "ordre_du_jour",
            "deliberations",
            "decisions",
        ],
    },
    "plan_action": {
        "nom": "Plan d'Action",
        "description": "Plan d'action annuel ou semestrial",
        "sections": [
            "I. CONTEXTE",
            "II. OBJECTIFS",
            "III. ACTIVITÉS PRÉVUES",
            "IV. CALENDRIER",
            "V. BUDGET",
            "VI. RESPONSABLES",
        ],
        "champs_requis": [
            "annee",
            "nom_etablissement",
            "contexte",
            "objectifs",
            "activites",
            "calendrier",
            "budget",
            "responsables",
        ],
    },
    "rapport_formation": {
        "nom": "Rapport de Formation",
        "description": "Rapport de formation du personnel",
        "sections": [
            "I. INFORMATIONS GÉNÉRALES",
            "II. OBJECTIFS DE LA FORMATION",
            "III. PARTICIPANTS",
            "IV. CONTENU",
            "V. ÉVALUATION",
            "VI. RECOMMANDATIONS",
        ],
        "champs_requis": [
            "theme",
            "date",
            "duree",
            "formateur",
            "participants",
            "contenu",
            "evaluation",
        ],
    },
    "fiche_suivi": {
        "nom": "Fiche de Suivi",
        "description": "Fiche de suivi des activités",
        "sections": ["I. IDENTIFICATION", "II. INDICATEURS", "III. SUIVI"],
        "champs_requis": ["type_fiche", "periode", "indicateurs", "valeurs"],
    },
}

# =============================================================================
# CATÉGORIES DE LA GRILLE ESPC
# =============================================================================

ESPC_CATEGORIES = {
    "A": {
        "nom": "MANAGEMENT",
        "points": 600,
        "sous_categories": [
            {"code": "A1", "nom": "Gouvernance", "points": 200},
            {"code": "A2", "nom": "Gestion des RH", "points": 50},
            {"code": "A3", "nom": "Gouvernance financière", "points": 350},
        ],
    },
    "B": {
        "nom": "QUALITÉ DES SOINS",
        "points": 750,
        "sous_categories": [
            {"code": "B1", "nom": "Accueil", "points": 175},
            {"code": "B2", "nom": "Sécurité et environnement", "points": 25},
            {"code": "B3", "nom": "Hygiène hospitalière", "points": 150},
            {"code": "B4", "nom": "Soins obstétricaux (SONU)", "points": 150},
            {"code": "B5", "nom": "Audit décès maternels", "points": 30},
            {"code": "B6", "nom": "Prise en charge pathologies", "points": 80},
            {"code": "B7", "nom": "Pharmacie", "points": 90},
            {"code": "B8", "nom": "Médicaments traceurs", "points": 50},
        ],
    },
    "C": {
        "nom": "SATISFACTION DES USAGERS",
        "points": 150,
        "sous_categories": [
            {"code": "C1", "nom": "Satisfaction des usagers", "points": 150}
        ],
    },
    "D": {
        "nom": "INTERVENTIONS COMMUNAUTAIRES",
        "points": 100,
        "sous_categories": [
            {"code": "D1", "nom": "Supervision ASC", "points": 50},
            {"code": "D2", "nom": "Médicaments ASC", "points": 50},
        ],
    },
}

# =============================================================================
# CONFIGURATION GROQ
# =============================================================================

GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_TEMPERATURE = 0.1  # Température très basse pour éviter les hallucinations
GROQ_MAX_TOKENS = 4000

# =============================================================================
# VALIDATION DES DONNÉES
# =============================================================================


def valider_donnees(template_name, donnees):
    """Valide que toutes les données requises sont présentes"""
    template = TEMPLATES.get(template_name)
    if not template:
        return False, f"Template '{template_name}' non trouvé"

    champs_manquants = []
    for champ in template["champs_requis"]:
        if champ not in donnees or donnees[champ] is None or donnees[champ] == "":
            champs_manquants.append(champ)

    if champs_manquants:
        return False, f"Champs manquants: {', '.join(champs_manquants)}"

    return True, "OK"
