# 🚀 GUIA COMPLETO: API Rodando + Frontend no Vercel

## 📋 Opções para Manter a API Rodando

### **OPÇÃO 1: PM2 (Recomendado para Windows/Linux)**

#### 1.1 Instalar PM2
```bash
npm install pm2 -g
```

#### 1.2 Ativar venv e iniciar API com PM2
```bash
# No diretório do projeto
.venv\Scripts\Activate.ps1

# Iniciar API
pm2 start api_producao.py --name "mde-api" --interpreter "python"

# Comandos úteis
pm2 list              # Ver processos rodando
pm2 logs mde-api      # Ver logs
pm2 restart mde-api   # Reiniciar
pm2 stop mde-api      # Parar
pm2 delete mde-api    # Remover
pm2 save              # Salvar configuração (inicia ao boot)
pm2 startup           # Iniciar ao ligar a máquina
```

**Vantagens:**
- ✅ Reinicia automaticamente se cair
- ✅ Monitora CPU/Memória
- ✅ Múltiplas instâncias
- ✅ Inicia ao boot do Windows

---

### **OPÇÃO 2: Windows Service**

Criar um arquivo `start_api.bat`:
```batch
@echo off
cd C:\Users\Filipe\Desktop\MDE-REPO\maris-decision-engine\MDE
.venv\Scripts\Activate.ps1
python api_producao.py
pause
```

**Para criar como serviço do Windows:**
```bash
# Usar NSSM (Non-Sucking Service Manager)
# Download: https://nssm.cc/download

nssm install "Maris Decision Engine API" "C:\Users\Filipe\Desktop\MDE-REPO\maris-decision-engine\MDE\start_api.bat"
nssm start "Maris Decision Engine API"
```

---

### **OPÇÃO 3: Task Scheduler do Windows**

1. Abrir "Task Scheduler"
2. Criar nova tarefa
3. Configurar:
   - **Trigger:** "At startup" ou "On a schedule"
   - **Action:** `C:\Users\Filipe\Desktop\MDE-REPO\maris-decision-engine\MDE\.venv\Scripts\python.exe`
   - **Arguments:** `api_producao.py`
   - **Start in:** `C:\Users\Filipe\Desktop\MDE-REPO\maris-decision-engine\MDE`

---

### **OPÇÃO 4: Docker (Mais Profissional)**

Criar `Dockerfile`:
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Copiar requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar código
COPY . .

# Expor porta
EXPOSE 5000

# Iniciar API
CMD ["python", "api_producao.py"]
```

Criar `requirements.txt`:
```bash
pip freeze > requirements.txt
```

Executar:
```bash
docker build -t mde-api .
docker run -p 5000:5000 --name mde-api -d mde-api
```

---

## 🌐 Configurar URL Pública (Para Vercel acessar)

### **Se a máquina está na rede local:**

#### Opção A: ngrok (Fácil e Temporária)
```bash
# Instalar: https://ngrok.com/download

ngrok http 5000

# Saída:
# Forwarding    https://xxxx-yyyy-zzzz.ngrok.io -> http://localhost:5000
```

Usar a URL `https://xxxx-yyyy-zzzz.ngrok.io` no frontend.

---

#### Opção B: Usar IP Fixo na Rede
```bash
# 1. Descobrir IP local (no PowerShell)
ipconfig

# Procurar por: IPv4 Address: 192.168.x.x

# 2. Usar no frontend: http://192.168.x.x:5000/api/health
```

---

#### Opção C: Port Forwarding no Router
1. Acessar roteador: `192.168.1.1` (geralmente)
2. Ir para "Port Forwarding" ou "NAT"
3. Configurar:
   - **External Port:** 5000
   - **Internal IP:** 192.168.x.x
   - **Internal Port:** 5000
4. Usar: `http://seu-ip-publico:5000`

---

#### Opção D: Usar um Servidor Cloud (Recomendado)
Deploy para um servidor em nuvem:
- **AWS EC2**
- **Azure VM**
- **DigitalOcean**
- **Render.com** (grátis)
- **Railway.app** (grátis)

---

## 📱 Integração no Vercel (Frontend)

### **1. Criar arquivo `.env.local` no projeto Next.js:**

```
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_LOCATION_ID=1
```

(Alterar URL conforme ambiente)

---

### **2. Usar no Frontend (React/Next.js):**

```javascript
// src/api/client.js
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export const fetchOperationalStatus = async (locationId) => {
  const response = await fetch(
    `${API_URL}/api/operational-status/${locationId}`
  );
  if (!response.ok) throw new Error(`API error: ${response.status}`);
  return response.json();
};

export const fetchAllLocationsStatus = async () => {
  const response = await fetch(`${API_URL}/api/all-locations-status`);
  if (!response.ok) throw new Error(`API error: ${response.status}`);
  return response.json();
};

export const fetchDecisionHistory = async (locationId, hours = 24) => {
  const response = await fetch(
    `${API_URL}/api/decision-history/${locationId}?hours=${hours}`
  );
  if (!response.ok) throw new Error(`API error: ${response.status}`);
  return response.json();
};

export const fetchWeatherRaw = async (locationId, hours = 24) => {
  const response = await fetch(
    `${API_URL}/api/weather-raw/${locationId}?hours=${hours}`
  );
  if (!response.ok) throw new Error(`API error: ${response.status}`);
  return response.json();
};
```

---

### **3. Usar em um Componente React:**

```javascript
// src/components/OperationalStatus.jsx
import { useState, useEffect } from 'react';
import { fetchOperationalStatus } from '../api/client';

export default function OperationalStatus({ locationId = 1 }) {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadStatus = async () => {
      try {
        setLoading(true);
        const data = await fetchOperationalStatus(locationId);
        setStatus(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadStatus();
    // Atualizar a cada 30 segundos
    const interval = setInterval(loadStatus, 30000);
    return () => clearInterval(interval);
  }, [locationId]);

  if (loading) return <div>Carregando...</div>;
  if (error) return <div>Erro: {error}</div>;
  if (!status) return <div>Sem dados</div>;

  const { decision, location } = status.data;

  return (
    <div className={`card bg-${decision.color}-100 border-4 border-${decision.color}-500`}>
      <h2>{location.name}</h2>
      <p>Plataforma: {location.platform_type}</p>
      
      <div className="metrics">
        <div>
          <label>IEA Score</label>
          <div className="progress">
            <div style={{ width: `${decision.iea_score}%` }} 
                 className={`bg-${decision.color}-500`}>
              {decision.iea_score}
            </div>
          </div>
        </div>

        <div>
          <label>Status Operacional</label>
          <h3 className={`text-${decision.color}-700`}>
            {decision.operational_status}
          </h3>
        </div>

        <div>
          <label>Probabilidade de Interrupção</label>
          <p>{decision.interruption_probability_percent}%</p>
        </div>

        <div>
          <label>Tendência</label>
          <p>{decision.trend_indicator}</p>
        </div>

        <div>
          <label>Pode Operar?</label>
          <p className={decision.is_operational ? 'text-green-600' : 'text-red-600'}>
            {decision.is_operational ? '✅ SIM' : '❌ NÃO'}
          </p>
        </div>
      </div>

      <small>Última atualização: {decision.timestamp}</small>
    </div>
  );
}
```

---

### **4. Dashboard com Múltiplas Localizações:**

```javascript
// src/pages/dashboard.js
import { useState, useEffect } from 'react';
import { fetchAllLocationsStatus } from '../api/client';
import OperationalStatus from '../components/OperationalStatus';

export default function Dashboard() {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAll = async () => {
      try {
        const data = await fetchAllLocationsStatus();
        setLocations(data.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadAll();
    // Atualizar a cada 60 segundos
    const interval = setInterval(loadAll, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div>Carregando dashboard...</div>;

  return (
    <div className="dashboard">
      <h1>Painel Operacional</h1>
      <p>Total de plataformas: {locations.length}</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {locations.map(loc => (
          <OperationalStatus key={loc.id} locationId={loc.id} />
        ))}
      </div>
    </div>
  );
}
```

---

## 🔒 Segurança

### **Environment Variables no Vercel:**

1. Ir em Vercel Dashboard → seu projeto
2. Settings → Environment Variables
3. Adicionar:
```
NEXT_PUBLIC_API_URL=https://seu-dominio-api.com
```

**⚠️ NÃO adicionar credenciais do banco no frontend!**

---

## 📊 Checklist de Deployment

- [ ] API rodando localmente com `api_producao.py`
- [ ] PM2, Docker ou serviço Windows configurado
- [ ] Endpoint de health check testado: `/api/health`
- [ ] CORS configurado para domínio Vercel
- [ ] URL pública obtida (ngrok, IP local, ou cloud)
- [ ] Frontend testado localmente com API
- [ ] Variáveis de ambiente configuradas no Vercel
- [ ] Deploy realizado no Vercel
- [ ] Endpoints acessíveis do Vercel

---

## 🧪 Teste de Integração

```bash
# Terminal 1 - Iniciar API
python api_producao.py

# Terminal 2 - Testar endpoint
curl http://localhost:5000/api/health

# Saída esperada:
# {
#   "status": "healthy",
#   "database_connected": true,
#   "database_time": "2026-03-05T...",
#   "api_time": "2026-03-05T..."
# }
```

---

## 🐛 Troubleshooting

### **CORS Error no Vercel**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solução:** Adicionar domínio Vercel em `api_producao.py`:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://seu-projeto.vercel.app",  ← Adicionar aqui
            "https://seu-dominio-custom.com",
        ],
    }
})
```

---

### **API não responde**
```bash
# Testar localmente
curl http://localhost:5000/api/health

# Se não funcionar, reiniciar:
pm2 restart mde-api

# Ou ver logs:
pm2 logs mde-api
```

---

### **Banco desconectado**
```
ORA-12170: could not connect to Oracle
```

**Solução:** Verificar se Oracle está rodando:
```bash
# Windows
net start OracleXEInst  # ou seu serviço Oracle

# Ou testar manualmente
python test_db_connection.py
```

---

## 📞 Comandos Úteis

```bash
# Iniciar API com PM2
pm2 start api_producao.py --name "mde-api" --interpreter "python"

# Ver status
pm2 status

# Ver logs em tempo real
pm2 logs mde-api -f

# Salvar configuração (startup automático)
pm2 save
pm2 startup

# Restart automático ao editar código
pm2 watch

# Monitorar recursos
pm2 monit
```

---

## ✨ Pronto para Produção!

Sua API está configurada para:
- ✅ Rodar 24/7
- ✅ Reiniciar automaticamente
- ✅ Aceitar requisições do Vercel
- ✅ Escalar conforme necessário
- ✅ Logs e monitoramento

**Próximo passo:** Deploy seu frontend no Vercel! 🚀

