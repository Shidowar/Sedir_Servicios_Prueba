import os
import io
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv()

app = Flask(__name__)

# Tu API Key que empieza con AQ.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Iniciar cliente oficial de google con la clave de forma nativa
cliente_gemini = genai.Client(api_key=GEMINI_API_KEY)

# PROCESAMIENTO DE IMAGEN
@app.route('/analyze', methods=['POST'])
def analizar_imagen():
    if 'imagen' not in request.files:
        return jsonify({"error": "No se subio ninguna imagen"}), 400
    
    archivo = request.files['imagen']
    if archivo.filename == '':
        return jsonify({"error": "Archivo no seleccionado"}), 400

    try:
        # Leer bytes de la imagen y abrirla con Pillow
        bytes_imagen = archivo.read()
        imagen_cargada = Image.open(io.BytesIO(bytes_imagen))

        instruccion = (
            "Analiza esta foto de comida. Identifica ingredientes nativos de Latinoamérica "
            "y calcula porciones, calorías, proteínas, grasas y carbohidratos. "
            "Devuelve estrictamente un formato estructurado JSON sin formato markdown, sin usar bloques de código ```json o texto adicional. "
            "Sigue exactamente esta estructura de llaves: "
            "{\"items\": [{\"nombre\": \"quinua\", \"calorias\": 120, \"proteinas\": 4, \"grasas\": 1, \"carbohidratos\": 21}], \"confianza\": 0.95}"
        )

        # Llama al modelo pasando la imagen y la instrucción
        respuesta = cliente_gemini.models.generate_content(
            model='gemini-2.5-flash',
            contents=[imagen_cargada, instruccion],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        return respuesta.text, 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return jsonify({"error": f"Error interno en S-02 con SDK (Imagen): {str(e)}"}), 500

# PROCESAMIENTO DE TEXTO
@app.route('/analyze-text', methods=['POST'])
def analizar_texto():
    data = request.get_json()
    
    # Validamos que el usuario envíe el campo 'texto'
    if not data or 'texto' not in data:
        return jsonify({"error": "Falta el campo 'texto' en la peticion"}), 400
    
    texto_usuario = data['texto']

    try:
        # Instrucción combinada con el texto descriptivo del usuario
        instruccion_texto = (
            f"Analiza la siguiente descripción de comida: '{texto_usuario}'. "
            "Identifica los platos e ingredientes nativos de Latinoamérica mencionados y calcula porciones, "
            "calorías, proteínas, grasas y carbohidratos aproximados. "
            "Devuelve estrictamente un formato estructurado JSON sin formato markdown, sin usar bloques de código ```json o texto adicional. "
            "Sigue exactamente esta estructura de llaves: "
            "{\"items\": [{\"nombre\": \"quinua\", \"calorias\": 120, \"proteinas\": 4, \"grasas\": 1, \"carbohidratos\": 21}], \"confianza\": 0.95}"
        )

        # Llama al modelo pasando únicamente el prompt de texto
        respuesta = cliente_gemini.models.generate_content(
            model='gemini-2.5-flash',
            contents=instruccion_texto,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        return respuesta.text, 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return jsonify({"error": f"Error interno en S-02 con SDK (Texto): {str(e)}"}), 500


if __name__ == '__main__':
    app.run(port=8082, debug=True)