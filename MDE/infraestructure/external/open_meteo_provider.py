# infrastructure/external/open_meteo_provider.py

import requests
from datetime import datetime
from domain.entities.weather import Weather
from domain.interfaces.weather_provider import WeatherProvider


class OpenMeteoProvider(WeatherProvider):

    def fetch(self, latitude: float, longitude: float) -> Weather:

        url = "https://marine-api.open-meteo.com/v1/marine"

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "wave_height,sea_surface_temperature",
            "current_weather": True,
            "timezone": "auto"
        }

        response = requests.get(url, params=params)
        data = response.json()

        return Weather(
            timestamp=datetime.utcnow(),
            wind_speed=data["current_weather"]["windspeed"],
            wind_direction=data["current_weather"]["winddirection"],
            wave_height=data["hourly"]["wave_height"][0],
            pressure=data["current_weather"].get("pressure"),
            sea_temp=data["hourly"]["sea_surface_temperature"][0],
            current_speed=None
        )