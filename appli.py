import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time

# -----------------------------
# Fonctions de simulation
# -----------------------------

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

# -----------------------------
# Interface Streamlit
# -----------------------------

st.set_page_config(page_title="Simulation PV Dynamique", layout="centered")
st.title("☀️ Simulation Dynamique Énergie Photovoltaïque")

# Paramètres utilisateur
puissance = st.slider("🔋 Puissance Crête (kWc)", 1.0, 20.0, 5.0, 0.5)
batterie = st.slider("🔋 Capacité Batterie (kWh)", 0.0, 20.0, 10.0, 0.5)
rendement = st.slider("⚙️ Rendement Système", 0.5, 1.0, 0.85, 0.01)
nb_jours = st.slider("📆 Nombre de jours à simuler", 1, 30, 3)

if st.button("🚀 Lancer la simulation dynamique"):
    st.subheader("⏱️ Simulation en cours...")
    placeholder = st.empty()
    progress_bar = st.progress(0)

    # Initialisation
    heures, prod, cons, stock = [], [], [], []
    energie_stockee = 0.0
    total_steps = nb_jours * 24

    for step in range(total_steps):
        h = step % 24
        jour = step // 24
        heure = datetime(2024, 1, 1) + timedelta(days=jour + 100, hours=h)
        heures.append(heure)

        p = production_solaire(h, jour + 100, puissance, rendement)
        c = consommation_foyer(h)
        surplus = p - c

        if surplus >= 0:
            energie_stockee = min(energie_stockee + surplus, batterie)
        else:
            energie_stockee = max(energie_stockee - abs(surplus), 0)

        prod.append(p)
        cons.append(c)
        stock.append(energie_stockee)

        # Affichage dynamique
        with placeholder.container():
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(heures, prod, label="Production", color='orange')
            ax.plot(heures, cons, label="Consommation", color='blue')
            ax.plot(heures, stock, label="Batterie", color='green')
            ax.set_xlabel("Temps")
            ax.set_ylabel("Énergie (kWh)")
            ax.set_title(f"🕒 Heure simulée : {heure.strftime('%Y-%m-%d %H:%M')}")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

        progress_bar.progress((step + 1) / total_steps)
        time.sleep(0.1)  # ralentir pour effet dynamique

    # Résultat final
    df = pd.DataFrame({
        "Heure": heures,
        "Production (kWh)": prod,
        "Consommation (kWh)": cons,
        "Stock Batterie (kWh)": stock
    })

    csv = df.to_csv(index=False).encode('utf-8')
    st.success("✅ Simulation terminée.")
    st.download_button("📥 Télécharger les résultats (CSV)", csv, file_name="simulation_pv.csv")
