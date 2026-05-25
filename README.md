# ESPC Generator - Documentation d'Utilisation

## Application Mise à Jour ✅

L'application a été améliorée avec les nouvelles fonctionnalités de gestion du personnel et des nominations.

### 🆕 Nouvelles Fonctionnalités

#### 1. Gestion du Personnel
- **Navigation**: Menu → "Gestion Personnel"
- **Fonctionnalités**:
  - Liste du personnel par catégorie
  - Ajouter/Modifier personnel
  - Fiches de poste préfabriquées
  - Nominations

#### 2. Fiches de Poste
- Templates pré-définis pour chaque catégorie:
  - CIM (Agent de Promotion de la Santé)
  - CNH (Chef de Négociation et de Hiérarchie)
  - CNM (Agent de Network Mobile)
  - IDE (Infirmier Diplômé d'État)
  - SFDE (Technicien de Laboratoire)
  - Agent d'Hygiène Hospitalière
  - Fille de Salle
  - Gardien
  - Ambulancier

#### 3. Nominations
- Enregistrement des nominations par session
- Génération automatique des fiches de nomination

#### 4. Checklists de Préparation
- **Nouvelle option**: "Checklist Préparation" dans "Générer Documents"
- Sections complètes:
  - Documents administratifs
  - Données statistiques
  - Infrastructures et équipements
  - Personnel
  - Activités communautaires
  - Santé maternelle
  - Santé infantile
  - Hygiène et infections
  - Pharmacie
  - Suivi et rapports

### 📋 Format 4 Pages
Tous les documents sont générés en format A4 prêt à l'emploi pour impression.

### 🚀 Comment Utiliser

1. **Démarrer l'application**:
   ```bash
   bash lancer.sh
   ```

2. **Ajouter du personnel**:
   - Menu → "Gestion Personnel" → "Ajouter/Modifier"
   - Remplir les informations (nom, catégorie, poste, etc.)

3. **Générer des fiches de poste**:
   - Sélectionner un personnel
   - Le template est pré-rempli avec les missions et qualifications standards
   - Personnaliser si nécessaire
   - Générer le document Word

4. **Créer des nominations**:
   - Menu → "Gestion Personnel" → "Nominations"
   - Choisir le personnel et le poste
   - Définir la session et la durée

5. **Utiliser les checklists**:
   - Menu → "Générer Documents" → "Checklist Préparation"
   - Prévisualiser et télécharger en Word
   - Marquer comme terminée

6. **Suivre l'historique**:
   - Menu → "Historique"
   - Voir tous les documents, checklists et nominations

### 📁 Fichiers Créés

- `postes.json`: Modèles de postes par catégorie
- `templates_checklist.json`: Checklists complètes
- `update_database.py`: Script de mise à jour
- Tables ajoutées à la base:
  - `personnel`
  - `fiches_poste`
  - `nominations`
  - `checklists`

### 🎯 Avantages

- **Gain de temps**: Templates pré-remplis
- **Conformité**: Respect des exigences ESPC
- **Traçabilité**: Historique complet des actions
- **Simplicité**: Interface intuitive pour les responsables

L'application est maintenant prête pour une gestion complète du centre de santé conforme aux normes ESPC.