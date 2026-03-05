# 🚀 MARIS DECISION ENGINE - API Documentation

## Visão Geral

Sistema de Inteligência para Decisão em Operações Marítimas/Offshore.

**Componentes:**
- ✅ Coleta de dados (WEATHER_RAW) - a cada 5 minutos
- ✅ Processamento de inteligência (WEATHER_PROCESSED)
- ✅ API REST com 7 endpoints
- ✅ Índice de Risco Ambiental (IEA) de 0-100
- ✅ Classificação automática de risco operacional

---

## 📊 Dados Disponíveis

### WEATHER_RAW (Dados Brutos)
```
- Wind Speed (km/h)
- Wind Direction (degrees)
- Wave Height (m)
- Current Speed (m/s)
- Pressure (hPa)
- Sea Temperature (°C)
```

### WEATHER_PROCESSED (Dados com Inteligência)
```
- IEA Score (0-100): Índice de Risco Ambiental
- Operational Status: EXCELENTE | BOM | MODERADO | RESTRITO | PROIBIDO
- Interruption Probability (%): Chance de interrupção
- Trend Indicator: MELHORANDO | ESTAVEL | PIORANDO
```

---

## 🔌 Endpoints da API

### 1️⃣ Health Check
```
GET /api/health
```
Verifica se a API está conectada ao banco.

**Resposta:**
```json
{
  "status": "healthy",
  "database_connected": true,
  "database_time": "2026-03-05T00:06:06",
  "api_time": "2026-03-05T00:06:15"
}
```

---

### 2️⃣ Listar Localizações
```
GET /api/locations
```
Retorna todas as plataformas/localizações cadastradas.

**Resposta:**
```json
{
  "status": "success",
  "locations_count": 2,
  "data": [
    {
      "id": 1,
      "name": "Plataforma Alpha",
      "latitude": -12.345678,
      "longitude": -38.456789,
      "platform_type": "Offshore Oil"
    }
  ]
}
```

---

### 3️⃣ Dados de Clima Brutos
```
GET /api/weather/raw/<location_id>?hours=24
```
Retorna dados brutos dos últimos N horas.

**Exemplo:** `GET /api/weather/raw/1?hours=24`

**Resposta:**
```json
{
  "status": "success",
  "location_id": 1,
  "records_count": 15,
  "data": [
    {
      "id": 123,
      "timestamp": "2026-03-05T02:49:37",
      "wind_speed_kmh": 2.7,
      "wind_direction_deg": 23.0,
      "wave_height_m": null,
      "pressure_hpa": null,
      "sea_temp_c": null,
      "current_speed_ms": null
    }
  ]
}
```

---

### 4️⃣ Dados Processados (Inteligência)
```
GET /api/decision/<location_id>
```
Retorna 10 últimos registros processados com IEA, status e tendência.

**Exemplo:** `GET /api/decision/1`

**Resposta:**
```json
{
  "status": "success",
  "location_id": 1,
  "records_count": 10,
  "data": [
    {
      "timestamp": "2026-03-05T02:49:37",
      "iea_score": 2.7,
      "operational_status": "EXCELENTE",
      "interruption_probability_percent": 2.7,
      "trend_indicator": "ESTAVEL"
    }
  ]
}
```

---

### 5️⃣ Status Operacional ATUAL
```
GET /api/operational-status/<location_id>
```
Retorna o status operacional **ATUAL** da localização.

**Exemplo:** `GET /api/operational-status/1`

**Resposta:**
```json
{
  "status": "success",
  "location": {
    "id": 1,
    "name": "Plataforma Alpha",
    "platform_type": "Offshore Oil"
  },
  "current_status": {
    "timestamp": "2026-03-05T02:49:37",
    "iea_score": 2.7,
    "operational_status": "EXCELENTE",
    "interruption_probability_percent": 2.7,
    "trend_indicator": "ESTAVEL",
    "is_operational": true
  }
}
```

---

### 6️⃣ Limites Operacionais
```
GET /api/operation-limits
```
Retorna os limites máximos por tipo de operação.

**Resposta:**
```json
{
  "status": "success",
  "limits_count": 2,
  "data": [
    {
      "operation_type": "Lançamento de ROV",
      "max_wind_kmh": 25.0,
      "max_wave_m": 1.8,
      "max_current_ms": 2.0
    },
    {
      "operation_type": "Helicóptero",
      "max_wind_kmh": 40.0,
      "max_wave_m": 2.5,
      "max_current_ms": 3.0
    }
  ]
}
```

---

### 7️⃣ Processar Dados
```
POST /api/process-weather
```
Processa dados brutos e gera inteligência (executa periodicamente).

**Resposta:**
```json
{
  "status": "success",
  "message": "6 registros processados com sucesso",
  "records_processed": 6
}
```

---

## 🔍 Classificações do IEA Score

| Score | Status | Risco | Operações |
|-------|--------|-------|-----------|
| 0-19 | EXCELENTE | Mínimo | ✅ Todas |
| 20-39 | BOM | Baixo | ✅ Todas |
| 40-59 | MODERADO | Médio | ⚠️ Restritas |
| 60-79 | RESTRITO | Alto | ⛔ Muito Restritas |
| 80-100 | PROIBIDO | Crítico | ❌ Nenhuma |

---

## 🌐 Como Iniciar a API

```bash
# Ativar virtual environment
.venv\Scripts\Activate.ps1

# Iniciar servidor
python api.py

# A API estará disponível em: http://localhost:5000
```

---

## 📱 Exemplos de Uso (JavaScript/Frontend)

### Exemplo 1: Buscar Status Operacional
```javascript
async function getOperationalStatus(locationId) {
  const response = await fetch(`http://localhost:5000/api/operational-status/${locationId}`);
  const data = await response.json();
  
  console.log(`Localização: ${data.location.name}`);
  console.log(`IEA Score: ${data.current_status.iea_score}`);
  console.log(`Status: ${data.current_status.operational_status}`);
  console.log(`Pode Operar: ${data.current_status.is_operational ? 'SIM' : 'NÃO'}`);
}

getOperationalStatus(1);
```

---

### Exemplo 2: Buscar Histórico de Inteligência
```javascript
async function getDecisionHistory(locationId) {
  const response = await fetch(`http://localhost:5000/api/decision/${locationId}`);
  const data = await response.json();
  
  data.data.forEach(record => {
    console.log(`${record.timestamp}: IEA=${record.iea_score} Status=${record.operational_status}`);
  });
}

getDecisionHistory(1);
```

---

### Exemplo 3: Buscar Dados Brutos
```javascript
async function getRawWeather(locationId, hours = 24) {
  const response = await fetch(
    `http://localhost:5000/api/weather/raw/${locationId}?hours=${hours}`
  );
  const data = await response.json();
  
  data.data.forEach(reading => {
    console.log(`Vento: ${reading.wind_speed_kmh} km/h`);
  });
}

getRawWeather(1, 24);
```

---

### Exemplo 4: Desencadear Processamento
```javascript
async function processWeatherData() {
  const response = await fetch('http://localhost:5000/api/process-weather', {
    method: 'POST'
  });
  const data = await response.json();
  
  console.log(`${data.records_processed} registros processados`);
}

processWeatherData();
```

---

## 📊 Fluxo de Dados

```
┌─────────────┐
│  Open-Meteo │  Coleta a cada 5 minutos
│  API        │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  WEATHER_RAW    │  Dados brutos armazenados
│  (6 registros)  │
└────────┬────────┘
         │
         ▼ (POST /api/process-weather)
┌──────────────────┐
│ Weather Engine   │  Calcula IEA, Status, Probabilidade
│ (processing)     │
└─────────┬────────┘
          │
          ▼
┌─────────────────────┐
│ WEATHER_PROCESSED   │  Inteligência gerada
│ (Decision Data)     │
└─────────┬───────────┘
          │
          ▼
┌──────────────────┐
│   API REST       │  7 Endpoints disponíveis
│ (Flask)          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Frontend App   │  Interface para o usuário
│   (Dashboard)    │
└──────────────────┘
```

---

## ✅ Checklist de Implementação

- [x] Coleta de dados brutos (WEATHER_RAW)
- [x] Engine de processamento (IEA, Status, Probabilidade)
- [x] Banco de dados estruturado (6 tabelas)
- [x] API REST com 7 endpoints
- [x] Scripts de teste (cada passo)
- [x] Documentação completa

---

## 🔧 Próximos Passos

1. **Integrar com Frontend:** Usar endpoints da API no seu dashboard
2. **Monitoramento em Tempo Real:** WebSocket para atualizações em live
3. **Histórico e Análises:** Gráficos de tendência
4. **Alertas:** Notificações quando status muda
5. **Integração com Incidentes:** Registrar quando interrupções ocorrem

---

## 📞 Suporte

Para questões sobre a API, verifique os arquivos:
- `api.py` - Código da API
- `weather_processor.py` - Engine de processamento
- `test_api_endpoints.py` - Testes de todos os endpoints

