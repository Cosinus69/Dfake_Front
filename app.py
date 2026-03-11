import streamlit as st
from PIL import Image
import numpy as np
import requests
import cv2
import random


#CONSTANT
API_URL='http://127.0.0.1:8000/predict_image/'
API_URL2= 'http://127.0.0.1:8000/generate_heatmap/'

#-------------------------
# Configuration des pages
#-------------------------

st.set_page_config(
    page_title="D-FAKE",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("D-FAKE App - Frontend Demo")

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

menu = st.sidebar.selectbox(
    "MENU",
    ["Home","Check a picture"]
)

# Home (dans menu déroulant)
#----------------------------
if menu == "Home":      # Dans page home on pourra faire un descriptif
                        # Je ferai des propositions avec logo wagon, Batch 2225..

    st.header("D-Fake Project")

    st.write("Upload an image to check if it's a Fake or Real.")
    st.write("This is a frontend demo: predictions and Grad-CAM are simulated.")

# Check a picture (dans menu déroulant)
#---------------------------------------
elif menu == "Check a picture":

    st.header("Image Detection")
    #objet fichier en mémoire déjà en binaire
    uploaded_file = st.file_uploader(
        "Upload your image",
        type=["jpg","jpeg","png","gif","bmp","webp"] # filtrage au niveau de l'interface
)
    # Un fichier a été uploadé
    if uploaded_file is not None:  # evite à Streamlit de bugger
         # validation préalable de l'image loadée et conversion en RGB
         image = validate_image(uploaded_file) # return image ou messages d'erreur à l'utilisateur si l'image n'est pas validée
         if image is not None :
            st.image(image, caption="Uploaded Picture", use_container_width=True)
            # Remise du pointeur au début après image.verify sinon fichier vide et erreur connection API
            uploaded_file.seek(0)
            #Envoi du fichier au back-end API
            files = {"file" : uploaded_file }
            response = requests.post(API_URL, files=files)
         if response.status_code == 200:
             data  = response.json()
             label = data["fake_real"]
             confidence = data["predict_value"]

             #st.write(f"Your picture is a **{label}** one !")
             # Real en vert et Fake en rouge
             if label == "Fake":
                    st.markdown(f'<p style="color:red; font-weight:bold;">Your picture is a {label} one !</p>', unsafe_allow_html=True)
             else:
                    st.markdown(f'<p style="color:green; font-weight:bold;">Your picture is a {label} one !</p>', unsafe_allow_html=True)

             # Barre de confiance
             st.write(f"Confidence level: **{confidence*100:.2f}%**") # on met les probas en pourcentage
             st.progress(int(confidence*100))

         else:
                 st.error("Error calling the API")

    else:
        st.write("No file uploaded")
