"""
EXEMPLO DE CONFIGURAÇÃO DO FRONTEND (Next.js/React + Vercel)
Copie este arquivo para seu projeto frontend
"""

# .env.local (para desenvolvimento local)
"""
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_LOCATION_ID=1
"""

# .env.production (para Vercel)
"""
NEXT_PUBLIC_API_URL=https://seu-dominio-api.com:5000
NEXT_PUBLIC_LOCATION_ID=1
"""

# src/api/weather.js ou utils/api.js
"""
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
const DEFAULT_LOCATION = parseInt(process.env.NEXT_PUBLIC_LOCATION_ID || '1');

// Headers padrão
const headers = {
  'Content-Type': 'application/json',
};

// Função auxiliar para requisições
const apiCall = async (endpoint, options = {}) => {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      headers,
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`[API Error] ${endpoint}:`, error.message);
    throw error;
  }
};

// ============ ENDPOINTS ==========

// Verificar saúde da API
export const checkHealthStatus = () => {
  return apiCall('/api/health');
};

// Buscar status operacional de uma localização
export const getOperationalStatus = (locationId = DEFAULT_LOCATION) => {
  return apiCall(`/api/operational-status/${locationId}`);
};

// Buscar status de TODAS as localizações
export const getAllLocationsStatus = () => {
  return apiCall('/api/all-locations-status');
};

// Buscar histórico de decisões
export const getDecisionHistory = (locationId = DEFAULT_LOCATION, hours = 24) => {
  return apiCall(`/api/decision-history/${locationId}?hours=${hours}`);
};

// Buscar dados brutos de clima
export const getWeatherRaw = (locationId = DEFAULT_LOCATION, hours = 24) => {
  return apiCall(`/api/weather-raw/${locationId}?hours=${hours}`);
};

// Disparar processamento de dados
export const processWeatherData = () => {
  return apiCall('/api/process-data', { method: 'POST' });
};
"""

print("=" * 80)
print("EXEMPLO DE CONFIGURAÇÃO FRONTEND")
print("=" * 80)
print("\n📁 Copie esses arquivos para seu projeto Next.js/React no Vercel:\n")
print("1. Criar .env.local para desenvolvimento:")
print("   NEXT_PUBLIC_API_URL=http://localhost:5000")
print("   NEXT_PUBLIC_LOCATION_ID=1\n")

print("2. Criar src/api/weather.js")
print("   (Veja acima para código completo)\n")

print("3. Usar em componentes:")
print("   import { getOperationalStatus } from '@/api/weather';")
print("   const data = await getOperationalStatus(1);\n")

print("4. No Vercel Dashboard:")
print("   → Settings → Environment Variables")
print("   → Adicionar:")
print("      NEXT_PUBLIC_API_URL=https://seu-dominio-api.com:5000")
print("      NEXT_PUBLIC_LOCATION_ID=1\n")

print("=" * 80)
