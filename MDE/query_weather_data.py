import oracledb
from datetime import datetime, timedelta

print("=" * 70)
print("Verificando dados armazenados em WEATHER_RAW")
print("=" * 70)

try:
    connection = oracledb.connect(
        user="system",
        password="K1lstrik098!",
        dsn="localhost:1521/XEPDB1"
    )
    
    cursor = connection.cursor()
    
    # 1. Verificar quantidade total de registros
    print("\n📊 Total de registros:")
    cursor.execute("SELECT COUNT(*) FROM WEATHER_RAW")
    total = cursor.fetchone()[0]
    print(f"   {total} registros na tabela")
    
    # 2. Estrutura da tabela
    print("\n📋 Estrutura da tabela WEATHER_RAW:")
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, NULLABLE
        FROM USER_TAB_COLUMNS
        WHERE TABLE_NAME = 'WEATHER_RAW'
        ORDER BY COLUMN_ID
    """)
    columns = cursor.fetchall()
    for col in columns:
        nullable = "✓ Null" if col[2] == 'Y' else "✗ Not Null"
        print(f"   {col[0]:<20} {col[1]:<15} {nullable}")
    
    if total > 0:
        # 3. Últimos registros inseridos
        print("\n📝 Últimos 5 registros:")
        cursor.execute("""
            SELECT 
                ID,
                LOCATION_ID,
                DATA_TIMESTAMP,
                WIND_SPEED,
                WIND_DIRECTION,
                WAVE_HEIGHT,
                PRESSURE,
                SEA_TEMP,
                CURRENT_SPEED,
                CREATED_AT
            FROM WEATHER_RAW
            ORDER BY CREATED_AT DESC
            FETCH FIRST 5 ROWS ONLY
        """)
        
        records = cursor.fetchall()
        for i, record in enumerate(records, 1):
            print(f"\n   Registro #{i}:")
            print(f"      ID: {record[0]}")
            print(f"      LOCATION_ID: {record[1]}")
            print(f"      DATA_TIMESTAMP: {record[2]}")
            print(f"      WIND_SPEED: {record[3]} km/h")
            print(f"      WIND_DIRECTION: {record[4]}°")
            print(f"      WAVE_HEIGHT: {record[5]}")
            print(f"      PRESSURE: {record[6]} hPa")
            print(f"      SEA_TEMP: {record[7]}°C")
            print(f"      CURRENT_SPEED: {record[8]}")
            print(f"      CREATED_AT: {record[9]}")
        
        # 4. Estatísticas
        print("\n📈 Estatísticas dos dados:")
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT LOCATION_ID) as locations,
                MIN(DATA_TIMESTAMP) as first_record,
                MAX(DATA_TIMESTAMP) as last_record,
                ROUND(AVG(WIND_SPEED), 2) as avg_wind_speed,
                MIN(WIND_SPEED) as min_wind_speed,
                MAX(WIND_SPEED) as max_wind_speed,
                ROUND(AVG(PRESSURE), 2) as avg_pressure
            FROM WEATHER_RAW
        """)
        
        stats = cursor.fetchone()
        print(f"   Localizações únicas: {stats[0]}")
        print(f"   Primeiro registro: {stats[1]}")
        print(f"   Último registro: {stats[2]}")
        print(f"   Velocidade média do vento: {stats[3]} km/h")
        print(f"   Vento mínimo: {stats[4]} km/h")
        print(f"   Vento máximo: {stats[5]} km/h")
        print(f"   Pressão média: {stats[6]} hPa")
        
        # 5. Registros por location_id
        print("\n📍 Registros por localização:")
        cursor.execute("""
            SELECT LOCATION_ID, COUNT(*) as quantidade
            FROM WEATHER_RAW
            GROUP BY LOCATION_ID
            ORDER BY LOCATION_ID
        """)
        
        locations = cursor.fetchall()
        for loc in locations:
            print(f"   LOCATION_ID {loc[0]}: {loc[1]} registros")
        
        print(f"\n✅ Dados estão sendo armazenados corretamente!")
        
    else:
        print("\n⚠️  Nenhum registro encontrado")
        print("   Execute 'python main.py' para coletar dados")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"\n❌ ERRO: {type(e).__name__}")
    print(f"   Detalhes: {str(e)}")

print("\n" + "=" * 70)
