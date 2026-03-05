"""
API REST - Decision Support System
Endpoints para fornecer dados ao frontend
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import oracledb
from datetime import datetime
from infraestructure.processing.weather_processor import WeatherProcessingEngine

app = Flask(__name__)
CORS(app)

# Configuração do banco
DB_CONFIG = {
    "user": "system",
    "password": "K1lstrik098!",
    "dsn": "localhost:1521/XEPDB1"
}

def get_connection():
    """Obter conexão com o banco"""
    return oracledb.connect(**DB_CONFIG)


@app.route('/api/weather/raw/<int:location_id>', methods=['GET'])
def get_raw_weather(location_id):
    """
    GET /api/weather/raw/1
    Retorna dados brutos de WEATHER_RAW
    """
    try:
        hours = request.args.get('hours', 24, type=int)
        
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(f"""
            SELECT 
                ID, LOCATION_ID, DATA_TIMESTAMP, WIND_SPEED, WIND_DIRECTION,
                WAVE_HEIGHT, PRESSURE, SEA_TEMP, CURRENT_SPEED, CREATED_AT
            FROM WEATHER_RAW
            WHERE LOCATION_ID = {location_id}
            AND CREATED_AT >= SYSDATE - {hours}/24
            ORDER BY DATA_TIMESTAMP DESC
            FETCH FIRST 100 ROWS ONLY
        """)
        
        records = []
        for row in cursor.fetchall():
            records.append({
                "id": row[0],
                "location_id": row[1],
                "timestamp": row[2].isoformat() if row[2] else None,
                "wind_speed_kmh": float(row[3]) if row[3] else None,
                "wind_direction_deg": float(row[4]) if row[4] else None,
                "wave_height_m": float(row[5]) if row[5] else None,
                "pressure_hpa": float(row[6]) if row[6] else None,
                "sea_temp_c": float(row[7]) if row[7] else None,
                "current_speed_ms": float(row[8]) if row[8] else None,
                "collected_at": row[9].isoformat() if row[9] else None
            })
        
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "location_id": location_id,
            "records_count": len(records),
            "data": records
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================================
# ENDPOINT 2: Dados processados e inteligência
# ============================================================================
@app.route('/api/decision/<int:location_id>', methods=['GET'])
def get_decision_data(location_id):
    """
    GET /api/decision/1
    Retorna dados processados com inteligência (IEA, status, probabilidade)
    """
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(f"""
            SELECT 
                ID, LOCATION_ID, DATA_TIMESTAMP, IEA_SCORE, OPERATIONAL_STATUS,
                INTERRUPTION_PROBABILITY, TREND_INDICATOR, CREATED_AT
            FROM WEATHER_PROCESSED
            WHERE LOCATION_ID = {location_id}
            ORDER BY DATA_TIMESTAMP DESC
            FETCH FIRST 10 ROWS ONLY
        """)
        
        records = []
        for row in cursor.fetchall():
            records.append({
                "id": row[0],
                "location_id": row[1],
                "timestamp": row[2].isoformat() if row[2] else None,
                "iea_score": float(row[3]) if row[3] else None,
                "operational_status": row[4],
                "interruption_probability_percent": float(row[5]) if row[5] else None,
                "trend_indicator": row[6],
                "processed_at": row[7].isoformat() if row[7] else None
            })
        
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "location_id": location_id,
            "records_count": len(records),
            "data": records
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================================
# ENDPOINT 3: Status operacional atual
# ============================================================================
@app.route('/api/operational-status/<int:location_id>', methods=['GET'])
def get_operational_status(location_id):
    """
    GET /api/operational-status/1
    Retorna status operacional ATUAL da localização
    """
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        # Buscar último registro processado
        cursor.execute(f"""
            SELECT 
                L.NAME, L.PLATFORM_TYPE,
                P.DATA_TIMESTAMP, P.IEA_SCORE, P.OPERATIONAL_STATUS,
                P.INTERRUPTION_PROBABILITY, P.TREND_INDICATOR
            FROM WEATHER_PROCESSED P
            JOIN LOCATIONS L ON L.ID = P.LOCATION_ID
            WHERE P.LOCATION_ID = {location_id}
            ORDER BY P.DATA_TIMESTAMP DESC
            FETCH FIRST 1 ROW ONLY
        """)
        
        row = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not row:
            return jsonify({
                "status": "error",
                "message": "Nenhum dado processado para esta localização"
            }), 404
        
        return jsonify({
            "status": "success",
            "location": {
                "id": location_id,
                "name": row[0],
                "platform_type": row[1]
            },
            "current_status": {
                "timestamp": row[2].isoformat() if row[2] else None,
                "iea_score": float(row[3]) if row[3] else None,
                "operational_status": row[4],
                "interruption_probability_percent": float(row[5]) if row[5] else None,
                "trend_indicator": row[6],
                "is_operational": row[4] in ["EXCELENTE", "BOM", "MODERADO"]
            }
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================================
# ENDPOINT 4: Processar dados e gerar inteligência  
# ============================================================================
@app.route('/api/process-weather', methods=['POST'])
def process_weather():
    """
    POST /api/process-weather
    Dispara processamento de dados brutos → inteligência processada
    """
    try:
        engine = WeatherProcessingEngine()
        engine.connect()
        
        processed_count = engine.process_raw_weather_data()
        
        engine.disconnect()
        
        return jsonify({
            "status": "success",
            "message": f"{processed_count} registros processados com sucesso",
            "records_processed": processed_count
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================================
# ENDPOINT 5: Lista todas as localizações
# ============================================================================
@app.route('/api/locations', methods=['GET'])
def get_locations():
    """
    GET /api/locations
    Retorna todas as localizações cadastradas
    """
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT ID, NAME, LATITUDE, LONGITUDE, PLATFORM_TYPE
            FROM LOCATIONS
            ORDER BY NAME
        """)
        
        locations = []
        for row in cursor.fetchall():
            locations.append({
                "id": row[0],
                "name": row[1],
                "latitude": float(row[2]),
                "longitude": float(row[3]),
                "platform_type": row[4]
            })
        
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "locations_count": len(locations),
            "data": locations
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================================
# ENDPOINT 6: Limites operacionais
# ============================================================================
@app.route('/api/operation-limits', methods=['GET'])
def get_operation_limits():
    """
    GET /api/operation-limits
    Retorna limites operacionais por tipo de operação
    """
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT ID, OPERATION_TYPE, MAX_WIND, MAX_WAVE, MAX_CURRENT
            FROM OPERATION_LIMITS
            ORDER BY OPERATION_TYPE
        """)
        
        limits = []
        for row in cursor.fetchall():
            limits.append({
                "id": row[0],
                "operation_type": row[1],
                "max_wind_kmh": float(row[2]) if row[2] else None,
                "max_wave_m": float(row[3]) if row[3] else None,
                "max_current_ms": float(row[4]) if row[4] else None
            })
        
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "limits_count": len(limits),
            "data": limits
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================================
# ENDPOINT 7: Status de saúde da API
# ============================================================================
@app.route('/api/health', methods=['GET'])
def health_check():
    """
    GET /api/health
    Verifica se a API está funcionando e conectada ao banco
    """
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT SYSDATE FROM DUAL")
        db_time = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "healthy",
            "message": "API está operacional",
            "database_connected": True,
            "database_time": db_time.isoformat() if db_time else None,
            "api_time": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "message": str(e),
            "database_connected": False
        }), 500

# ============================================================================
# Rota raiz
# ============================================================================
@app.route('/', methods=['GET'])
def index():
    """Documentação dos endpoints disponíveis"""
    return jsonify({
        "app": "Maris Decision Engine - API",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /api/health",
            "locations": "GET /api/locations",
            "raw_weather": "GET /api/weather/raw/<location_id>?hours=24",
            "processed_decision": "GET /api/decision/<location_id>",
            "operational_status": "GET /api/operational-status/<location_id>",
            "operation_limits": "GET /api/operation-limits",
            "process_weather": "POST /api/process-weather"
        }
    }), 200

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 API REST - Decision Support System")
    print("=" * 80)
    print("\n📚 Endpoints disponíveis:")
    print("   GET  /api/health")
    print("   GET  /api/locations")
    print("   GET  /api/weather/raw/<location_id>")
    print("   GET  /api/decision/<location_id>")
    print("   GET  /api/operational-status/<location_id>")
    print("   GET  /api/operation-limits")
    print("   POST /api/process-weather")
    print("\n🌐 Acessar: http://localhost:5000")
    print("=" * 80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
