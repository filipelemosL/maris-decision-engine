import oracledb
import time
import schedule
from datetime import datetime

from infraestructure.external.open_meteo_provider import OpenMeteoProvider
from infraestructure.database.oracle_weather_repository import OracleWeatherRepository
from application.use_cases.collect_weather import CollectWeatherUseCase


def collect_weather():
    """Função que coleta dados de clima a cada execução"""
    try:
        connection = oracledb.connect(
            user="system",
            password="K1lstrik098!",
            dsn="localhost:1521/XEPDB1"
        )

        provider = OpenMeteoProvider()
        repository = OracleWeatherRepository(connection)

        use_case = CollectWeatherUseCase(provider, repository)

        result = use_case.execute(
            location_id=1,
            lat=-11.0325631,
            lon=-37.0829041
        )

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] ✅ Coleta realizada com sucesso! Vento: {result.wind_speed} km/h")
        
        connection.close()
        
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] ❌ Erro na coleta: {str(e)}")


def main():
    """Função principal que agenda coletas a cada 5 minutos"""
    print("=" * 70)
    print("COLETOR DE DADOS DE CLIMA - Scheduler")
    print("=" * 70)
    print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Coleta agendada a cada: 5 minutos")
    print("=" * 70)
    print()
    
    # Agendar coleta a cada 5 minutos
    schedule.every(5).minutes.do(collect_weather)
    
    # Executar coleta imediatamente na inicialização
    collect_weather()
    
    # Loop infinito para manter o scheduler rodando
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)  # Verifica a cada 1 segundo se há tarefa agendada
    except KeyboardInterrupt:
        print("\n" + "=" * 70)
        print("⛔ Scheduler interrompido pelo usuário")
        print(f"Encerrado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)


if __name__ == "__main__":
    main()