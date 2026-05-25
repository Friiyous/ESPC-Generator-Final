"""
Application Streamlit - Générateur Documents ESPC
Conforme à la grille ESPC
"""
import streamlit as st
import os
import json
import calendar
import pandas as pd
from datetime import datetime
from groq import Groq
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn

# =============================================================================
# CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Générateur Documents ESPC",
    page_icon="🏥",
    layout="centered"
)

# Configuration de la clé API Groq
import os
from dotenv import load_dotenv

# Déterminer le répertoire racine du projet (fonctionne même dans Streamlit)
if "__file__" in dir():
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
else:
    _BASE_DIR = os.getcwd()

# Charger les variables d'environnement depuis .env (fallback local)
_env_path = os.path.join(_BASE_DIR, '.env')
load_dotenv(_env_path)

# Configuration de la clé API Groq via st.secrets (Streamlit Cloud) ou .env (local)
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    st.warning("🔑 Clé API Groq non configurée. La génération IA sera désactivée.")
    st.info("""
    **Pour configurer:**
    1. Fichier `.env` à la racine : `GROQ_API_KEY=votre_clé`
    2. Redémarre l'application
    """)
else:
    _ = Groq(api_key=GROQ_API_KEY)  # Validation de la clé

# =============================================================================
# CONTEXTE DU CSR NAGNENEFOUN
# =============================================================================

def get_contexte_csr():
    """Génère le contexte du CSR NAGNENEFOUN"""
    contexte = """
CONTEXTE DU CSR NAGNENEFOUN (PORO, District KORHOGO 1):
- Population totale: 34055 habitants
- Infrastructure: Dispensaire, Maternité, Château d'eau
- Activités principales: Consultations, CPN, Accouchements, PEV, Paludisme, VIH, Nutrition, IEC/CCC
- Maladies principales: Paludisme (76%), IRA (19%), Diarrhées (5%)
"""
    return contexte

# =============================================================================
# CHARGEMENT DES TEMPLATES
# =============================================================================

@st.cache_data
def charger_templates():
    """Charge les templates depuis le fichier JSON"""
    try:
        with open("templates.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def sauvegarder_templates(templates):
    """Sauvegarde les templates dans le fichier JSON"""
    with open("templates.json", "w", encoding="utf-8") as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)

templates = charger_templates()

def get_sections_template(doc_key):
    """Retourne les sections d'un template"""
    if templates and doc_key in templates:
        return templates[doc_key]["sections"]
    return []

# =============================================================================
# PROMPTS STRICTS - CONFORMES À LA GRILLE ESPC
# =============================================================================

PROMPTS = {

    "pv_reunion_mensuelle": {
        "system": """Tu es un responsable de centre de santé (CSR) en Côte d'Ivoire. Tu rédiges un PROCÈS-VERBAL DE RÉUNION MENSUELLE conforme à la grille ESPC.

CONTEXTE DU CSR NAGNENEFOUN:
- District: KORHOGO 1 (PORO)
- Population: 34 055 habitants
- Personnel: Infirmiers, Sages-femmes, Aides-soignants, ASC, Filles de salle, Secrétaire, Gardiens
- Fréquence: Réunion mensuelle (tous les mois)

RÈGLES TRÈS IMPORTANTES:
1. Utilise les données réelles du CSR (personnel, statistiques, activités mensuelles)
2. Génère un contenu COMPLET sans placeholders ni [À compléter]
3. N'inclus JAMAIS de section "LISTE DE PRÉSENCE" ou "SIGNATURES" - ces parties sont saisies manuellement
4. Le PV doit contenir un TABLEAU DES DÉLIBÉRATIONS avec 4 colonnes: N° | Point discuté | Décisions prises | Responsable/Délai""",

        "user": """Génère PV RÉUNION MENSUELLE pour {nom_etablissement} - {periode}.

CONTEXTE DU CENTRE:
{contexte}

THÈMES À TRAITER:
{themes}

SECTIONS À INCLURE:
{sections}

## I. OUVERTURE
- Date: __/__/{periode}
- Lieu: Salle de réunion du CSR {nom_etablissement}
- Heure: 08h30
- Président de séance: Chef de Centre
- Secrétaire de séance: Major
- Objet: Réunion mensuelle de {mois} {periode}

## II. MOT D'OUVERTURE
Le Chef de Centre souhaite la bienvenue à tout le personnel et rappelle l'importance de ces réunions mensuelles pour évaluer les activités du service, partager les informations et prendre des décisions collégiales pour l'amélioration de la qualité des soins au CSR {nom_etablissement}.

## III. LECTURE ET ADOPTION DU PV PRÉCÉDENT
Lecture du procès-verbal de la réunion du mois précédent.
- Observations/Suggestions: [RAS]
- Adoption: Le PV est adopté à l'unanimité

## IV. ORDRE DU JOUR
{themes}

## V. DÉLIBÉRATIONS (TABLEAU)

Génère un tableau avec 4 colonnes: N° | Point discuté | Décisions prises | Responsable/Délai
|---|---|---|---
| 1 | [Point 1] | [Décision] | [Responsable] - [Délai] |
| 2 | [Point 2] | [Décision] | [Responsable] - [Délai] |
| 3 | [Point 3] | [Décision] | [Responsable] - [Délai] |

Pour chaque thème de l'ordre du jour, génère un point avec décision et responsable.

## VI. DIVERS
- Questions diverses soulevées par le personnel
- Informations administratives
- Prochaine réunion

## VII. CLÔTURE
- Heure de clôture: 10h30
- Prochaine réunion: __/__/20..
- Le Chef de Centre remercie les participants et lève la séance

Génère le PV complet avec des décisions spécifiques et contextualisées pour {mois} {periode} en lien avec le thème: {themes}."""
    },

    "pv_coges": {
        "system": """Tu es un responsable de centre de santé (CSR) en Côte d'Ivoire. Tu rédiges un PROCÈS-VERBAL DE RÉUNION DU COMITÉ DE GESTION (COGES) conforme à la grille ESPC - Norme 1.02.

CONTEXTE DU CSR NAGNENEFOUN:
- District: KORHOGO 1 (PORO)
- Population: 34 055 habitants
- Fréquence: Réunion trimestrielle (T1-T4)
- Membres COGES: Président, Vice-Président, Secrétaire, Trésorier, Commissaire aux Comptes, Membres

RÈGLES TRÈS IMPORTANTES:
1. Le terme correct est COMITÉ DE GESTION ou COGES - JAMAIS "Conseil de Gestion"
2. Utilise les données réelles du CSR (personnel, statistiques, activités)
3. N'inclus JAMAIS de section "LISTE DE PRÉSENCE" ou "SIGNATURES" - ces parties sont saisies manuellement
4. Inclus un TABLEAU DES DÉLIBÉRATIONS avec 4 colonnes: N° | Point discuté | Décisions prises | Responsable/Délai""",

        "user": """Génère un PROCÈS-VERBAL DE RÉUNION DU COMITÉ DE GESTION (COGES) pour {nom_etablissement} - {periode}.

CONTEXTE DU CENTRE:
{contexte}

THÈMES À TRAITER:
{themes}

SECTIONS À INCLURE:
{sections}

## I. OUVERTURE
- Date: __/__/{periode}
- Lieu: Salle de réunion du CSR {nom_etablissement}
- Heure: 09h00
- Président de séance: [Président du COGES]
- Secrétaire de séance: [Secrétaire du COGES]
- Objet: Réunion trimestrielle du COGES du {trimestre} {periode}

## II. MOT D'OUVERTURE
Le Président du COGES souhaite la bienvenue à tous les membres et remercie le Chef de Centre pour l'organisation. Il rappelle le rôle du COGES dans la gestion participative du centre de santé et l'importance de ces réunions trimestrielles.

## III. LECTURE ET ADOPTION DU PV PRÉCÉDENT
Lecture du procès-verbal de la réunion COGES du trimestre précédent.
- Observations/Suggestions:
- Adoption: Le PV est adopté à l'unanimité

## IV. ORDRE DU JOUR
{themes}

## V. DÉLIBÉRATIONS (TABLEAU)

Génère un tableau avec 4 colonnes: N° | Point discuté | Décisions prises | Responsable/Délai
|---|---|---|---
| 1 | [Point COGES 1] | [Décision] | [Responsable] - [Délai] |
| 2 | [Point COGES 2] | [Décision] | [Responsable] - [Délai] |
| 3 | [Point COGES 3] | [Décision] | [Responsable] - [Délai] |

Points typiques COGES:
- Gestion financière et recettes du centre
- États des dépenses et budget
- État du personnel et des équipements
- Projets de développement du CSR
- Relations avec le District Sanitaire
- Difficultés et recommandations

## VI. DÉCISIONS ADOPTÉES
- Décision N°1: [Résumé de la décision]
- Décision N°2: [Résumé de la décision]
- Décision N°3: [Résumé de la décision]

## VII. QUESTIONS DIVERSES
- Prochaine réunion COGES: [Date]
- Recommandations au Chef de Centre

## VIII. CLÔTURE
- Heure de clôture: 11h00
- Prochaine réunion: __/__/20..
- Le Président remercie les participants et lève la séance

Génère le PV complet adapté au CSR {nom_etablissement} pour le {trimestre} {periode} en lien avec les thèmes COGES."""
    },

    "pv_ag": {
        "system": """Tu es un responsable de centre de santé (CSR) en Côte d'Ivoire. Tu rédiges un PROCÈS-VERBAL D'ASSEMBLÉE GÉNÉRALE conforme à la grille ESPC - Norme 1.03.

CONTEXTE DU CSR NAGNENEFOUN:
- District: KORHOGO 1 (PORO)
- Population: 34 055 habitants
- Fréquence: Assemblée Générale annuelle
- Participants: COGES, Personnel du centre, Représentants de la communauté, Autorités locales

RÈGLES:
1. Utilise les données réelles du CSR
2. N'inclus JAMAIS de section "LISTE DE PRÉSENCE" ou "SIGNATURES" - ces parties sont saisies manuellement
3. Inclus un TABLEAU DES POINTS ABORDÉS avec 4 colonnes: N° | Point discuté | Décisions/Votes | Observations""",

        "user": """Génère un PROCÈS-VERBAL D'ASSEMBLÉE GÉNÉRALE pour {nom_etablissement} - {periode}.

CONTEXTE DU CENTRE:
{contexte}

THÈMES À TRAITER:
{themes}

SECTIONS À INCLURE:
{sections}

## I. OUVERTURE
- Date: __/__/{periode}
- Lieu: CSR {nom_etablissement}
- Heure: 09h00
- Président de séance: Chef de Centre / Président du COGES
- Secrétaire de séance: Major
- Objet: Assemblée Générale Annuelle du CSR {nom_etablissement}

## II. MOT D'OUVERTURE
Le Chef de Centre ouvre l'Assemblée Générale et souhaite la bienvenue à tous les participants (COGES, Personnel, Communauté, Autorités). Il présente le rapport moral de l'année {periode} et remercie les partenaires.

## III. ÉLECTION DU BUREAU DE SÉANCE
- Président de séance: [Élu(e)]
- Secrétaire: [Élu(e)]
- Assesseurs: [Élu(e)s]

## IV. LECTURE ET ADOPTION DU PV PRÉCÉDENT
Lecture du procès-verbal de l'Assemblée Générale de [Année N-1].
- Adoption à l'unanimité

## V. ADOPTION DE L'ORDRE DU JOUR
{themes}

## VI. DÉLIBÉRATIONS ET DÉCISIONS (TABLEAU)

Génère un tableau avec 4 colonnes: N° | Point discuté | Décisions/Votes adoptés | Observations
|---|---|---|---
| 1 | [Point AG 1] | [Décision] | [Obs] |
| 2 | [Point AG 2] | [Décision] | [Obs] |
| 3 | [Point AG 3] | [Décision] | [Obs] |

Points typiques AG annuelle:
- Rapport d'activités de l'année écoulée
- Rapport financier et budget
- Projets et perspectives
- Élection/Renouvellement des membres COGES
- Questions diverses

## VII. RECOMMANDATIONS ADOPTÉES
1. [Recommandation 1]
2. [Recommandation 2]
3. [Recommandation 3]

## VIII. CLÔTURE
- Heure de clôture: 12h00
- Prochaine Assemblée Générale: Année [N+1]
- Le Président remercie les participants et lève la séance

Génère le PV complet adapté au CSR {nom_etablissement} pour l'année {periode}."""
    },

    "rapport_supervision_asc": {
        "system": """Tu es un assistant spécialisé dans les rapports de supervision ASC pour les CSR en Côte d'Ivoire.

RÈGLES:
1. Utilise les données réelles du CSR (3 ASC, villages, activités communautaires)
2. N'inclus JAMAIS de "SIGNATURES" ou "LISTE PRÉSENCE" - ces parties sont saisies manuellement""",

        "user": """Génère RAPPORT SUPERVISION ASC pour {nom_etablissement}.
{contexte}

STRUCTURE (Norme 14.01 - sans SIGNATURES):
I. INFOS GÉNÉRALES
II. PLAN SUPERVISION ANNUEL
III. EFFECTIFS SUPERVISÉS (3 ASC)
IV. LISTE ASC
V. GRILLE SUPERVISION
VI. ACTIVITÉS (sensibilisation, dépistage, référence)
VII. RÉSULTATS
VIII. DISPO MÉDICAMENTS
IX. DIFFICULTÉS
X. RECOMMANDATIONS
XI. TRANSMISSION DISTRICT

Génère un rapport contextualisé."""
    },

    "rapport_plaintes": {
        "system": """Tu es un assistant spécialisé dans les rapports de boîte à suggestions pour CSR en Côte d'Ivoire.
RÈGLES: Génère un contenu COMPLET contextualisé, sans SIGNATURES.""",

        "user": """Génère RAPPORT BOÎTE À SUGGESTIONS pour {nom_etablissement}.
{contexte}

INFORMATIONS:
- Nombre de suggestions: {nb_suggestions}
- Types de suggestions: {types_suggestions}
- Actions menées: {actions}

STRUCTURE DU DOCUMENT:
{sections}
I. CONTEXTE
II. STATISTIQUES
III. TYPES SUGGESTIONS
IV. ACTIONS MENÉES
V. RÉSULTATS
VI. RECOMMANDATIONS

Génère un rapport contextualisé."""
    },

    # =============================================================================
    # FICHE DE POSTE - Templates par catégorie - Conforme Grille ESPC 2.01
    # =============================================================================
    "fiche_poste": {
        "system": """Tu es un responsable des ressources humaines dans un centre de santé (CSR) en Côte d'Ivoire. Tu rédiges une FICHE DE POSTE officielle conforme à la grille ESPC - Norme 2.01 a,b,c.

CONTEXTE DU CSR:
- Établissement: CSR NAGNENEFOUN
- District Sanitaire: KORHOGO 1 (Région Sanitaire du PORO)
- Population desservie: 34 055 habitants
- Infrastructure: Dispensaire, Maternité, Château d'eau

RÈGLES ABSOLUES:
1. Génère un document professionnel officiel avec en-tête administrative complète
2. Adapte le contenu (missions, qualifications, compétences) à la catégorie de personnel choisie
3. Sois précis et réaliste - chaque catégorie a des missions spécifiques
4. N'inclus JAMAIS de zone de signature ou cadre de signature (signé manuellement)
5. La section des missions doit être détaillée avec au moins 5-8 missions concrètes
6. Les qualifications doivent être précises (diplômes, années d'expérience, inscriptions ordinales)
7. Inclus les relations fonctionnelles internes et externes adaptées à chaque catégorie""",
        "user": """Génère une FICHE DE POSTE officielle pour {nom_etablissement}.

----------------------------------------------------
INFORMATIONS GÉNÉRALES
----------------------------------------------------
CATÉGORIE: {categorie_poste}
TITRE DU POSTE: {titre_poste}
NOM DU TITULAIRE: {nom_titulaire}
SUPÉRIEUR HIÉRARCHIQUE: {superieur}
RÉGIME DE TRAVAIL: {regime_travail}

CONTEXTE DU CENTRE:
{contexte}

----------------------------------------------------
STRUCTURE À GÉNÉRER (conserver impérativement):
----------------------------------------------------
{sections}

## I. IDENTIFICATION DU POSTE
- Établissement: {nom_etablissement}
- Intitulé du poste: {titre_poste}
- Catégorie: {categorie_poste}
- Supérieur hiérarchique direct: {superieur}
- Lieu d'affectation: CSR NAGNENEFOUN, District Sanitaire de KORHOGO 1, Région Sanitaire du PORO
- Régime de travail: {regime_travail}

## II. MISSIONS PRINCIPALES
{missions_poste}

Rédige chaque mission sous forme d'un paragraphe détaillé expliquant concrètement ce que la personne fait au quotidien. Minimum 7 missions détaillées.

## III. QUALIFICATIONS REQUISES
{qualifications_poste}

Détaille par catégorie :
- Formation académique requise (diplôme précis)
- Inscription ordinale / autorisation d'exercer
- Expérience professionnelle minimale
- Formations complémentaires souhaitables

## IV. COMPÉTENCES ET APTITUDES
{competences_poste}

- Compétences techniques spécifiques
- Compétences relationnelles
- Aptitudes personnelles (rigueur, discrétion, etc.)
- Capacités d'adaptation et d'initiative

## V. RESPONSABILITÉS
{responsabilites_poste}

Détail des responsabilités par domaine : clinique, administratif, managérial, formation

## VI. MOYENS ET RESSOURCES MISES À DISPOSITION
{moyens_poste}

Équipement, matériel, locaux, ressources humaines encadrées

## VII. RELATIONS FONCTIONNELLES
- Interne: Direction du centre, Personnel soignant et administratif, COGES
- Externe: District Sanitaire de KORHOGO 1, Communauté, Partenaires techniques (PSI, UNICEF, etc.)

## VIII. OBSERVATIONS PARTICULIÈRES
- Conditions d'exercice spécifiques
- Astreintes et gardes (si applicable)
- Formation continue obligatoire

Génère la fiche de poste complète et professionnelle. Sois TRÈS DÉTAILLÉ et précis dans chaque section."""
    },

        # =============================================================================
    # FICHE DE NOMINATION - 12 types conformes Grille ESPC
    # =============================================================================
    "fiche_nomination": {
        "system": """Tu es un responsable administratif de centre de santé (CSR) en Côte d'Ivoire. Tu rédiges des documents administratifs officiels.

FORMAT OFFICIEL (EN-TÊTE OBLIGATOIRE):
RÉPUBLIQUE DE CÔTE D'IVOIRE
Union – Discipline – Travail

MINISTÈRE DE LA SANTÉ, DE L'HYGIÈNE PUBLIQUE ET DE LA COUVERTURE MALADIE UNIVERSELLE
RÉGION SANITAIRE DU PORO
DISTRICT SANITAIRE DE KORHOGO 1

CSR NAGNENEFOUN

CONTEXTE GÉNÉRAL:
- District: KORHOGO 1 (PORO)
- Population: 34 055 habitants
- Infrastructure: Dispensaire, Maternité, Château d'eau

RÈGLES ABSOLUES:
1. L'en-tête républicaine officielle DOIT être incluse
2. Adapte le format (Note de service / Arrêté / Fiche de poste / Liste) selon le TYPE DE DOCUMENT demandé
3. Génère un document officiel complet et réaliste
4. N'inclus JAMAIS de zone de signature (les originaux sont signés manuellement)
5. Le document doit être PRÊT À IMPRIMER sur papier officiel
6. Pour les "Notes de service" : inclure un cachet "Vu et approuvé" sans cadre de signature
7. Pour les "Arrêtés" : format juridique avec "Considérant que..." et articles
8. Pour les "Fiches de poste signées" : format fiche technique détaillée""",
        "user": """Génère un DOCUMENT ADMINISTRATIF OFFICIEL pour {nom_etablissement}.

----------------------------------------------------
PARAMÈTRES DU DOCUMENT
----------------------------------------------------
TYPE DE DOCUMENT: {type_nomination}
OBJET / FONCTION: {objet_nomination}
NORME ESPC: {reference_norme}
SIGNATAIRE REQUIS: {signataire}
NOM DU BÉNÉFICIAIRE: {nom_beneficiaire}
FONCTION DU BÉNÉFICIAIRE: {fonction_beneficiaire}
DATE PRISE D'EFFET: {date_effet}
NUMÉRO D'ORDRE: {numero_ordre}

CONTEXTE DU CENTRE:
{contexte}

----------------------------------------------------
STRUCTURE À GÉNÉRER:
----------------------------------------------------
{sections}

I. EN-TÊTE OFFICIEL
RÉPUBLIQUE DE CÔTE D'IVOIRE
Union – Discipline – Travail
MINISTÈRE DE LA SANTÉ, DE L'HYGIÈNE PUBLIQUE ET DE LA COUVERTURE MALADIE UNIVERSELLE
RÉGION SANITAIRE DU PORO
DISTRICT SANITAIRE DE KORHOGO 1
{nom_etablissement}
---

{type_nomination} N° {numero_ordre}

II. PRÉAMBULE / VU
(Inclure les textes légaux : Code de la santé publique, Loi N°... portant organisation sanitaire, etc.)

III. DISPOSITIONS / DÉSIGNATION
- Article 1: {nom_beneficiaire} est nommé(e) en qualité de {fonction_beneficiaire}
- Article 2: {objet_nomination}
- Missions et attributions détaillées

IV. ATTRIBUTIONS / MISSIONS DÉTAILLÉES
(Description complète des missions confiées au bénéficiaire)

V. DISPOSITIONS FINALES
- SIGNATAIRE: {signataire}
- DATE D'EFFET: {date_effet}
- DIFFUSION: {nom_etablissement}, District Sanitaire KORHOGO 1, Intéressé(e), Archives

---
Cachet "Vu et approuvé" - Signature manuelle requise

Génère le document officiel complet, prêt à imprimer. Adapte le style et le format selon le TYPE DE DOCUMENT."""
    },

    "programme_reunions_trimestrielles": {
        "system": """Tu es un responsable de centre de santé (CSR) en Côte d'Ivoire. Tu génères un PROGRAMME DE RÉUNIONS TRIMESTRIELLES stratégique.

CONTEXTE DU CSR NAGNENEFOUN:
- District: KORHOGO 1 (PORO)
- Population: 34 055 habitants
- Infrastructure: Dispensaire, Maternité, Château d'eau
- Activités: Consultations, CPN, Accouchements, PEV, Paludisme, VIH, Nutrition, IEC/CCC
- Maladies principales: Paludisme (76%), IRA (19%), Diarrhées (5%)

FORMAT OBLIGATOIRE DU TABLEAU (markdown):
Génère le calendrier sous forme de tableau markdown avec 5 colonnes et 4 lignes (T1 à T4).
Le séparateur doit être: |---|---|----|----|----|
Chaque cellule doit contenir du texte EXPLICITE, précis et développé (pas de simples listes à puces).""",
        "user": """Génère PROGRAMME RÉUNIONS TRIMESTRIELLES pour {nom_etablissement} - {periode}.

CONTEXTE DU CENTRE:
{contexte}

SECTIONS À INCLURE:
{sections}

## I. INFORMATIONS GÉNÉRALES
- Établissement: {nom_etablissement}
- Année: {periode}
- Population: 34 055 habitants
- District: KORHOGO 1 (PORO)

## II. CALENDRIER STRATÉGIQUE DES RÉUNIONS TRIMESTRIELLES

Génère un tableau markdown avec 5 colonnes: Trimestre | Mois | Thème de la réunion | Activités clés à mener | Responsable

Exemple de structure (à remplir avec du contenu détaillé et contextualisé pour le CSR):
| Trimestre | Mois | Thème de la réunion | Activités clés à mener | Responsable |
|---|---|---|---|---|
| T1 | Janvier - Mars | Planification annuelle et stratégies PEV | Définir le plan d'action annuel 2026, organiser la campagne de vaccination PEV de routine, planifier les séances de CPN et accouchements, budgétiser les intrants et consommables, former le personnel sur les nouveaux protocoles paludisme | Chef de Centre, Major, Équipe encadrement |
| T2 | Avril - Juin | Suivi des activités et campagne paludisme | Évaluer les indicateurs CPN et accouchements du 1er trimestre, organiser la campagne de chimio-prévention du paludisme saisonnier (CPS), assurer le PEV de rattrapage des enfants perdus de vue, intensifier les séances IEC/CCC sur le paludisme et la nutrition | IDE, Sage-femme, ASC, Chargé PEV |
| T3 | Juillet - Septembre | Nutrition et surveillance épidémiologique | Analyser les données nutritionnelles et les indicateurs VIH/PTME, renforcer la surveillance des IRA et diarrhées (saison des pluies), organiser les séances de dépistage VIH et malnutrition, évaluer l'état des stocks de médicaments et intrants | Infirmier, Chargé VIH, Nutritionniste, Pharmacien |
| T4 | Octobre - Décembre | Évaluation annuelle et perspectives N+1 | Réaliser le bilan annuel des activités et indicateurs PEP/DBS, élaborer le rapport d'activités annuel, préparer la planification opérationnelle N+1, évaluer la performance du personnel et les besoins en formation, organiser la réunion COGES bilan | Chef de Centre, COGES, Toute l'équipe |

## III. OBJECTIFS STRATÉGIQUES PAR TRIMESTRE
Décrire en 2-3 phrases par trimestre les objectifs poursuivis.

## IV. MODALITÉS D'AFFICHAGE
- Lieu d'affichage: Tableau d'affichage du centre, Salle de réunion du personnel
- Période d'affichage: De janvier à décembre {periode}
- Responsable de l'affichage: Chef de Centre adjoint

Génère le tableau ci-dessus avec le contenu détaillé adapté au CSR NAGNENEFOUN."""
    },

    "calendrier_nettoyage": {
        "system": """Tu es un responsable de centre de santé (CSR) en Côte d'Ivoire. Tu génères un CALENDRIER DE NETTOYAGE conforme à la Norme 6.01 de la grille ESPC.

CONTEXTE DU CSR NAGNENEFOUN:
- District: KORHOGO 1 (PORO)
- Infrastructure: Dispensaire, Maternité, Château d'eau, Hall d'attente, Toilettes, Cour
- Activités: Consultations, CPN, Accouchements, PEV, Paludisme, VIH, Nutrition

FORMAT OBLIGATOIRE:
- Génère le calendrier sous forme de TABLEAU avec minimum 5 colonnes
- Le séparateur doit être: |---|---|---|---|---|
- Chaque cellule doit contenir des informations précises, explicites et détaillées""",
        "user": """Génère CALENDRIER DE NETTOYAGE pour {nom_etablissement} - {periode}.

CONTEXTE DU CENTRE:
{contexte}

SECTIONS À INCLURE:
{sections}

## I. PRÉSENTATION
Le présent calendrier de nettoyage est établi conformément à la Norme 6.01 de la grille ESPC. Il définit les tâches de nettoyage, les fréquences, les responsables et les produits à utiliser pour chaque zone du CSR {nom_etablissement}.

Établissement: {nom_etablissement}
Période: {periode}

## II. ZONES À NETTOYER
Les zones suivantes sont identifiées au CSR: {zones}

Fréquences applicables: {frequences}

## III. CALENDRIER DE NETTOYAGE (TABLEAU)

Génère un tableau avec 5 colonnes: Zone | Fréquence | Activités de nettoyage détaillées | Responsable | Produits/Matériel

Le tableau doit être complet et couvrir:

| Zone | Fréquence | Activités de nettoyage détaillées | Responsable | Produits/Matériel |
|---|---|---|---|---|
| Salle de consultation | Quotidien | Nettoyer et désinfecter la table d'examen après chaque patient, laver le sol à l'eau de javel diluée, dépoussiérer les surfaces de travail (bureau, armoires), vider et nettoyer la poubelle médicale, vérifier la disponibilité du savon et de l'eau | Infirmier / Aide-soignant | Eau de javel 0.5%, Savon liquide, Gants ménagers, Chiffons, Balai, Poubelle |
| Salle de consultation | Hebdomadaire | Laver les murs et les vitres, désinfecter les poignées de porte et interrupteurs, nettoyer les luminaires, vérifier l'état du matériel et signaler les dégradations, faire l'inventaire des produits d'entretien, aérer la salle | Aide-soignant | Détergent, Éponge, Seau, Brosse, Gants |
| Maternité | Quotidien | Nettoyer et désinfecter la table d'accouchement après chaque usage, laver le sol avec détergent puis eau de javel, nettoyer les incubateurs et berceaux, vider les poubelles DASRI, vérifier les kits d'accouchement, approvisionner en eau potable | Sage-femme / Aide-soignant | Eau de javel 0.5%, Savon antiseptique, Gants stériles, Poubelle DASRI, Chiffons |
| Maternité | Hebdomadaire | Nettoyer les murs et les plafonds, laver les rideaux et les linges, désinfecter le matériel d'accouchement, vérifier la stérilisation du matériel, nettoyer les rangements et tiroirs, contrôler la chaîne de froid des vaccins | Sage-femme | Autoclave, Détergent, Gants, Brosse, Savon |
| Hall d'attente | Quotidien | Balayer et laver le sol, nettoyer les bancs et chaises, vider les poubelles, vérifier la propreté des affiches et supports IEC/CCC, approvisionner le point d'eau | Aide-soignant / Planton | Balai, Savon, Seau, Eau de javel, Poubelle |
| Hall d'attente | Hebdomadaire | Laver les murs, vitres et portes, désinfecter les rampes et poignées, nettoyer les ventilateurs et luminaires, ranger et organiser la documentation IEC, inspecter l'état de la toiture | Aide-soignant | Détergent, Éponge, Savon, Gants |
| Toilettes | Quotidien | Nettoyer et désinfecter les cuvettes et urinoirs, laver le sol et les murs carrelés, approvisionner en eau et savon, vider les poubelles, vérifier le bon fonctionnement des chasses d'eau, désodoriser | Aide-soignant / Planton | Acide chlorhydrique dilué, Eau de javel, Balai-brosse, Gants, Désodorisant |
| Toilettes | Hebdomadaire | Nettoyer les plafonds et les aérations, détartrer les canalisations, inspecter l'état des installations sanitaires, signaler les fuites et réparations nécessaires, désinfecter les poignées de porte | Aide-soignant | Détartrant, Brosse métallique, Gants, Éponge |
| Cour / Extérieur | Quotidien | Balayer la cour et les abords, ramasser les déchets solides, vider les poubelles extérieures, arroser les espaces verts, vérifier l'état du château d'eau et de la clôture | Planton / Gardien | Balai, Brouette, Râteau, Tuyau d'arrosage, Poubelle |
| Cour / Extérieur | Hebdomadaire | Désherber les allées et abords, nettoyer le caniveau et les regards, laver les murs extérieurs, vérifier le système d'évacuation des eaux usées, contrôler l'état des fosses septiques | Planton / Gardien | Désherbant, Pelle, Pioche, Gants |

## IV. PLAN DE NETTOYAGE QUOTIDIEN DU SOIR (FILLES DE SALLE)

Personnel dédié: Filles de salle (agents d'entretien) - passages chaque soir

Génère un tableau avec 5 colonnes: Zone | Horaire | Tâches de nettoyage du soir | Responsable | Durée

| Zone | Horaire | Tâches de nettoyage du soir | Responsable | Durée |
|---|---|---|---|---|
| Salle de consultation | 17h00 - 17h30 | Balayer et laver le sol à grande eau, désinfecter la table d'examen, vider la poubelle médicale, nettoyer le bureau et les armoires, vérifier les stocks de savon et désinfectant, passer la serpillière avec eau de javel diluée | Fille de salle | 30 min |
| Maternité | 17h30 - 18h15 | Nettoyer et désinfecter la table d'accouchement, laver le sol avec détergent puis eau de javel, désinfecter les incubateurs et berceaux, vider les poubelles DASRI, nettoyer les toilettes de la maternité, approvisionner en eau potable et savon liquide, ranger le linge propre | Fille de salle | 45 min |
| Hall d'attente | 18h15 - 18h45 | Balayer et laver le sol, nettoyer les bancs et chaises avec désinfectant, vider les poubelles, dépoussiérer les affiches IEC/CCC, vérifier la propreté du point d'eau, nettoyer les portes et poignées | Fille de salle | 30 min |
| Toilettes (patients) | 18h45 - 19h15 | Nettoyer et désinfecter les cuvettes et urinoirs avec détergent et désinfectant, laver le sol et les murs carrelés, approvisionner en eau et savon, vider les poubelles, désodoriser, vérifier l'état des chasses d'eau et signaler les fuites | Fille de salle | 30 min |
| Toilettes (personnel) | 19h15 - 19h30 | Nettoyer et désinfecter la cuvette et le lavabo, laver le sol, approvisionner en savon et papier hygiénique, vider la poubelle, désodoriser | Fille de salle | 15 min |
| Bureau Chef de Centre | 19h30 - 19h45 | Dépoussiérer le bureau et les étagères, nettoyer le sol, vider la corbeille, aérer la pièce | Fille de salle | 15 min |
| Pharmacie / Magasin | 19h45 - 20h00 | Balayer le sol, dépoussiérer les étagères et rangements, vérifier l'état des murs et plafonds, signaler tout problème d'humidité ou d'infiltration | Fille de salle | 15 min |
| Cour / Abords | 20h00 - 20h30 | Balayer la cour et le parking, ramasser et évacuer les déchets solides, vérifier la propreté du château d'eau et des abords, fermer les portails et vérifier la clôture | Fille de salle / Gardien | 30 min |

## V. OBSERVATIONS
- Les produits d'entretien doivent être stockés dans un local fermé et identifié
- Le personnel doit porter des gants et des bottes pour les tâches de nettoyage
- Les fiches de suivi de nettoyage doivent être signées chaque jour
- La vérification mensuelle est assurée par le Major / Chef de Centre
- Les filles de salle sont tenues de signer la fiche de présence quotidienne chaque soir après le nettoyage

## VI. AFFICHAGE
- Lieu d'affichage: Dans chaque zone concernée et au tableau d'affichage central
- Responsable du suivi: Major du centre
- Période d'affichage: {periode} (renouvelé chaque année)

Génère le calendrier complet avec le tableau détaillé ci-dessus adapté au CSR NAGNENEFOUN."""
    },

    "calendrier_reunions_mensuelles": {
        "system": """Tu es un responsable de centre de santé (CSR) en Côte d'Ivoire. Tu génères un CALENDRIER DE RÉUNIONS MENSUELLES.

CONTEXTE DU CSR NAGNENEFOUN:
- District: KORHOGO 1 (PORO)
- Population: 34 055 habitants
- Infrastructure: Dispensaire, Maternité, Château d'eau
- Activités: Consultations, CPN, Accouchements, PEV, Paludisme, VIH, Nutrition, IEC/CCC
- Maladies principales: Paludisme (76%), IRA (19%), Diarrhées (5%)

FORMAT OBLIGATOIRE DU TABLEAU:
Génère le calendrier sous forme de tableau markdown avec 4 colonnes et 12 lignes (une par mois).
Le séparateur doit être: |---|---|---|---|
Chaque cellule doit contenir du texte EXPLICITE, précis et développé pour le mois concerné.""",
        "user": """Génère CALENDRIER RÉUNIONS MENSUELLES pour {nom_etablissement} - {periode}.

CONTEXTE DU CENTRE:
{contexte}

SECTIONS À INCLURE:
{sections}

## I. INFORMATIONS GÉNÉRALES
- Établissement: {nom_etablissement}
- Année: {periode}

## II. CALENDRIER DES RÉUNIONS MENSUELLES

Génère un tableau avec 4 colonnes: Mois | Thème de la réunion | Activités clés à mener | Responsable

Pour chaque mois, le contenu doit être contextualisé au CSR NAGNENEFOUN (paludisme 76%, PEV, CPN/accouchements, VIH, nutrition, etc.).

Exemple de structure du tableau (à adapter avec le vrai contexte du CSR):
| Mois | Thème de la réunion | Activités clés à mener | Responsable |
|---|---|---|---|
| Janvier | Planification opérationnelle annuelle et stratégies PEV | Élaborer le plan d'action 2026, organiser les stratégies avancées PEV, planifier les CPN et accouchements du 1er trimestre, définir le calendrier des séances IEC/CCC | Chef de Centre, Major, Équipe |
| Février | Campagne paludisme et suivi des indicateurs | Analyser les indicateurs de morbidité paludisme (76% des cas), organiser la distribution des MII, renforcer le dépistage et traitement rapide du paludisme, superviser les ASC dans les villages | Infirmier, ASC, Chargé Paludisme |
| Mars | Gestion des stocks et approvisionnement en intrants | Évaluer l'état des stocks de médicaments (antipaludiques, ARV, vaccins), passer les commandes au district, vérifier la chaîne de froid et la conservation des vaccins | Pharmacien, Major |
| Avril | Santé maternelle et CPN/Accouchements | Évaluer les indicateurs CPN (consultations prénatales), analyser les données accouchements, renforcer la PTME et le dépistage VIH chez les femmes enceintes, organiser les séances de planification familiale | Sage-femme, Chargé VIH |
| Mai | Campagne CPS et activités PEV de rattrapage | Organiser la chimio-prévention du paludisme saisonnier (CPS), réaliser le PEV de rattrapage des enfants perdus de vue, intensifier les consultations curatives IRA (19%) et diarrhées (5%) | IDE, Chargé PEV, ASC |
| Juin | Surveillance épidémiologique et hygiène | Analyser les données épidémiologiques, renforcer la surveillance des maladies à potentiel épidémique, évaluer l'hygiène et l'assainissement du centre, planifier les activités de désinfection | Chef de Centre, Major, Équipe |
| Juillet | Nutrition et prise en charge des cas de malnutrition | Évaluer les indicateurs nutritionnels, organiser le dépistage de la malnutrition chez les enfants, renforcer les séances d'éducation nutritionnelle, coordonner avec le programme nutrition | Infirmier, Nutritionniste, ASC |
| Août | VIH/PTME et activités communautaires | Analyser les indicateurs VIH (dépistage, mise sous ARV), évaluer la PTME chez les femmes enceintes, superviser les activités des ASC dans les aires sanitaires, planifier les séances de sensibilisation | Chargé VIH, Sage-femme, ASC |
| Septembre | Gestion des ressources et formation du personnel | Évaluer les besoins en formation continue, organiser une séance de recyclage sur les protocoles, vérifier les équipements et infrastructures, planifier les réparations/maintenance | Chef de Centre, Major |
| Octobre | Campagne PEV intensifiée et IEC/CCC | Organiser la campagne de vaccination de masse, intensifier les séances IEC/CCC sur le paludisme et le VIH, réaliser les consultations mobiles dans les villages reculés | Chargé PEV, IDE, ASC |
| Novembre | Évaluation à mi-parcours et ajustements | Faire le point sur les indicateurs PEP/DBS, évaluer l'atteinte des objectifs, ajuster les stratégies pour le dernier trimestre, préparer les rapports d'activités | Chef de Centre, Toute l'équipe |
| Décembre | Bilan annuel et perspectives N+1 | Élaborer le rapport annuel d'activités, présenter les résultats au COGES, planifier les activités de l'année N+1, organiser la réunion bilan avec le personnel | Chef de Centre, COGES, Toute l'équipe |

## III. OBSERVATIONS
- Fréquence des réunions: 1 réunion par mois
- Durée recommandée: 2h
- Lieu: Salle de réunion du CSR NAGNENEFOUN
- Participants: Personnel du centre, ASC (selon ordre du jour), COGES (si nécessaire)

## IV. AFFICHAGE
- Lieu d'affichage: Tableau d'affichage du centre, Salle de réunion
- Période d'affichage: De janvier à décembre {periode}
- Responsable: Chef de Centre

Génère le tableau ci-dessus avec le contenu détaillé adapté au CSR NAGNENEFOUN."""
    },

    "grille_supervision_asc": {
        "system": """Tu es un superviseur de centre de santé (CSR) en Côte d'Ivoire. Tu génères une GRILLE DE SUPERVISION ASC conforme à la grille ESPC.

CONTEXTE DU CSR NAGNENEFOUN:
- District: KORHOGO 1 (PORO)
- Population: 34 055 habitants
- Activités ASC: Sensibilisation communautaire, Dépistage paludisme, Référence des cas, Causeries éducatives, Suivi des patients perdus de vue
- Maladies principales: Paludisme (76%), IRA (19%), Diarrhées (5%)

RÈGLE ABSOLUE: Génère un TABLEAU structuré avec colonnes, notation sur 3 niveaux (A=Bon, B=Moyen, C=Faible) et observations.""",
        "user": """Génère GRILLE SUPERVISION ASC pour {nom_etablissement} - {periode}.

CONTEXTE DU CENTRE:
{contexte}

SECTIONS À INCLURE:
{sections}

## I. INFORMATIONS GÉNÉRALES
- Établissement: {nom_etablissement}
- Période: {periode}
- District: KORHOGO 1 (PORO)
- Population: 34 055 habitants
- ASC supervisé: [Nom et prénom(s) de l'ASC]
- Village/Aire sanitaire: [Nom du village]
- Date de supervision: [Date]
- Superviseur: Chef de Centre / Major / Infirmier superviseur

## II. CRITÈRES DE SUPERVISION (TABLEAU)

Génère un tableau d'évaluation avec 5 colonnes: Critère | Indicateurs évalués | Note (A/B/C) | Observations | Actions recommandées

Le tableau doit couvrir les critères suivants avec des indicateurs précis:

| Critère | Indicateurs évalués | Note (A/B/C) | Observations | Actions recommandées |
|---|---|---|---|---|
| 1. Accueil et relation communautaire | Qualité de l'accueil des patients, Tenue et présentation de l'ASC, Discrétion et confidentialité, Respect des heures de travail, Relation avec les relais communautaires | A B C | (observations détaillées) | (actions concrètes) |
| 2. Sensibilisation et IEC/CCC | Organisation des causeries éducatives, Thèmes abordés (paludisme, VIH, nutrition, hygiène), Utilisation des supports IEC, Tenue de registre des séances, Participation communautaire | A B C | (observations détaillées) | (actions concrètes) |
| 3. Dépistage et prise en charge paludisme | Utilisation des TDR paludisme, Traitement correct des cas simples, Application du protocole national, Gestion des cas graves (référence), Tenue du registre paludisme | A B C | (observations détaillées) | (actions concrètes) |
| 4. Référence des cas vers le CSR | Identification des cas à référer (paludisme grave, malnutrition, complications grossesse), Remplissage de la fiche de référence, Suivi des patients référés, Contre-référence du CSR, Taux de référence | A B C | (observations détaillées) | (actions concrètes) |
| 5. Documentation et rapports | Tenue correcte des registres (consultations, TDR, références), Remplissage des rapports mensuels, Transmission des données au CSR, Archivage des documents, Utilisation des fiches de suivi | A B C | (observations détaillées) | (actions concrètes) |
| 6. Gestion des intrants et médicaments | Gestion des stocks TDR et antipaludiques, Conservation des médicaments (chaleur, humidité), Tenue de la fiche de stock, Gestion des périmés, Mouvement des intrants | A B C | (observations détaillées) | (actions concrètes) |
| 7. Hygiène et salubrité du poste | Propreté du poste de santé/ASC, Gestion des déchets biomédicaux, Hygiène des mains, État du matériel, Disponibilité de l'eau et du savon | A B C | (observations détaillées) | (actions concrètes) |
| 8. Participation aux activités du CSR | Présence aux réunions mensuelles, Participation aux campagnes (PEV, CPS), Collaboration avec le personnel du centre, Participation aux séances de démonstration, Implication dans les enquêtes | A B C | (observations détaillées) | (actions concrètes) |

## III. ÉVALUATION GLOBALE
- Total des A: /8
- Total des B: /8
- Total des C: /8
- Appréciation générale: Satisfaisante / Moyenne / Insuffisante
- Décision: Poursuite / Supervision renforcée / Avertissement / Remplacement

## IV. OBSERVATIONS ET RECOMMANDATIONS
- Points forts de l'ASC:
- Points à améliorer:
- Recommandations du superviseur:
- Date de la prochaine supervision:

## V. SIGNATURES
- Signature de l'ASC: ____________________
- Signature du Superviseur: ____________________
- Date: ____/____/______

Génère la grille complète avec le tableau d'évaluation détaillé, les notes et les rubriques à remplir."""
    },

    "liste_coges": {
        "system": """Tu es un responsable de centre de santé (CSR) en Côte d'Ivoire. Tu génères une LISTE DU PERSONNEL COGES conforme au format grille ESPC, prête à imprimer et afficher.

CONTEXTE CSR NAGNENEFOUN:
- District: KORHOGO 1 (PORO)
- Population: 34 055 habitants

FORMAT: Génère un tableau structuré avec 4 colonnes: N° | Nom & Prénoms | Fonction au COGES | Contacts/Téléphone""",
        "user": """Génère LISTE PERSONNEL COGES pour {nom_etablissement} - {periode}.

CONTEXTE DU CENTRE:
{contexte}

SECTIONS À INCLURE:
{sections}

## I. EN-TÊTE OFFICIEL
RÉPUBLIQUE DE CÔTE D'IVOIRE
Union – Discipline – Travail
MINISTÈRE DE LA SANTÉ, DE L'HYGIÈNE PUBLIQUE ET DE LA COUVERTURE MALADIE UNIVERSELLE
RÉGION SANITAIRE DU PORO
DISTRICT SANITAIRE DE KORHOGO 1
{nom_etablissement}

## II. LISTE DU PERSONNEL COGES (TABLEAU)

Génère un tableau avec 4 colonnes: N° | Nom & Prénoms | Fonction au COGES | Contacts/Téléphone

Le tableau doit reprendre les membres ci-dessous avec leurs informations complètes:
{membres}

Colonne par colonne, voici ce qui doit figurer:
- N°: Numérotation de 1 à N
- Nom & Prénoms: Nom complet du membre
- Fonction au COGES: Président, Vice-Président, Secrétaire, Trésorier, Commissaire aux Comptes, Membre
- Contacts/Téléphone: Numéro de téléphone mobile

## III. RÉCAPITULATIF
- Nombre total de membres: 
- Nombre d'hommes: 
- Nombre de femmes:
- Date de mise en place: Janvier {periode}
- Durée du mandat: 2 ans renouvelable

## IV. CONTACTS UTILES
- Président: [Nom] - Tél: [numéro]
- Vice-Président: [Nom] - Tél: [numéro]
- Secrétaire: [Nom] - Tél: [numéro]
- Trésorier: [Nom] - Tél: [numéro]
- Point focal CSR: Chef de Centre CSR NAGNENEFOUN - Tél: [numéro]

## V. OBSERVATIONS

## VI. APPROBATION
- Vu et approuvé par le Chef de Centre:
- Date: ____/____/{periode}
- Cachet et signature:

Génère la liste complète avec le tableau détaillé, prête à l'emploi, avec les mentions officielles de la République de Côte d'Ivoire."""
    },

    "plan_action_infections_nosocomiales": {
        "system": """Tu es un responsable de centre de santé (CSR) en Côte d'Ivoire. Tu génères un PLAN D'ACTION CONTRE LES INFECTIONS NOSOCOMIALES conforme à la grille ESPC.

CONTEXTE DU CSR NAGNENEFOUN:
- District: KORHOGO 1 (PORO)
- Population: 34 055 habitants
- Infrastructure: Dispensaire, Maternité, Château d'eau
- Activités médicales: Consultations curatives, CPN, Accouchements, PEV, Chirurgie mineure, Soins infirmiers

FORMAT OBLIGATOIRE:
- Génère le plan sous forme de TABLEAU avec 6 colonnes
- Le séparateur doit être: |---|---|---|---|---|---|
- Chaque cellule doit contenir du texte EXPLICITE, précis et contextualisé""",
        "user": """Génère PLAN D'ACTION INFECTIONS NOSOCOMIALES pour {nom_etablissement} - {periode}.

CONTEXTE DU CENTRE:
{contexte}

SECTIONS À INCLURE:
{sections}

## I. CONTEXTE ET JUSTIFICATION
Les infections nosocomiales constituent un problème majeur de santé publique dans les centres de santé. Le présent plan d'action vise à prévenir et contrôler les infections associées aux soins au CSR {nom_etablissement}.

Établissement: {nom_etablissement}
Période: {periode}
District: KORHOGO 1 (PORO)
Population couverte: 34 055 habitants

Domaines d'action: {activites}

## II. OBJECTIFS
- Objectif général: Réduire l'incidence des infections nosocomiales de 80% au CSR NAGNENEFOUN
- Objectifs spécifiques:
  1. Renforcer les pratiques d'hygiène des mains du personnel
  2. Assurer la désinfection et la stérilisation du matériel médical
  3. Améliorer la gestion des déchets biomédicaux
  4. Former le personnel sur les protocoles de prévention des infections

## III. PLAN D'ACTION DÉTAILLÉ (TABLEAU)

Génère un tableau avec 6 colonnes: N° | Domaine d'action | Activités spécifiques | Responsable | Périodicité | Indicateur de suivi

Le tableau doit être complet et couvrir tous les aspects:

| N° | Domaine d'action | Activités spécifiques | Responsable | Périodicité | Indicateur de suivi |
|---|---|---|---|---|---|
| 1 | Hygiène des mains | Former tout le personnel sur les 5 moments du lavage des mains selon l'OMS, installer des points de lavage avec savon liquide et essuie-mains à usage unique dans chaque salle de soins, organiser des séances de démonstration pratique du lavage des mains au savon et à la solution hydro-alcoolique, afficher les protocoles de lavage des mains dans chaque zone de soins, évaluer mensuellement la conformité du lavage des mains par observation directe | Major, Infirmier hygiéniste | Trimestrielle | % de personnel formé, Nombre de points de lavage fonctionnels, Taux de conformité aux 5 moments |
| 2 | Désinfection et stérilisation | Établir un protocole écrit de désinfection du matériel médical (table d'examen, spéculums, pinces), organiser la stérilisation à l'autoclave des instruments réutilisables (boîtes d'accouchement, instruments chirurgicaux), contrôler mensuellement l'efficacité de la stérilisation avec des tests biologiques, désinfecter les surfaces et le matériel entre chaque patient, remplacer le matériel défectueux et les gants troués | Sage-femme, Infirmier major | Hebdomadaire | % de matériel stérilisé conforme, Nombre de protocoles affichés, Registre de stérilisation tenu à jour |
| 3 | Gestion des déchets biomédicaux | Mettre en place un système de tri des déchets (boîtes jaunes DASRI, poubelles noires ordinaires), former le personnel sur le tri et l'élimination des déchets biomédicaux conformément à la réglementation nationale, organiser l'incinération ou l'enlèvement des déchets DASRI par le district, tenir un registre de collecte et d'évacuation des déchets, approvisionner en boîtes de sécurité et sacs plastiques de couleur | Major, Aide-soignant, Planton | Quotidienne | % de déchets correctement triés, Nombre de boîtes de sécurité disponibles, Registre d'évacuation rempli |
| 4 | Hygiène de l'environnement | Assurer le nettoyage quotidien des salles de soins et de la maternité avec de l'eau de javel diluée à 0.5%, désinfecter les surfaces (poignées de porte, rampes, interrupteurs) avec un détergent-désinfectant, organiser la désinfection hebdomadaire des murs, plafonds et vitres, contrôler la qualité de l'eau du château d'eau et des points d'utilisation, entretenir les installations sanitaires et la plomberie | Aide-soignant, Fille de salle, Gardien | Quotidienne / Hebdomadaire | Fiche de suivi de nettoyage signée, Résultats analyse eau, Nombre de zones conformes |
| 5 | Précautions standard et isolement | Établir et diffuser les précautions standard pour tous les soins (port de gants, masque, blouse), organiser la mise en isolement des patients suspects d'infection contagieuse, approvisionner en équipements de protection individuelle (EPI) : gants, masques, charlottes, sur-blouses, tabliers, former le personnel à l'utilisation correcte des EPI, gérer les accidents d'exposition au sang (AES) | Chef de Centre, Major | Continue | % de soignants utilisant correctement les EPI, Nombre d'AES déclarés, Stock d'EPI disponible |
| 6 | Surveillance des infections | Mettre en place un registre de suivi des infections nosocomiales, notifier et investiguer tout cas suspect d'infection post-opératoire ou post-partum, analyser mensuellement les données de surveillance, organiser une réunion trimestrielle du comité de lutte contre les infections, élaborer un rapport trimestriel sur les infections nosocomiales | Chef de Centre, Major | Trimestrielle | Nombre d'infections notifiées, Taux d'incidence des infections, Rapports trimestriels produits |
| 7 | Formation et supervision | Organiser une séance de formation annuelle sur la prévention des infections nosocomiales pour tout le personnel, former les nouveaux agents dès leur arrivée, organiser des séances de recyclage semestrielles, superviser les pratiques d'hygiène lors des soins, évaluer les connaissances du personnel par un pré-test et post-test | Chef de Centre, Major | Semestrielle | % de personnel formé, Score moyen aux tests de connaissances, Nombre de séances de supervision effectuées |

## IV. SUIVI ET ÉVALUATION
- Le suivi est assuré par le Major du centre sous la supervision du Chef de Centre
- Une réunion trimestrielle du comité de lutte contre les infections est organisée
- Un rapport d'évaluation annuel est produit et transmis au District Sanitaire de KORHOGO 1

## V. AFFICHAGE
- Le plan est affiché dans la salle de réunion du personnel et dans chaque zone de soins
- Responsable: Chef de Centre / Major
- Période d'affichage: {periode} (renouvelé chaque année)

Génère le plan complet avec le tableau détaillé ci-dessus adapté au CSR NAGNENEFOUN."""
    },

    "rapport_formation": {
        "system": """Tu es un responsable de centre de santé (CSR) en Côte d'Ivoire. Tu génères un RAPPORT DE FORMATION DU PERSONNEL conforme à la grille ESPC - Norme 2.01.

CONTEXTE DU CSR NAGNENEFOUN:
- District: KORHOGO 1 (PORO)
- Population: 34 055 habitants
- Personnel: Infirmiers, Sages-femmes, Aides-soignants, Filles de salle, ASC, Secrétaire, Gardiens

FORMAT OBLIGATOIRE:
- Rapport TRIMESTRIEL (T1: Jan-Mar, T2: Avr-Juin, T3: Juil-Sept, T4: Oct-Déc)
- Génère un tableau RÉCAPITULATIF DES SESSIONS avec 5 colonnes
- Le séparateur doit être: |---|---|---|---|---|
- Les listes de présence sont gérées manuellement (NE PAS inclure dans le rapport)
- Chaque cellule doit contenir des informations précises et contextualisées""",
        "user": """Génère RAPPORT DE FORMATION DU PERSONNEL pour {nom_etablissement} - {periode}.

CONTEXTE DU CENTRE:
{contexte}

SECTIONS À INCLURE:
{sections}

## I. INFORMATIONS GÉNÉRALES
Établissement: {nom_etablissement}
Période: {periode}
Trimestre concerné: {trimestre}
Domaine de formation: {domaine}
Date de la formation: {date_formation}
Durée: {duree}
Formateur(s): {formateur}
Lieu: Salle de réunion du CSR {nom_etablissement}

## II. OBJECTIFS DE LA FORMATION
- Objectif général: Renforcer les capacités du personnel du CSR {nom_etablissement} en {domaine}
- Objectifs spécifiques:
  1. Acquérir les connaissances théoriques sur {domaine}
  2. Maîtriser les techniques pratiques liées à {domaine}
  3. Améliorer la qualité des prestations dans le domaine
  4. Uniformiser les pratiques conformément aux protocoles nationaux

## III. RÉCAPITULATIF DES SESSIONS (TABLEAU)
| N° | Thème/Session | Contenu abordé | Méthode pédagogique | Durée |
|---|---|---|---|---|
| 1 | Introduction et contexte | Présentation du contexte, des objectifs, rappel des protocoles nationaux | Exposé interactif | 30 min |
| 2 | Module théorique | Définition, concepts clés, grands principes, protocoles et directives nationales | Exposé, Support PPT, Documentation | 1h 30 min |
| 3 | Démonstration pratique | Démonstration des gestes techniques, procédures, manipulation du matériel | Démonstration, Simulation | 1h |
| 4 | Travaux pratiques | Mise en situation, études de cas, exercices pratiques par groupe de 2-3 | Atelier pratique, Jeux de rôles | 1h 30 min |
| 5 | Discussion et échanges | Questions-réponses, partage d'expériences, clarification des difficultés | Table ronde interactive | 30 min |
| 6 | Évaluation | Pré-test et post-test, questionnaire de satisfaction | Questionnaire individuel | 30 min |
| Total | - | - | - | 5h 30 min |

## IV. ÉVALUATION DE LA FORMATION
- Pré-test: Score moyen de [X]%
- Post-test: Score moyen de [Y]%
- Progression: +[Z] points
- Taux de satisfaction: [W]%
- Points forts:
- Points à améliorer:

## V. DIFFICULTÉS RENCONTRÉES
- [À compléter]

## VI. RECOMMANDATIONS
1. Organiser une session de recyclage
2. Superviser la mise en pratique des acquis lors des soins quotidiens
3. Mettre à disposition les documents techniques de référence
4. Évaluer l'impact de la formation à 3 mois

## VII. SUIVI
- Responsable du suivi: Major du CSR et Chef de Centre
- Modalités: Supervision des pratiques, observation directe
- Prochaine session: [À définir]

Génère le rapport complet adapté au CSR {nom_etablissement} pour le trimestre {trimestre} en {domaine} avec {nb_participants} participants."""
    },

    # =============================================================================
    # NOTES DE SERVICE (6 types exigés par la Grille ESPC)
    # =============================================================================
    "note_service": {
        "system": """Tu es un Chef de centre de santé (CSR) en Côte d'Ivoire. Tu rédiges des notes de service officielles.
Format officiel: République de Côte d'Ivoire - Union – Discipline – Travail / MSHP / Région Sanitaire / District / CSR.
Utilise le contexte réel du centre (population, personnel, infrastructures, activités).
N'inclus JAMAIS de zone de signature - signée manuellement.""",
        "user": """Génère une NOTE DE SERVICE pour {nom_etablissement}.

TYPE DE NOTE: {type_note}
DATE: {date_note}
NOM DU RESPONSABLE DÉSIGNÉ: {nom_responsable}
FONCTION: {fonction_responsable}

CONTEXTE:
{contexte}

SECTIONS:
{sections}

I. PRÉAMBULE / CONSIDÉRANTS
II. DÉSIGNATION
III. ATTRIBUTIONS / MISSIONS
IV. APPLICATION
V. DIFFUSION

Génère une note de service officielle et conforme à la réglementation."""
    }
}

# =============================================================================
# LISTE DES DOCUMENTS
# =============================================================================

DOCUMENTS_LIST = [
    ("PV Réunion Mensuelle", "pv_reunion_mensuelle"),
    ("PV Réunion COGES", "pv_coges"),
    ("PV Assemblée Générale", "pv_ag"),
    ("Rapport Supervision ASC", "rapport_supervision_asc"),
    ("Rapport Plaintes/Suggestions", "rapport_plaintes"),
    ("Fiche de Poste", "fiche_poste"),
    ("Fiche de Nomination", "fiche_nomination"),
    ("Programme Réunions Trimestrielles", "programme_reunions_trimestrielles"),
    ("Calendrier Nettoyage Centre", "calendrier_nettoyage"),
    ("Calendrier Réunions Mensuelles", "calendrier_reunions_mensuelles"),
    ("Grille Supervision ASC", "grille_supervision_asc"),
    ("Liste Personnel COGES", "liste_coges"),
    ("Plan Action Infections Nosocomiales", "plan_action_infections_nosocomiales"),
    ("Plan Supervision ASC", "plan_supervision_asc"),
    ("Rapport Formation Personnel", "rapport_formation"),
    ("Liste Personnel Centre", "liste_personnel_centre"),
    ("Note de Service", "note_service"),
]

# =============================================================================
# FONCTIONS
# =============================================================================

def generer_avec_groq(system_prompt, user_prompt):
    """Génère du contenu avec l'API Groq en créant un client frais à chaque appel"""
    from dotenv import load_dotenv
    import os
    
    # Déterminer le bon dossier de base
    if "__file__" in dir():
        _base = os.path.dirname(os.path.abspath(__file__))
    else:
        _base = os.getcwd()
    
    # Charger la clé depuis .env
    load_dotenv(os.path.join(_base, '.env'))
    
    # Récupérer la clé (priorité: variable d'env existante > .env)
    api_key = os.environ.get("GROQ_API_KEY", "")
    
    if not api_key:
        return "⚠️ Clé API Groq non configurée."
    
    try:
        _client = Groq(api_key=api_key)
        response = _client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur: {str(e)}"

def creer_document_word(titre, contenu, meta=None):
    doc = Document()
    heading = doc.add_heading(titre, level=0)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

    if meta:
        for key, value in meta.items():
            p = doc.add_paragraph()
            p.add_run(f"{key}: ").bold = True
            p.add_run(str(value))

    doc.add_paragraph()

    # Parcours intelligent: détection des tableaux markdown et des paragraphes
    lignes = contenu.split('\n')
    i = 0
    
    while i < len(lignes):
        para = lignes[i]
        para_strip = para.strip()
        
        if not para_strip:
            i += 1
            continue
        
        # Détection d'un tableau markdown (ligne qui commence par |)
        if para_strip.startswith('|') and para_strip.endswith('|'):
            # Collecter toutes les lignes du tableau
            rows = []
            while i < len(lignes) and lignes[i].strip().startswith('|'):
                row_text = lignes[i].strip()
                # Ignorer la ligne de séparation (|---|---|)
                if '---' in row_text or '—' in row_text:
                    i += 1
                    continue
                # Extraire les cellules
                cells = [c.strip() for c in row_text.split('|')[1:-1]]
                rows.append(cells)
                i += 1
            
            # Créer le tableau Word
            if rows:
                nb_cols = max(len(row) for row in rows)
                word_table = doc.add_table(rows=len(rows), cols=nb_cols)
                word_table.style = 'Light Grid Accent 1'
                
                for row_idx, row_data in enumerate(rows):
                    for col_idx in range(nb_cols):
                        cell_text = row_data[col_idx] if col_idx < len(row_data) else ""
                        cell = word_table.cell(row_idx, col_idx)
                        cell.text = cell_text
                        # Mettre en gras la première ligne (en-tête)
                        if row_idx == 0:
                            for paragraph in cell.paragraphs:
                                for run in paragraph.runs:
                                    run.bold = True
                doc.add_paragraph()
            continue
        
        # Titres et paragraphes
        if any(x in para_strip.upper() for x in ['I.', 'II.', 'III.', 'IV.', 'V.', 'VI.', 'VII.', 'VIII.', 'IX.', 'X.']) and len(para_strip) < 60:
            doc.add_heading(para_strip, level=1)
        elif any(x in para_strip.upper() for x in ['CONTEXTE', 'INFORMATIONS', 'DÉLIBÉRATIONS', 'DÉCISIONS', 'SIGNATURES', 'LISTE', 'OBSERVATIONS', 'CALENDRIER', 'OBJECTIFS', 'ACTIVITÉS', 'AFFICHAGE']) and len(para_strip) < 50:
            doc.add_heading(para_strip, level=2)
        elif para_strip.startswith('##'):
            doc.add_heading(para_strip.replace('#', '').strip(), level=2)
        elif len(para_strip) > 0:
            p = doc.add_paragraph(para_strip)
        
        i += 1
    
    return doc

# =============================================================================
# FORMULAIRES PRÉ-CONFORMES
# =============================================================================

def get_form_fields(doc_type):
    fields = {}

    if doc_type == "pv_reunion_mensuelle":
        st.markdown("### 📋 PV RÉUNION MENSUELLE (Conforme Grille ESPC)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["periode"] = st.text_input("Période (Année)", "2026")
        fields["mois"] = st.selectbox("Mois", ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"])
        # L'IA génère automatiquement tout le contenu

    elif doc_type == "pv_coges":
        st.markdown("### 📋 PV COGES (Trimestriel - Conforme Norme 1.02)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["periode"] = st.text_input("Période (Année)", "2026")
        fields["trimestre"] = st.selectbox("Trimestre de réunion", ["T1 - Janvier-Mars", "T2 - Avril-Juin", "T3 - Juillet-Septembre", "T4 - Octobre-Décembre"])

    elif doc_type == "pv_ag":
        st.markdown("### 📋 PV ASSEMBLÉE GÉNÉRALE (Annuelle - Conforme Norme 1.03)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["periode"] = st.text_input("Année de l'AG", "2026")

    elif doc_type == "rapport_supervision_asc":
        st.markdown("### 📋 RAPPORT SUPERVISION ASC (Conforme Norme 14.01)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        # L'IA génère automatiquement

    elif doc_type == "rapport_plaintes":
        st.markdown("### 📋 RAPPORT BOÎTE À SUGGESTIONS")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["nb_suggestions"] = st.text_input("Nombre de suggestions reçues", "")
        fields["types_suggestions"] = st.text_area("Types de suggestions (séparées par ;)", "Amélioration accueil ; Attente ; Hygiène ; Médicaments ; Autre")
        fields["actions"] = st.text_area("Actions menées (séparées par ;)", "Analyse des suggestions ; Réunion de réflexion ; Plan d'action")

    elif doc_type == "fiche_poste":
        st.markdown("### 📋 FICHE DE POSTE (Template par catégorie)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        
        categories_poste = {
            "Chef de Centre": {
                "titre": "Chef de Centre de Santé",
                "superieur": "Médecin Chef du District Sanitaire de KORHOGO 1",
                "regime": "Temps plein - 40h/semaine",
                "missions": "Assurer la coordination générale des activités du CSR ; Superviser l'équipe du personnel ; Garantir la qualité des soins ; Élaborer et exécuter le plan d'action annuel ; Assurer la gestion administrative et financière ; Rendre compte au District Sanitaire ; Présider les réunions de staff ; Assurer le suivi des indicateurs de performance",
                "qualifications": "Diplôme d'État de Sage-Femme ou Infirmier Diplômé d'État (IDE) ; Diplôme en Santé Publique (optionnel) ; Expérience minimale de 3 ans dans un centre de santé",
                "competences": "Leadership et management d'équipe ; Maîtrise des outils de planification ; Bonne connaissance du système de santé ivoirien",
                "responsabilites": "Responsable de la bonne marche du centre ; Responsable de la gestion du personnel ; Responsable de la qualité des soins",
                "moyens": "Bureau équipé (ordinateur, imprimante) ; Véhicule de service (si disponible) ; Budget de fonctionnement"
            },
            "Major / Sage-Femme": {
                "titre": "Major / Sage-Femme Diplômé(e) d'État",
                "superieur": "Chef de Centre",
                "regime": "Temps plein - 40h/semaine",
                "missions": "Superviser les soins obstétricaux et néonatals ; Gérer la maternité et les activités de CPN ; Assurer les accouchements et soins post-partum ; Coordonner les activités de PF et PTME ; Gérer les urgences obstétricales",
                "qualifications": "Diplôme d'État de Sage-Femme (DESF) ; Inscription à l'Ordre national des Sages-Femmes ; Expérience minimale de 2 ans en maternité",
                "competences": "Maîtrise des techniques obstétricales ; Capacité à gérer les urgences vitales ; Leadership et encadrement d'équipe",
                "responsabilites": "Responsable des activités de la maternité ; Responsable de la qualité des soins maternels et infantiles",
                "moyens": "Salle d'accouchement équipée ; Matériel de réanimation néonatale ; Kits d'accouchement"
            },
            "Infirmier Diplômé d'État (IDE)": {
                "titre": "Infirmier Diplômé d'État (IDE)",
                "superieur": "Chef de Centre / Major",
                "regime": "Temps plein - 40h/semaine",
                "missions": "Assurer les consultations curatives ; Administrer les médicaments et traitements ; Réaliser les soins infirmiers ; Participer aux activités de vaccination (PEV) ; Assurer la prise en charge du paludisme",
                "qualifications": "Diplôme d'État d'Infirmier (DEI) ; Inscription à l'Ordre national des Infirmiers ; Expérience minimale de 1 an",
                "competences": "Maîtrise des protocoles de soins infirmiers ; Capacité à diagnostiquer les pathologies courantes ; Bon relationnel avec les patients",
                "responsabilites": "Responsable des soins infirmiers quotidiens ; Responsable de la tenue des registres",
                "moyens": "Bocson médical complet ; Stéthoscope, tensiomètre ; Matériel de soins"
            },
            "Chargé(e) de Programme (PEV/Paludisme/VIH)": {
                "titre": "Chargé(e) de Programme",
                "superieur": "Chef de Centre",
                "regime": "Temps plein - 40h/semaine",
                "missions": "Planifier et coordonner les activités du programme ; Gérer les intrants et vaccins ; Organiser les séances de vaccination ; Superviser les ASC ; Collecter et analyser les données du programme",
                "qualifications": "Diplôme d'État d'Infirmier ou Sage-Femme ; Formation spécifique au programme ; Expérience minimale de 2 ans",
                "competences": "Maîtrise des protocoles du programme ; Capacité à former et superviser ; Gestion de données",
                "responsabilites": "Responsable de l'atteinte des objectifs du programme ; Responsable de la gestion des intrants",
                "moyens": "Bureau partagé avec équipement informatique ; Matériel de supervision"
            },
            "Aide-Soignant(e)": {
                "titre": "Aide-Soignant(e)",
                "superieur": "Major / IDE de garde",
                "regime": "Temps plein - 40h/semaine",
                "missions": "Assister l'infirmier dans les soins courants ; Préparer et entretenir le matériel de soins ; Assurer l'hygiène des salles de soins ; Accueillir et orienter les patients",
                "qualifications": "Certificat d'Aide-Soignant(e) ; Expérience en milieu de santé (1 an minimum)",
                "competences": "Sens de l'organisation et de la propreté ; Capacité à suivre les consignes ; Empathie et respect des patients",
                "responsabilites": "Responsable de la propreté des zones de soins ; Responsable de l'entretien du matériel",
                "moyens": "Matériel d'entretien et de nettoyage ; Équipements de protection"
            },
            "Secrétaire / Agent Administratif": {
                "titre": "Secrétaire / Agent Administratif",
                "superieur": "Chef de Centre",
                "regime": "Temps plein - 40h/semaine",
                "missions": "Assurer la gestion administrative et le secrétariat ; Tenir les registres administratifs ; Accueillir et orienter les usagers ; Saisir les rapports et documents",
                "qualifications": "Diplôme de Secrétariat ou BTS Administration ; Maîtrise des outils bureautiques",
                "competences": "Excellente présentation ; Maîtrise de la bureautique ; Organisation et rigueur",
                "responsabilites": "Responsable de la tenue des archives ; Responsable de la gestion du courrier",
                "moyens": "Bureau équipé (ordinateur, imprimante, téléphone)"
            },
            "Agent d'Entretien / Fille de Salle": {
                "titre": "Agent d'Entretien",
                "superieur": "Major / IDE de garde",
                "regime": "Temps plein - 40h/semaine",
                "missions": "Assurer le nettoyage et la désinfection des locaux ; Gérer les déchets biomédicaux ; Entretenir le linge ; Assurer la propreté des sanitaires",
                "qualifications": "Niveau primaire ou secondaire ; Formation aux règles d'hygiène",
                "competences": "Sens de la propreté ; Connaissance des techniques d'entretien ; Ponctualité",
                "responsabilites": "Responsable de la propreté des locaux ; Responsable du tri des déchets",
                "moyens": "Produits d'entretien et de désinfection ; Équipements de protection"
            },
            "Gardien / Planton": {
                "titre": "Gardien / Planton",
                "superieur": "Chef de Centre",
                "regime": "Temps plein - Garde 24h/24 (roulement)",
                "missions": "Assurer la sécurité du centre ; Contrôler les entrées et sorties ; Surveiller les locaux ; Ouvrir et fermer le centre selon les horaires",
                "qualifications": "Niveau primaire minimum ; Expérience en surveillance (optionnel)",
                "competences": "Vigilance ; Ponctualité et fiabilité ; Sens des responsabilités",
                "responsabilites": "Responsable de la sécurité du centre ; Responsable des clés",
                "moyens": "Local de garde ; Lampe torche ; Téléphone de service"
            },
            "ASC (Agent de Santé Communautaire)": {
                "titre": "Agent de Santé Communautaire (ASC)",
                "superieur": "Chargé de Programme / Chef de Centre",
                "regime": "Temps partiel - Communautaire",
                "missions": "Mener des séances de sensibilisation ; Dépister les cas suspects ; Faire la référence des patients ; Distribuer les MILD ; Animer les causeries éducatives",
                "qualifications": "Niveau secondaire (BEPC minimum) ; Formation ASC validée ; Parlant la langue locale",
                "competences": "Capacité à communiquer ; Connaissance de la communauté ; Dynamisme",
                "responsabilites": "Responsable des activités communautaires ; Responsable du matériel de sensibilisation",
                "moyens": "Kit ASC ; MILD et préservatifs ; Supports IEC/CCC ; Vélo (si disponible)"
            },
            "Pharmacien / Chargé Pharmacie": {
                "titre": "Pharmacien / Chargé de la Pharmacie",
                "superieur": "Chef de Centre",
                "regime": "Temps plein - 40h/semaine",
                "missions": "Gérer les stocks de médicaments ; Assurer la dispensation ; Tenir les fiches de stock ; Commander et réceptionner les médicaments ; Contrôler les périmés",
                "qualifications": "Diplôme de Technicien Supérieur en Pharmacie ou IDE formé ; Expérience de 2 ans",
                "competences": "Maîtrise de la gestion des stocks ; Connaissance des médicaments essentiels ; Rigueur et organisation",
                "responsabilites": "Responsable de la gestion des médicaments ; Responsable de la pharmacie",
                "moyens": "Pharmacie équipée ; Logiciel de gestion de stock ; Mobilier de rangement"
            }
        }
        
        cat_choice = st.selectbox("Catégorie du personnel", list(categories_poste.keys()))
        cat_data = categories_poste[cat_choice]
        fields["categorie_poste"] = cat_choice
        fields["titre_poste"] = cat_data["titre"]
        nom_titulaire = st.text_input("Nom du titulaire du poste", "")
        fields["nom_titulaire"] = nom_titulaire if nom_titulaire else "[Nom du titulaire]"
        fields["superieur"] = cat_data["superieur"]
        fields["regime_travail"] = cat_data["regime"]
        fields["missions_poste"] = cat_data["missions"]
        fields["qualifications_poste"] = cat_data["qualifications"]
        fields["competences_poste"] = cat_data["competences"]
        fields["responsabilites_poste"] = cat_data["responsabilites"]
        fields["moyens_poste"] = cat_data["moyens"]
        fields["match_categorie"] = f"CATÉGORIE: {cat_choice}"

    elif doc_type == "fiche_nomination":
        st.markdown("### 📋 FICHE DE NOMINATION (12 types conformes Grille ESPC)")

        types_nomination = [
            ("Note de service", "Responsable de l'ESPC (Chef d'établissement)", "1.01 d", "Directeur Départemental (DD)"),
            ("Note de service", "Responsable de chaque service (dispensaire, maternité...)", "1.01 d", "Responsable de l'ESPC"),
            ("Arrêté préfectoral / sous-préfectoral", "Mise en place du COGES", "1.02 a", "Préfet / Sous-préfet"),
            ("Note de service", "Point focal CMU", "4.03 c", "Responsable de l'ESPC"),
            ("Fiche de poste signée", "Agent d'accueil et d'orientation", "4.02 b", "Agent + Responsable ESPC"),
            ("Note de service", "Responsable de l'hygiène hospitalière", "6.01 a", "Responsable ESPC"),
            ("Note de service", "Responsable de la gestion des déchets biomédicaux", "6.05 a", "Responsable ESPC"),
            ("Note de service + fiche de poste", "Gestionnaire des médicaments (pharmacie)", "11.01 g", "Agent + Responsable ESPC"),
            ("Fiche de poste signée", "Personnel qualifié pour accouchements (SF/IDE/Maïeuticien)", "7.02 a", "Agent + Responsable ESPC"),
            ("Fiche de poste signée", "Tout agent (vérifié sur 3 noms)", "2.01 b", "Agent + Responsable ESPC"),
            ("Liste officielle nominative", "Agents de santé communautaire (ASC)", "14.01 a", "District sanitaire"),
            ("Grille de supervision ASC", "Acte de supervision ASC", "14.01 c", "ASC + Superviseur")
        ]

        type_index = st.selectbox("Type de document", range(len(types_nomination)),
            format_func=lambda i: f"{types_nomination[i][0]} - {types_nomination[i][1]} (Norme {types_nomination[i][2]})")

        type_choisi = types_nomination[type_index]
        fields["type_nomination"] = type_choisi[0]
        fields["objet_nomination"] = type_choisi[1]
        fields["reference_norme"] = type_choisi[2]
        fields["signataire"] = type_choisi[3]
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["nom_beneficiaire"] = st.text_input("Nom du bénéficiaire", "")
        fields["fonction_beneficiaire"] = st.text_input("Fonction du bénéficiaire", type_choisi[1].split(" (")[0] if " (" in type_choisi[1] else type_choisi[1])
        fields["date_effet"] = st.text_input("Date de prise d'effet (JJ/MM/AAAA)", "")
        fields["numero_ordre"] = st.text_input("Numéro d'ordre", "____/MS/RS-PORO/DS-K1/CSR NAGNENEFOUN")
        st.caption(f"**Signataire requis :** {type_choisi[3]} | **Norme ESPC :** {type_choisi[2]}")

        fields["match_categorie"] = f"TYPE: {type_choisi[0]} | OBJET: {type_choisi[1]} | NORME: {type_choisi[2]}"

    elif doc_type == "programme_reunions_trimestrielles":
        st.markdown("### 📋 PROGRAMME RÉUNIONS TRIMESTRIELLES")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["periode"] = st.text_input("Période (Année)", "2026")

    elif doc_type == "calendrier_nettoyage":
        st.markdown("### 📋 CALENDRIER NETTOYAGE (Conforme Norme 6.01 - À AFFICHER)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["periode"] = st.text_input("Période (Année)", "2026")
        fields["zones"] = st.text_area("Zones à nettoyer (séparées par ;)", "Salle de consultation ; Maternité ; Hall d'attente ; Toilettes ; Cour")
        fields["frequences"] = st.text_area("Fréquences (séparées par ;)", "Quotidien ; Hebdomadaire ; Mensuel")

    elif doc_type == "calendrier_reunions_mensuelles":
        st.markdown("### 📋 CALENDRIER RÉUNIONS MENSUELLES")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["periode"] = st.text_input("Période (Année)", "2026")

    elif doc_type == "grille_supervision_asc":
        st.markdown("### 📋 GRILLE SUPERVISION ASC (À signer ASC + Superviseur)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["periode"] = st.text_input("Période (Année)", "2026")
        fields["criteria"] = st.text_area("Critères de supervision (séparés par ;)", "Accueil ; Sensibilisation ; Dépistage ; Référence ; Documentation")

    elif doc_type == "liste_coges":
        st.markdown("### 📋 LISTE PERSONNEL COGES (Format grille ESPC)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["periode"] = st.text_input("Période (Année)", "2026")
        fields["membres"] = st.text_area(
            "Membres COGES (Nom ; Fonction ; Téléphone)",
            "Koffi Kouassi ; Président ; 0102030405\n"
            "Ahoua N'Guessan ; Vice-Président ; 0102030406\n"
            "Konan Bertille ; Secrétaire ; 0102030407\n"
            "Kouamé Yao ; Trésorier ; 0102030408\n"
            "Soro Fatoumata ; Commissaire aux Comptes ; 0102030409\n"
            "Touré Mamadou ; Membre ; 0102030410"
        )

    elif doc_type == "liste_personnel_centre":
        st.markdown("### 📋 LISTE PERSONNEL CENTRE (Statique CSR NAGNENEFOUN)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["periode"] = st.text_input("Période (Année)", "2026")

    elif doc_type == "plan_action_infections_nosocomiales":
        st.markdown("### 📋 PLAN ACTION INFECTIONS NOSOCOMIALES")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["periode"] = st.text_input("Période (Année)", "2026")
        fields["activites"] = st.text_area("Activités principales (séparées par ;)", "Formation personnel ; Désinfection ; Lavage des mains ; Gestion des déchets ; Surveillance")

    elif doc_type == "plan_supervision_asc":
        st.markdown("### 📋 PLAN SUPERVISION ASC (Plan annuel)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["periode"] = st.text_input("Période (Année)", "2026")
        fields["activites"] = st.text_area("Activités de supervision (séparées par ;)", "Inspection terrain ; Formation ; Dépistage communautaire ; Référence")

    elif doc_type == "rapport_formation":
        st.markdown("### 📋 RAPPORT FORMATION (Trimestriel - Norme 2.01)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["periode"] = st.text_input("Période (Année)", "2026")
        fields["trimestre"] = st.selectbox("Trimestre", ["T1 - Janvier-Mars", "T2 - Avril-Juin", "T3 - Juillet-Septembre", "T4 - Octobre-Décembre"])
        fields["domaine"] = st.text_input("Domaine de formation", "ex: Paludisme, PEV, VIH, CPN, Hygiène...")
        fields["date_formation"] = st.text_input("Date de la formation", "00/00/2026")
        fields["duree"] = st.text_input("Durée", "1 jour (5h30)")
        fields["formateur"] = st.text_input("Formateur(s)", "Major / Infirmier superviseur / Chargé de programme")
        fields["nb_participants"] = st.number_input("Nombre de participants", min_value=1, max_value=50, value=12)

    elif doc_type == "note_service":
        st.markdown("### 📋 NOTE DE SERVICE (Conforme Grille ESPC)")

        types_notes = [
            "Désignation du Chef de Centre",
            "Désignation du Responsable de Service",
            "Désignation du Point Focal CMU",
            "Désignation du Responsable de l'Hygiène",
            "Désignation du Responsable de la Gestion des Déchets Biomédicaux",
            "Désignation du Gestionnaire des Médicaments en Pharmacie"
        ]
        fields["type_note"] = st.selectbox("Type de note de service", types_notes)
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["date_note"] = st.text_input("Date (JJ/MM/AAAA)", "")
        fields["nom_responsable"] = st.text_input("Nom du responsable désigné", "")
        fields["fonction_responsable"] = st.text_input("Fonction du responsable", "")

    return fields

# =============================================================================
# GÉNÉRATEUR DE PLANNING - Cycle PG → R → P
# =============================================================================

PLANNING_CYCLE = ["PG", "R", "P"]

PLANNING_CATEGORIES = [
    {"id": "infirmier-dispensaire", "label": "Infirmiers (Dispensaire)", "prefixe": "Infirmier"},
    {"id": "aide-dispensaire", "label": "Aides (Dispensaire)", "prefixe": "Aide"},
    {"id": "sage-femme-maternite", "label": "Sages-femmes (Maternité)", "prefixe": "Sage-femme"},
    {"id": "aide-maternite", "label": "Aides (Maternité)", "prefixe": "Aide"},
    {"id": "fille-salle", "label": "Filles de salle", "prefixe": "Fille de salle"},
]

PLANNING_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "employes.json")

def charger_employes():
    try:
        if os.path.exists(PLANNING_DATA_FILE):
            with open(PLANNING_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return []

def sauvegarder_employes(employes):
    with open(PLANNING_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(employes, f, ensure_ascii=False, indent=2)

def generer_planning_employe(cycle_position, annee, mois):
    jours_dans_mois = calendar.monthrange(annee, mois + 1)[1]
    planning = []
    position = cycle_position
    for jour in range(1, jours_dans_mois + 1):
        planning.append({"jour": f"{jour:02d}", "shift": PLANNING_CYCLE[position]})
        position = (position + 1) % len(PLANNING_CYCLE)
    return planning, position

def set_shading(cell, color_hex):
    from docx.oxml import OxmlElement
    tc = cell._element.get_or_add_tcPr()
    for shd in tc.findall(qn('w:shd')):
        tc.remove(shd)
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), color_hex)
    tc.append(shd)

def exporter_planning_word(plannings_data, service_label, mois, annee, centre_sante=""):
    doc = Document()
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width, section.page_height = section.page_height, section.page_width
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)

    p = doc.add_paragraph("MINISTÈRE DE LA SANTÉ, DE L'HYGIÈNE PUBLIQUE ET DE LA CMU")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph("RÉPUBLIQUE DE CÔTE D'IVOIRE - Union – Discipline – Travail")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if centre_sante:
        p = doc.add_paragraph(f"Centre: {centre_sante}")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("")

    titre = doc.add_paragraph()
    titre.add_run(f"PLANNING MENSUEL - {mois} {annee}").bold = True
    titre.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sp = doc.add_paragraph(f"Service: {service_label}")
    sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("")

    if plannings_data:
        jours = len(plannings_data[0]["planning"])
        table = doc.add_table(rows=len(plannings_data) + 1, cols=jours + 1)
        table.style = "Table Grid"
        header_cells = table.rows[0].cells
        header_cells[0].text = "NOM & PRENOM"
        set_shading(header_cells[0], "3498DB")
        for i in range(jours):
            header_cells[i + 1].text = f"{i + 1:02d}"
            set_shading(header_cells[i + 1], "3498DB")
        for i, emp in enumerate(plannings_data):
            row = table.rows[i + 1].cells
            row[0].text = f"{emp['nom']}"
            for j, shift in enumerate(emp["planning"]):
                row[j + 1].text = shift["shift"]
    return doc

def afficher_page_planning():
    st.markdown("<h1 style='text-align: center;'>🏥 GÉNÉRATEUR DE PLANNING</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Cycle automatique: <b>PG</b> (Permanence+Garde) → <b>P</b> (Permanence) → <b>R</b> (Repos)</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1: st.markdown("**PG** = Permanence + Garde")
    with col2: st.markdown("**P** = Permanence")
    with col3: st.markdown("**R** = Repos")
    st.divider()

    employes_fresh = charger_employes()

    # Gestion du personnel
    st.header("👥 Gestion du Personnel")
    # Adapter le nombre de colonnes selon la largeur
    n_cols = min(5, max(2, len(PLANNING_CATEGORIES)))
    cols = st.columns(n_cols)
    for idx, cat in enumerate(PLANNING_CATEGORIES):
        with cols[idx]:
            st.subheader(cat["label"])
            employes_cat = [e for e in employes_fresh if e["service"] == cat["id"]]
            st.caption(f"{len(employes_cat)} employé(s)")
            with st.form(f"plan_form_{cat['id']}"):
                nouveau_nom = st.text_input("Nom", placeholder="Ex: YEO", key=f"plan_nom_{cat['id']}")
                submitted = st.form_submit_button("➕ Ajouter", use_container_width=True)
                if submitted and nouveau_nom:
                    employes_meme_service = [e for e in employes_fresh if e["service"] == cat["id"]]
                    nouvelle_pos = (max([e["cyclePosition"] for e in employes_meme_service]) + 1) % len(PLANNING_CYCLE) if employes_meme_service else 0
                    nouveau = {"id": len(employes_fresh) + 1, "nom": nouveau_nom.upper(), "prenom": cat["prefixe"], "service": cat["id"], "cyclePosition": nouvelle_pos}
                    employes_fresh.append(nouveau)
                    sauvegarder_employes(employes_fresh)
                    st.rerun()
            for emp in employes_cat:
                col_a, col_b = st.columns([3, 1])
                with col_a: st.markdown(f"**{emp['nom']}**")
                with col_b:
                    if st.button("×", key=f"plan_del_{emp['id']}_{cat['id']}"):
                        employes_fresh = [e for e in employes_fresh if e["id"] != emp["id"]]
                        sauvegarder_employes(employes_fresh)
                        st.rerun()
    st.divider()

    # Générateur
    st.header("📅 Générer le Planning")
    centre_sante = st.text_input("🏥 Nom du Centre", placeholder="Ex: CSR NAGNENEFOUN", value="CSR NAGNENEFOUN")
    col1, col2, col3 = st.columns(3)
    with col1:
        mois = st.selectbox("Mois", ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"], index=datetime.now().month - 1)
    with col2:
        annee = st.number_input("Année", min_value=2020, max_value=2030, value=datetime.now().year)
    with col3:
        generer_tous = st.checkbox("Tous les services", value=False)
        service = None if generer_tous else st.selectbox("Service", PLANNING_CATEGORIES, format_func=lambda x: x["label"])

    if st.button("🔄 Générer le Planning", type="primary", use_container_width=True):
        employes_service = employes_fresh if service is None else [e for e in employes_fresh if e["service"] == service["id"]]
        if not employes_service:
            st.warning("Aucun employé dans ce service !")
        else:
            mois_num = ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"].index(mois)
            employes_fresh = charger_employes()
            employes_service = employes_fresh if service is None else [e for e in employes_fresh if e["service"] == service["id"]]
            plannings = []
            for emp in employes_service:
                planning, _ = generer_planning_employe(emp["cyclePosition"], annee, mois_num)
                plannings.append({"nom": emp["nom"], "prenom": emp["prenom"], "planning": planning})
            st.success(f"✅ Planning généré pour {len(plannings)} employé(s)")
            jours = len(plannings[0]["planning"])
            html = '<div style="overflow-x:auto;max-width:100%;"><table style="width:100%;border-collapse:collapse;font-size:12px;"><thead><tr><th style="border:1px solid #ddd;padding:8px;background-color:#3498DB;color:white;text-align:center;white-space:nowrap;">Nom & Prénom</th>'
            for i in range(jours):
                html += f'<th style="border:1px solid #ddd;padding:8px;background-color:#3498DB;color:white;text-align:center;">{i+1:02d}</th>'
            html += '</tr></thead><tbody>'
            for emp in plannings:
                html += f'<tr><td style="border:1px solid #ddd;padding:8px;font-weight:bold;">{emp["nom"]}</td>'
                for shift in emp["planning"]:
                    color = "#d4edda" if shift["shift"] == "R" else ("#fff3cd" if shift["shift"] == "PG" else "#f8f9fa")
                    html += f'<td style="border:1px solid #ddd;padding:8px;text-align:center;background:{color};">{shift["shift"]}</td>'
                html += '</tr>'
            html += '</tbody></table></div>'
            st.markdown(html, unsafe_allow_html=True)
            service_label = service["label"] if service else "Tous les services"
            doc = exporter_planning_word(plannings, service_label, mois, annee, centre_sante)
            temp_file = f"planning_{service['id'] if service else 'tous'}_{mois}_{annee}.docx"
            doc.save(temp_file)
            with open(temp_file, "rb") as f:
                st.download_button("📄 Exporter en Word", f.read(), file_name=temp_file, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# =============================================================================
# INTERFACE PRINCIPALE
# =============================================================================

def main():
    # =============================================================================
    # PAGE D'ACCUEIL
    # =============================================================================
    if "page" not in st.session_state:
        st.session_state.page = "accueil"

    # CSS responsive pour mobile
    st.markdown("""
    <style>
        /* Réduction générale sur mobile */
        @media (max-width: 768px) {
            /* Titres plus petits */
            h1 { font-size: 1.5rem !important; }
            h2 { font-size: 1.2rem !important; }
            h3 { font-size: 1rem !important; }
            /* Sidebar navigation compacte */
            section[data-testid="stSidebar"] .stButton button {
                font-size: 0.8rem !important;
                padding: 6px 10px !important;
            }
            section[data-testid="stSidebar"] h3 {
                font-size: 0.9rem !important;
            }
            /* Boutons principaux */
            .stButton button {
                font-size: 0.85rem !important;
                padding: 8px 12px !important;
            }
            /* Colonnes empilées */
            div[data-testid="column"] {
                min-width: 100% !important;
                margin-bottom: 10px;
            }
            /* Inputs et selects */
            input, select, textarea {
                font-size: 16px !important; /* évite zoom sur iOS */
            }
            /* Tableaux responsive avec scroll */
            table {
                font-size: 10px !important;
                max-width: 100% !important;
            }
            td, th {
                padding: 3px 4px !important;
            }
            /* Expand/collapse plus compacts */
            .streamlit-expanderHeader {
                font-size: 0.85rem !important;
                padding: 8px 12px !important;
            }
            /* Espacement réduit */
            .stMarkdown, .stText {
                margin-bottom: 8px !important;
            }
            .st-emotion-cache-1y4p8pa {
                padding: 1rem 0.5rem !important;
            }
            /* Bouton téléchargement */
            .stDownloadButton button {
                font-size: 0.8rem !important;
                padding: 6px 10px !important;
            }
            /* Success/warning messages */
            .stAlert {
                font-size: 0.85rem !important;
                padding: 8px !important;
            }
        }
        @media (max-width: 480px) {
            h1 { font-size: 1.2rem !important; }
            .st-emotion-cache-1y4p8pa { padding: 0.5rem 0.3rem !important; }
            div[data-testid="stSidebarNav"] { display: none !important; }
        }
        /* Sidebar fixe sur desktop, fine sur mobile */
        section[data-testid="stSidebar"] {
            min-width: 200px !important;
        }
        @media (max-width: 768px) {
            section[data-testid="stSidebar"] {
                min-width: 100% !important;
            }
            section[data-testid="stSidebar"] > div {
                padding: 8px !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    # Boutons de navigation dans la sidebar (toujours visibles)
    with st.sidebar:
        st.markdown("### 🏠 Navigation")
        pages = {
            "accueil": "🏠 Accueil",
            "generateur": "📄 Générateur de documents",
            "planning": "🏥 Planning Personnel",
            "templates_rapides": "⚡ Templates Rapides",
            "guide": "📋 Guide Cahiers / Registres"
        }
        for key, label in pages.items():
            if st.button(label, use_container_width=True, 
                         type="primary" if st.session_state.page == key else "secondary"):
                st.session_state.page = key
                st.rerun()
        st.markdown("---")

    if st.session_state.page == "accueil":
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px;">
            <h1 style="font-size: 3rem; margin-bottom: 5px;">🏥 Générateur Documents ESPC</h1>
            <p style="font-size: 1.2rem; color: #666; margin-bottom: 30px;">
                Conforme à la Grille d'Évaluation des Établissements Sanitaires de Premier Contact
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            ### 📄 17 documents prêts à l'emploi
            - PV Réunions (Mensuelle, COGES, AG)
            - Rapports (Supervision ASC, Plaintes, Formation)
            - Fiches (Poste, Nomination)
            - Calendriers (Nettoyage, Réunions)
            - Plans (Action, Supervision ASC)
            - Grilles, Listes et Notes de Service

            **Tous conformes à la grille ESPC**
            """)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 ACCÉDER AU GÉNÉRATEUR", type="primary", use_container_width=True):
                st.session_state.page = "generateur"
                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⚡ TEMPLATES RAPIDES (prêts à imprimer)", type="secondary", use_container_width=True):
                st.session_state.page = "templates_rapides"
                st.rerun()

        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #888; font-size: 0.9rem;">
            <p>⚙️ Personnalisez vos modèles | 📥 Export Word | 👁️ Aperçu avant téléchargement</p>
            <p><strong>CSR NAGNENEFOUN</strong> — District Sanitaire de KORHOGO 1 — Région du PORO</p>
        </div>
        """, unsafe_allow_html=True)

    elif st.session_state.page == "planning":
        afficher_page_planning()

    elif st.session_state.page == "templates_rapides":
        st.markdown("<h1 style='text-align: center;'>⚡ TEMPLATES RAPIDES</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 1.1rem;'>Documents pré-remplis CSR NAGNENEFOUN — Imprimez et complétez le nom + la date manuellement</p>", unsafe_allow_html=True)
        st.markdown("---")

        rapides = [
            ("👨‍⚕️", "Fiche de Poste - Chef de Centre", "Chef de Centre CSR - Missions, qualifications, responsabilités", """RÉPUBLIQUE DE CÔTE D'IVOIRE
Union – Discipline – Travail
MINISTÈRE DE LA SANTÉ, HYGIÈNE PUBLIQUE ET CMU
RÉGION SANITAIRE DU PORO - DISTRICT KORHOGO 1
CSR NAGNENEFOUN

FICHE DE POSTE N° ____/MS/RS-PORO/DS-K1/CSR NAGNENEFOUN

I. IDENTIFICATION DU POSTE
Établissement: CSR NAGNENEFOUN
Poste: Chef de Centre de Santé
Supérieur: Médecin Chef District KORHOGO 1
Régime: Temps plein - 40h/semaine
Nom du titulaire: [À COMPLÉTER]
Date: ____/____/______

II. MISSIONS PRINCIPALES
1. Coordonner les activités cliniques, administratives et financières du CSR
2. Superviser l'équipe du personnel (IDE, SF, Aide-soignants, administratif)
3. Garantir la qualité des soins et le respect des protocoles nationaux
4. Élaborer et exécuter le plan d'action annuel
5. Gérer le budget et les ressources du centre
6. Présider les réunions de staff mensuelles et COGES trimestrielles
7. Assurer le suivi des indicateurs et la transmission des rapports au District
8. Représenter le centre auprès des autorités et partenaires

III. QUALIFICATIONS
- IDE ou Sage-Femme Diplômé d'État
- Expérience minimale de 3 ans en centre de santé
- Inscription à l'Ordre national

IV. SIGNATURE
Cachet et Signature du Chef de Centre:
Date: ____/____/______"""),
            ("👩‍⚕️", "Fiche de Poste - Major / Sage-Femme", "Major/SF - Maternité, CPN, accouchements", """FICHE DE POSTE N° ____/MS/RS-PORO/DS-K1/CSR NAGNENEFOUN

I. IDENTIFICATION
Poste: Major / Sage-Femme Diplômé(e) d'État
Supérieur: Chef de Centre
Régime: Temps plein
Nom: [À COMPLÉTER]

II. MISSIONS
1. Superviser les soins obstétricaux et néonatals
2. Assurer les CPN, CPoN et accouchements
3. Coordonner la PF et PTME
4. Gérer les urgences obstétricales
5. Tenir les registres de la maternité

III. QUALIFICATIONS
- DESF (Diplôme d'État de Sage-Femme)
- Inscription Ordre national
- Expérience 2 ans minimum

Signature: ____/____/______"""),
            ("🩺", "Fiche de Poste - IDE", "Infirmier - Consultations, soins, PEV", """FICHE DE POSTE N° ____/MS/RS-PORO/DS-K1/CSR NAGNENEFOUN

I. IDENTIFICATION
Poste: Infirmier Diplômé d'État (IDE)
Supérieur: Chef de Centre / Major
Régime: Temps plein
Nom: [À COMPLÉTER]

II. MISSIONS
1. Consultations curatives (paludisme, IRA, diarrhées)
2. Administration des médicaments et soins infirmiers
3. PEV et stratégies avancées
4. Prise en charge paludisme (TDR, ACT)
5. Dépistage VIH et lien PTME
6. Tenue des registres et rapports SIG

III. QUALIFICATIONS
- DEI (Diplôme d'État d'Infirmier)
- Inscription Ordre national

Signature: ____/____/______"""),
            ("🩹", "Fiche de Poste - Aide-Soignant(e)", "Aide-Soignant - Assistance, hygiène", """FICHE DE POSTE N° ____/MS/RS-PORO/DS-K1/CSR NAGNENEFOUN

I. IDENTIFICATION
Poste: Aide-Soignant(e)
Supérieur: Major / IDE de garde
Régime: Temps plein
Nom: [À COMPLÉTER]

II. MISSIONS
1. Assister l'infirmier dans les soins courants
2. Préparer et entretenir le matériel de soins
3. Assurer l'hygiène des salles de soins
4. Accueillir et orienter les patients

III. QUALIFICATIONS
- Certificat d'Aide-Soignant(e)
- Expérience 1 an minimum

Signature: ____/____/______"""),
            ("📋", "Fiche de Poste - Agent Administratif", "Secrétaire - Gestion administrative", """FICHE DE POSTE N° ____/MS/RS-PORO/DS-K1/CSR NAGNENEFOUN

I. IDENTIFICATION
Poste: Secrétaire / Agent Administratif
Supérieur: Chef de Centre
Régime: Temps plein
Nom: [À COMPLÉTER]

II. MISSIONS
1. Gestion administrative et secrétariat
2. Tenue des registres administratifs
3. Accueil et orientation des usagers
4. Saisie des rapports et documents

III. QUALIFICATIONS
- BTS Administration / Diplôme de Secrétariat
- Maîtrise bureautique

Signature: ____/____/______"""),
            ("🧹", "Fiche de Poste - Agent d'Entretien", "Agent d'entretien - Nettoyage, hygiène", """FICHE DE POSTE N° ____/MS/RS-PORO/DS-K1/CSR NAGNENEFOUN

I. IDENTIFICATION
Poste: Agent d'Entretien / Fille de Salle
Supérieur: Major / IDE de garde
Régime: Temps plein
Nom: [À COMPLÉTER]

II. MISSIONS
1. Nettoyage et désinfection des locaux
2. Gestion des déchets biomédicaux
3. Entretien du linge
4. Propreté des sanitaires

Signature: ____/____/______"""),
            ("🔐", "Fiche de Poste - Gardien", "Gardien/Planton - Sécurité", """FICHE DE POSTE N° ____/MS/RS-PORO/DS-K1/CSR NAGNENEFOUN

I. IDENTIFICATION
Poste: Gardien / Planton
Supérieur: Chef de Centre
Régime: Garde 24h (roulement)
Nom: [À COMPLÉTER]

II. MISSIONS
1. Assurer la sécurité du centre
2. Contrôler les entrées/sorties
3. Ouvrir et fermer le centre selon les horaires

Signature: ____/____/______"""),
            ("📝", "Note de Service - Chef de Centre", "Désignation Chef de Centre (Norme 1.01 d)", """RÉPUBLIQUE DE CÔTE D'IVOIRE
Union – Discipline – Travail
MSHP-CMU / RÉGION PORO / DISTRICT KORHOGO 1
CSR NAGNENEFOUN

NOTE DE SERVICE N° ____/MS/RS-PORO/DS-K1/CSR NAGNENEFOUN

OBJET: Désignation du Chef de Centre

Le Médecin Chef du District de KORHOGO 1,

VU les textes organiques;
VU les besoins de service;

DÉSIGNE

Nom: [À COMPLÉTER]
Fonction: Chef de Centre - CSR NAGNENEFOUN
Date d'effet: ____/____/______

Missions: Coordination, supervision, gestion, qualité des soins, rapports District.

Fait à KORHOGO 1, le ____/____/______
Le Médecin Chef du District

[Cachet et Signature]

Diffusion: Intéressé(e), District, Archives"""),
            ("📝", "Note de Service - Point Focal CMU", "Point Focal CMU (Norme 4.03 c)", """NOTE DE SERVICE N° ____/MS/RS-PORO/DS-K1/CSR NAGNENEFOUN

OBJET: Désignation Point Focal CMU

Le Chef du CSR NAGNENEFOUN,

DÉSIGNE

Nom: [À COMPLÉTER]
Fonction: Point Focal CMU
Date d'effet: ____/____/______

Missions: Accueil CMU, enregistrement, complétude registre, transmission SurveyCTO.

Fait à CSR NAGNENEFOUN, le ____/____/______
Le Chef de Centre

[Cachet et Signature]"""),
            ("📝", "Note de Service - Responsable Hygiène", "Responsable Hygiène (Norme 6.01 a)", """NOTE DE SERVICE N° ____/MS/RS-PORO/DS-K1/CSR NAGNENEFOUN

OBJET: Désignation Responsable Hygiène Hospitalière

Le Chef du CSR NAGNENEFOUN,

DÉSIGNE

Nom: [À COMPLÉTER]
Fonction: Responsable Hygiène
Date d'effet: ____/____/______

Missions: Supervision hygiène, déchets biomédicaux, formation personnel.

Fait à CSR NAGNENEFOUN, le ____/____/______
Le Chef de Centre

[Cachet et Signature]"""),
            ("📝", "Note de Service - Gestionnaire Pharmacie", "Gestionnaire Médicaments (Norme 11.01 g)", """NOTE DE SERVICE N° ____/MS/RS-PORO/DS-K1/CSR NAGNENEFOUN

OBJET: Désignation Gestionnaire des Médicaments

Le Chef du CSR NAGNENEFOUN,

DÉSIGNE

Nom: [À COMPLÉTER]
Fonction: Gestionnaire Pharmacie
Date d'effet: ____/____/______

Missions: Gestion stocks, dispensation, commandes, contrôle périmés.

Fait à CSR NAGNENEFOUN, le ____/____/______
Le Chef de Centre

[Cachet et Signature]"""),
            ("📜", "Arrêté - Mise en place COGES", "Arrêté COGES (Norme 1.02 a)", """RÉPUBLIQUE DE CÔTE D'IVOIRE
Union – Discipline – Travail
RÉGION PORO / DISTRICT KORHOGO 1

ARRÊTÉ N° ____/MS/RS-PORO/DS-K1/PORTANT MISE EN PLACE COGES

Le Préfet/Sous-Préfet de [À COMPLÉTER],

Considérant les textes organiques;
Considérant la grille ESPC (Norme 1.02 a);

ARRÊTE

Art.1: Le COGES du CSR NAGNENEFOUN est mis en place.
Président: [À COMPLÉTER]
Vice-Président: [À COMPLÉTER]
Secrétaire: [À COMPLÉTER]
Trésorier: [À COMPLÉTER]
Commissaire: [À COMPLÉTER]

Art.2: Le COGES assure la gestion participative, mobilisation des ressources, suivi des activités.

Art.3: Mandat de 3 ans renouvelable.

Fait à [Lieu], le ____/____/______
Le Préfet/Sous-Préfet

[Cachet et Signature]"""),
            ("📜", "Arrêté - Liste Nominative ASC", "Liste officielle ASC (Norme 14.01 a)", """RÉPUBLIQUE DE CÔTE D'IVOIRE
Union – Discipline – Travail
RÉGION PORO / DISTRICT KORHOGO 1

ARRÊTÉ N° ____/MS/RS-PORO/DS-K1/PORTANT LISTE ASC

Le Médecin Chef du District de KORHOGO 1,

ARRÊTE

Liste des ASC rattachés au CSR NAGNENEFOUN:

N° | Nom & Prénoms | Village | Téléphone
1. | [À COMPLÉTER] | [À COMPLÉTER] | [À COMPLÉTER]
2. | [À COMPLÉTER] | [À COMPLÉTER] | [À COMPLÉTER]
3. | [À COMPLÉTER] | [À COMPLÉTER] | [À COMPLÉTER]

Fait à KORHOGO 1, le ____/____/______
Le Médecin Chef du District

[Cachet et Signature]"""),
        ]

        for icone, titre, desc, contenu in rapides:
            with st.expander(f"{icone} **{titre}** — {desc}", expanded=False):
                st.text_area("Contenu du template", contenu, height=200, key=f"rapide_{titre}")
                doc = creer_document_word(titre, contenu)
                from io import BytesIO
                buf = BytesIO()
                doc.save(buf)
                buf.seek(0)
                st.download_button(f"📥 Télécharger {titre} (.docx)", buf, f"{titre}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    elif st.session_state.page == "guide":
        st.title("📋 Guide des Cahiers / Registres / Outils Physiques")
        st.markdown("**Références conformes à la Grille ESPC — Contrôle District / Région**")
        st.markdown("---")

        guide_data = [
            ("1", "Cahier de présence", "2.01 e", "Renseignement correct : date, nom, fonction, heure arrivée/sortie, signature, absence de saut de ligne"),
            ("2", "Journal de caisse (cahier brouillard)", "3.01 a", "Existence et tenue à jour"),
            ("3", "Rapport financier trimestriel de trésorerie", "3.01 b", "Prise en compte de toutes les ressources"),
            ("4", "États de redevances mensuels", "3.01 c", "Ressources perçues auprès des clients (3 derniers mois)"),
            ("5", "Ordres de paiement (OP) et liasses", "3.01 d", "Vérification des pièces (factures, PV, bon de commande)"),
            ("6", "Cahier d'inventaire des produits d'entretien", "6.06 b", "Inventaire mensuel des 3 derniers mois"),
            ("7", "Fiche de stock (médicaments)", "11.02 a.ii / 12.01", "Disponibilité, concordance avec stock physique, ruptures"),
            ("8", "Cahier d'inventaire (pharmacie)", "11.02 a.iii", "Inventaire régulier"),
            ("9", "Cahiers de recettes journalières et de versements", "11.02 a.iv", "Tenue et archivage"),
            ("10", "Ordonnancier / Facture", "11.02 a.v", "Disponibilité"),
            ("11", "Registre d'accouchement", "7.02 a, 7.03, 7.08, 8.01 c", "Identification personnel, partogramme, administration médicaments, GATPA, CPoN, décès"),
            ("12", "Registre CPoN (consultation postnatale)", "7.08 b", "Renseignement complet de tous les items"),
            ("13", "Registre de consultation curative", "7.03 e, 10.01 a, 12.01", "Prise en charge paludisme, IRA, diarrhée, triangulation stocks"),
            ("14", "Registre de prise en charge des assurés CMU", "4.03 g", "Complétude, transmission surveyCTO"),
            ("15", "Cahier de transmission (CMU) au district", "4.03 h", "Bordereaux déchargés"),
            ("16", "Rapport SIG mensuel", "1.04 d", "Cohérence, corrections apportées"),
            ("17", "Matrice de cohérence", "1.04 d", "Triangulation avec rapports SIG"),
            ("18", "Fiche de notification de décès maternel (5 fiches vierges)", "8.01 a", "Disponibilité, bon rangement"),
            ("19", "Rapport mensuel communautaire des ASC", "8.01 b, 14.01 f", "Disponibilité par mois, concordance"),
            ("20", "Outils primaires de collecte des données", "8.01 c", "Existence et tenue (registres CPN, soins curatifs, accouchements)"),
            ("21", "Fiche de stock ASC", "15.01 a", "Disponibilité, à jour"),
            ("22", "Rapport mensuel d'activité communautaire (par ASC)", "15.01 b", "Disponibilité"),
        ]

        # Tableau principal
        cols = st.columns([0.5, 3, 1.5, 4])
        cols[0].markdown("**N°**")
        cols[1].markdown("**Désignation du cahier / registre**")
        cols[2].markdown("**Norme ESPC**")
        cols[3].markdown("**Ce que le contrôleur vérifie**")
        st.markdown("---")

        for row in guide_data:
            with st.container():
                c1, c2, c3, c4 = st.columns([0.5, 3, 1.5, 4])
                c1.markdown(f"**{row[0]}**")
                c2.markdown(row[1])
                c3.markdown(f"`{row[2]}`")
                c4.markdown(row[3])
            st.markdown("---")

        st.markdown("## 📂 Récapitulatif par service")
        st.markdown("---")

        recap_sections = [
            ("💼 Gestion / Administration", [
                "Cahier de présence",
                "Journal de caisse (brouillard)",
                "États de redevances",
                "Ordres de paiement et liasses",
                "Rapports financiers",
                "Fiches de stock (pharmacie)",
                "Cahier d'inventaire (pharmacie)",
                "Cahiers de recettes journalières",
                "Ordonnancier",
            ]),
            ("👶 Maternité / SONU", [
                "Registre d'accouchement",
                "Registre CPoN",
                "Registre de consultation curative",
                "Fiche de notification décès maternel",
            ]),
            ("🆔 CMU", [
                "Registre de prise en charge des assurés CMU",
                "Cahier de transmission CMU",
            ]),
            ("🏘️ Communautaire (ASC)", [
                "Rapport mensuel communautaire (ESPC)",
                "Fiche de stock ASC",
                "Rapport mensuel d'activité de chaque ASC",
            ]),
            ("🧹 Hygiène", [
                "Cahier d'inventaire des produits d'entretien",
            ]),
        ]

        tab_labels = [s[0] for s in recap_sections]
        tabs = st.tabs(tab_labels)

        for i, (title, items) in enumerate(recap_sections):
            with tabs[i]:
                for item in items:
                    st.markdown(f"- ✅ {item}")
                st.markdown("")
                st.info(f"**{len(items)}** cahier(s)/registre(s) à vérifier dans ce service")

    elif st.session_state.page == "generateur":
        # =============================================================================
        # GÉNÉRATEUR DE DOCUMENTS
        # =============================================================================
        st.title("🏥 Générateur Documents ESPC")
        st.markdown("**Conforme à la Grille ESPC**")

        # =============================================================================
        # SECTION PERSONNALISATION DES TEMPLATES
        # =============================================================================
        with st.expander("⚙️ Personnaliser les templates"):
            st.markdown("### Modifier la structure des documents")

            # Choisir quel document modifier
            template_options = list(templates.keys()) if templates else []
            template_noms = {k: templates[k]["nom"] for k in template_options} if templates else {}
            template_choice = st.selectbox(
                "Choisir le document à modifier",
                template_options,
                format_func=lambda x: template_noms.get(x, x)
            )

            if template_choice and templates:
                st.markdown(f"#### 📄 {templates[template_choice]['nom']}")

                # Afficher les sections actuelles
                sections_actuelles = templates[template_choice]["sections"]

                # Modifier les sections
                sections_text = st.text_area(
                    "Sections (une par ligne)",
                    value="\n".join(sections_actuelles),
                    height=150
                )

                # Convertir en liste
                nouvelles_sections = [s.strip() for s in sections_text.split("\n") if s.strip()]

                # Bouton pour sauvegarder
                if st.button("💾 Sauvegarder les modifications"):
                    templates[template_choice]["sections"] = nouvelles_sections
                    sauvegarder_templates(templates)
                    st.success(f"✅ Template '{templates[template_choice]['nom']}' mis à jour!")
                    st.rerun()

                # Bouton pour réinitialiser
                if st.button("↩️ Réinitialiser"):
                    # Recréer le fichier original
                    sauvegarder_templates(templates)
                    st.success("Template réinitialisé!")
                    st.rerun()

        st.markdown("---")

        doc_options = [d[0] for d in DOCUMENTS_LIST]
        type_doc = st.selectbox("📄 Choisir le document", doc_options)

        doc_key = None
        for name, key in DOCUMENTS_LIST:
            if name == type_doc:
                doc_key = key
                break

        st.markdown("---")

        # Sélecteur de thème principal (uniquement pour les PV et rapports d'activités)
        docs_avec_themes = ["pv_reunion_mensuelle", "pv_coges", "pv_ag", "rapport_supervision_asc", "rapport_plaintes", "rapport_formation"]

        theme_principal = ""
        if doc_key in docs_avec_themes:
            st.markdown("### 🎯 Thème principal")
            themes_disponibles = [
                "Santé maternelle (CPN, accouchements, PF, PTME)",
                "Santé infantile (PEV, croissance, malnutrition)",
                "Paludisme (dépistage, traitement, prévention)",
                "Hygiène et infection",
                "Gouvernance (réunions, COGES)",
                "Surveillance épidémiologique",
                "Pharmacie et médicaments",
                "Nutrition",
                "IEC/CCC (sensibilisation)",
                "Activités communautaires (ASC)",
                "Gestion des équipements",
                "Rapports et données"
            ]
            theme_principal = st.selectbox(
                "Choisir le thème principal du document",
                themes_disponibles
            )

        st.markdown("---")

        if doc_key:
            donnees = get_form_fields(doc_key)
            # Ajouter le contexte du CSR aux données
            donnees["contexte"] = get_contexte_csr()
            # Ajouter les thèmes sélectionnés
            if theme_principal:
                donnees["themes"] = f"- {theme_principal}"
            else:
                donnees["themes"] = ""

            # Dossier de sauvegarde (répertoire de l'application)
            dossier_sortie = os.path.join(os.path.dirname(os.path.abspath(__file__)), "documents_generes")
            if not os.path.exists(dossier_sortie):
                os.makedirs(dossier_sortie)

        st.markdown("---")

        if st.button("🚀 Générer le document", type="primary"):
            with st.spinner("Génération en cours..."):
                # Cas spécial: Liste Personnel Centre (statique, sans IA)
                if doc_key == "liste_personnel_centre":
                    personnel_data = [
                        ("1", "Kouassi Yao", "Chef de Centre", "0102030401", "Infirmerie"),
                        ("2", "Koné Abibata", "Major / Sage-femme", "0102030402", "Maternité"),
                        ("3", "Touré Fatoumata", "Chargée PEV", "0102030403", "PEV"),
                        ("4", "Koffi Aka", "Chargé Paludisme", "0102030404", "Consultation"),
                        ("5", "N'Guessan Kouamé", "Chargé VIH/PTME", "0102030405", "VIH"),
                        ("6", "Kouakou Akissi", "Chargée CPN", "0102030406", "Maternité"),
                        ("7", "Bamba Sékou", "Chargé Pharmacie", "0102030407", "Pharmacie"),
                        ("8", "Kra Adjo", "Agent d'entretien", "0102030408", "Nettoyage"),
                        ("9", "Dibi Franck", "Planton", "0102030409", "Accueil"),
                        ("10", "Kouamé Bertine", "Secrétaire", "0102030410", "Secrétariat"),
                        ("11", "Gnahoua Olivier", "Gardien", "0102030411", "Sécurité"),
                        ("12", "Konan Blanche", "ASC", "0102030412", "Communautaire"),
                    ]

                    contenu = f"""LISTE DU PERSONNEL DU CSR NAGNENEFOUN

    I. EN-TÊTE OFFICIEL
    RÉPUBLIQUE DE CÔTE D'IVOIRE
    Union – Discipline – Travail
    MINISTÈRE DE LA SANTÉ
    RÉGION SANITAIRE DU PORO
    DISTRICT SANITAIRE DE KORHOGO 1
    {donnees.get('nom_etablissement', 'CSR NAGNENEFOUN')}

    II. LISTE DU PERSONNEL (TABLEAU)
    N° | Nom & Prénoms | Fonction | Contact | Service"""

                    for row in personnel_data:
                        contenu += f"\n| {' | '.join(row)} |"

                    contenu += f"""

    III. RÉCAPITULATIF
    - Effectif total: 12 agents
    - Infirmiers: 4
    - Sages-femmes: 2
    - Personnel d'appui: 4
    - ASC: 1
    - Secrétaire: 1

    IV. OBSERVATIONS
    - Cette liste est établie pour l'année {donnees.get('periode', '2026')}
    - Tout changement de personnel doit être signalé au District Sanitaire de KORHOGO 1

    V. APPROBATION
    - Vu par le Chef de Centre:
    - Date: ____/____/{donnees.get('periode', '2026')}
    - Cachet et signature:
    """
                    meta = {
                        "Établissement": donnees.get("nom_etablissement", ""),
                        "Période": donnees.get("periode", "")
                    }
                    doc = creer_document_word(type_doc, contenu, meta)

                    from io import BytesIO
                    buffer = BytesIO()
                    doc.save(buffer)
                    buffer.seek(0)

                    # Sauvegarder dans le dossier
                    nom_fichier = f"{type_doc}_{donnees.get('nom_etablissement', 'document')}.docx"
                    chemin_fichier = os.path.join(dossier_sortie, nom_fichier)
                    with open(chemin_fichier, "wb") as f:
                        f.write(buffer.getvalue())

                    st.success(f"✅ Document généré! Sauvegardé dans: documents_generes/")

                    st.download_button(
                        "📥 Télécharger",
                        buffer,
                        f"{type_doc}_{donnees.get('nom_etablissement', 'document')}.docx",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

                    with st.expander("👁️ Aperçu"):
                        st.text(contenu)

                elif doc_key == "plan_supervision_asc":
                    contenu = f"""PLAN DE SUPERVISION DES ASC - CSR NAGNENEFOUN - {donnees.get('periode', '2026')}

    I. CONTEXTE
    Le présent plan de supervision est établi conformément à la grille ESPC pour encadrer et évaluer les Agents de Santé Communautaires (ASC) rattachés au CSR NAGNENEFOUN. Il couvre les activités de supervision sur le terrain et au centre pour l'année {donnees.get('periode', '2026')}.

    Établissement: {donnees.get('nom_etablissement', 'CSR NAGNENEFOUN')}
    Période: {donnees.get('periode', '2026')}
    District: KORHOGO 1 (PORO)

    II. OBJECTIFS DE LA SUPERVISION
    - Objectif général: Assurer la qualité des prestations des ASC dans la communauté
    - Objectifs spécifiques:
      1. Évaluer les connaissances et compétences techniques des ASC
      2. Vérifier la qualité des données et des rapports
      3. Renforcer les capacités par des formations continues
      4. Assurer la disponibilité des intrants et médicaments
      5. Améliorer la référence des cas vers le CSR

    III. PLAN DE SUPERVISION ANNUEL (TABLEAU)
    Période | ASC/Village | Thème de la supervision | Activités détaillées | Superviseur
    |---|---|---|---|---
    | Janvier - Février | Tous les ASC | Planification annuelle et évaluation des connaissances | Organiser une réunion de planification avec tous les ASC, évaluer les connaissances sur le paludisme (TDR et traitement), vérifier les registres et rapports de l'année précédente, distribuer les nouveaux supports IEC/CCC, planifier le calendrier des stratégies avancées | Chef de Centre, Major |
    | Mars - Avril | ASC Villages Aire 1 | Supervision terrain paludisme et IEC/CCC | Accompagner l'ASC en stratégie avancée, observer une séance de sensibilisation IEC/CCC sur le paludisme, vérifier la réalisation des TDR et l'application du protocole, contrôler l'état des stocks d'intrants (TDR, ACT, MII), évaluer la qualité du remplissage des registres | Infirmier superviseur, Chargé paludisme |
    | Mai - Juin | ASC Villages Aire 2 | Campagne CPS et PEV communautaire | Superviser la campagne de chimio-prévention du paludisme saisonnier (CPS), vérifier l'administration correcte des doses, observer les séances de vaccination PEV en stratégie avancée, évaluer la gestion de la chaîne de froid, contrôler les formulaires de rapport CPS | IDE, Chargé PEV |
    | Juillet - Août | Tous les ASC | Nutrition et dépistage malnutrition | Organiser une formation sur le dépistage de la malnutrition, superviser les séances de démonstration nutritionnelle, vérifier l'utilisation du périmètre brachial (MUAC), évaluer la référence des cas de malnutrition vers le CSR, contrôler la tenue du registre nutrition | Infirmier, Nutritionniste |
    | Septembre - Octobre | ASC Villages Aire 3 | VIH/PTME et suivi des patients perdus de vue | Vérifier l'orientation des femmes enceintes pour la PTME, évaluer le dépistage VIH dans la communauté, superviser le suivi des patients sous ARV perdus de vue, contrôler la tenue du registre VIH, organiser une séance de sensibilisation sur le VIH | Chargé VIH, Sage-femme |
    | Novembre - Décembre | Tous les ASC | Évaluation annuelle et bilan N+1 | Réaliser l'évaluation annuelle des performances de chaque ASC, compiler les données de supervision de l'année, organiser une réunion de bilan avec tous les ASC, identifier les besoins en formation pour l'année N+1, élaborer le rapport annuel de supervision | Chef de Centre, Major |

    IV. GRILLE D'ÉVALUATION DES ASC
    Les ASC sont évalués selon les critères suivants:
    1. Accueil et relation communautaire - Note A/B/C
    2. Qualité des sensibilisations IEC/CCC - Note A/B/C
    3. Compétence en dépistage et TDR paludisme - Note A/B/C
    4. Gestion des intrants et médicaments - Note A/B/C
    5. Qualité des rapports et registres - Note A/B/C
    6. Taux de référence des cas vers le CSR - Note A/B/C
    7. Hygiène et tenue du poste - Note A/B/C
    8. Participation aux activités du CSR - Note A/B/C
    Légende: A = Bon (satisfaisant), B = Moyen (à améliorer), C = Faible (nécessite formation)

    V. RESPONSABILITÉS
    - Chef de Centre: Supervision globale et validation des rapports
    - Major: Coordination des activités de supervision
    - Infirmier superviseur: Supervisions terrain et formation des ASC
    - Chargé PEV: Supervision des activités PEV et CPS
    - Sage-femme: Supervision des activités PTME et santé maternelle

    VI. AFFICHAGE
    - Lieu d'affichage: Tableau d'affichage du CSR NAGNENEFOUN
    - Période d'affichage: {donnees.get('periode', '2026')}
    - Responsable de l'affichage: Chef de Centre adjoint
    """
                    meta = {
                        "Établissement": donnees.get("nom_etablissement", ""),
                        "Période": donnees.get("periode", "")
                    }
                    doc = creer_document_word(type_doc, contenu, meta)

                    from io import BytesIO
                    buffer = BytesIO()
                    doc.save(buffer)
                    buffer.seek(0)

                    nom_fichier = f"{type_doc}_{donnees.get('nom_etablissement', 'document')}.docx"
                    chemin_fichier = os.path.join(dossier_sortie, nom_fichier)
                    with open(chemin_fichier, "wb") as f:
                        f.write(buffer.getvalue())

                    st.success(f"✅ Document généré! Sauvegardé dans: documents_generes/")

                    st.download_button(
                        "📥 Télécharger",
                        buffer,
                        f"{type_doc}_{donnees.get('nom_etablissement', 'document')}.docx",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

                    with st.expander("👁️ Aperçu"):
                        st.text(contenu)

                else:
                    prompts = PROMPTS.get(doc_key)

                    if prompts:
                        sections = get_sections_template(doc_key)
                        sections_str = "\n".join([f"I. {s}" for s in sections])

                        # Ajouter les sections aux données
                        donnees["sections"] = sections_str

                    user_prompt = prompts["user"].format(**donnees)
                    contenu = generer_avec_groq(prompts["system"], user_prompt)

                    if "Erreur" in contenu:
                        st.error(contenu)
                    else:
                        meta = {
                            "Établissement": donnees.get("nom_etablissement", ""),
                            "Période": donnees.get("periode", "")
                        }

                        doc = creer_document_word(type_doc, contenu, meta)

                        from io import BytesIO
                        buffer = BytesIO()
                        doc.save(buffer)
                        buffer.seek(0)

                        # Sauvegarder dans le dossier
                        nom_fichier = f"{type_doc}_{donnees.get('nom_etablissement', 'document')}.docx"
                        chemin_fichier = os.path.join(dossier_sortie, nom_fichier)
                        with open(chemin_fichier, "wb") as f:
                            f.write(buffer.getvalue())

                        st.success(f"✅ Document généré! Sauvegardé dans: documents_generes/")

                        st.download_button(
                            "📥 Télécharger",
                            buffer,
                            f"{type_doc}_{donnees.get('nom_etablissement', 'document')}.docx",
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )

                        with st.expander("👁️ Aperçu"):
                            st.text(contenu)

if __name__ == "__main__":
    main()
