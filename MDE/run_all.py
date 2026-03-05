#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🚀 Maris Decision Engine - Coleta de Dados + API em UM ÚNICO COMANDO

Executa:
1. Scheduler de coleta (a cada 5 minutos)
2. API Flask (servindo dados)

Tudo ao mesmo tempo com: python run_all.py
"""

import threading
import schedule
import time
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import oracledb

# ============================================================================
# 1. IMPORTAR LÓGICA DE COLETA
# ============================================================================

from application.use_cases.collect_weather import CollectWeatherUseCase
from infraestructure.external.open_meteo_provider import OpenMeteoProvider
from infraestructure.database.oracle_weather_repository import OracleWeatherRepository

# ============================================================================
# 2. CONFIGURAR FLASK API
# ============================================================================

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["localhost:3000", "localhost:3000", "*.vercel.app", "*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
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
# 3. ENDPOINTS DA API
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check - verifica se API e DB estão online"""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT SYSDATE FROM DUAL")
        db_time = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "healthy",
            "message": "🚀 API e Scheduler rodando!",
            "database_connected": True,
            "database_time": db_time.isoformat() if db_time else None,
            "api_time": datetime.now().isoformat(),
            "scheduler_active": True
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "message": str(e),
            "database_connected": False
        }), 500


@app.route('/api/all-locations-status', methods=['GET'])
def get_all_locations_status():
    """Retorna status de todas as plataformas"""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT 
                L.ID, L.NAME, L.PLATFORM_TYPE,
                L.LATITUDE, L.LONGITUDE,
                COALESCE(P.IEA_SCORE, 0) as IEA_SCORE,
                COALESCE(P.OPERATIONAL_STATUS, 'DESCONHECIDO') as STATUS,
                P.DATA_TIMESTAMP
            FROM LOCATIONS L
            LEFT JOIN WEATHER_PROCESSED P ON L.ID = P.LOCATION_ID
                AND P.DATA_TIMESTAMP = (
                    SELECT MAX(DATA_TIMESTAMP) 
                    FROM WEATHER_PROCESSED 
                    WHERE LOCATION_ID = L.ID
                )
            ORDER BY L.ID
        """)
        
        locations = []
        for row in cursor.fetchall():
            status = row[6] if row[6] else "DESCONHECIDO"
            iea = float(row[5]) if row[5] else 0
            
            # Definir cor baseado no status
            color_map = {
                "EXCELENTE": "#00AA00",
                "BOM": "#44DD44",
                "MODERADO": "#FFAA00",
                "RESTRITO": "#FF6600",
                "PROIBIDO": "#FF0000",
                "DESCONHECIDO": "#CCCCCC"
            }
            
            locations.append({
                "id": row[0],
                "name": row[1],
                "platform_type": row[2],
                "coordinates": {
                    "latitude": float(row[3]),
                    "longitude": float(row[4])
                },
                "iea_score": iea,
                "operational_status": status,
                "can_operate": status in ["EXCELENTE", "BOM", "MODERADO"],
                "color": color_map.get(status, "#CCCCCC"),
                "last_update": row[7].isoformat() if row[7] else None
            })
        
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "count": len(locations),
            "data": locations,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/operational-status/<int:location_id>', methods=['GET'])
def get_operational_status(location_id):
    """Retorna status operacional atual de uma plataforma"""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(f"""
            SELECT 
                L.NAME, L.PLATFORM_TYPE, L.LATITUDE, L.LONGITUDE,
                P.DATA_TIMESTAMP, P.IEA_SCORE, P.OPERATIONAL_STATUS,
                P.INTERRUPTION_PROBABILITY, P.TREND_INDICATOR
            FROM LOCATIONS L
            LEFT JOIN WEATHER_PROCESSED P ON L.ID = P.LOCATION_ID
                AND P.DATA_TIMESTAMP = (
                    SELECT MAX(DATA_TIMESTAMP) 
                    FROM WEATHER_PROCESSED 
                    WHERE LOCATION_ID = L.ID
                )
            WHERE L.ID = {location_id}
        """)
        
        row = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not row:
            return jsonify({"status": "error", "message": "Localização não encontrada"}), 404
        
        operational_status = row[6] if row[6] else "DESCONHECIDO"
        iea_score = float(row[5]) if row[5] else 0
        
        color_map = {
            "EXCELENTE": "#00AA00",
            "BOM": "#44DD44",
            "MODERADO": "#FFAA00",
            "RESTRITO": "#FF6600",
            "PROIBIDO": "#FF0000",
            "DESCONHECIDO": "#CCCCCC"
        }
        
        return jsonify({
            "status": "success",
            "location": {
                "id": location_id,
                "name": row[0],
                "platform_type": row[1],
                "latitude": float(row[2]),
                "longitude": float(row[3])
            },
            "decision": {
                "timestamp": row[4].isoformat() if row[4] else None,
                "iea_score": iea_score,
                "operational_status": operational_status,
                "interruption_probability_percent": float(row[7]) if row[7] else 0,
                "trend_indicator": row[8] if row[8] else "N/A",
                "is_operational": operational_status in ["EXCELENTE", "BOM", "MODERADO"],
                "color": color_map.get(operational_status, "#CCCCCC"),
                "risk_level": "minimo" if iea_score < 20 else "baixo" if iea_score < 40 else "medio" if iea_score < 60 else "alto" if iea_score < 80 else "critico"
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/decision-history/<int:location_id>', methods=['GET'])
def get_decision_history(location_id):
    """Retorna histórico de decisões (últimas 24h)"""
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
            ORDER BY DATA_TIMESTAMP DESC
            FETCH FIRST 100 ROWS ONLY
        """)
        
        records = []
        for row in cursor.fetchall():
            records.append({
                "timestamp": row[0].isoformat() if row[0] else None,
                "iea_score": float(row[1]) if row[1] else 0,
                "status": row[2] if row[2] else "DESCONHECIDO",
                "interruption_probability": float(row[3]) if row[3] else 0,
                "trend": row[4] if row[4] else "N/A"
            })
        
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "location_id": location_id,
            "hours": hours,
            "count": len(records),
            "data": records,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/weather-raw/<int:location_id>', methods=['GET'])
def get_weather_raw(location_id):
    """Retorna dados brutos meteorológicos"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(f"""
            SELECT 
                DATA_TIMESTAMP, WIND_SPEED, WIND_DIRECTION,
                WAVE_HEIGHT, CURRENT_SPEED, PRESSURE
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
                "current_speed_ms": float(row[4]) if row[4] else None,
                "pressure_hpa": float(row[5]) if row[5] else None
            })
        
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success",
            "location_id": location_id,
            "count": len(records),
            "data": records,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/process-data', methods=['POST'])
def process_data():
    """Dispara processamento manual de dados brutos"""
    try:
        from infraestructure.processing.weather_processor import WeatherProcessingEngine
        
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
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/', methods=['GET'])
def index():
    """Rota raiz com documentação"""
    return jsonify({
        "app": "🚀 Maris Decision Engine",
        "version": "2.0",
        "mode": "Coleta + API (Integrado)",
        "status": "RODANDO ✅",
        "features": {
            "scheduler": "Ativo - coleta a cada 5 minutos",
            "api": "Ativa - servindo dados",
            "database": "Conectado ao Oracle"
        },
        "endpoints": {
            "health": "GET /api/health",
            "all_locations": "GET /api/all-locations-status",
            "location_status": "GET /api/operational-status/<id>",
            "history": "GET /api/decision-history/<id>",
            "weather_raw": "GET /api/weather-raw/<id>",
            "process": "POST /api/process-data"
        }
    }), 200

# ============================================================================
# 4. SCHEDULER DE COLETA (Thread separada)
# ============================================================================

class DataCollectorScheduler:
    """Gerencia o scheduler de coleta de dados"""
    
    def __init__(self):
        self.running = False
        self.thread = None
    
    def collect_weather(self):
        """Executa uma coleta de dados"""
        try:
            print(f"\n⏰ [{datetime.now().strftime('%H:%M:%S')}] Iniciando coleta de dados...")
            
            # Conectar ao banco
            connection = oracledb.connect(
                user="system",
                password="K1lstrik098!",
                dsn="localhost:1521/XEPDB1"
            )
            
            # Inicializar provider e repository
            provider = OpenMeteoProvider()
            repository = OracleWeatherRepository(connection)
            
            # Criar e executar use case
            use_case = CollectWeatherUseCase(provider, repository)
            result = use_case.execute(
                location_id=1,
                lat=-11.0325631,
                lon=-37.0829041
            )
            
            print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Coleta concluída! Vento: {result.wind_speed:.2f} km/h")
            
            connection.close()
            
        except Exception as e:
            print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Erro na coleta: {str(e)}")
    
    def schedule_jobs(self):
        """Define os jobs do scheduler"""
        schedule.every(5).minutes.do(self.collect_weather)
        
        # Primeira coleta ao iniciar
        self.collect_weather()
    
    def run(self):
        """Roda o scheduler indefinidamente"""
        self.running = True
        self.schedule_jobs()
        
        print("\n" + "="*80)
        print("📊 SCHEDULER INICIADO")
        print("="*80)
        print("⏰ Coleta agendada: A cada 5 minutos")
        print("="*80 + "\n")
        
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def start_thread(self):
        """Inicia o scheduler em uma thread separada"""
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        print("✅ Thread de coleta iniciada")
    
    def stop(self):
        """Para o scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

# ============================================================================
# 5. INICIAR TUDO
# ============================================================================

if __name__ == "__main__":
    scheduler = DataCollectorScheduler()
    
    print("\n" + "="*80)
    print("🚀 MARIS DECISION ENGINE - COLETA + API INTEGRADAS")
    print("="*80)
    print("\n📊 Iniciando componentes...")
    
    # 1. Iniciar scheduler em thread separada
    scheduler.start_thread()
    time.sleep(2)
    
    # 2. Iniciar Flask API na thread principal
    print("\n" + "="*80)
    print("🌐 API REST INICIANDO")
    print("="*80)
    print("📍 URL: http://localhost:5000")
    print("📍 URL: http://0.0.0.0:5000 (Rede)")
    print("="*80)
    print("\n📚 Endpoints disponíveis:")
    print("   GET  /api/health")
    print("   GET  /api/all-locations-status")
    print("   GET  /api/operational-status/<location_id>")
    print("   GET  /api/decision-history/<location_id>")
    print("   GET  /api/weather-raw/<location_id>")
    print("   POST /api/process-data")
    print("\n🚀 Tudo rodando! Use Ctrl+C para parar.\n")
    print("="*80 + "\n")
    
    try:
        app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
    except KeyboardInterrupt:
        print("\n\n⏹️  Parando tudo...")
        scheduler.stop()
        print("✅ Finalizado")
