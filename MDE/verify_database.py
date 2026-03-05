import oracledb

print("=" * 80)
print("Verificando estrutura do banco de dados")
print("=" * 80)

try:
    connection = oracledb.connect(
        user="system",
        password="K1lstrik098!",
        dsn="localhost:1521/XEPDB1"
    )
    
    cursor = connection.cursor()
    
    # Listar todas as tabelas
    cursor.execute("""
        SELECT TABLE_NAME 
        FROM USER_TABLES 
        ORDER BY TABLE_NAME
    """)
    
    tables = cursor.fetchall()
    
    print("\n📊 Tabelas encontradas:")
    print("-" * 80)
    
    for table in tables:
        table_name = table[0]
        
        # Contar registros
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  ✅ {table_name:<25} ({count:,} registros)")
        except:
            print(f"  ⚠️  {table_name:<25} (erro ao contar)")
    
    # Verificar views
    cursor.execute("""
        SELECT VIEW_NAME 
        FROM USER_VIEWS 
        ORDER BY VIEW_NAME
    """)
    
    views = cursor.fetchall()
    
    if views:
        print("\n👁️  Views encontradas:")
        print("-" * 80)
        for view in views:
            print(f"  ✅ {view[0]}")
    
    cursor.close()
    connection.close()
    
    print("\n" + "=" * 80)
    print("✅ Banco verificado com sucesso!")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ ERRO: {type(e).__name__}")
    print(f"   {str(e)}")
