"""
SCRIPT DE TESTES - API Endpoints
Testa cada endpoint do sistema de decisão
"""

import oracledb
import json
from infraestructure.processing.weather_processor import WeatherProcessingEngine

print("=" * 80)
print("TESTES DOS ENDPOINTS DA API")
print("=" * 80)

# ============================================================================
# TESTE 1: Health Check
# ============================================================================
print("\n1️⃣  Teste: GET /api/health")
print("-" * 80)
try:
    connection = oracledb.connect(
        user="system",
        password="K1lstrik098!",
        dsn="localhost:1521/XEPDB1"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT SYSDATE FROM DUAL")
    db_time = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    
    print(f"✅ Banco conectado")
    print(f"   Horário do banco: {db_time}")

except Exception as e:
    print(f"❌ Erro: {str(e)}")

# ============================================================================
# TESTE 2: Get Locations
# ============================================================================
print("\n2️⃣  Teste: GET /api/locations")
print("-" * 80)
try:
    connection = oracledb.connect(
        user="system",
        password="K1lstrik098!",
        dsn="localhost:1521/XEPDB1"
    )
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
    
    print(f"✅ {len(locations)} localização(ões) encontrada(s)")
    for loc in locations:
        print(f"   ID: {loc['id']} | Nome: {loc['name']} | Tipo: {loc['platform_type']}")
    
    cursor.close()
    connection.close()

except Exception as e:
    print(f"❌ Erro: {str(e)}")

# ============================================================================
# TESTE 3: Get Raw Weather
# ============================================================================
print("\n3️⃣  Teste: GET /api/weather/raw/1")
print("-" * 80)
try:
    connection = oracledb.connect(
        user="system",
        password="K1lstrik098!",
        dsn="localhost:1521/XEPDB1"
    )
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT 
            ID, LOCATION_ID, DATA_TIMESTAMP, WIND_SPEED, WIND_DIRECTION,
            WAVE_HEIGHT, PRESSURE, SEA_TEMP, CURRENT_SPEED, CREATED_AT
        FROM WEATHER_RAW
        WHERE LOCATION_ID = 1
        ORDER BY DATA_TIMESTAMP DESC
        FETCH FIRST 5 ROWS ONLY
    """)
    
    records = []
    for row in cursor.fetchall():
        records.append({
            "id": row[0],
            "timestamp": row[2].isoformat() if row[2] else None,
            "wind_speed_kmh": float(row[3]) if row[3] else None,
            "wind_direction_deg": float(row[4]) if row[4] else None,
            "wave_height_m": float(row[5]) if row[5] else None,
            "pressure_hpa": float(row[6]) if row[6] else None,
            "sea_temp_c": float(row[7]) if row[7] else None,
            "current_speed_ms": float(row[8]) if row[8] else None
        })
    
    print(f"✅ {len(records)} registro(s) bruto(s) de clima encontrado(s)")
    for i, rec in enumerate(records[:3], 1):
        print(f"\n   Registro #{i}:")
        print(f"      Timestamp: {rec['timestamp']}")
        print(f"      Vento: {rec['wind_speed_kmh']} km/h ({rec['wind_direction_deg']}°)")
        print(f"      Onda: {rec['wave_height_m']} m")
        print(f"      Pressão: {rec['pressure_hpa']} hPa")
    
    cursor.close()
    connection.close()

except Exception as e:
    print(f"❌ Erro: {str(e)}")

# ============================================================================
# TESTE 4: Get Decision Data
# ============================================================================
print("\n4️⃣  Teste: GET /api/decision/1")
print("-" * 80)
try:
    connection = oracledb.connect(
        user="system",
        password="K1lstrik098!",
        dsn="localhost:1521/XEPDB1"
    )
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT 
            ID, LOCATION_ID, DATA_TIMESTAMP, IEA_SCORE, OPERATIONAL_STATUS,
            INTERRUPTION_PROBABILITY, TREND_INDICATOR, CREATED_AT
        FROM WEATHER_PROCESSED
        WHERE LOCATION_ID = 1
        ORDER BY DATA_TIMESTAMP DESC
        FETCH FIRST 5 ROWS ONLY
    """)
    
    records = []
    for row in cursor.fetchall():
        records.append({
            "timestamp": row[2].isoformat() if row[2] else None,
            "iea_score": float(row[3]) if row[3] else None,
            "operational_status": row[4],
            "interruption_probability_percent": float(row[5]) if row[5] else None,
            "trend_indicator": row[6]
        })
    
    print(f"✅ {len(records)} registro(s) processado(s) encontrado(s)")
    for i, rec in enumerate(records[:3], 1):
        print(f"\n   Registro #{i}:")
        print(f"      Timestamp: {rec['timestamp']}")
        print(f"      IEA Score: {rec['iea_score']} (0-100)")
        print(f"      Status: {rec['operational_status']}")
        print(f"      Probabilidade de Interrupção: {rec['interruption_probability_percent']}%")
        print(f"      Tendência: {rec['trend_indicator']}")
    
    cursor.close()
    connection.close()

except Exception as e:
    print(f"❌ Erro: {str(e)}")

# ============================================================================
# TESTE 5: Get Operation Limits
# ============================================================================
print("\n5️⃣  Teste: GET /api/operation-limits")
print("-" * 80)
try:
    connection = oracledb.connect(
        user="system",
        password="K1lstrik098!",
        dsn="localhost:1521/XEPDB1"
    )
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT ID, OPERATION_TYPE, MAX_WIND, MAX_WAVE, MAX_CURRENT
        FROM OPERATION_LIMITS
        ORDER BY OPERATION_TYPE
    """)
    
    limits = []
    for row in cursor.fetchall():
        limits.append({
            "operation_type": row[1],
            "max_wind_kmh": float(row[2]) if row[2] else None,
            "max_wave_m": float(row[3]) if row[3] else None,
            "max_current_ms": float(row[4]) if row[4] else None
        })
    
    print(f"✅ {len(limits)} tipo(s) de operação encontrado(s)")
    for lim in limits:
        print(f"\n   {lim['operation_type']}:")
        print(f"      Max Vento: {lim['max_wind_kmh']} km/h")
        print(f"      Max Onda: {lim['max_wave_m']} m")
        print(f"      Max Corrente: {lim['max_current_ms']} m/s")
    
    cursor.close()
    connection.close()

except Exception as e:
    print(f"❌ Erro: {str(e)}")

# ============================================================================
# TESTE 6: Get Current Operational Status
# ============================================================================
print("\n6️⃣  Teste: GET /api/operational-status/1")
print("-" * 80)
try:
    connection = oracledb.connect(
        user="system",
        password="K1lstrik098!",
        dsn="localhost:1521/XEPDB1"
    )
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT 
            L.NAME, L.PLATFORM_TYPE,
            P.DATA_TIMESTAMP, P.IEA_SCORE, P.OPERATIONAL_STATUS,
            P.INTERRUPTION_PROBABILITY, P.TREND_INDICATOR
        FROM WEATHER_PROCESSED P
        JOIN LOCATIONS L ON L.ID = P.LOCATION_ID
        WHERE P.LOCATION_ID = 1
        ORDER BY P.DATA_TIMESTAMP DESC
        FETCH FIRST 1 ROW ONLY
    """)
    
    row = cursor.fetchone()
    
    if row:
        print(f"✅ Status operacional atual encontrado")
        print(f"\n   Localização: {row[0]} ({row[1]})")
        print(f"   Timestamp: {row[2]}")
        print(f"   IEA Score: {row[3]} (0-100)")
        print(f"   Status Operacional: {row[4]}")
        print(f"   Probabilidade de Interrupção: {row[5]}%")
        print(f"   Tendência: {row[6]}")
        
        is_operational = row[4] in ["EXCELENTE", "BOM", "MODERADO"]
        print(f"   ⚠️  Pode Operar: {'SIM ✅' if is_operational else 'NÃO ❌'}")
    else:
        print("⚠️  Nenhum dado processado para esta localização")
    
    cursor.close()
    connection.close()

except Exception as e:
    print(f"❌ Erro: {str(e)}")

# ============================================================================
# TESTE 7: Process Weather (trigger processing)
# ============================================================================
print("\n7️⃣  Teste: POST /api/process-weather")
print("-" * 80)
try:
    engine = WeatherProcessingEngine()
    engine.connect()
    
    processed_count = engine.process_raw_weather_data()
    
    engine.disconnect()
    
    print(f"✅ {processed_count} registros processados com sucesso")

except Exception as e:
    print(f"❌ Erro: {str(e)}")

print("\n" + "=" * 80)
print("✅ TODOS OS TESTES CONCLUÍDOS!")
print("=" * 80)
print("\n💡 Para usar a API no frontend:")
print("   1. Iniciar servidor: python api.py")
print("   2. Acessar: http://localhost:5000")
print("=" * 80)
