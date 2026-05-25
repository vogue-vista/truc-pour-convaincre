import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

# -------------------------
# CONFIGURATION DE LA PAGE
# -------------------------
st.set_page_config(page_title="FAQ Produit IA Pro", page_icon="❓", layout="wide")

# Masquer la sidebar par défaut et injecter le style épuré
st.markdown("""
<style>
[data-testid="stSidebar"] {display: none !important;}
[data-testid="stSidebarNav"] {display: none !important;}
@import url('https://googleapis.com');
html, body, div, p, h1, h2, h3, h4, h5, h6, span {
    font-family: 'Poppins', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# CONFIGURATION PAYPAL
# -------------------------
PAYPAL_CLIENT_ID = "DEMO"  # Mettez votre Client ID ici plus tard
PAYPAL_PLAN_ID = "DEMO"    # Mettez votre Plan ID ici plus tard

# -------------------------
# GESTION DE L'ACCÈS (SESSION STATE)
# -------------------------
if "est_abonne" not in st.session_state:
    st.session_state.est_abonne = False

try:
    API_KEY = st.secrets["GROQ_API_KEY"]
except:
    API_KEY = ""

# -------------------------
# INTERFACE SÉCURISÉE
# -------------------------
st.title("❓ Générateur de FAQ Produit IA — Version Pro")

# CAS 1 : L'UTILISATEUR N'A PAS PAYÉ
if not st.session_state.est_abonne:
    st.warning("🔒 Cette application est réservée aux membres de la version Premium.")
    
    col_offre, col_connexion = st.columns(2, gap="large")
    
    with col_offre:
        st.subheader("🚀 Débloquez l'IA pour 20 $/mois")
        st.write("Anticipez les doutes de vos acheteurs. Générez instantanément une FAQ stratégique et optimisée pour vos fiches produits afin de maximiser vos conversions.")
        st.write("Le paiement est entièrement sécurisé par **PayPal**.")
        
        if PAYPAL_CLIENT_ID == "DEMO":
            paypal_html = """
            <a href="https://paypal.com" target="_blank" style="text-decoration: none;">
                <div style="background-color: #ffc439; color: #003087; text-align: center; 
                            padding: 12px; font-family: Arial, sans-serif; font-weight: bold; 
                            border-radius: 4px; max-width: 300px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    🟨 S'abonner avec PayPal (Démo)
                </div>
            </a>
            """
        else:
            paypal_html = f"""
            <div id="paypal-button-container-fixed" style="max-width: 350px; margin-top: 20px;"></div>
            <script src="https://paypal.com{PAYPAL_CLIENT_ID}&vault=true&intent=subscription" data-sdk-integration-source="button-factory"></script>
            <script>
              paypal.Buttons({{
                  style: {{ shape: 'rect', color: 'gold', layout: 'vertical', label: 'subscribe' }},
                  createSubscription: function(data, actions) {{
                    return actions.subscription.create({{ 'plan_id': '{PAYPAL_PLAN_ID}' }});
                  }},
                  onApprove: function(data, actions) {{
                    alert('Abonnement réussi ! ID : ' + data.subscriptionID);
                  }}
              }}).render('#paypal-button-container-fixed');
            </script>
            """
        
        components.html(paypal_html, height=150, scrolling=False)
        
    with col_connexion:
        st.subheader("🔑 Déjà abonné ?")
        st.write("Connectez-vous pour activer vos accès.")
        email = st.text_input("Adresse e-mail")
        mot_de_passe = st.text_input("Mot de passe", type="password")
        
        if st.button("Se connecter", use_container_width=True):
            if email == "test@client.com" and mot_de_passe == "access20":
                st.session_state.est_abonne = True
                st.success("Accès accordé !")
                st.rerun()
            else:
                st.error("Identifiants incorrects ou abonnement PayPal inactif.")

# CAS 2 : L'UTILISATEUR EST ABONNÉ -> ACCÈS COMPLET
else:
    st.write("✨ **Bienvenue dans votre espace Premium.** Votre abonnement est actif.")
    if st.button("🚪 Se déconnecter", key="logout"):
        st.session_state.est_abonne = False
        st.rerun()
        
    st.write("---")

    with st.container(border=True):
        col_input, col_options = st.columns(2)
        
        with col_input:
            nom_produit = st.text_input("Nom de votre produit", placeholder="Ex: Matelas orthopédique Nuage, Écouteurs sans fil SportX...")
            description = st.text_area("Description courte ou caractéristiques", placeholder="Ex: Matelas à mémoire de forme, idéal pour le mal de dos, garantie 10 ans, livré roulé...")
            
        with col_options:
            style_faq = st.selectbox("Style des réponses", [
                "⚡ Direct & Rassurant (Idéal e-commerce)", 
                "🤝 Commercial & Persuasif (Axé bénéfices)", 
                "🔬 Technique & Détaillé (Idéal produits complexes)"
            ])
            langue = st.selectbox("Langue de la FAQ", ["Français", "Anglais", "Espagnol", "Allemand"])

        generer = st.button("🚀 Générer la FAQ Produit", use_container_width=True)

    if generer:
        if not API_KEY:
            st.error("⚠️ Erreur : La clé GROQ_API_KEY est manquante dans les Secrets du serveur.")
        elif not nom_produit:
            st.error("⚠️ Veuillez indiquer le nom de votre produit.")
        else:
            with st.spinner("L'IA de Groq génère vos questions/réponses..."):
                try:
                    client = Groq(api_key=API_KEY)
                    
                    prompt_systeme = """Tu es un expert en UX Writing et en optimisation du taux de conversion (CRO) pour le e-commerce.
                    Tu dois générer une FAQ (Foire Aux Questions) composée de 5 questions/réponses stratégiques qui détruisent les objections des clients.
                    Formate obligatoirement ta réponse sous cette forme textuelle en Markdown :
                    **Q1 : [La question]**
                    *Réponse : [La réponse]*
                    
                    Ne fais aucun blabla d'introduction ou de conclusion, donne directement les questions et les réponses."""

                    reponse = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": prompt_systeme},
                            {"role": "user", "content": f"Produit : '{nom_produit}'. Description : '{description}'. Style de rédaction : {style_faq}. Langue : {langue}."}
                        ],
                        temperature=0.6
                    )
                    
                    faq_genere = reponse.choices.message.content
                    st.success("✨ Votre FAQ optimisée est prête !")
                    st.markdown(faq_genere)
                    st.text_area("Copier le bloc brut :", value=faq_genere, height=300)

                except Exception as e:
                    st.error(f"Erreur technique Groq : {str(e)}")
