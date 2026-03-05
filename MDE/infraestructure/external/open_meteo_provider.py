import requests
from datetime import datetime
from domain.entities.weather import Weather

class OpenMeteoProvider:

    URL = "https://api.open-meteo.com/v1/forecast"

    def get_weather(self, lat, lon):

        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "hourly": "pressure_msl"
        }

        response = requests.get(self.URL, params=params)
        data = response.json()

        current = data["current_weather"]

        weather = Weather(
            timestamp=datetime.utcnow(),
            wind_speed=current["windspeed"],
            wind_direction=current["winddirection"],
            wave_height=None,
            pressure=None,
            sea_temp=None,
            current_speed=None
        )

        return weather