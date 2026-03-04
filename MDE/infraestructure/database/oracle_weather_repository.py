import oracledb
from domain.interfaces.weather_repository import WeatherRepository
from domain.entities.weather import Weather


class OracleWeatherRepository(WeatherRepository):

    def __init__(self, connection):
        self.connection = connection

    def save(self, location_id: int, weather: Weather):

        cursor = self.connection.cursor()

        sql = """
            INSERT INTO WEATHER_RAW (
                LOCATION_ID,
                DATA_TIMESTAMP,
                WIND_SPEED,
                WIND_DIRECTION,
                WAVE_HEIGHT,
                PRESSURE,
                SEA_TEMP,
                CURRENT_SPEED
            ) VALUES (
                :1, :2, :3, :4, :5, :6, :7, :8
            )
        """

        cursor.execute(sql, (
            location_id,
            weather.timestamp,
            weather.wind_speed,
            weather.wind_direction,
            weather.wave_height,
            weather.pressure,
            weather.sea_temp,
            weather.current_speed
        ))

        self.connection.commit()