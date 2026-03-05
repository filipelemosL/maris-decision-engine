import oracledb

print("=" * 60)
print("Criando tabela WEATHER_RAW")
print("=" * 60)

try:
    connection = oracledb.connect(
        user="system",
        password="K1lstrik098!",
        dsn="localhost:1521/XEPDB1"
    )
    
    cursor = connection.cursor()
    
    # Criar a tabela
    sql = """
    CREATE TABLE WEATHER_RAW (
        ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        LOCATION_ID NUMBER NOT NULL,
        DATA_TIMESTAMP TIMESTAMP NOT NULL,
        WIND_SPEED NUMBER,
        WIND_DIRECTION NUMBER,
        WAVE_HEIGHT NUMBER,
        PRESSURE NUMBER,
        SEA_TEMP NUMBER,
        CURRENT_SPEED NUMBER,
        CREATED_AT TIMESTAMP DEFAULT SYSDATE
    )
    """
    
    cursor.execute(sql)
    connection.commit()
    
    print("\n✅ Tabela WEATHER_RAW criada com SUCESSO!")
    
    # Criar índice para melhorar performance
    cursor.execute("""
        CREATE INDEX IDX_WEATHER_LOCATION_DATE 
        ON WEATHER_RAW(LOCATION_ID, DATA_TIMESTAMP)
    """)
    connection.commit()
    
    print("✅ Índice criado com SUCESSO!")
    
    cursor.close()
    connection.close()
    
    print("\n✅ Banco está pronto! Você pode executar: python main.py")
    
except oracledb.exceptions.DatabaseError as e:
    if "ORA-00955" in str(e):
        print("⚠️  Tabela já existe no banco")
    else:
        print(f"❌ ERRO: {e}")
except Exception as e:
    print(f"❌ ERRO: {e}")

print("=" * 60)
