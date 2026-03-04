from abc import ABC, abstractmethod
from domain.entities.weather import Weather


class WeatherRepository(ABC):

    @abstractmethod
    def save(self, location_id: int, weather: Weather):
        pass