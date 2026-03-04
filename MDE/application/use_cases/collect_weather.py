class CollectWeatherUseCase:

    def __init__(self, provider, repository):
        self.provider = provider
        self.repository = repository

    def execute(self, location_id: int, latitude: float, longitude: float):

        weather = self.provider.fetch(latitude, longitude)
        self.repository.save(location_id, weather)