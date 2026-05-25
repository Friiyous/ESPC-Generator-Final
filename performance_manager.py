"""
Gestion des Performances Module
"""

import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import (
    get_etablissements,
    get_periodes,
    get_donnees_periode,
    get_personnel,
    get_nominations,
    get_checklists,
)


class PerformanceManager:
    def __init__(self):
        self.colors = {
            "primary": "#4CAF50",
            "secondary": "#2196F3",
            "warning": "#FF9800",
            "danger": "#F44336",
            "success": "#8BC34A",
        }

    def get_personnel_performance(self, personnel_id=None):
        """Calculer les performances du personnel"""
        personnel = get_personnel()

        if personnel_id:
            personnel = [p for p in personnel if p["id"] == personnel_id]

        performance_data = []
        for pers in personnel:
            # Calculer score basé sur nominations et activités
            score = self.calculate_personnel_score(pers)
            performance_data.append(
                {
                    "nom": f"{pers['prenom']} {pers['nom']}",
                    "categorie": pers["categorie"],
                    "score": score,
                    "statut": pers["statut"],
                    "date_embauche": pers["date_embauche"],
                }
            )

        return performance_data

    def calculate_personnel_score(self, personnel):
        """Calculer le score de performance d'un membre du personnel"""
        score = 50  # Base score

        # Bonus pour les nominations
        nominations = get_nominations()
        personnel_nominations = [
            n for n in nominations if n["personnel_id"] == personnel["id"]
        ]
        score += len(personnel_nominations) * 10

        # Bonus pour les activités récentes
        if personnel["statut"] == "actif":
            score += 20

        # Bonus pour l'ancienneté
        if personnel["date_embauche"]:
            embauche = datetime.strptime(personnel["date_embauche"], "%Y-%m-%d")
            anciennete = (datetime.now() - embauche).days
            if anciennete > 365:  # Plus d'un an
                score += 10

        return min(score, 100)  # Max score of 100

    def get_etablishment_performance(self, etablissement_id):
        """Calculer les performances de l'établissement"""
        periodes = get_periodes(etablissement_id)

        performance_data = []
        for periode in periodes:
            donnees = get_donnees_periode(periode["id"])

            # Calculer score global
            score = self.calculate_period_score(donnees)

            performance_data.append(
                {
                    "periode": periode["periode"],
                    "trimestre": periode["trimestre"],
                    "annee": periode["annee"],
                    "score": score,
                    "nombre_indicateurs": len(donnees),
                    "completude": self.calculate_completeness(donnees),
                }
            )

        return performance_data

    def calculate_period_score(self, donnees):
        """Calculer le score pour une période donnée"""
        if not donnees:
            return 0

        # Simple scoring based on positive responses
        positive_count = sum(1 for d in donnees if d["valeur"] == "Oui")
        total_count = len(donnees)

        return (positive_count / total_count) * 100 if total_count > 0 else 0

    def calculate_completeness(self, donnees):
        """Calculer le taux de complétude"""
        if not donnees:
            return 0

        completed = sum(1 for d in donnees if d["valeur"] and d["valeur"] != "")
        total = len(donnees)

        return (completed / total) * 100

    def create_performance_dashboard(self):
        """Create the performance dashboard"""
        st.header("📊 Dashboard de Performance")

        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["Personnel", "Établissement", "Comparatif"])

        with tab1:
            self.personnel_performance_view()

        with tab2:
            self.etablishment_performance_view()

        with tab3:
            self.comparative_view()

    def personnel_performance_view(self):
        """Personnel performance view"""
        personnel = get_personnel()

        if not personnel:
            st.info("Aucun personnel enregistré")
            return

        # Filter by category
        categories = list(set(p["categorie"] for p in personnel))
        category_filter = st.selectbox("Filtrer par catégorie", ["Toutes"] + categories)

        filtered_personnel = personnel
        if category_filter != "Toutes":
            filtered_personnel = [
                p for p in personnel if p["categorie"] == category_filter
            ]

        # Calculate performance
        performance_data = self.get_personnel_performance()

        # Create DataFrame
        df = pd.DataFrame(performance_data)

        # Display performance chart
        fig = px.bar(
            df,
            x="nom",
            y="score",
            color="categorie",
            title="Performance du Personnel",
            labels={"score": "Score de Performance", "nom": "Personnel"},
        )
        fig.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

        # Performance table
        st.subheader("Détails des Performances")
        st.dataframe(
            df.sort_values("score", ascending=False),
            column_config={
                "score": st.column_config.ProgressColumn(
                    "Score",
                    help="Performance du personnel",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                )
            },
        )

        # Recommendations
        st.subheader("Recommandations")
        low_performers = df[df["score"] < 60]
        if not low_performers.empty:
            st.warning(f"⚠️ {len(low_performers)} agent(s) nécessitent une attention:")
            for _, row in low_performers.iterrows():
                st.write(
                    f"- {row['nom']}: Score {row['score']:.1f}% - Considérer une formation ou mentorat"
                )

        # High performers
        high_performers = df[df["score"] >= 80]
        if not high_performers.empty:
            st.success(f"🎉 {len(high_performers)} agent(s) performants:")
            for _, row in high_performers.iterrows():
                st.write(
                    f"- {row['nom']}: Score {row['score']:.1f}% - Bonne performance, continuer à encourager"
                )

    def etablishment_performance_view(self):
        """Establishment performance view"""
        etablissements = get_etablissements()

        if not etablissements:
            st.info("Aucun établissement enregistré")
            return

        etab = etablissements[0]  # Take first establishment
        performance_data = self.get_etablishment_performance(etab["id"])

        if not performance_data:
            st.info("Aucune donnée de performance disponible")
            return

        # Create DataFrame
        df = pd.DataFrame(performance_data)

        # Performance over time
        fig = px.line(
            df,
            x="periode",
            y="score",
            title="Évolution de la Performance",
            labels={"score": "Score de Performance", "periode": "Période"},
        )
        fig.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

        # Completeness chart
        fig2 = px.bar(
            df,
            x="periode",
            y="completude",
            title="Taux de Complétude",
            labels={"completude": "Complétude (%)", "periode": "Période"},
        )
        fig2.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig2, use_container_width=True)

        # Summary statistics
        st.subheader("Statistiques Récapitulatives")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Performance Moyenne", f"{df['score'].mean():.1f}%")
        with col2:
            st.metric("Meilleure Performance", f"{df['score'].max():.1f}%")
        with col3:
            st.metric("Taux de Complétude Moyen", f"{df['completude'].mean():.1f}%")
        with col4:
            st.metric("Périodes Évaluées", len(df))

    def comparative_view(self):
        """Comparative performance view"""
        st.subheader("Comparaison des Performances")

        # Get all establishments
        etablissements = get_etablissements()

        if len(etablissements) < 2:
            st.info("Au moins 2 établissements nécessaires pour la comparaison")
            return

        # Multi-select for comparison
        selected_etabs = st.multiselect(
            "Sélectionner les établissements à comparer",
            [e["nom"] for e in etablissements],
            default=[e["nom"] for e in etablissements[:2]],
        )

        if len(selected_etabs) < 2:
            st.info("Sélectionnez au moins 2 établissements")
            return

        # Calculate performance for each selected establishment
        comparison_data = []
        for etab_name in selected_etabs:
            etab = next(e for e in etablissements if e["nom"] == etab_name)
            performance_data = self.get_etablishment_performance(etab["id"])

            if performance_data:
                avg_score = sum(p["score"] for p in performance_data) / len(
                    performance_data
                )
                comparison_data.append(
                    {
                        "etablissement": etab_name,
                        "performance": avg_score,
                        "personnel_count": len(get_personnel()),
                    }
                )

        # Create comparison chart
        df = pd.DataFrame(comparison_data)

        fig = px.bar(
            df,
            x="etablissement",
            y="performance",
            title="Comparaison des Performances",
            labels={
                "performance": "Performance Moyenne",
                "etablissement": "Établissement",
            },
        )
        fig.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

        # Detailed comparison
        st.subheader("Analyse Comparative")
        for data in comparison_data:
            st.write(f"""
**{data["etablissement"]}**
- Performance moyenne: {data["performance"]:.1f}%
- Nombre de personnel: {data["personnel_count"]}
            """)


# Global performance manager instance
performance_manager = PerformanceManager()
