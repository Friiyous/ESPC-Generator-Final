"""
Application Streamlit - Générateur Documents ESPC
Conforme à la grille ESPC
"""
import streamlit as st
import os
import json
from groq import Groq
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

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

# Essayer d'abord avec st.secrets (Streamlit Cloud)
try:
    if "GROQ_API_KEY" in st.secrets:
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    else:
        GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
except:
    # Mode local
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    st.error("❌ Clé API non configurée!")
    st.info("""
    Pour configurer:
    1. Allez dans Settings > Secrets
    2. Ajoutez: GROQ_API_KEY = "votre_clé"
    3. Redéployez l'app
    """)
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# =============================================================================
# CHARGEMENT DES DONNÉES DU CSR
# =============================================================================

@st.cache_data
def charger_donnees_csr():
    """Charge les données du CSR depuis le fichier JSON"""
    try:
        with open("data_csr.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

donnees_csr = charger_donnees_csr()

def get_contexte_csr():
    """Génère le contexte contextualisé pour les prompts"""
    if not donnees_csr:
        return ""

    e = donnees_csr["etablissement"]
    p = donnees_csr["population"]
    r = donnees_csr["ressources_humaines"]
    s = donnees_csr["statistiques_cles"]

    contexte = f"""
CONTEXTE DU CSR {e['nom']} ({e['region']}, District {e['district']}):
- Population totale: {p['totale']} habitants
- Grossesses attendues: {p['grossesses_attendues']}
- Personnel: {r['IDE']} IDE, {r['SFDE']} SFDE, {r['aides_soignants']} aides-soignants, {r['agents_hygiene']} agents hygiene, {r['filles_salle']} filles de salle, {r['asc']} ASC
- Statistiques clés: CPN1: {s['cpn1']}, CPN4: {s['cpn4']}, Accouchements assistés: {s['accouchements_assistes']}
- Activités principales: Consultations, CPN, Accouchements, PEV, Paludisme, VIH, Nutrition, IEC/CCC
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
        "system": """Tu es un assistant spécialisé dans les PV pour CSR en Côte d'Ivoire.

RÈGLES TRÈS IMPORTANTES:
1. Utilise les données réelles du CSR (personnel, statistiques, activités)
2. Génère un contenu COMPLET sans placeholders
3. N'inclus JAMAIS de section "LISTE DE PRÉSENCE" ou "SIGNATURES" - ces parties sont saisies manuellement""",

        "user": """Génère PV RÉUNION MENSUELLE pour {nom_etablissement}.
{contexte}

THÈMES À TRAITER:
{themes}

STRUCTURE (sans LISTE PRÉSENCE ni SIGNATURES):
I. OUVERTURE
II. LECTURE PV PRÉCÉDENT
III. ORDRE DU JOUR
IV. DÉLIBÉRATIONS (traiter les thèmes sélectionnés)
V. DÉCISIONS
VI. CLÔTURE

Génère un contenu contextualisé avec les thèmes choisis."""
    },

    "pv_coges": {
        "system": """Tu es un assistant spécialisé dans la rédaction de PV COGES pour les Centres de Santé ruraux en Côte d'Ivoire.

RÈGLES TRÈS IMPORTANTES:
1. Le terme correct est COMITÉ DE GESTION ou COGES - JAMAIS "Conseil de Gestion"
2. Utilise les données réelles du CSR (personnel, statistiques, activités)
3. N'inclus JAMAIS de section "LISTE DE PRÉSENCE" ou "SIGNATURES" - ces parties sont saisies manuellement""",

        "user": """Génère un PROCÈS-VERBAL DE RÉUNION DU COMITÉ DE GESTION (COGES) pour {nom_etablissement}.
{contexte}

THÈMES À TRAITER:
{themes}

STRUCTURE (Norme 1.02 - sans LISTE PRÉSENCE ni SIGNATURES):
I. OUVERTURE
II. LECTURE PV PRÉCÉDENT
III. ORDRE DU JOUR
IV. DÉLIBÉRATIONS (traiter les thèmes sélectionnés)
V. DÉCISIONS
VI. CLÔTURE

Génère un PV contextualisé."""
    },

    "pv_ag": {
        "system": """Tu es un assistant spécialisé dans les PV d'AG pour les Centres de Santé ruraux en Côte d'Ivoire.

RÈGLES:
1. Utilise les données réelles du CSR
2. N'inclus JAMAIS de section "LISTE DE PRÉSENCE" ou "SIGNATURES" - ces parties sont saisies manuellement""",

        "user": """Génère un PROCÈS-VERBAL D'ASSEMBLÉE GÉNÉRALE pour {nom_etablissement}.
{contexte}

THÈMES À TRAITER:
{themes}

STRUCTURE (Norme 1.03 - sans LISTE PRÉSENCE ni SIGNATURES):
I. OUVERTURE
II. ÉLECTION BUREAU
III. LECTURE PV PRÉCÉDENT
IV. ADOPTION OJ
V. DISCUSSIONS (traiter les thèmes sélectionnés)
VI. DÉCISIONS/VOTES
VII. CLÔTURE

Génère un PV contextualisé."""
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

    # PROMPTS AVEC CHAMPS - L'IA génère automatiquement
    "fiche_poste": {
        "system": """Tu es un assistant spécialisé dans les fiches de poste pour CSR en Côte d'Ivoire.
RÈGLES: Génère une fiche de poste professionnelle sans placeholders.""",
        "user": """Génère FICHE DE POSTE pour {nom_etablissement}.

INFORMATIONS:
- Titre du poste: {titre_poste}
- Missions: {missions}
- Qualifications: {qualifications}

STRUCTURE DU DOCUMENT:
{sections}

Génère une fiche complète."""
    },

    "fiche_nomination": {
        "system": """Tu es un assistant spécialisé dans les actes de nomination pour CSR en Côte d'Ivoire.
RÈGLES: Génère un acte de nomination professionnel.""",
        "user": """Génère ACTE DE NOMINATION pour {nom_etablissement}.

INFORMATIONS:
- Nom de la personne: {nom_personne}
- Fonction attribuée: {fonction}
- Date de nomination: {date_nomination}

STRUCTURE DU DOCUMENT:
{sections}
I. VU (texte réglementaire)
II. DÉSIGNE (nom et fonction)
III. MISSION
IV. DATEEFFET

Génère un acte complet."""
    },

    "programme_reunions_trimestrielles": {
        "system": """Tu es un assistant spécialisé dans les programmes de réunions pour CSR.""",
        "user": """Génère PROGRAMME RÉUNIONS TRIMESTRIELLES pour {nom_etablissement}.

INFORMATIONS:
- Période: {periode}

STRUCTURE DU DOCUMENT:
{sections}
I. INFOS GÉNÉRALES
II. CALENDRIER T1-T4
III. OBSERVATIONS
IV. AFFICHAGE

Génère un programme complet."""
    },

    "calendrier_nettoyage": {
        "system": """Tu es un assistant spécialisé dans les calendriers d'hygiène pour CSR. Norme 6.01 - À AFFICHER.""",
        "user": """Génère CALENDRIER DE NETTOYAGE pour {nom_etablissement}.

INFORMATIONS:
- Zones: {zones}
- Fréquences: {frequences}

STRUCTURE DU DOCUMENT:
{sections}
I. PRÉSENTATION
II. ZONES
III. FRÉQUENCE
IV. RESPONSABLES
V. CALENDRIER
VI. AFFICHAGE

Génère un calendrier complet (Norme 6.01)."""
    },

    "calendrier_reunions_mensuelles": {
        "system": """Tu es un assistant spécialisé dans les calendriers de réunions.""",
        "user": """Génère CALENDRIER RÉUNIONS MENSUELLES pour {nom_etablissement}.

INFORMATIONS:
- Période: {periode}

STRUCTURE DU DOCUMENT:
{sections}
I. INFOS GÉNÉRALES
II. CALENDRIER (12 mois)
III. OBSERVATIONS
IV. AFFICHAGE

Génère un calendrier complet."""
    },

    "grille_supervision_asc": {
        "system": """Tu es un assistant spécialisé dans les grilles de supervision ASC.""",
        "user": """Génère GRILLE SUPERVISION ASC pour {nom_etablissement}.

INFORMATIONS:
- Critères: {criteria}

STRUCTURE DU DOCUMENT:
{sections}
I. INFOS GÉNÉRALES
II. CRITÈRES
III. ÉVALUATION
IV. OBSERVATIONS

Génère une grille complète."""
    },

    "liste_coges": {
        "system": """Tu es un assistant spécialisé dans les listes COGES pour CSR en Côte d'Ivoire. Format grille ESPC.""",
        "user": """Génère LISTE PERSONNEL COGES pour {nom_etablissement}.

INFORMATIONS:
- Membres: {membres}

STRUCTURE DU DOCUMENT:
{sections}
I. EN-TÊTE (République de Côte d'Ivoire)
II. TABLEAU MEMBRES
III. RÉCAPITULATIF
IV. CONTACTS
V. OBSERVATIONS
VI. APPROBATION

Génère une liste complète."""
    },

    "plan_action_infections_nosocomiales": {
        "system": """Tu es un assistant spécialisé dans les plans d'action contre les infections nosocomiales.""",
        "user": """Génère PLAN ACTION INFECTIONS NOSOCOMIALES pour {nom_etablissement}.

INFORMATIONS:
- Activités: {activites}

STRUCTURE DU DOCUMENT:
{sections}
I. CONTEXTE
II. OBJECTIFS
III. ACTIVITÉS
IV. CALENDRIER
V. RESPONSABLES
VI. SUIVI

Génère un plan complet."""
    },

    "plan_supervision_asc": {
        "system": """Tu es un assistant spécialisé dans les plans de supervision ASC.""",
        "user": """Génère PLAN SUPERVISION ASC pour {nom_etablissement}.

INFORMATIONS:
- Activités: {activites}

STRUCTURE DU DOCUMENT:
{sections}
I. CONTEXTE
II. OBJECTIFS
III. ACTIVITÉS
IV. LOCALITÉS
V. CALENDRIER
VI. RESPONSABLES

Génère un plan complet."""
    },

    "rapport_formation": {
        "system": """Tu es un assistant spécialisé dans les rapports de formation. Norme 2.01 - Sans SIGNATURES ni ATTESTATION.""",
        "user": """Génère RAPPORT FORMATION pour {nom_etablissement}.
{contexte}

INFORMATIONS:
- Domaine: {domaine}
- Nombre de participants: {nb_participants}

STRUCTURE (sans SIGNATURES ni ATTESTATION):
I. INFOS GÉNÉRALES
II. OBJECTIFS
III. DOMAINE
IV. CONTENU
V. PARTICIPANTS
VI. ÉVALUATION
VII. DIFFICULTÉS
VIII. RECOMMANDATIONS

Génère un rapport contextualisé."""
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
]

# =============================================================================
# FONCTIONS
# =============================================================================

def generer_avec_groq(system_prompt, user_prompt):
    try:
        response = client.chat.completions.create(
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

    for para in contenu.split('\n'):
        if para.strip():
            if any(x in para.upper() for x in ['I.', 'II.', 'III.', 'IV.', 'V.', 'VI.', 'VII.', 'VIII.', 'IX.', 'X.']) and len(para) < 60:
                doc.add_heading(para, level=1)
            elif any(x in para.upper() for x in ['CONTEXTE', 'INFORMATIONS', 'DÉLIBÉRATIONS', 'DÉCISIONS', 'SIGNATURES', 'LISTE', 'OBSERVATIONS', 'CALENDRIER', 'OBJECTIFS', 'ACTIVITÉS', 'AFFICHAGE']) and len(para) < 50:
                doc.add_heading(para, level=2)
            else:
                doc.add_paragraph(para)

    return doc

# =============================================================================
# FORMULAIRES PRÉ-CONFORMES
# =============================================================================

def get_form_fields(doc_type):
    fields = {}

    if doc_type == "pv_reunion_mensuelle":
        st.markdown("### 📋 PV RÉUNION MENSUELLE (Conforme Grille ESPC)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        # L'IA génère automatiquement tout le contenu

    elif doc_type == "pv_coges":
        st.markdown("### 📋 PV COGES (Conforme Norme 1.02)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        # Les autres champs sont optionnels - l'IA génère automatiquement

    elif doc_type == "pv_ag":
        st.markdown("### 📋 PV ASSEMBLÉE GÉNÉRALE (Conforme Norme 1.03)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        # L'IA génère automatiquement

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
        st.markdown("### 📋 FICHE DE POSTE")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["titre_poste"] = st.text_input("Titre du poste", "Infirmier Diplômé d'État (IDE)")
        fields["missions"] = st.text_area("Missions principales (séparées par ;)", "Consultations ; Soins ; Vaccination ; Gestion des urgences")
        fields["qualifications"] = st.text_area("Qualifications (séparées par ;)", "Diplôme IDE ; Expérience en CSR ; Connaissance des protocoles")

    elif doc_type == "fiche_nomination":
        st.markdown("### 📋 FICHE DE NOMINATION")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["nom_personne"] = st.text_input("Nom et prénom de la personne nominée", "")
        fields["fonction"] = st.text_input("Fonction attribuée", "")
        fields["date_nomination"] = st.text_input("Date de nomination", "")

    elif doc_type == "programme_reunions_trimestrielles":
        st.markdown("### 📋 PROGRAMME RÉUNIONS TRIMESTRIELLES")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["periode"] = st.text_input("Période (Année)", "2026")

    elif doc_type == "calendrier_nettoyage":
        st.markdown("### 📋 CALENDRIER NETTOYAGE (Conforme Norme 6.01 - À AFFICHER)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["zones"] = st.text_area("Zones à nettoyer (séparées par ;)", "Salle de consultation ; Maternité ; Hall d'attente ; Toilettes ; Cour")
        fields["frequences"] = st.text_area("Fréquences (séparées par ;)", "Quotidien ; Hebdomadaire ; Mensuel")

    elif doc_type == "calendrier_reunions_mensuelles":
        st.markdown("### 📋 CALENDRIER RÉUNIONS MENSUELLES")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["periode"] = st.text_input("Période (Année)", "2026")

    elif doc_type == "grille_supervision_asc":
        st.markdown("### 📋 GRILLE SUPERVISION ASC (À signer ASC + Superviseur)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["criteria"] = st.text_area("Critères de supervision (séparés par ;)", "Accueil ; Sensibilisation ; Dépistage ; Référence ; Documentation")

    elif doc_type == "liste_coges":
        st.markdown("### 📋 LISTE PERSONNEL COGES (Format grille ESPC)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["membres"] = st.text_area("Membres COGES (Nom ; Fonction)", "Koffi Kouassi ; Président\nAhoua N'Guessan ; Vice-Président\nKonan Bertille ; Secrétaire")

    elif doc_type == "plan_action_infections_nosocomiales":
        st.markdown("### 📋 PLAN ACTION INFECTIONS NOSOCOMIALES")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["activites"] = st.text_area("Activités principales (séparées par ;)", "Formation personnel ; Désinfection ; Lavage des mains ; Gestion des déchets ; Surveillance")

    elif doc_type == "plan_supervision_asc":
        st.markdown("### 📋 PLAN SUPERVISION ASC (Plan annuel)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["activites"] = st.text_area("Activités de supervision (séparées par ;)", "Inspection terrain ; Formation ; Dépistage communautaire ; Référence")

    elif doc_type == "rapport_formation":
        st.markdown("### 📋 RAPPORT FORMATION (Conforme Norme 2.01 - 3 trim.)")
        fields["nom_etablissement"] = st.text_input("Établissement", "CSR NAGNENEFOUN")
        fields["domaine"] = st.text_input("Domaine de formation", "")
        fields["nb_participants"] = st.text_input("Nombre de participants", "")

    return fields

# =============================================================================
# INTERFACE PRINCIPALE
# =============================================================================

def main():
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
        # Ajouter le thème principal seulement s'il est défini
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
            prompts = PROMPTS.get(doc_key)

            if prompts:
                # Ajouter les sections du template au prompt
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
