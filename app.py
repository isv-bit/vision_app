import os
import streamlit as st
import base64
from openai import OpenAI

# ------------------ FUNCIONES ------------------
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# ------------------ CONFIG ------------------
st.set_page_config(
    page_title="Análisis de Imagen",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ------------------ ESTILOS ------------------
st.markdown("""
<style>

/* Fondo degradado */
.stApp {
    background: linear-gradient(135deg, #00c6ff, #0072ff, #6a11cb);
    color: white;
}

/* Títulos */
.main-title {
    font-size: 45px;
    font-weight: 800;
    text-align: center;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    margin-bottom: 20px;
}

/* Card glass */
.card {
    background: rgba(255, 255, 255, 0.15);
    padding: 25px;
    border-radius: 20px;
    backdrop-filter: blur(10px);
    box-shadow: 0px 8px 25px rgba(0,0,0,0.3);
    margin-top: 20px;
}

/* Botones */
.stButton>button {
    background: linear-gradient(90deg, #00f5a0, #00d9f5);
    color: black;
    border-radius: 12px;
    height: 50px;
    font-size: 16px;
    border: none;
    font-weight: bold;
}

.stButton>button:hover {
    transform: scale(1.05);
    transition: 0.2s;
}

/* Inputs */
.stTextInput>div>div>input {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown('<p class="main-title">🤖 Análisis de Imagen</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Sube una imagen y obtén una descripción inteligente</p>', unsafe_allow_html=True)

# ------------------ CARD ------------------
st.markdown('<div class="card">', unsafe_allow_html=True)

# TEXTO DENTRO DE LA CARD
st.markdown("""
<div style="text-align:center; font-size:18px; font-weight:600; margin-bottom:15px;">
📸 Sube una imagen para analizar su contenido
</div>
""", unsafe_allow_html=True)

# API KEY
ke = st.text_input('🔑 Ingresa tu Clave', type="password")
os.environ['OPENAI_API_KEY'] = ke

api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

# UPLOADER
uploaded_file = st.file_uploader("📂 Subir imagen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    with st.expander("🖼 Imagen cargada", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# OPCIÓN DETALLES
show_details = st.toggle("📝 Preguntar algo específico sobre la imagen", value=False)

if show_details:
    additional_details = st.text_area(
        "Agrega contexto adicional:",
        disabled=not show_details
    )

# BOTÓN
analyze_button = st.button("🔍 Analizar imagen")

# ------------------ PROCESO ------------------
if uploaded_file is not None and api_key and analyze_button:

    with st.spinner("Analizando ..."):
        base64_image = encode_image(uploaded_file)
    
        prompt_text = ("Describe lo que ves en la imagen en español")
    
        if show_details and additional_details:
            prompt_text += (
                f"\n\nContexto adicional del usuario:\n{additional_details}"
            )
    
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                ],
            }
        ]
    
        try:
            full_response = ""
            message_placeholder = st.empty()

            for completion in client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1200,
                stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)
    
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

else:
    if not uploaded_file and analyze_button:
        st.warning("⚠️ Por favor sube una imagen.")
    if not api_key:
        st.warning("⚠️ Ingresa tu API key.")

# CIERRE CARD
st.markdown('</div>', unsafe_allow_html=True)
