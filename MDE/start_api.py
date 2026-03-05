"""
SCRIPT PARA INICIAR API EM MODO PRODUÇÃO
Execute isto para manter a API rodando
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("=" * 80)
    print("🚀 INICIALIZADOR - Maris Decision Engine API")
    print("=" * 80)
    
    # Caminho do projeto
    project_path = Path(__file__).parent
    
    print("\n📋 Verificações iniciais...\n")
    
    # 1. Verificar Python
    print("✓ Python:", sys.version.split()[0])
    
    # 2. Verificar venv
    venv_path = project_path / ".venv"
    if venv_path.exists():
        print("✓ Virtual Environment encontrado")
    else:
        print("✗ Virtual Environment não encontrado!")
        print("  Execute: python -m venv .venv")
        return
    
    # 3. Verificar se está ativado
    if sys.prefix == str(venv_path):
        print("✓ Virtual Environment está ativado")
    else:
        print("⚠️  Virtual Environment não está ativado")
        print("  Execute (PowerShell): .venv\\Scripts\\Activate.ps1")
        return
    
    # 4. Verificar dependências
    print("\n📦 Verificando dependências...\n")
    
    required_packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'oracledb': 'oracledb',
        'requests': 'requests',
        'schedule': 'schedule'
    }
    
    missing = []
    for module, name in required_packages.items():
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name}")
            missing.append(name)
    
    if missing:
        print(f"\n❌ Dependências faltando: {', '.join(missing)}")
        print("Execute: pip install " + " ".join(missing))
        return
    
    # 5. Testar conexão com banco
    print("\n🗄️  Testando banco de dados...\n")
    try:
        import oracledb
        conn = oracledb.connect(
            user="system",
            password="K1lstrik098!",
            dsn="localhost:1521/XEPDB1"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT SYSDATE FROM DUAL")
        db_time = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"✓ Banco Oracle conectado")
        print(f"  Horário: {db_time}")
    except Exception as e:
        print(f"✗ Erro ao conectar banco: {str(e)}")
        return
    
    # 6. Iniciar API
    print("\n" + "=" * 80)
    print("🚀 INICIANDO API PRODUCTION")
    print("=" * 80)
    print("\n🌐 Endpoints disponíveis:")
    print("   • GET  /api/health")
    print("   • GET  /api/all-locations-status")
    print("   • GET  /api/operational-status/<id>")
    print("   • GET  /api/decision-history/<id>?hours=24")
    print("   • GET  /api/weather-raw/<id>?hours=24")
    print("   • POST /api/process-data")
    print("\n📡 Server: http://0.0.0.0:5000")
    print("💻 Local:  http://localhost:5000")
    print("\n🔐 CORS habilitado para:")
    print("   • localhost:3000 (frontend local)")
    print("   • *.vercel.app (Vercel)")
    print("\n⏹️  Para parar: CTRL+C")
    print("\n" + "=" * 80 + "\n")
    
    # Iniciar API
    api_file = project_path / "api_producao.py"
    
    try:
        subprocess.run(
            [sys.executable, str(api_file)],
            cwd=str(project_path)
        )
    except KeyboardInterrupt:
        print("\n\n⛔ API parada pelo usuário")
        print("=" * 80)
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    main()
