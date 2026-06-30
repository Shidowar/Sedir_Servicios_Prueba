import os
import io
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv()

app = Flask(__name__)

# Tu API Key que empieza con AQ.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Inicializamos el cliente oficial de Google pasando la clave de forma nativa
cliente_gemini = genai.Client(api_key=GEMINI_API_KEY)

@app.route('/analyze', methods=['POST'])
def analizar_imagen():
    if 'imagen' not in request.files:
        return jsonify({"error": "No se subió ninguna imagen"}), 400
    
    archivo = request.files['imagen']
    if archivo.filename == '':
        return jsonify({"error": "Archivo no seleccionado"}), 400

    try:
        # 1. Leer los bytes de la imagen y cargarla con Pillow
        bytes_imagen = archivo.read()
        imagen_cargada = Image.open(io.BytesIO(bytes_imagen))

        # 2. Prompt optimizado para la respuesta estructurada de tu app
        instruccion = (
            "Analiza esta foto de comida. Identifica ingredientes nativos de Latinoamérica "
            "y calcula porciones, calorías, proteínas, grasas y carbohidratos. "
            "Devuelve estrictamente un formato estructurado JSON sin formato markdown, sin usar bloques de código ```json o texto adicional. "
            "Sigue exactamente esta estructura de llaves: "
            "{\"elementos\": [{\"nombre\": \"quinua\", \"calorias\": 120, \"proteinas\": 4, \"grasas\": 1, \"carbohidratos\": 21}], \"confianza\": 0.95}"
        )

        # 3. Llamada al modelo usando el cliente oficial SDK
        respuesta = cliente_gemini.models.generate_content(
            model='gemini-2.5-flash',
            contents=[imagen_cargada, instruccion],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        # 4. Retornar los datos limpios directamente
        return respuesta.text, 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return jsonify({"error": f"Error interno en S-02 con SDK: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(port=8082, debug=True)