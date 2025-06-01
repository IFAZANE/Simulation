import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from io import StringIO

# ----------------------------------------
# Fonctions de simulation
# ----------------------------------------

def production_solaire(h, jour_annee, puissance_crete, rendement):
    if 6 <= h <= 18:
        heure_solaire = (np.pi / 12) * (h - 6)
        saison = np.cos((jour_annee - 172) * 2 * np.pi / 365)
        return max(puissance_crete * rendement * np.sin(heure_solaire) * (0.6 + 0.4 * saison), 0)
    return 0

def consommation_foyer(h):
    if 6 <= h <= 9:
        return 1.5
    elif 18 <= h <= 22:
        return 2.0
    return 0.5

def simuler(puissance_crete, capacite_batterie, rendement, nb_jours):
    heures, prod, cons, stock = [], [], [], []
    energie_stockee = 0.0
    jour_depart = 100  # printemps

    for jour in range(nb_jours):
        for h in range(24):
            heure = datetime(2024, 1, 1) + timedelta(days=jour + jour_depart, hours=h)
            heures.append(heure)

            p = production_solaire(h, jour + jour_depart, puissance_crete, rendement)
            c = consommation_foyer(h)
            surplus = p - c

            if surplus >= 0:
                energie_stockee = min(energie_stockee + surplus, capacite_batterie)
            else:
                energie_stockee = max(energie_stockee - abs(surplus), 0)

            prod.append(p)
            cons.append(c)
            stock.append(energie_stockee)

    return pd.DataFrame({
        "Heure": heures,
        "Production (kWh)": prod,
        "Consommation (kWh)": cons,
        "Stock Batterie (kWh)": stock
    })

# ----------------------------------------
# Interface Streamlit
# ----------------------------------------

st.set_page_config(page_title="Simulation Photovoltaïque", layout="centered")
st.title("☀️ Simulation Énergie Photovoltaïque")

# Entrée utilisateur
puissance = st.slider("Puissance Crête (kWc)", 1.0, 20.0, 5.0, 0.5)
batterie = st.slider("Capacité Batterie (kWh)", 0.0, 20.0, 10.0, 0.5)
rendement = st.slider("Rendement Système", 0.5, 1.0, 0.85, 0.01)
nb_jours = st.slider("Nombre de jours simulés", 1, 30, 7)

# Bouton de lancement
if st.button("Lancer la simulation"):
    df = simuler(puissance, batterie, rendement, nb_jours)

    # Affichage du graphique
    st.subheader("📊 Évolution horaire")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df["Heure"], df["Production (kWh)"], label="Production", color='orange')
    ax.plot(df["Heure"], df["Consommation (kWh)"], label="Consommation", color='blue')
    ax.plot(df["Heure"], df["Stock Batterie (kWh)"], label="Batterie", color='green')
    ax.set_xlabel("Temps")
    ax.set_ylabel("Énergie (kWh)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # Téléchargement CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger les données en CSV",
        data=csv,
        file_name="simulation_photovoltaique.csv",
        mime='text/csv',
    )
