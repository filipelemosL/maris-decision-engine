# domain/entities/weather.py

from datetime import datetime


class Weather:

    def __init__(
        self,
        timestamp: datetime,
        wind_speed: float,
        wind_direction: float,
        wave_height: float,
        pressure: float,
        sea_temp: float,
        current_speed: float
    ):
        self.timestamp = timestamp
        self.wind_speed = wind_speed
        self.wind_direction = wind_direction
        self.wave_height = wave_height
        self.pressure = pressure
        self.sea_temp = sea_temp
        self.current_speed = current_speed