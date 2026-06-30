Aplicaciones:
  
  Python 3.10 o superior
  
  MongoDB Community Server y Compass
  
  Una API Key de Google Gemini

Instalacion 02:
  
  cd s02_food_recognition
  
  python -m venv venv
  
  venv\Scripts\activate
  
  pip install flask python-dotenv google-genai pillow

  Crear un archivo llamando .env y colocar:
  
  GEMINI_API_KEY= CLAVE API

Instalacion 03:
  
  cd s06_analytics
  
  python -m venv venv
  
  venv\Scripts\activate
  
  pip install flask python-dotenv pymongo

  Crear un archivo llamando .env y colocar:
  
  MONGO_URI=mongodb://localhost:27017/calio_db

Activar S02:
  
  cd s02_food_recognition
  
  venv\Scripts\activate
  
  python app.py
  
Activar S06:
  
  cd s06_analytics
  
  venv\Scripts\activate
  
  python app.py
