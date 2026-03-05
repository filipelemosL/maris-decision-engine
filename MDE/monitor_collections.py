import oracledb
import time
from datetime import datetime

print("=" * 80)
print("MONITOR - Verificando coletas a cada 5 minutos")
print("=" * 80)
print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Pressione Ctrl+C para parar\n")

try:
    previous_count = 0
    
    while True:
        try:
            connection = oracledb.connect(
                user="system",
                password="K1lstrik098!",
                dsn="localhost:1521/XEPDB1"
            )
            
            cursor = connection.cursor()
            
            # Contar total de registros
            cursor.execute("SELECT COUNT(*) FROM WEATHER_RAW")
            total_count = cursor.fetchone()[0]
            
            # Buscar último registro
            cursor.execute("""
                SELECT 
                    ID,
                    LOCATION_ID,
                    DATA_TIMESTAMP,
                    WIND_SPEED,
                    WIND_DIRECTION,
                    CREATED_AT
                FROM WEATHER_RAW
                ORDER BY CREATED_AT DESC
                FETCH FIRST 1 ROW ONLY
            """)
            
            last_record = cursor.fetchone()
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}]", end=" ")
            
            if total_count > previous_count:
                new_records = total_count - previous_count
                print(f"✅ {new_records} novo(s) registro(s) inserido(s)! Total: {total_count}")
                if last_record:
                    print(f"  └─ ID: {last_record[0]} | LOC: {last_record[1]} | Vento: {last_record[3]} km/h")
                previous_count = total_count
            else:
                print(f"⏳ Aguardando... (Total: {total_count} registros)")
            
            cursor.close()
            connection.close()
            
            # Aguardar 10 segundos antes de verificar novamente
            # (para poupar recursos, enquanto aguarda coleta a cada 5 min)
            time.sleep(10)
            
        except Exception as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] ❌ Erro ao conectar: {str(e)}")
            time.sleep(10)

except KeyboardInterrupt:
    print("\n" + "=" * 80)
    print("⛔ Monitor interrompido pelo usuário")
    print(f"Encerrado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
