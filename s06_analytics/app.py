import os
from datetime import datetime
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)

# Conexión con la base de datos MongoDB local
cliente_mongo = MongoClient(os.getenv("MONGO_URI"))
base_datos = cliente_mongo.get_database()
coleccion_analiticas = base_datos['user_analytics']

@app.route('/stats/week/<int:id_usuario>', methods=['GET'])
def obtener_estadisticas_semanales(id_usuario):
    try:
        estadisticas_usuario = coleccion_analiticas.find_one({"user_id": id_usuario}, {"_id": 0})
        
        # Si el usuario no existe, inicializar con estructura completa para gráficas
        if not estadisticas_usuario:
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            datos_iniciales = {
                "user_id": id_usuario,
                "weight_progress": [
                    {"date": "2026-06-22", "weight": 74.5},
                    {"date": "2026-06-24", "weight": 74.2},
                    {"date": "2026-06-26", "weight": 73.9},
                    {"date": fecha_hoy, "weight": 74.0}
                ],
                "streak_days": 5,
                "logros": ["Perfil inicializado"],
                "historial_calorias": [
                    {"date": "2026-06-28", "calories_consumed": 1800, "calories_burned": 350},
                    {"date": fecha_hoy, "calories_consumed": 0, "calories_burned": 0}
                ],
                "weekly_macros": {
                    "calories": 0,
                    "proteins": 0,
                    "carbs": 0,
                    "fats": 0
                }
            }
            coleccion_analiticas.insert_one(datos_iniciales.copy())
            if "_id" in datos_iniciales: del datos_iniciales["_id"]
            return jsonify(datos_iniciales), 200
            
        return jsonify(estadisticas_usuario), 200

    except Exception as e:
        return jsonify({"error": f"Error en S-06 (GET Stats): {str(e)}"}), 500


# RUTA LOG: comida de la IA, acumula semanales y actualiza el historial diario
@app.route('/analytics/log', methods=['POST'])
def registrar_macros_comida():
    try:
        datos = request.get_json()
        if not datos or 'id_usuario' not in datos or 'elementos' not in datos:
            return jsonify({"error": "Faltan datos obligatorios (id_usuario o elementos)"}), 400

        id_usuario = int(datos['id_usuario'])
        elementos = datos['elementos']
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")

        # Calcular la suma del plato actual
        total_calorias = sum(elemento.get('calorias', 0) for elemento in elementos)
        total_proteinas = sum(elemento.get('proteinas', 0) for elemento in elementos)
        total_carbohidratos = sum(elemento.get('carbohidratos', 0) for elemento in elementos)
        total_grasas = sum(elemento.get('grasas', 0) for elemento in elementos)

        # Existe usuario en la bd
        usuario_existe = coleccion_analiticas.find_one({"user_id": id_usuario})
        if not usuario_existe:
            # Creacion si es nuevo
            obtener_estadisticas_semanales(id_usuario)

        # Actualiza macros acumulados totales de la semana ($inc)
        coleccion_analiticas.update_one(
            {"user_id": id_usuario},
            {
                "$inc": {
                    "weekly_macros.calories": total_calorias,
                    "weekly_macros.proteins": total_proteinas,
                    "weekly_macros.carbs": total_carbohidratos,
                    "weekly_macros.fats": total_grasas
                }
            }
        )

        # 3. Guardar en el historial diario para las gráficas
        # Si existe dia se suma y si no se crea otro dia
        dia_existente = coleccion_analiticas.find_one(
            {"user_id": id_usuario, "historial_calorias.date": fecha_hoy}
        )

        if dia_existente:
            coleccion_analiticas.update_one(
                {"user_id": id_usuario, "historial_calorias.date": fecha_hoy},
                {"$inc": {"historial_calorias.$.calories_consumed": total_calorias}}
            )
        else:
            coleccion_analiticas.update_one(
                {"user_id": id_usuario},
                {
                    "$push": {
                        "historial_calorias": {
                            "date": fecha_hoy,
                            "calories_consumed": total_calorias,
                            "calories_burned": 0
                        }
                    }
                }
            )

        return jsonify({
            "estatus": "exito",
            "mensaje": "Comida añadida al total semanal e historial de gráficas diarias",
            "macros_añadidos": {
                "calorias": total_calorias,
                "proteinas": total_proteinas,
                "carbohidratos": total_carbohidratos,
                "grasas": total_grasas
            }
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error en S-06 (POST Log): {str(e)}"}), 500


# NUEVA RUTA PARA TU GRÁFICA DE PESO
@app.route('/analytics/chart/weight/<int:id_usuario>', methods=['GET'])
def datos_grafica_peso(id_usuario):
    try:
        usuario = coleccion_analiticas.find_one({"user_id": id_usuario}, {"weight_progress": 1, "_id": 0})
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify(usuario["weight_progress"]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# NUEVA RUTA PARA TU GRÁFICA DE CALORÍAS (Consumidas vs Quemadas)
@app.route('/analytics/chart/calories/<int:id_usuario>', methods=['GET'])
def datos_grafica_calorias(id_usuario):
    try:
        usuario = coleccion_analiticas.find_one({"user_id": id_usuario}, {"historial_calorias": 1, "_id": 0})
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify(usuario["historial_calorias"]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=8086, debug=True)