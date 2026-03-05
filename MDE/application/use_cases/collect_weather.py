class CollectWeatherUseCase:

    def __init__(self, provider, repository):
        self.provider = provider
        self.repository = repository

    def execute(self, location_id, lat, lon):

        weather = self.provider.get_weather(lat, lon)

        self.repository.save(location_id, weather)

        return weather