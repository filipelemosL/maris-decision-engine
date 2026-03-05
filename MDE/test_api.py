import requests
import json
from datetime import datetime

print("=" * 70)
print("Testando API Open-Meteo")
print("=" * 70)

# Coordenadas de teste (Rio de Janeiro: -12.345678, -38.456789)
LAT = -12.345678
LON = -38.456789

URL = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": LAT,
    "longitude": LON,
    "current_weather": True,
    "hourly": "pressure_msl",
    "timezone": "auto"
}

try:
    print(f"\n🌐 Fazendo requisição para Open-Meteo API...")
    print(f"   URL: {URL}")
    print(f"   Coordenadas: LAT={LAT}, LON={LON}")
    print(f"   Parâmetros: {json.dumps(params, indent=2)}")
    
    response = requests.get(URL, params=params, timeout=10)
    
    print(f"\n📊 Status da resposta: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCESSO! API respondeu")
        
        data = response.json()
        
        # Dados gerais
        print(f"\n📍 Localização:")
        print(f"   Latitude: {data.get('latitude')}")
        print(f"   Longitude: {data.get('longitude')}")
        print(f"   Elevation: {data.get('elevation')}")
        print(f"   Timezone: {data.get('timezone')}")
        
        # Dados de clima atual
        current = data.get("current_weather", {})
        print(f"\n⛅ Clima Atual (Current Weather):")
        print(f"   Temperatura: {current.get('temperature')} °C")
        print(f"   Velocidade do vento: {current.get('windspeed')} km/h")
        print(f"   Direção do vento: {current.get('winddirection')} °")
        print(f"   Code (WMO): {current.get('weathercode')}")
        print(f"   Timestamp: {current.get('time')}")
        
        # Dados horários de pressão
        hourly = data.get("hourly", {})
        if hourly.get("pressure_msl"):
            pressures = hourly["pressure_msl"]
            print(f"\n📉 Dados Horários de Pressão:")
            print(f"   Total de registros: {len(pressures)}")
            print(f"   Primeiros 3 registros: {pressures[:3]}")
            print(f"   Última medida: {pressures[-1]}")
        
        print(f"\n✅ API está funcionando corretamente!")
        print(f"\n📄 JSON completo:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
    else:
        print(f"❌ Erro! Status: {response.status_code}")
        print(f"   Resposta: {response.text}")

except requests.exceptions.Timeout:
    print(f"\n❌ ERRO: Timeout na requisição (>10 segundos)")
    print("   Verifique sua conexão com a internet")

except requests.exceptions.ConnectionError:
    print(f"\n❌ ERRO: Não foi possível conectar à API")
    print("   Verifique sua conexão com a internet")

except Exception as e:
    print(f"\n❌ ERRO: {type(e).__name__}")
    print(f"   Detalhes: {str(e)}")

print("\n" + "=" * 70)
