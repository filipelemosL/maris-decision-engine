class Weather:

    def __init__(
        self,
        timestamp,
        wind_speed,
        wind_direction,
        wave_height,
        pressure,
        sea_temp,
        current_speed
    ):
        self.timestamp = timestamp
        self.wind_speed = wind_speed
        self.wind_direction = wind_direction
        self.wave_height = wave_height
        self.pressure = pressure
        self.sea_temp = sea_temp
        self.current_speed = current_speed