"""
ENGINE DE PROCESSAMENTO DE DADOS
Converte dados brutos em inteligência operacional
"""

import oracledb
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class WeatherProcessingEngine:
    """Engine que processa dados de WEATHER_RAW e gera WEATHER_PROCESSED"""
    
    def __init__(self):
        self.connection = None
        
    def connect(self):
        """Conectar ao banco de dados"""
        self.connection = oracledb.connect(
            user="system",
            password="K1lstrik098!",
            dsn="localhost:1521/XEPDB1"
        )
    
    def disconnect(self):
        """Desconectar do banco"""
        if self.connection:
            self.connection.close()
    
    def calculate_iea_score(self, wind_speed: float, wave_height: float, 
                           current_speed: float, pressure: float) -> float:
        """
        Calcula Índice de Risco Ambiental (IEA) de 0 a 100
        
        IEA = (Vento_norm * 0.4) + (Onda_norm * 0.3) + (Corrente_norm * 0.2) + (Pressão_norm * 0.1)
        
        Normalização: valores entre 0 (bom) e 100 (ruim)
        """
        
        # Normalizar vento (0-100) - máximo operacional ~40 km/h
        wind_norm = min((wind_speed / 40) * 100, 100) if wind_speed else 0
        
        # Normalizar onda (0-100) - máximo operacional ~3m
        wave_norm = min((wave_height / 3) * 100, 100) if wave_height else 0
        
        # Normalizar corrente (0-100) - máximo operacional ~3 m/s
        current_norm = min((current_speed / 3) * 100, 100) if current_speed else 0
        
        # Pressão normal = ~1013 hPa; anomalias aumentam risco
        pressure_norm = 0
        if pressure:
            # Desvio de 1013 hPa
            deviation = abs(pressure - 1013)
            pressure_norm = min((deviation / 50) * 100, 100)
        
        # Calcular IEA
        iea = (wind_norm * 0.4) + (wave_norm * 0.3) + (current_norm * 0.2) + (pressure_norm * 0.1)
        
        return round(iea, 2)
    
    def get_operational_status(self, iea_score: float) -> str:
        """Classificar status operacional baseado no IEA"""
        if iea_score < 20:
            return "EXCELENTE"
        elif iea_score < 40:
            return "BOM"
        elif iea_score < 60:
            return "MODERADO"
        elif iea_score < 80:
            return "RESTRITO"
        else:
            return "PROIBIDO"
    
    def calculate_interruption_probability(self, iea_score: float) -> float:
        """
        Probabilidade de interrupção de operações (% de 0 a 100)
        Baseado no IEA score
        """
        # Aproximação: probabilidade aumenta exponencialmente com IEA
        prob = min((iea_score / 100) * 100, 100)
        return round(prob, 2)
    
    def get_trend_indicator(self, location_id: int, hours_back: int = 24) -> str:
        """
        Indicador de tendência: melhorando/piorando/estável
        Compara últimas leituras
        """
        cursor = self.connection.cursor()
        
        # Buscar últimos scores
        cursor.execute(f"""
            SELECT IEA_SCORE, CREATED_AT
            FROM WEATHER_PROCESSED
            WHERE LOCATION_ID = {location_id}
            AND CREATED_AT >= SYSDATE - {hours_back}/24
            ORDER BY CREATED_AT DESC
            FETCH FIRST 2 ROWS ONLY
        """)
        
        rows = cursor.fetchall()
        cursor.close()
        
        if len(rows) < 2:
            return "INSUFICIENTE"
        
        current_score = rows[0][0]
        previous_score = rows[1][0]
        
        if current_score < previous_score - 5:
            return "MELHORANDO"
        elif current_score > previous_score + 5:
            return "PIORANDO"
        else:
            return "ESTAVEL"
    
    def get_best_operation_window(self, location_id: int, hours_ahead: int = 24) -> Dict:
        """
        Encontra a melhor janela para operação nas próximas horas
        """
        cursor = self.connection.cursor()
        
        # Buscar previsão de dados (simulado com WEATHER_RAW)
        cursor.execute(f"""
            SELECT 
                DATA_TIMESTAMP,
                WIND_SPEED,
                WAVE_HEIGHT,
                CURRENT_SPEED,
                PRESSURE
            FROM WEATHER_RAW
            WHERE LOCATION_ID = {location_id}
            AND DATA_TIMESTAMP >= SYSDATE
            AND DATA_TIMESTAMP <= SYSDATE + {hours_ahead}/24
            ORDER BY DATA_TIMESTAMP ASC
            FETCH FIRST 24 ROWS ONLY
        """)
        
        rows = cursor.fetchall()
        cursor.close()
        
        best_window = {
            "timestamp": None,
            "iea_score": 100,
            "duration_hours": 0
        }
        
        for i, row in enumerate(rows):
            iea = self.calculate_iea_score(
                row[1], row[2], row[3], row[4]
            )
            
            if iea < best_window["iea_score"]:
                best_window["timestamp"] = row[0]
                best_window["iea_score"] = iea
        
        return best_window
    
    def process_raw_weather_data(self) -> int:
        """
        Processa todos os dados brutos não processados e insere em WEATHER_PROCESSED
        Retorna número de registros processados
        """
        cursor = self.connection.cursor()
        
        # Buscar dados não processados
        cursor.execute("""
            SELECT wr.ID, wr.LOCATION_ID, wr.DATA_TIMESTAMP, 
                   wr.WIND_SPEED, wr.WAVE_HEIGHT, wr.CURRENT_SPEED, wr.PRESSURE
            FROM WEATHER_RAW wr
            WHERE NOT EXISTS (
                SELECT 1 FROM WEATHER_PROCESSED wp
                WHERE wp.LOCATION_ID = wr.LOCATION_ID
                AND wp.DATA_TIMESTAMP = wr.DATA_TIMESTAMP
            )
            ORDER BY wr.CREATED_AT DESC
            FETCH FIRST 100 ROWS ONLY
        """)
        
        rows = cursor.fetchall()
        processed_count = 0
        
        for row in rows:
            location_id = row[1]
            data_timestamp = row[2]
            wind_speed = row[3]
            wave_height = row[4]
            current_speed = row[5]
            pressure = row[6]
            
            # Calcular métricas
            iea_score = self.calculate_iea_score(
                wind_speed or 0, 
                wave_height or 0,
                current_speed or 0,
                pressure or 1013
            )
            
            operational_status = self.get_operational_status(iea_score)
            interruption_prob = self.calculate_interruption_probability(iea_score)
            trend_indicator = self.get_trend_indicator(location_id)
            
            # Inserir em WEATHER_PROCESSED
            cursor.execute("""
                INSERT INTO WEATHER_PROCESSED 
                (LOCATION_ID, DATA_TIMESTAMP, IEA_SCORE, OPERATIONAL_STATUS, 
                 INTERRUPTION_PROBABILITY, TREND_INDICATOR)
                VALUES (:1, :2, :3, :4, :5, :6)
            """, (location_id, data_timestamp, iea_score, operational_status,
                  interruption_prob, trend_indicator))
            
            processed_count += 1
        
        self.connection.commit()
        cursor.close()
        
        return processed_count


# Script de teste
if __name__ == "__main__":
    print("=" * 80)
    print("Testando Weather Processing Engine")
    print("=" * 80)
    
    engine = WeatherProcessingEngine()
    engine.connect()
    
    # 1. Testar cálculo de IEA
    print("\n1️⃣  Testando cálculos de IEA")
    iea1 = engine.calculate_iea_score(wind_speed=10, wave_height=1.0, 
                                       current_speed=1.0, pressure=1013)
    print(f"   Condições boas: IEA={iea1}, Status={engine.get_operational_status(iea1)}")
    
    iea2 = engine.calculate_iea_score(wind_speed=35, wave_height=2.5, 
                                       current_speed=2.5, pressure=980)
    print(f"   Condições ruins: IEA={iea2}, Status={engine.get_operational_status(iea2)}")
    
    # 2. Testar processamento
    print("\n2️⃣  Processando dados brutos...")
    processed = engine.process_raw_weather_data()
    print(f"   ✅ {processed} registros processados")
    
    # 3. Buscar dados processados
    print("\n3️⃣  Dados processados:")
    cursor = engine.connection.cursor()
    cursor.execute("""
        SELECT LOCATION_ID, DATA_TIMESTAMP, IEA_SCORE, OPERATIONAL_STATUS, 
               INTERRUPTION_PROBABILITY, TREND_INDICATOR
        FROM WEATHER_PROCESSED
        ORDER BY CREATED_AT DESC
        FETCH FIRST 3 ROWS ONLY
    """)
    
    for row in cursor.fetchall():
        print(f"   LOC:{row[0]} | TS:{row[1]} | IEA:{row[2]} | Status:{row[3]} | Prob:{row[4]}% | Trend:{row[5]}")
    
    cursor.close()
    engine.disconnect()
    
    print("\n" + "=" * 80)
    print("✅ Engine funcionando!")
    print("=" * 80)
