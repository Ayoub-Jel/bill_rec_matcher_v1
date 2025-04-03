import streamlit as st
import os
import io
from utils import Utils
from config import Config


class App:
    """Classe principale de l'application Streamlit"""
    
    def __init__(self):
        self.invoice_processor = InvoiceProcessor()
        self.bank_processor = BankStatementProcessor()
        self.matcher = Matcher(self.invoice_processor, self.bank_processor)
        self.setup_app()
        
    def setup_app(self):
        """Configure l'application Streamlit"""
        st.set_page_config(
            page_title="Matching Factures/Relevés Bancaires",
            page_icon="📊",
            layout="wide"
        )
        
        # Créer les dossiers nécessaires
        Utils.create_folders()
        os.makedirs("exports", exist_ok=True)
        
        # Styliser l'application avec CSS personnalisé
        self.add_custom_css()
        
        # Chargement des fichiers existants
        self.invoice_processor.load_existing_invoices()
        
        # Lancer l'interface principale
        self.run()
        
    def add_custom_css(self):
        """Ajoute du CSS personnalisé à l'application"""
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1E88E5;
            text-align: center;
            margin-bottom: 1rem;
        }
        .section-header {
            font-size: 1.5rem;
            font-weight: bold;
            color: #333;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }
        .info-box {
            background-color: #f0f7ff;
            padding: 1rem;
            border-radius: 5px;
            border-left: 5px solid #1E88E5;
            margin-bottom: 1rem;
        }
        .result-box {
            background-color: #e8f5e9;
            padding: 1rem;
            border-radius: 5px;
            border-left: 5px solid #43a047;
            margin-top: 1rem;
        }
        .warning-box {
            background-color: #fff8e1;
            padding: 1rem;
            border-radius: 5px;
            border-left: 5px solid #ffb300;
            margin-bottom: 1rem;
        }
        .stButton button {
            background-color: #1E88E5;
            color: white;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }
        .download-btn {
            background-color: #43a047 !important;
        }
        .match-highlight {
            background-color: #e8f5e9;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def sidebar_upload_section(self):
        """Section de la sidebar pour télécharger les fichiers"""
        with st.sidebar:
            st.markdown("<div class='section-header'>Configuration</div>", unsafe_allow_html=True)
            
            # Configuration de la clé API Mistral
            api_key = st.text_input("Clé API Mistral", type="password")
            if api_key:
                Config.MISTRAL_API_KEY = api_key
                
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<div class='section-header'>Téléchargement de Factures</div>", unsafe_allow_html=True)
            
            # Upload d'images de factures
            uploaded_invoices = st.file_uploader(
                "Télécharger des factures (images JPG, PNG)", 
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True
            )
            
            if uploaded_invoices:
                with st.spinner("Traitement des factures en cours..."):
                    for uploaded_file in uploaded_invoices:
                        self.invoice_processor.process_invoice(uploaded_file)
                    st.success(f"{len(uploaded_invoices)} facture(s) traitée(s)")
            
            # Affichage du nombre de factures disponibles
            invoices = self.invoice_processor.get_invoices()
            if invoices:
                st.info(f"{len(invoices)} facture(s) disponible(s)")
            
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<div class='section-header'>Téléchargement de Relevés Bancaires</div>", unsafe_allow_html=True)
            
            # Upload de relevés bancaires
            uploaded_bank_statement = st.file_uploader(
                "Télécharger un relevé bancaire (CSV)", 
                type=["csv"],
                accept_multiple_files=False
            )
            
            if uploaded_bank_statement:
                with st.spinner("Traitement du relevé bancaire en cours..."):
                    df = self.bank_processor.process_bank_statement(uploaded_bank_statement)
                    if df is not None:
                        st.success("Relevé bancaire traité avec succès")
                        # Stocker les noms des colonnes dans la session
                        st.session_state["bank_columns"] = df.columns.tolist()
                    else:
                        st.error("Erreur lors du traitement du relevé bancaire")
    
    def main_panel_results(self):
        """Section principale pour afficher les résultats"""
        st.markdown("<div class='main-header'>Matching Factures / Relevés Bancaires</div>", unsafe_allow_html=True)
        
        # Vérifier si nous avons des factures et un relevé bancaire
        invoices = self.invoice_processor.get_invoices()
        bank_df = self.bank_processor.get_dataframe()
        
        if not invoices:
            st.info("Veuillez télécharger des factures depuis la sidebar.")
            return
            
        if bank_df is None or bank_df.empty:
            st.info("Veuillez télécharger un relevé bancaire depuis la sidebar.")
            return
            
        # Afficher les paramètres de configuration pour le matching
        st.markdown("<div class='section-header'>Configuration du Matching</div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        bank_columns = st.session_state.get("bank_columns", [])
        
        with col1:
            amount_column = st.selectbox(
                "Colonne des montants",
                options=bank_columns,
                index=0 if bank_columns else None,
                key="amount_column"
            )
            
        with col2:
            date_column = st.selectbox(
                "Colonne des dates",
                options=bank_columns,
                index=0 if bank_columns else None,
                key="date_column"
            )
            
        with col3:
            description_column = st.selectbox(
                "Colonne des descriptions",
                options=bank_columns,
                index=0 if bank_columns else None,
                key="description_column"
            )
            
        # Bouton pour lancer le matching
        if st.button("Lancer le Matching"):
            if not amount_column or not date_column or not description_column:
                st.warning("Veuillez sélectionner toutes les colonnes nécessaires.")
                return
                
            with st.spinner("Matching en cours..."):
                matches = self.matcher.perform_matching(amount_column, date_column, description_column)
                
                if matches:
                    st.session_state["matches"] = matches
                    st.success(f"{len(matches)} correspondance(s) trouvée(s)")
                else:
                    st.warning("Aucune correspondance trouvée.")
        
        # Afficher les résultats du matching s'ils existent
        if "matches" in st.session_state and st.session_state["matches"]:
            self._display_matching_results(bank_df)
    
    def _display_matching_results(self, bank_df):
        """Affiche les résultats du matching et permet l'export"""
        st.markdown("<div class='section-header'>Résultats du Matching</div>", unsafe_allow_html=True)
        
        matches = st.session_state["matches"]
        
        # Créer un DataFrame de résultats pour l'affichage
        result_df = bank_df.copy()
        
        # Ajouter des colonnes pour les résultats du matching
        result_df["Facture_Trouvée"] = False
        result_df["Nom_Fichier_Facture"] = ""
        result_df["Vendeur"] = ""
        result_df["Date_Facture"] = ""
        result_df["Confiance"] = 0.0
        
        # Pour chaque match, marquer la transaction correspondante
        for match in matches:
            invoice = match["invoice"]
            transaction = match["transaction"]
            
            # Trouver l'index de la transaction dans le DataFrame original
            mask = True
            for col in bank_df.columns:
                col_value = transaction[col]
                mask = mask & (bank_df[col] == col_value)
            
            idx = bank_df.loc[mask].index
            if not idx.empty:
                result_df.loc[idx, "Facture_Trouvée"] = True
                result_df.loc[idx, "Nom_Fichier_Facture"] = invoice.get("filename", "")
                result_df.loc[idx, "Vendeur"] = invoice.get("vendor", "")
                result_df.loc[idx, "Date_Facture"] = invoice.get("date", "")
                result_df.loc[idx, "Confiance"] = f"{match['confidence']:.2f}"
        
        # Afficher le tableau de résultats avec mise en évidence des correspondances
        st.dataframe(
            result_df.style.apply(
                lambda row: ['background-color: #e8f5e9' if row['Facture_Trouvée'] else '' for _ in row],
                axis=1
            ),
            use_container_width=True
        )
        
        # Bouton pour exporter les résultats
        export_filename = st.text_input("Nom du fichier d'export", "resultats_matching.xlsx")
        
        if st.download_button(
            label="Télécharger le rapport Excel",
            data=self._get_excel_report(bank_df, matches, export_filename),
            file_name=export_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_button",
            use_container_width=True
        ):
            st.success(f"Rapport exporté avec succès sous le nom {export_filename}")
    
    def _get_excel_report(self, bank_df, matches, filename):
        """Génère un rapport Excel des résultats de matching"""
        # Utiliser un buffer en mémoire pour l'Excel
        output = io.BytesIO()
        
        # Récupérer les colonnes sélectionnées
        amount_column = st.session_state.get("amount_column", "")
        date_column = st.session_state.get("date_column", "")
        description_column = st.session_state.get("description_column", "")
        
        # Mapper les colonnes
        columns_mapping = {
            "amount": amount_column,
            "date": date_column,
            "description": description_column
        }
        
        # Exporter vers Excel en utilisant la fonction du matcher
        temp_path = self.matcher.export_to_excel(filename, bank_df, columns_mapping)
        
        # Lire le fichier généré
        with open(temp_path, 'rb') as f:
            output.write(f.read())
        
        # Réinitialiser le curseur du buffer
        output.seek(0)
        
        return output
        
    def run(self):
        """Exécute l'application"""
        # Sidebar pour l'upload
        self.sidebar_upload_section()
        
        # Panel principal pour les résultats
        self.main_panel_results()


# Instancier et exécuter l'application si le script est exécuté directement
if __name__ == "__main__":
    app = App()