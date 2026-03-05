import oracledb

print("=" * 60)
print("Testando conexão com Oracle Database")
print("=" * 60)

try:
    print("\n🔄 Tentando conectar ao banco...")
    print("   Host: localhost:1521/XEPDB1")
    print("   User: system")
    
    connection = oracledb.connect(
        user="system",
        password="K1lstrik098!",
        dsn="localhost:1521/XEPDB1"
    )
    
    print("\n✅ SUCESSO! Banco Oracle está rodando!")
    
    # Testar com um comando simples
    cursor = connection.cursor()
    cursor.execute("SELECT SYSDATE FROM DUAL")
    result = cursor.fetchone()
    print(f"   Data/Hora do servidor: {result[0]}")
    
    # Verificar se a tabela WEATHER_RAW existe
    cursor.execute("""
        SELECT COUNT(*)
        FROM USER_TABLES 
        WHERE TABLE_NAME = 'WEATHER_RAW'
    """)
    table_exists = cursor.fetchone()[0]
    
    if table_exists > 0:
        print(f"\n✅ Tabela WEATHER_RAW já existe no banco!")
    else:
        print(f"\n❌ Tabela WEATHER_RAW NÃO existe no banco")
        print("   Você pode criá-la com: python create_table.py")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"\n❌ ERRO! Banco NÃO está acessível")
    print(f"\n   Tipo de erro: {type(e).__name__}")
    print(f"   Detalhes: {str(e)}")
    print("\n💡 Verifique:")
    print("   1. Se o Oracle está rodando: tnsping XEPDB1")
    print("   2. Se as credenciais estão corretas")
    print("   3. Se o firewall não está bloqueando a porta 1521")

print("\n" + "=" * 60)
