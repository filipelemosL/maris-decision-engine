# main.py

import oracledb

from infrastructure.external.open_meteo_provider import OpenMeteoProvider
from infrastructure.database.oracle_weather_repository import OracleWeatherRepository
from application.use_cases.collect_weather import CollectWeatherUseCase


def main():

    connection = oracledb.connect(
        user="SEU_USER",
        password="SUA_SENHA",
        dsn="localhost:1521/XEPDB1"
    )

    provider = OpenMeteoProvider()
    repository = OracleWeatherRepository(connection)

    use_case = CollectWeatherUseCase(provider, repository)

    # exemplo fixo
    use_case.execute(
        location_id=1,
        latitude=-12.345678,
        longitude=-38.456789
    )

    print("Coleta realizada com sucesso.")


if __name__ == "__main__":
    main()