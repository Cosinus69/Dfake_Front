import streamlit as st
from PIL import Image #Package pillow =PIL


# Déjà installés dans le package Python version 3.12.9
import requests
import cv2
import random
import base64
import io


#CONSTANT

#API url
API_URL='http://127.0.0.1:8000/predict_image/'
API_URL2= 'http://127.0.0.1:8000/generate_heatmap/'

#Colors
ROUGE = '#FF4B4B'
BLEU = '#1f77b4'
VERT = '#2ECC71'
ORANGE = '#F39C12'
BLEU_FONCE = "#1F4E79"
JAUNE = '#F1C40F'
VIOLET = '#8E44AD'
CYAN = '#1ABC9C'
GRIS_CLAIR = '#F5F7FA'
GRIS_FONCE = '#34495E'
NOIR = '#000000'
BLANC = '#FFFFFF'

#-------------------------
# Configuration des pages
#-------------------------

st.set_page_config(
    page_title="D-FAKE",
    layout="wide",
    initial_sidebar_state="expanded"
)
#st.title("D-FAKE")
st.markdown("""
<h1 style='text-align:center; color:BLACK;'>
D-FAKE
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<p style='text-align:center; font-size:25px;'>
<b>Protecting authenticity in the age of AI !</b>
</p>
""", unsafe_allow_html=True)

#st.markdown("""
#<p style='text-align:center; font-size:21px;'>
#<b>Protecting authenticity in the age of AI !</b>
#</p>
#""", unsafe_allow_html=True)

# ------------------------------------------------
# Validation image loadée avant envoie à l'API
# ------------------------------------------------
def validate_image(uploaded_file, max_size=4000): #Taille à valider avec équipe
    try:
        image = Image.open(uploaded_file)
        image.verify()  # vérification de l'intégrité
    except Exception:
        st.error("Corrupted image file")
        return None

    # On réouvre après verify
    image = Image.open(uploaded_file)

    # verification du format pour éviter les virus avec changement d'extension
    allowed_formats = ["JPEG","PNG","GIF","BMP","WEBP"] # on rajoute d'autres formats ?
    if image.format not in allowed_formats:
        st.error(f"Unsupported format: {image.format}")
        return None
    # verification de la taille de l'image loadéé (A CONFIRMER ENSEMBLE pour max_size)
    if image.width > max_size or image.height > max_size:
        st.error("Image too large")
        return None

    # conversion en (224,224,3) comme cela vous êtes tranquille pour le back end
    # convertit aussi les images en noir et blanc et format PNG transparent
    if image.mode != "RGB":
        image = image.convert("RGB")

    return image


# -------------------------
# Sidebar Menu
# -------------------------
#st.sidebar.title("Navigation")
menu = st.sidebar.selectbox('MENU',["Home","Check your image"])

# Home (dans menu déroulant)
#----------------------------
if menu == "Home":      # Dans page home on pourra faire un descriptif
                        # Je ferai des propositions avec logo wagon, Batch 2225..

    # Logo du Wagon centré
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(
        "images/wagon.jpg",
        caption="#BATCH-2235-LYON",
        use_container_width=True
    )

    st.markdown("### How it works ?")

    st.write("""
    1. Upload your image
    2. AI based on DeepLearning analyzes your image
    3. The model predicts **Real or Fake**
    4. GRAD Cam shows you the fake areas
    """)

# Check a picture (dans menu déroulant)
#---------------------------------------
elif menu == "Check your image":

    st.header("Upload your image")
    #objet fichier en mémoire déjà en binaire
    uploaded_file = st.file_uploader(
        " ",
        type=["jpg","jpeg","png","gif","bmp","webp"] # filtrage au niveau de l'interface
)
    # Un fichier a été uploadé
    if uploaded_file is not None:  # evite à Streamlit de bugger
         # validation préalable de l'image loadée et conversion en RGB
         image = validate_image(uploaded_file) # return image ou messages d'erreur à l'utilisateur si l'image n'est pas validée
         if image is not None :
            #st.image(image, caption="Uploaded Picture", use_container_width=True)
            #Remise du pointeur au début après image.verify sinon fichier vide et erreur connection API
            uploaded_file.seek(0)
            #Envoi du fichier au back-end API
            files = {"file" : uploaded_file }
            response = requests.post(API_URL2, files=files)

         if response.status_code == 200:
             data  = response.json()
             label = data["fake_real"]
             confidence = data["predict_value"]
             image_uploaded_data = base64.b64decode(data["image_resized"]) # Image est en binaire
             image_heatmap_data = base64.b64decode(data["heatmap"]) # Heatmap est en binaire

             #st.write(f"Your picture is a **{label}** one !")
             # Real en vert et Fake en rouge avec couluer de progress bar rouge ou verte et plus bleu
             if label == "FAKE":
                    st.markdown(f'<p style="color:red; font-weight:bold;">Your picture is a {label} one !</p>', unsafe_allow_html=True)

             else:
                    st.markdown(f'<p style="color:green; font-weight:bold;">Your picture is a {label} one !</p>', unsafe_allow_html=True)

             # Barre de confiance
             st.write(f"Confidence level: **{confidence*100:.2f}%**") # on met les probas en pourcentage
             st.progress(int(confidence*100))

             # Transformation des deux images binaires en fichier mémoire ouvrables avec PIL
             initial_image_uploaded = Image.open(io.BytesIO(image_uploaded_data))
             image_heatmap = Image.open(io.BytesIO(image_heatmap_data))

             # Option 1 : Affichage images côte à côte
             #----------
             col1, col2 = st.columns(2)
             col1.image(initial_image_uploaded , caption="Uploaded Image", use_container_width=True)
             col2.image(image_heatmap , caption=f"{label} - Important Zones", use_container_width=True)

             #Option 2 : affichage images l'une en dessous de l'autre(Visuel moins écrasé)
             #---------
             #st.image(initial_image_uploaded , caption="Uploaded Image", use_container_width=True)
             #st.image(image_heatmap , caption=f"{label} - Important Zones", use_container_width=True)

         else:
                 st.error("Error calling the API")

    else:
        st.write("No file uploaded yet")
