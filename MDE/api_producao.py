"""
CONFIGURAÇÃO PARA PRODUÇÃO
API rodando permanentemente + Frontend no Vercel
"""

import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import oracledb
from datetime import datetime
from infraestructure.processing.weather_processor import WeatherProcessingEngine

# ============================================================================
# CONFIGURAR VARIÁVEIS DE AMBIENTE
# ============================================================================
# Criar arquivo .env na raiz do projeto com:
"""
FLASK_ENV=production
FLASK_DEBUG=False
API_PORT=5000
API_HOST=0.0.0.0
VERCEL_URL=https://seu-dominio.vercel.app
"""

app = Flask(__name__)

# ============================================================================
# CONFIGURAR CORS PARA VERCEL
# ============================================================================
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",           # Desenvolvimento local
            "http://localhost:5000",           # API local
            "https://*.vercel.app",            # Todos subdomínios Vercel
            "https://seu-dominio.vercel.app",  # Seu domínio específico
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

# Configuração do banco
DB_CONFIG = {
    "user": "system",
    "password": "K1lstrik098!",
    "dsn": "localhost:1521/XEPDB1"
}

def get_connection():
    """Obter conexão com o banco"""
    return oracledb.connect(**DB_CONFIG)

# ============================================================================
# ENDPOINT 1: Health Check
# ============================================================================
@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica saúde da API"""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT SYSDATE FROM DUAL")
        db_time = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "healthy",
            "message": "API online e operacional",
            "database_connected": True,
            "database_time": db_time.isoformat() if db_time else None,
            "api_time": datetime.now().isoformat(),
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "message": str(e),
            "database_connected": False,
            "timestamp": datetime.now().isoformat()
        }), 500

# ============================================================================
# ENDPOINT 2: Status Operacional (PRINCIPAL - mais usado)
# ============================================================================
@app.route('/api/operational-status/<int:location_id>', methods=['GET'])
def get_operational_status(location_id):
    """Retorna status operacional ATUAL - para exibir no dashboard"""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(f"""
            SELECT 
                L.ID, L.NAME, L.PLATFORM_TYPE, L.LATITUDE, L.LONGITUDE,
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
                "message": "Nenhum dado disponível para esta localização"
            }), 404
        
        # Determinar cor/ícone baseado no status
        status_colors = {
            "EXCELENTE": "green",
            "BOM": "blue",
            "MODERADO": "yellow",
            "RESTRITO": "orange",
            "PROIBIDO": "red"
        }
        
        return jsonify({
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "location": {
                "id": row[0],
                "name": row[1],
                "platform_type": row[2],
                "latitude": float(row[3]),
                "longitude": float(row[4])
            },
            "decision": {
                "timestamp": row[5].isoformat() if row[5] else None,
                "iea_score": float(row[6]) if row[6] else None,
                "operational_status": row[7],
                "interruption_probability_percent": float(row[8]) if row[8] else None,
                "trend_indicator": row[9],
                "is_operational": row[7] in ["EXCELENTE", "BOM", "MODERADO"],
                "color": status_colors.get(row[7], "gray"),
                "risk_level": {
                    "EXCELENTE": "minimo",
                    "BOM": "baixo",
                    "MODERADO": "medio",
                    "RESTRITO": "alto",
                    "PROIBIDO": "critico"
                }.get(row[7], "desconhecido")
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# ============================================================================
# ENDPOINT 3: Todas as Localizações com Status
# ============================================================================
@app.route('/api/all-locations-status', methods=['GET'])
def get_all_locations_status():
    """Retorna status de TODAS as localizações - para dashboard com múltiplas plataformas"""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT 
                L.ID, L.NAME, L.PLATFORM_TYPE, L.LATITUDE, L.LONGITUDE,
                COALESCE(P.DATA_TIMESTAMP, SYSDATE) as TIMESTAMP,
                COALESCE(P.IEA_SCORE, 0) as IEA_SCORE,
                COALESCE(P.OPERATIONAL_STATUS, 'DESCONHECIDO') as STATUS,
                COALESCE(P.INTERRUPTION_PROBABILITY, 0) as INTERRUPT_PROB,
                COALESCE(P.TREND_INDICATOR, 'N/A') as TREND
            FROM LOCATIONS L
            LEFT JOIN (
                SELECT * FROM WEATHER_PROCESSED
                WHERE (LOCATION_ID, DATA_TIMESTAMP) IN (
                    SELECT LOCATION_ID, MAX(DATA_TIMESTAMP)
                    FROM WEATHER_PROCESSED
                    GROUP BY LOCATION_ID
                )
            ) P ON L.ID = P.LOCATION_ID
            ORDER BY L.NAME
        """)
        
        locations = []
        status_colors = {
            "EXCELENTE": "green",
            "BOM": "blue",
            "MODERADO": "yellow",
            "RESTRITO": "orange",
            "PROIBIDO": "red",
            "DESCONHECIDO": "gray"
        }
        
        for row in cursor.fetchall():
            locations.append({
                "id": row[0],
                "name": row[1],
                "platform_type": row[2],
                "coordinates": {
                    "latitude": float(row[3]),
                    "longitude": float(row[4])
                },
                "last_update": row[5].isoformat() if row[5] else None,
                "iea_score": float(row[6]) if row[6] else 0,
                "operational_status": row[7],
                "color": status_colors.get(row[7], "gray"),
                "interruption_probability": float(row[8]) if row[8] else 0,
                "trend": row[9],
                "can_operate": row[7] in ["EXCELENTE", "BOM", "MODERADO"]
            })
        
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "count": len(locations),
            "timestamp": datetime.now().isoformat(),
            "data": locations
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ============================================================================
# ENDPOINT 4: Histórico de Decisões
# ============================================================================
@app.route('/api/decision-history/<int:location_id>', methods=['GET'])
def get_decision_history(location_id):
    """Retorna histórico de decisões para gráficos"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(f"""
            SELECT 
                DATA_TIMESTAMP, IEA_SCORE, OPERATIONAL_STATUS,
                INTERRUPTION_PROBABILITY, TREND_INDICATOR
            FROM WEATHER_PROCESSED
            WHERE LOCATION_ID = {location_id}
            AND DATA_TIMESTAMP >= SYSDATE - {hours}/24
            ORDER BY DATA_TIMESTAMP ASC
            FETCH FIRST 100 ROWS ONLY
        """)
        
        records = []
        for row in cursor.fetchall():
            records.append({
                "timestamp": row[0].isoformat() if row[0] else None,
                "iea_score": float(row[1]) if row[1] else None,
                "status": row[2],
                "interruption_probability": float(row[3]) if row[3] else None,
                "trend": row[4]
            })
        
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "location_id": location_id,
            "hours": hours,
            "count": len(records),
            "timestamp": datetime.now().isoformat(),
            "data": records
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ============================================================================
# ENDPOINT 5: Dados Brutos Recentes
# ============================================================================
@app.route('/api/weather-raw/<int:location_id>', methods=['GET'])
def get_raw_weather(location_id):
    """Retorna dados brutos para análise detalhada"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(f"""
            SELECT 
                DATA_TIMESTAMP, WIND_SPEED, WIND_DIRECTION,
                WAVE_HEIGHT, PRESSURE, SEA_TEMP, CURRENT_SPEED
            FROM WEATHER_RAW
            WHERE LOCATION_ID = {location_id}
            AND DATA_TIMESTAMP >= SYSDATE - {hours}/24
            ORDER BY DATA_TIMESTAMP DESC
            FETCH FIRST 100 ROWS ONLY
        """)
        
        records = []
        for row in cursor.fetchall():
            records.append({
                "timestamp": row[0].isoformat() if row[0] else None,
                "wind_speed_kmh": float(row[1]) if row[1] else None,
                "wind_direction_deg": float(row[2]) if row[2] else None,
                "wave_height_m": float(row[3]) if row[3] else None,
                "pressure_hpa": float(row[4]) if row[4] else None,
                "sea_temp_c": float(row[5]) if row[5] else None,
                "current_speed_ms": float(row[6]) if row[6] else None
            })
        
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "location_id": location_id,
            "count": len(records),
            "timestamp": datetime.now().isoformat(),
            "data": records
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ============================================================================
# ENDPOINT 6: Processar Dados (dispara manualmente)
# ============================================================================
@app.route('/api/process-data', methods=['POST'])
def process_data():
    """Processa dados brutos e gera inteligência"""
    try:
        engine = WeatherProcessingEngine()
        engine.connect()
        processed_count = engine.process_raw_weather_data()
        engine.disconnect()
        
        return jsonify({
            "status": "success",
            "message": f"{processed_count} registros processados",
            "records_processed": processed_count,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ============================================================================
# ROTA RAIZ - Documentação
# ============================================================================
@app.route('/', methods=['GET'])
def index():
    """Documentação dos endpoints"""
    return jsonify({
        "app": "Maris Decision Engine",
        "version": "2.0.0",
        "environment": "production",
        "description": "Sistema de Inteligência para Decisão em Operações Marítimas",
        "endpoints": {
            "health": "GET /api/health",
            "all_locations_status": "GET /api/all-locations-status",
            "operational_status": "GET /api/operational-status/<location_id>",
            "decision_history": "GET /api/decision-history/<location_id>?hours=24",
            "weather_raw": "GET /api/weather-raw/<location_id>?hours=24",
            "process_data": "POST /api/process-data"
        }
    }), 200

if __name__ == "__main__":
    # Modo produção
    port = int(os.environ.get('API_PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("=" * 80)
    print("🚀 MARIS DECISION ENGINE - API em PRODUÇÃO")
    print("=" * 80)
    print(f"\n📡 Servidor: 0.0.0.0:{port}")
    print(f"🌐 Endpoint: http://localhost:{port}")
    print(f"📱 Frontend pode acessar via CORS")
    print("\n✨ Endpoints disponíveis:")
    print("   • /api/health")
    print("   • /api/all-locations-status")
    print("   • /api/operational-status/<id>")
    print("   • /api/decision-history/<id>")
    print("   • /api/weather-raw/<id>")
    print("   • /api/process-data")
    print("\n" + "=" * 80 + "\n")
    
    app.run(debug=debug, host='0.0.0.0', port=port, threaded=True)
