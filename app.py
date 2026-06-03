import streamlit as st
import pandas as pd
import os
from io import BytesIO

st.set_page_config(page_title="Gestion des Offres Partenaires", layout="wide")

DB_FILE = "offres_partenaires.csv"

def charger_donnees():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df["ID"] = df["ID"].astype(int)
        return df
    return pd.DataFrame(columns=["ID", "Partenaire", "Offre", "Début", "Fin", "Modalités"])

def sauvegarder_donnees(df):
    df.to_csv(DB_FILE, index=False)

def exporter_en_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Offres Partenaires')
    processed_data = output.getvalue()
    return processed_data

if "df" not in st.session_state:
    st.session_state.df = charger_donnees()

st.title("🤝 Gestion Dynamique des Offres Partenaires")
st.write("Ajoutez, consultez et modifiez vos modalités de partenariat en temps réel.")

st.sidebar.header("📝 Formulaire Offre")

options_mode = ["Ajouter une nouvelle offre"]
if not st.session_state.df.empty:
    options_mode.append("Modifier une offre existante")
    options_mode.append("Supprimer une offre")

mode = st.sidebar.radio("Action :", options_mode)

if mode == "Ajouter une nouvelle offre":
    st.sidebar.subheader("Nouvelle Offre")
    partenaire = st.sidebar.text_input("Nom du Partenaire")
    offre = st.sidebar.text_input("Nom de l'Offre")
    debut = st.sidebar.text_input("Mois de Début", placeholder="Ex: Janvier 2026")
    fin = st.sidebar.text_input("Mois de Fin", placeholder="Ex: En cours")
    modalites = st.sidebar.text_area("Modalités / Conditions")

    if st.sidebar.button("✨ Enregistrer l'offre", type="primary"):
        if partenaire and offre and modalites:
            nouveau_id = int(st.session_state.df["ID"].max()) + 1 if not st.session_state.df.empty else 1
            nouvelle_ligne = {
                "ID": nouveau_id, "Partenaire": partenaire, "Offre": offre,
                "Début": debut, "Fin": fin, "Modalités": modalites
            }
            st.session_state.df = pd.concat(
                [st.session_state.df, pd.DataFrame([nouvelle_ligne])],
                ignore_index=True
            )
            sauvegarder_donnees(st.session_state.df)
            st.sidebar.success("Offre ajoutée avec succès !")
            st.rerun()
        else:
            st.sidebar.error("Veuillez remplir les champs obligatoires (Partenaire, Offre, Modalités).")

elif mode == "Modifier une offre existante":
    st.sidebar.subheader("Modifier une Offre")
    liste_offres = st.session_state.df.apply(
        lambda r: f"[{r['ID']}] {r['Partenaire']} - {r['Offre']}", axis=1
    ).tolist()
    offre_selectionnee = st.sidebar.selectbox("Sélectionner l'offre à modifier :", liste_offres)

    id_modif = int(offre_selectionnee.split("]")[0].replace("[", ""))
    ligne_index = st.session_state.df[st.session_state.df["ID"] == id_modif].index[0]
    row = st.session_state.df.loc[ligne_index]

    partenaire = st.sidebar.text_input("Nom du Partenaire", value=row["Partenaire"])
    offre = st.sidebar.text_input("Nom de l'Offre", value=row["Offre"])
    debut = st.sidebar.text_input("Mois de Début", value=str(row["Début"]))
    fin = st.sidebar.text_input("Mois de Fin", value=str(row["Fin"]))
    modalites = st.sidebar.text_area("Modalités / Conditions", value=row["Modalités"])

    if st.sidebar.button("⚠️ Mettre à jour l'offre", type="primary"):
        st.session_state.df.loc[ligne_index] = [id_modif, partenaire, offre, debut, fin, modalites]
        sauvegarder_donnees(st.session_state.df)
        st.sidebar.success("Offre mise à jour !")
        st.rerun()

else:
    st.sidebar.subheader("Supprimer une Offre")
    liste_offres = st.session_state.df.apply(
        lambda r: f"[{r['ID']}] {r['Partenaire']} - {r['Offre']}", axis=1
    ).tolist()
    offre_selectionnee = st.sidebar.selectbox("Sélectionner l'offre à supprimer :", liste_offres)

    id_suppr = int(offre_selectionnee.split("]")[0].replace("[", ""))

    if st.sidebar.button("🗑️ Supprimer cette offre", type="primary"):
        st.session_state.df = st.session_state.df[st.session_state.df["ID"] != id_suppr].reset_index(drop=True)
        sauvegarder_donnees(st.session_state.df)
        st.sidebar.success("Offre supprimée !")
        st.rerun()

st.subheader("📊 Liste de vos contrats et modalités")

if st.session_state.df.empty:
    st.info("Aucune offre enregistrée pour le moment. Utilisez le panneau de gauche pour ajouter votre premier partenaire.")
else:
    recherche = st.text_input("🔍 Recherche rapide (par partenaire ou offre) :")
    df_affiche = st.session_state.df
    if recherche:
        df_affiche = df_affiche[
            df_affiche["Partenaire"].str.contains(recherche, case=False, na=False) |
            df_affiche["Offre"].str.contains(recherche, case=False, na=False)
        ]

    st.dataframe(df_affiche, use_container_width=True, hide_index=True)
    
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        excel_data_all = exporter_en_excel(st.session_state.df)
        st.download_button(
            label="📥 Télécharger (Excel)",
            data=excel_data_all,
            file_name="offres_partenaires_completes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            icon="📊"
        )
    
    with col2:
        if recherche and len(df_affiche) < len(st.session_state.df):
            excel_data_filtered = exporter_en_excel(df_affiche)
            st.download_button(
                label="📥 Télécharger (Filtrés)",
                data=excel_data_filtered,
                file_name="offres_partenaires_filtrees.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                icon="🔍"
            )
    
    with col3:
        st.caption(f"Total : {len(st.session_state.df)} offre(s) active(s) ou passée(s) enregistrée(s).")

