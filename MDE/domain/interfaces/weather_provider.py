from abc import ABC, abstractmethod


class WeatherProvider(ABC):

    @abstractmethod
    def fetch(self, latitude: float, longitude: float):
        pass