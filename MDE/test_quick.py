#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
teste rápido de todos os endpoints da API
"""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:5000"

def print_header(text):
    print("\n" + "="*80)
    print(f"✅ {text}")
    print("="*80)

def print_response(endpoint, method="GET", data=None):
    try:
        if method == "GET":
            response = requests.get(f"{API_URL}{endpoint}", timeout=5)
        else:
            response = requests.post(f"{API_URL}{endpoint}", json=data, timeout=5)
        
        print(f"\n📍 Endpoint: {endpoint}")
        print(f"📊 Status: {response.status_code}")
        print(f"📦 Response:")
        
        try:
            json_data = response.json()
            print(json.dumps(json_data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
            
        return response.status_code < 400
    
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERRO: Não consegui conectar em {API_URL}")
        print("➜ A API está rodando? Tente: python api_producao.py")
        return False
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        return False

def main():
    print("\n" + "#"*80)
    print("# 🚀 TESTE RÁPIDO DA API - Maris Decision Engine")
    print("#"*80)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 URL: {API_URL}")

    results = {}

    # Teste 1: Health Check
    print_header("1️⃣ TESTE: Health Check (Status da API)")
    results['health'] = print_response("/api/health")

    # Teste 2: Todas as localizações
    print_header("2️⃣ TESTE: Todas as Localizações")
    results['locations'] = print_response("/api/all-locations-status")

    # Teste 3: Status operacional de uma localização
    print_header("3️⃣ TESTE: Status Operacional (Localização 1)")
    results['operational'] = print_response("/api/operational-status/1")

    # Teste 4: Histórico de decisões
    print_header("4️⃣ TESTE: Histórico de Decisões (Localização 1)")
    results['history'] = print_response("/api/decision-history/1")

    # Teste 5: Dados meteorológicos brutos
    print_header("5️⃣ TESTE: Dados Meteorológicos (Localização 1)")
    results['weather'] = print_response("/api/weather-raw/1")

    # Teste 6: Limites operacionais
    print_header("6️⃣ TESTE: Limites Operacionais")
    results['limits'] = print_response("/api/operation-limits")

    # Teste 7: Processar dados (POST)
    print_header("7️⃣ TESTE: Processar Dados Meteorológicos (POST)")
    results['process'] = print_response("/api/process-data", method="POST")

    # Resumo
    print_header("📊 RESUMO DOS TESTES")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n✅ Testes passados: {passed}/{total}")
    
    for endpoint, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"  {status} - {endpoint}")

    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM! API está funcionando!")
        print("\n📝 Próximos passos:")
        print("   1. Escolher opção de como manter API rodando (ver QUICK_START.txt)")
        print("   2. Expor API para internet (ngrok ou cloud)")
        print("   3. Configurar frontend Vercel com NEXT_PUBLIC_API_URL")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main()
