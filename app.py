import os
import streamlit as st
import base64
from openai import OpenAI
import openai
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
from streamlit_drawable_canvas import st_canvas

Expert = " "
profile_imgenh = " "

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

# Set creative page config
st.set_page_config(page_title='Tablero Inteligente', page_icon="🧠")

# Add creative style
st.markdown("""
    <style>
        body {
            font-family: 'Courier New', monospace;
            color: #333333;
        }
        h1, h2, h3 {
            color: #0d47a1;
            text-shadow: 2px 2px 5px #64b5f6;
        }
        .stButton>button {
            background-color: #42a5f5;
            color: white;
            border-radius: 12px;
            padding: 10px 20px;
        }
        .stTextInput>div>input {
            border: 2px solid #64b5f6;
            border-radius: 8px;
        }
        .stCanvas {
            border: 4px dashed #42a5f5;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.title('🧠 Tablero Inteligente')

# Sidebar
with st.sidebar:
    st.subheader("Acerca de:")
    st.info("En esta aplicación, veremos cómo una máquina puede interpretar un boceto.")
st.subheader("Dibuja el boceto en el panel y presiona el botón para analizarlo")

# Add color switcher to the sidebar
color_choice = st.sidebar.selectbox('Selecciona el color para dibujar', ['Negro', 'Verde', 'Azul', 'Rojo'])
color_map = {'Negro': '#000000', 'Verde': '#008000', 'Azul': '#0000FF', 'Rojo': '#FF0000'}
stroke_color = color_map[color_choice]

# Add canvas component
drawing_mode = "freedraw"
stroke_width = st.sidebar.slider('Selecciona el ancho de línea', 1, 30, 5)
bg_color = '#FFFFFF'

# Create canvas component
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Transparent orange fill
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

# OpenAI API Key input
ke = st.text_input('Ingresa tu Clave', type="password")
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']

# Button to analyze image
analyze_button = st.button("Analiza la imagen", type="secondary")

# Check if conditions to analyze are met
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("Analizando..."):
        # Encode the image
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
        input_image.save('img.png')

        # Encode the image in base64
        base64_image = encode_image_to_base64("img.png")
        prompt_text = (f"Describe en español brevemente la imagen")

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/png;base64,{base64_image}",
                    },
                ],
            }
        ]

        # Make the request to the OpenAI API
        try:
            full_response = ""
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                        },
                    ],
                }],
                max_tokens=500,
            )

            if response.choices[0].message.content is not None:
                full_response += response.choices[0].message.content
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)
            if Expert == profile_imgenh:
                st.session_state.mi_respuesta = response.choices[0].message.content

        except Exception as e:
            st.error(f"Error: {e}")

else:
    if not api_key:
        st.warning("Por favor ingresa tu API key.")

