import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Datacenter", layout="wide")
st.title("Dashboard metier - Datacenter")

# --- Chargement des donnees ---
equipment = pd.read_csv("equipment_raw_cleaned.csv")
maintenance = pd.read_csv("maintenance_raw_cleaned.csv")
incidents = pd.read_csv("incidents_raw_cleaned.csv")

equipment["temperature"] = pd.to_numeric(equipment["temperature"], errors="coerce")
equipment["energy_kwh"] = pd.to_numeric(equipment["energy_kwh"], errors="coerce")
maintenance["duration_min"] = pd.to_numeric(maintenance["duration_min"], errors="coerce")

# --- Chargement des donnees rejetees ---
eq_cols = ["equipment_id", "site", "zone", "temperature", "energy_kwh", "status", "recorded_at"]
maint_cols = ["task_id", "site", "technician", "duration_min", "result", "planned_at"]
inc_cols = ["incident_id", "equipment_id", "severity", "incident_type", "opened_at", "resolved"]

eq_rejected = pd.read_csv("equipment_raw_rejected.csv", header=None, names=eq_cols)
maint_rejected = pd.read_csv("maintenance_raw_rejected.csv", header=None, names=maint_cols)
inc_rejected = pd.read_csv("incidents_raw_rejected.csv", header=None, names=inc_cols)

eq_ids_rejected = eq_rejected["equipment_id"].tolist()

# --- Filtre global par site ---
sites = ["Tous"] + sorted(equipment["site"].unique().tolist())
filtre_site = st.selectbox("Site", sites)

if filtre_site != "Tous":
    equipment = equipment[equipment["site"] == filtre_site]
    maintenance = maintenance[maintenance["site"] == filtre_site]
    eq_ids = equipment["equipment_id"].tolist()
    incidents = incidents[incidents["equipment_id"].isin(eq_ids)]

# IDs valides après filtre site, sans les rejetés
eq_ids_valid = equipment["equipment_id"].tolist()
equipment_kpi = equipment[~equipment["equipment_id"].isin(eq_ids_rejected)]
incidents_kpi = incidents[incidents["equipment_id"].isin(eq_ids_valid)]

st.divider()

# --- Indicateurs cles ---
st.header("Indicateurs cles")
col1, col2, col3, col4 = st.columns(4)

nb_incidents_ouverts = len(incidents_kpi[incidents_kpi["resolved"] == "no"])
nb_critical = len(incidents_kpi[incidents_kpi["severity"].str.upper() == "CRITICAL"])
temp_max = equipment_kpi["temperature"].max()
energie_totale = equipment_kpi["energy_kwh"].sum()

col1.metric("Incidents ouverts", nb_incidents_ouverts)
col2.metric("Incidents critiques", nb_critical)
col3.metric("Temperature max (C)", f"{temp_max:.1f}")
col4.metric("Energie totale (kWh)", f"{energie_totale:.1f}")

st.divider()

# --- Graphiques ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Temperature par equipement")
    fig, ax = plt.subplots()
    colors = ["red" if t > 40 or t < 0 else "steelblue" for t in equipment["temperature"]]
    ax.bar(equipment["equipment_id"], equipment["temperature"], color=colors)
    ax.axhline(40, color="orange", linestyle="--", linewidth=1, label="Seuil haut (40C)")
    ax.axhline(0, color="blue", linestyle="--", linewidth=1, label="Seuil bas (0C)")
    ax.set_ylabel("Temperature (C)")
    ax.legend()
    st.pyplot(fig)

with col_right:
    st.subheader("Incidents par severite")
    severity_counts = incidents["severity"].str.upper().value_counts()
    colors_sev = {"CRITICAL": "red", "HIGH": "orange", "MEDIUM": "gold", "LOW": "green"}
    bar_colors = [colors_sev.get(s, "gray") for s in severity_counts.index]
    fig2, ax2 = plt.subplots()
    ax2.bar(severity_counts.index, severity_counts.values, color=bar_colors)
    ax2.set_ylabel("Nombre d'incidents")
    st.pyplot(fig2)

col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("Statut des equipements")
    status_counts = equipment["status"].str.lower().value_counts()
    fig3, ax3 = plt.subplots()
    ax3.pie(status_counts.values, labels=status_counts.index, autopct="%1.0f%%", startangle=90)
    st.pyplot(fig3)

with col_right2:
    st.subheader("Taux de resolution des incidents")
    resolved_counts = incidents["resolved"].value_counts()
    fig4, ax4 = plt.subplots()
    ax4.pie(resolved_counts.values, labels=resolved_counts.index,
            colors=["green", "red"], autopct="%1.0f%%", startangle=90)
    st.pyplot(fig4)

st.divider()

# --- Onglets donnees ---
tab1, tab2, tab3 = st.tabs(["Equipements", "Incidents", "Maintenances"])

with tab1:
    statuts = ["Tous"] + sorted(equipment["status"].str.lower().unique().tolist())
    filtre_status = st.selectbox("Filtrer par statut", statuts)
    df_equipment = equipment.copy()
    df_equipment["status"] = df_equipment["status"].str.lower()
    if filtre_status != "Tous":
        df_equipment = df_equipment[df_equipment["status"] == filtre_status]
    st.caption(f"{len(df_equipment)} equipement(s) affiches")
    st.dataframe(df_equipment, use_container_width=True)

with tab2:
    severites = ["Tous"] + sorted(incidents["severity"].str.upper().unique().tolist())
    filtre_severity = st.selectbox("Filtrer par severite", severites)
    df_incidents = incidents.copy()
    df_incidents["severity"] = df_incidents["severity"].str.upper()
    if filtre_severity != "Tous":
        df_incidents = df_incidents[df_incidents["severity"] == filtre_severity]
    st.caption(f"{len(df_incidents)} incident(s) affiches")
    st.dataframe(df_incidents, use_container_width=True)

with tab3:
    resultats = ["Tous"] + sorted(maintenance["result"].str.lower().unique().tolist())
    filtre_result = st.selectbox("Filtrer par resultat", resultats)
    df_maintenance = maintenance.copy()
    df_maintenance["result"] = df_maintenance["result"].str.lower()
    if filtre_result != "Tous":
        df_maintenance = df_maintenance[df_maintenance["result"] == filtre_result]
    st.caption(f"{len(df_maintenance)} maintenance(s) affichee(s)")
    st.dataframe(df_maintenance, use_container_width=True)

st.divider()

# --- Donnees rejetees ---
st.header("Données à valider")
st.caption("Ces lignes ont été exclues des indicateurs clés car elles contiennent des erreurs.")

rtab1, rtab2, rtab3 = st.tabs(["Equipements", "Incidents", "Maintenances"])

with rtab1:
    st.caption(f"{len(eq_rejected)} ligne(s)")
    st.dataframe(eq_rejected, use_container_width=True)

with rtab2:
    st.caption(f"{len(inc_rejected)} ligne(s)")
    st.dataframe(inc_rejected, use_container_width=True)

with rtab3:
    st.caption(f"{len(maint_rejected)} ligne(s)")
    st.dataframe(maint_rejected, use_container_width=True)
