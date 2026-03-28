# 🗄️ Criar Banco de Dados Compatível com MDE

## 📑 Índice

1. [Instalação do Oracle](#instalação-do-oracle)
2. [Criar Banco de Dados](#criar-banco-de-dados)
3. [Scripts SQL das Tabelas](#scripts-sql-das-tabelas)
4. [Configurar Credenciais](#configurar-credenciais)
5. [Conectar via SQL*Plus](#conectar-via-sqlplus)
6. [Conectar via Python](#conectar-via-python)
7. [Configurar a Aplicação](#configurar-a-aplicação)
8. [Testar Conexão](#testar-conexão)

---

## 🔧 Instalação do Oracle

### Opção 1: Oracle XE (Express Edition) - Gratuito ⭐ Recomendado

**Oracle XE** é a versão gratuita e ideal para desenvolvimento.

#### Windows

1. Baixe em: https://www.oracle.com/database/technologies/xe-downloads.html
2. Escolha: **Oracle Database XE 21c** (Windows)
3. Faça download e execute o instalador
4. Na instalação:
   - **Path**: Deixe padrão (C:\oracleXE)
   - **SID**: Deixe padrão (**XEPDB1**)
   - **Porta**: Deixe padrão (**1521**)
   - **Senha do admin**: Escolha uma senha forte (ex: `MeuBanco2024!`)
5. Aguarde completar (leva 10-30 minutos)
6. Reinicie o computador

#### Linux (Ubuntu/Debian)

```bash
# Baixe do site Oracle
# Ou use Docker:

docker run -d \
  -p 1521:1521 \
  -e ORACLE_PWD=MeuBanco2024! \
  gvenzl/oracle-xe:21-full
```

#### Mac

1. Baixe em: https://www.oracle.com/database/technologies/xe-downloads.html
2. Instale normalmente
3. Ou use Docker (veja Linux acima)

---

### Opção 2: Oracle Database (Edição Completa)

Se quiser usar a edição completa:
- https://www.oracle.com/database/technologies/oracle-database-software-downloads.html
- Requer mais espaço em disco
- Processo de instalação mais complexo

**Para começar, recomendo usar XE!**

---

## 📊 Criar Banco de Dados

### Verificar se Oracle Está Rodando

#### Windows
```powershell
# Verificar serviço
Get-Service | Where-Object {$_.Name -like "*Oracle*"}

# Se não estiver rodando:
Start-Service OracleServiceXEPDB1

# Aguarde 30 segundos
```

#### Linux
```bash
# Verificar
systemctl status oracle-xe

# Se não estiver:
sudo systemctl start oracle-xe
```

---

### Conectar como Admin

#### Windows - SQL*Plus
```powershell
cd "C:\oracleXE\21\sqlplus"

# Conectar como admin
sqlplus sys as sysdba
# Digite a senha que escolheu na instalação
```

#### Linux - SQL*Plus
```bash
sqlplus sys as sysdba
# Digite a senha
```

#### Windows - SQL*Developer (Interface Gráfica)
- Abra: Start Menu → Oracle Database XE → SQL Developer
- Crie nova conexão com:
  - Name: `Local`
  - Username: `sys`
  - Password: `sua_senha_do_admin`
  - Role: `SYSDBA`
  - Hostname: `localhost`
  - Port: `1521`
  - Service Name: `XEPDB1`

---

## � Configurar Credenciais

### Criar Usuário Específico (Recomendado)

Por segurança, crie um usuário específico para a aplicação (em vez de usar `sys` ou `system`):

**SQL (execute como SYSDBA):**

```sql
-- Criar usuário
CREATE USER seu_usuario IDENTIFIED BY sua_senha_segura;

-- Dar permissões
GRANT CREATE SESSION TO seu_usuario;
GRANT CREATE TABLE TO seu_usuario;
GRANT CREATE INDEX TO seu_usuario;
GRANT UNLIMITED TABLESPACE TO seu_usuario;

COMMIT;
```

**Exemplo prático:**

```sql
-- Criar usuário 'weather_app' com senha 'AppSenha123!'
CREATE USER weather_app IDENTIFIED BY AppSenha123!;

GRANT CREATE SESSION TO weather_app;
GRANT CREATE TABLE TO weather_app;
GRANT CREATE INDEX TO weather_app;
GRANT UNLIMITED TABLESPACE TO weather_app;

COMMIT;
```

> **Importante**: Escolha uma senha forte! Use combinação de letras, números e caracteres especiais.

---

### Suas Credenciais

Después de criar o usuário, você terá:

```
Usuário: seu_usuario        (ex: weather_app)
Senha: sua_senha_segura     (ex: AppSenha123!)
Host: localhost
Porta: 1521
Database/SID: XEPDB1
```

**Formato DSN:**
```
localhost:1521/XEPDB1
```

**Connection String:**
```
seu_usuario/sua_senha_segura@localhost:1521/XEPDB1
```

---

## 🗃️ Scripts SQL das Tabelas

### 1️⃣ Criar Tabela WEATHER_RAW

**O que é:** Armazena dados brutos de sensores (vento, onda, pressão, etc)

```sql
-- Executar como seu_usuario
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
);

-- Criar índices para melhorar performance
CREATE INDEX IDX_WEATHER_RAW_LOCATION_DATE 
ON WEATHER_RAW(LOCATION_ID, DATA_TIMESTAMP);

COMMIT;
```

---

### 2️⃣ Criar Tabela WEATHER_PROCESSED

**O que é:** Armazena dados processados com inteligência (scores, status, tendências)

```sql
-- Executar como seu_usuario
CREATE TABLE WEATHER_PROCESSED (
    ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    LOCATION_ID NUMBER NOT NULL,
    DATA_TIMESTAMP TIMESTAMP NOT NULL,
    IEA_SCORE NUMBER,
    OPERATIONAL_STATUS VARCHAR2(50),
    INTERRUPTION_PROBABILITY NUMBER,
    TREND_INDICATOR VARCHAR2(50),
    CREATED_AT TIMESTAMP DEFAULT SYSDATE
);

-- Criar índice
CREATE INDEX IDX_WEATHER_PROCESSED_LOCATION_DATE 
ON WEATHER_PROCESSED(LOCATION_ID, DATA_TIMESTAMP);

COMMIT;
```

---

### 3️⃣ Criar Tabela LOCATIONS

**O que é:** Armazena informações das plataformas/embarcações

```sql
-- Executar como seu_usuario
CREATE TABLE LOCATIONS (
    ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    NAME VARCHAR2(100) NOT NULL,
    LATITUDE NUMBER NOT NULL,
    LONGITUDE NUMBER NOT NULL,
    PLATFORM_TYPE VARCHAR2(50),
    CREATED_AT TIMESTAMP DEFAULT SYSDATE
);

COMMIT;
```

---

### 4️⃣ Criar Tabela OPERATION_LIMITS

**O que é:** Define limites operacionais por tipo de operação

```sql
-- Executar como seu_usuario
CREATE TABLE OPERATION_LIMITS (
    ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    OPERATION_TYPE VARCHAR2(100) NOT NULL,
    MAX_WIND NUMBER,
    MAX_WAVE NUMBER,
    MAX_CURRENT NUMBER,
    CREATED_AT TIMESTAMP DEFAULT SYSDATE
);

COMMIT;
```

---

### 5️⃣ Inserir Dados Iniciais - LOCATIONS

**Exemplo:** Adicione suas plataformas/embarcações

```sql
-- Executar como seu_usuario
INSERT INTO LOCATIONS (NAME, LATITUDE, LONGITUDE, PLATFORM_TYPE)
VALUES ('Plataforma 1', -11.0, -37.0, 'FPSO');

INSERT INTO LOCATIONS (NAME, LATITUDE, LONGITUDE, PLATFORM_TYPE)
VALUES ('Plataforma 2', -10.5, -36.8, 'TLP');

INSERT INTO LOCATIONS (NAME, LATITUDE, LONGITUDE, PLATFORM_TYPE)
VALUES ('Embarcação 1', -11.5, -37.5, 'NAVIO');

COMMIT;

-- Verificar
SELECT * FROM LOCATIONS;
```

---

### 6️⃣ Inserir Dados Iniciais - OPERATION_LIMITS

**Exemplo:** Configure limites por tipo de operação

```sql
-- Executar como seu_usuario
INSERT INTO OPERATION_LIMITS (OPERATION_TYPE, MAX_WIND, MAX_WAVE, MAX_CURRENT)
VALUES ('HELICÓPTERO', 45, 3.5, 1.5);

INSERT INTO OPERATION_LIMITS (OPERATION_TYPE, MAX_WIND, MAX_WAVE, MAX_CURRENT)
VALUES ('EMBARCAÇÃO_PEQUENA', 55, 4.5, 2.0);

INSERT INTO OPERATION_LIMITS (OPERATION_TYPE, MAX_WIND, MAX_WAVE, MAX_CURRENT)
VALUES ('EMBARCAÇÃO_GRANDE', 60, 5.0, 2.5);

INSERT INTO OPERATION_LIMITS (OPERATION_TYPE, MAX_WIND, MAX_WAVE, MAX_CURRENT)
VALUES ('MERGULHO', 30, 2.0, 1.0);

COMMIT;

-- Verificar
SELECT * FROM OPERATION_LIMITS;
```

---

## 7️⃣ Script Completo (Tudo de Uma Vez)

**Salve como `setup.sql` e execute:**

```sql
-- ====================================================================
-- SCRIPT COMPLETO: Criar todas as tabelas e dados
-- Executar como: seu_usuario
-- ====================================================================

-- 1. WEATHER_RAW
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
);
CREATE INDEX IDX_WEATHER_RAW_LOCATION_DATE 
ON WEATHER_RAW(LOCATION_ID, DATA_TIMESTAMP);

-- 2. WEATHER_PROCESSED
CREATE TABLE WEATHER_PROCESSED (
    ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    LOCATION_ID NUMBER NOT NULL,
    DATA_TIMESTAMP TIMESTAMP NOT NULL,
    IEA_SCORE NUMBER,
    OPERATIONAL_STATUS VARCHAR2(50),
    INTERRUPTION_PROBABILITY NUMBER,
    TREND_INDICATOR VARCHAR2(50),
    CREATED_AT TIMESTAMP DEFAULT SYSDATE
);
CREATE INDEX IDX_WEATHER_PROCESSED_LOCATION_DATE 
ON WEATHER_PROCESSED(LOCATION_ID, DATA_TIMESTAMP);

-- 3. LOCATIONS
CREATE TABLE LOCATIONS (
    ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    NAME VARCHAR2(100) NOT NULL,
    LATITUDE NUMBER NOT NULL,
    LONGITUDE NUMBER NOT NULL,
    PLATFORM_TYPE VARCHAR2(50),
    CREATED_AT TIMESTAMP DEFAULT SYSDATE
);

-- 4. OPERATION_LIMITS
CREATE TABLE OPERATION_LIMITS (
    ID NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    OPERATION_TYPE VARCHAR2(100) NOT NULL,
    MAX_WIND NUMBER,
    MAX_WAVE NUMBER,
    MAX_CURRENT NUMBER,
    CREATED_AT TIMESTAMP DEFAULT SYSDATE
);

-- 5. Inserir dados de exemplo em LOCATIONS
INSERT INTO LOCATIONS (NAME, LATITUDE, LONGITUDE, PLATFORM_TYPE)
VALUES ('Plataforma 1', -11.0, -37.0, 'FPSO');
INSERT INTO LOCATIONS (NAME, LATITUDE, LONGITUDE, PLATFORM_TYPE)
VALUES ('Plataforma 2', -10.5, -36.8, 'TLP');

-- 6. Inserir dados de exemplo em OPERATION_LIMITS
INSERT INTO OPERATION_LIMITS (OPERATION_TYPE, MAX_WIND, MAX_WAVE, MAX_CURRENT)
VALUES ('HELICÓPTERO', 45, 3.5, 1.5);
INSERT INTO OPERATION_LIMITS (OPERATION_TYPE, MAX_WIND, MAX_WAVE, MAX_CURRENT)
VALUES ('EMBARCAÇÃO_PEQUENA', 55, 4.5, 2.0);
INSERT INTO OPERATION_LIMITS (OPERATION_TYPE, MAX_WIND, MAX_WAVE, MAX_CURRENT)
VALUES ('EMBARCAÇÃO_GRANDE', 60, 5.0, 2.5);

COMMIT;
```

---

## 8️⃣ Verificar Estrutura Criada

```sql
-- Ver todas as tabelas do seu usuário
SELECT TABLE_NAME FROM USER_TABLES 
WHERE TABLE_NAME IN ('WEATHER_RAW', 'WEATHER_PROCESSED', 'LOCATIONS', 'OPERATION_LIMITS');

-- Ver estrutura de uma tabela
DESC WEATHER_RAW;

-- Contar registros
SELECT COUNT(*) as total_locations FROM LOCATIONS;
SELECT COUNT(*) as total_limits FROM OPERATION_LIMITS;

-- Ver dados
SELECT * FROM LOCATIONS;
SELECT * FROM OPERATION_LIMITS;
```
---

## 🔗 Conectar via SQL*Plus

### Windows

```powershell
# 1. Verificar Oracle está rodando
Get-Service | Where-Object {$_.Name -like "*Oracle*"}

# 2. Conectar como seu usuário
sqlplus seu_usuario/sua_senha@localhost:1521/XEPDB1

# 3. Executar script
sqlplus seu_usuario/sua_senha@localhost:1521/XEPDB1 < setup.sql

# 4. Interativo
sqlplus
# SQL> seu_usuario
# SQL> sua_senha
# SQL> @C:\caminho\para\setup.sql
```

### Linux/Mac

```bash
# 1. Conectar como seu usuário
sqlplus seu_usuario/sua_senha@localhost:1521/XEPDB1

# 2. Executar script
sqlplus seu_usuario/sua_senha@localhost:1521/XEPDB1 < setup.sql
```

### Comandos Úteis

```sql
-- Ver usuário atual
SHOW USER;

-- Listar suas tabelas
SELECT TABLE_NAME FROM USER_TABLES;

-- Sair
EXIT;
```

---

## 🐍 Conectar via Python

### Instalação

```bash
pip install oracledb
```

### Teste de Conexão

```python
import oracledb

try:
    connection = oracledb.connect(
        user="seu_usuario",
        password="sua_senha",
        dsn="localhost:1521/XEPDB1"
    )
    
    print("✅ Conectado com sucesso!")
    
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM LOCATIONS")
    
    for row in cursor.fetchall():
        print(row)
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")
```

---

## 🔌 Configurar a Aplicação

### 1. Alterar Credenciais em `api.py`

**Arquivo:** `MDE/api.py` (linhas ~15-21)

Encontre:
```python
DB_CONFIG = {
    "user": "system",
    "password": "K1lstrik098!",
    "dsn": "localhost:1521/XEPDB1"
}
```

Altere para suas credenciais:
```python
DB_CONFIG = {
    "user": "seu_usuario",      # ← Seu usuário (ex: weather_app)
    "password": "sua_senha",    # ← Sua senha
    "dsn": "localhost:1521/XEPDB1"  # ← Altere se usou SID diferente
}
```

---

### 2. Alterar Credenciais em `main.py`

**Arquivo:** `MDE/main.py` (funções de coleta)

Encontre:
```python
connection = oracledb.connect(
    user="system",
    password="K1lstrik098!",
    dsn="localhost:1521/XEPDB1"
)
```

Altere para:
```python
connection = oracledb.connect(
    user="seu_usuario",      # ← Seu usuário
    password="sua_senha",    # ← Sua senha  
    dsn="localhost:1521/XEPDB1"  # ← Se necessário
)
```

---

### 3. Alterar em Outros Arquivos

Procure por arquivos que fazem conexão:

```bash
# Procurar por "oracledb.connect" em todo o projeto
grep -r "oracledb.connect" MDE/

# No PowerShell:
Get-ChildItem -Recurse -Filter "*.py" | Select-String "oracledb.connect"
```

E altere todas as ocorrências com suas credenciais.

---

## ✅ Testar Conexão

### Teste via Python

**Salve como `test_connection.py`:**

```python
import oracledb

print("\n" + "="*60)
print("TESTE DE CONEXÃO COM BANCO")
print("="*60 + "\n")

# ALTERE AQUI COM SUAS CREDENCIAIS
seu_usuario = "seu_usuario"      # ← Mude para seu usuário
sua_senha = "sua_senha"          # ← Mude para sua senha
host = "localhost"
porta = 1521
database = "XEPDB1"

try:
    dsn = f"{host}:{porta}/{database}"
    print(f"Conectando como: {seu_usuario}@{dsn}")
    
    connection = oracledb.connect(
        user=seu_usuario,
        password=sua_senha,
        dsn=dsn
    )
    
    print("✅ CONEXÃO BEM-SUCEDIDA!\n")
    
    cursor = connection.cursor()
    
    # Teste 1: Ver usuário
    cursor.execute("SELECT USER FROM DUAL")
    user = cursor.fetchone()[0]
    print(f"Usuário conectado: {user}")
    
    # Teste 2: Contar tabelas
    cursor.execute("""
        SELECT COUNT(*) FROM USER_TABLES 
        WHERE TABLE_NAME IN ('WEATHER_RAW', 'WEATHER_PROCESSED', 'LOCATIONS', 'OPERATION_LIMITS')
    """)
    count = cursor.fetchone()[0]
    print(f"Tabelas criadas: {count}/4")
    
    # Teste 3: Contar registros
    if count == 4:
        cursor.execute("SELECT COUNT(*) FROM LOCATIONS")
        loc_count = cursor.fetchone()[0]
        print(f"Registros em LOCATIONS: {loc_count}")
        
        cursor.execute("SELECT * FROM LOCATIONS")
        print("\nPrimeira localização:")
        row = cursor.fetchone()
        if row:
            print(f"  ID: {row[0]}, Nome: {row[1]}")
    
    cursor.close()
    connection.close()
    
    print("\n✅ TODOS OS TESTES PASSARAM!")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"❌ ERRO DE CONEXÃO:")
    print(f"  {e}\n")
    print("Verifique:")
    print("  1. Oracle está rodando?")
    print("  2. SID é XEPDB1?")
    print("  3. Usuário e senha estão corretos?")
    print("  4. Tabelas foram criadas?")
    print("="*60 + "\n")
```

**Execute:**

```bash
python test_connection.py
```

---

### Teste via SQL*Plus

```sql
-- Conectar como seu usuário
sqlplus seu_usuario/sua_senha@localhost:1521/XEPDB1

-- Listar tabelas
SELECT TABLE_NAME FROM USER_TABLES;

-- Ver dados
SELECT * FROM LOCATIONS;
SELECT * FROM OPERATION_LIMITS;

-- Sair
EXIT;
```

---

## 📋 Checklist Final

- [ ] Oracle instalado e rodando
- [ ] Usuário criado (ex: `weather_app`)
- [ ] Tabelas criadas com `setup.sql`
- [ ] Dados de exemplo inseridos
- [ ] Conexão testada com Python
- [ ] Credenciais atualizadas em `api.py`
- [ ] Credenciais atualizadas em `main.py`
- [ ] Aplicação consegue conectar ao banco

---

## 🔐 Dicas de Segurança

✅ **Faça:**
- Use senha forte (mín. 12 caracteres)
- Não compartilhe credenciais
- Use variáveis de ambiente (veja abaixo)

❌ **Não faça:**
- Não deixe password em código público
- Não use `system` em produção
- Não use senhas simples

### Usar Variáveis de Ambiente

**Windows (PowerShell):**

```powershell
$env:DB_USER = "seu_usuario"
$env:DB_PASSWORD = "sua_senha"
$env:DB_HOST = "localhost"
$env:DB_PORT = "1521"
$env:DB_SID = "XEPDB1"
```

**Python:**

```python
import os
import oracledb

connection = oracledb.connect(
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dsn=f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_SID')}"
)
```

---

**✅ Pronto!** Seu banco está configurado e a aplicação pode conectar!
