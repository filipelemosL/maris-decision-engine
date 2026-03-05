import oracledb

from infraestructure.external.open_meteo_provider import OpenMeteoProvider
from infraestructure.database.oracle_weather_repository import OracleWeatherRepository
from application.use_cases.collect_weather import CollectWeatherUseCase


def main():

    connection = oracledb.connect(
        user="s",
        password="!",
        dsn="localhost:1521/XEPDB1"
    )

    provider = OpenMeteoProvider()
    repository = OracleWeatherRepository(connection)

    use_case = CollectWeatherUseCase(provider, repository)

    result = use_case.execute(
        location_id=1,
        lat=-12.345678,
        lon=-38.456789
    )

    print("Wind:", result.wind_speed)


if __name__ == "__main__":
    main()