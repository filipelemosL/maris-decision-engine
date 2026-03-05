import oracledb
import json
import csv
from datetime import datetime
from pathlib import Path

print("=" * 80)
print("Ferramenta de Consulta - WEATHER_RAW")
print("=" * 80)

try:
    connection = oracledb.connect(
        user="system",
        password="K1lstrik098!",
        dsn="localhost:1521/XEPDB1"
    )
    
    cursor = connection.cursor()
    
    # Buscar todos os dados
    print("\n📊 Buscando todos os dados da tabela WEATHER_RAW...\n")
    
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
    """)
    
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    
    if not rows:
        print("⚠️  Nenhum dado encontrado na tabela!")
    else:
        # 1. Exibir em formato tabular
        print("📋 Dados em formato tabular:")
        print("-" * 80)
        
        # Cabeçalho
        header = f"{'ID':<5} {'LOC':<5} {'DATA/HORA':<19} {'VENTO':<8} {'DIR':<5} {'ONDA':<8} {'PRESS':<8} {'TEMP':<6}"
        print(header)
        print("-" * 80)
        
        # Dados
        for row in rows:
            id_val = row[0]
            location = row[1]
            timestamp = row[2].strftime("%Y-%m-%d %H:%M:%S") if row[2] else "N/A"
            wind_speed = f"{row[3]:.1f}" if row[3] else "N/A"
            wind_dir = f"{row[4]}" if row[4] else "N/A"
            wave = f"{row[5]}" if row[5] else "N/A"
            pressure = f"{row[6]}" if row[6] else "N/A"
            sea_temp = f"{row[7]}" if row[7] else "N/A"
            
            line = f"{id_val:<5} {location:<5} {timestamp:<19} {wind_speed:<8} {wind_dir:<5} {wave:<8} {pressure:<8} {sea_temp:<6}"
            print(line)
        
        print("-" * 80)
        print(f"Total: {len(rows)} registro(s)\n")
        
        # 2. Exportar como JSON
        print("💾 Exportando dados como JSON...")
        json_data = []
        for row in rows:
            record = {
                "ID": row[0],
                "LOCATION_ID": row[1],
                "DATA_TIMESTAMP": row[2].isoformat() if row[2] else None,
                "WIND_SPEED": float(row[3]) if row[3] else None,
                "WIND_DIRECTION": float(row[4]) if row[4] else None,
                "WAVE_HEIGHT": float(row[5]) if row[5] else None,
                "PRESSURE": float(row[6]) if row[6] else None,
                "SEA_TEMP": float(row[7]) if row[7] else None,
                "CURRENT_SPEED": float(row[8]) if row[8] else None,
                "CREATED_AT": row[9].isoformat() if row[9] else None
            }
            json_data.append(record)
        
        json_file = "weather_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Arquivo salvo: {json_file}")
        
        # 3. Exportar como CSV
        print("💾 Exportando dados como CSV...")
        csv_file = "weather_data.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(column_names)
            for row in rows:
                writer.writerow(row)
        print(f"✅ Arquivo salvo: {csv_file}")
        
        # 4. Exibir em formato JSON na tela
        print("\n📄 Dados em formato JSON:")
        print("-" * 80)
        print(json.dumps(json_data, indent=2, ensure_ascii=False))
    
    cursor.close()
    connection.close()

except Exception as e:
    print(f"❌ ERRO: {type(e).__name__}")
    print(f"   Detalhes: {str(e)}")

print("\n" + "=" * 80)
