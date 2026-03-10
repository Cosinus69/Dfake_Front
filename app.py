import streamlit as st
from PIL import Image
import numpy as np
import requests
import cv2
import random


#CONSTANT
#API_URL = 'http://localhost:8000/predict_image/'


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
        image.verify()  # vérification de l' intégrité
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

# --------------------------------------------------------------------
# Simulation prediction en attendant la fonction "predict_image" (Thomas)
# --------------------------------------------------------------------
def mock_predict(image):
    labels = ["Fake", "Real"]
    label = random.choice(labels)
    confidence = random.uniform(0.5, 1.0)
    return label, confidence

# ---------------------------------------------------------------------
# Simulation Grad-CAM en attendant la fonction "generate heatmap" (Diego)
# ---------------------------------------------------------------------
def mock_gradcam(image):
    h, w = image.height, image.width
    heatmap = np.random.rand(h, w)
    heatmap = cv2.applyColorMap(np.uint8(255*heatmap), cv2.COLORMAP_JET)
    img = np.array(image)
    superimposed_img = cv2.addWeighted(img, 0.6, heatmap, 0.4, 0)
    return Image.fromarray(superimposed_img)


# -------------------------
# Sidebar Menu
# -------------------------

menu = st.sidebar.selectbox(
    "MENU",
    ["Home","Check a picture"]
)

# Home
#-------
if menu == "Home":      # Dans page home on pourra faire un descriptif
                        # Je ferai des propositions

    st.header("D-Fake Project")

    st.write("Upload an image to check if it's a Fake or Real.")
    st.write("This is a frontend demo: predictions and Grad-CAM are simulated.")

# Check a picture
#------------------
elif menu == "Check a picture":

    st.header("Image Detection")
    #objet fichier en mémoire déjà en binaire
    uploaded_file = st.file_uploader(
        "Upload your image",
        type=["jpg","jpeg","png","gif","bmp","webp"] # filtrage au niveau de l'interface
)


    if uploaded_file is not None:  # evite à Streamlit de bugger
         # validation préalable de l'image loadée
         image = validate_image(uploaded_file) # return image ou messages d'erreur à l'utilisateur si l'image n'est pas validée
         if image is not None :
             #on affiche l'image originale

             #st.image(image, caption="Uploaded Picture", use_container_width=True)

             # simulation de la prediction en attendant la fonction
             label, confidence = mock_predict(image)
             #st.write(f"Your picture is a **{label}** one !")
             # Real en vert et Fake en rouge
             if label == "Fake":
                st.markdown(f'<p style="color:red; font-weight:bold;">Your picture is a {label} one !</p>', unsafe_allow_html=True)
             else:
                st.markdown(f'<p style="color:green; font-weight:bold;">Prediction: {label}</p>', unsafe_allow_html=True)

             # Barre de confiance
             st.write(f"Confidence level: **{confidence*100:.2f}%**") # on met les probas en pourcentage
             st.progress(int(confidence*100))
             #st.metric(label="Confidence", value=f"{confidence*100:.2f}%", delta_color="inverse")

             #simulation Grad CAM en attendant la fonction, prévoir que si image est fake !
             cam_image = mock_gradcam(image)
             #st.image(cam_image, caption=f"{label} - Importantes Zones", use_container_width=True)
             col1, col2 = st.columns(2)
             col1.image(image, caption="Uploaded Image", use_container_width=True)
             col2.image(cam_image, caption=f"{label} - Important Zones", use_container_width=True)
