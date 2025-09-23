# 📊 Análisis EDA - Dataset de Dengue Argentina

**Generado:** 22/09/2025 a las 21:46

## 📈 Estadísticas Generales

| Métrica | Valor |
|---------|-------|
| Total de registros | 68,126 |
| Total de columnas | 9 |
| Período de datos | 2018 - 2025 |
| Total de casos de dengue | 765,848.0 |
| Población promedio | 216,043 |

## 📋 Información de Columnas

| Columna | Tipo | Valores Únicos | Valores Faltantes | Descripción |
|---------|------|----------------|-------------------|-------------|
| **id_uta** | int64 | 429 | 0 | Código UTA 2020 único |
| **departamento_nombre** | object | 429 | 0 | Nombre del departamento/partido |
| **provincia_nombre** | object | 24 | 0 | Nombre de la provincia |
| **ano** | int64 | 8 | 0 | Año de los datos epidemiológicos |
| **semanas_epidemiologicas** | float64 | 53 | 0 | Semana epidemiológica (1-52) |
| **grupo_edad_id** | int64 | 11 | 0 | ID numérico del grupo etario |
| **grupo_edad_desc** | object | 11 | 0 | Descripción del grupo etario |
| **cantidad_casos** | float64 | 430 | 0 | Número de casos de dengue |
| **poblacion** | int64 | 1,474 | 0 | Población del departamento |

## 🏆 Top 10 Departamentos con Más Registros

| Posición | Departamento | Registros |
|----------|--------------|----------|
| 1 | san fernando | 1,053 |
| 2 | general jose de san martin | 1,003 |
| 3 | rosario | 908 |
| 4 | formosa | 868 |
| 5 | general guemes | 829 |
| 6 | cordoba capital | 769 |
| 7 | corrientes capital | 744 |
| 8 | patino | 725 |
| 9 | la capital | 711 |
| 10 | general san martin | 705 |

## 🦠 Top 10 Departamentos con Más Casos de Dengue

| Posición | Departamento | Casos |
|----------|--------------|-------|
| 1 | cordoba capital | 63,655.0 |
| 2 | rosario | 42,999.0 |
| 3 | tucuman capital | 38,893.0 |
| 4 | santiago del estero capital | 24,395.0 |
| 5 | san fernando | 21,037.0 |
| 6 | cruz alta | 19,143.0 |
| 7 | salta capital | 16,344.0 |
| 8 | comuna 1 | 14,849.0 |
| 9 | la matanza | 13,987.0 |
| 10 | san justo | 13,505.0 |

## 📅 Casos de Dengue por Año

| Año | Casos |
|-----|-------|
| 2018 | 1,607.0 |
| 2019 | 2,790.0 |
| 2020 | 45,079.0 |
| 2021 | 3,847.0 |
| 2022 | 793.0 |
| 2023 | 141,429.0 |
| 2024 | 553,535.0 |
| 2025 | 16,768.0 |

## 📊 Estadísticas por Columna

### id_uta

| Estadística | Valor |
|-------------|-------|
| Media | 37954.49 |
| Mediana | 30028.00 |
| Desviación estándar | 30283.96 |
| Mínimo | 2001.00 |
| Máximo | 94028.00 |

### departamento_nombre

**Valores únicos:** 429

**Top 5 valores más frecuentes:**

- san fernando: 1,053 (1.55%)
- general jose de san martin: 1,003 (1.47%)
- rosario: 908 (1.33%)
- formosa: 868 (1.27%)
- general guemes: 829 (1.22%)

### provincia_nombre

**Valores únicos:** 24

**Top 5 valores más frecuentes:**

- buenos aires: 11,798 (17.32%)
- chaco: 6,523 (9.57%)
- santa fe: 5,604 (8.23%)
- cordoba: 5,289 (7.76%)
- tucuman: 4,961 (7.28%)

### ano

| Estadística | Valor |
|-------------|-------|
| Media | 2022.99 |
| Mediana | 2024.00 |
| Desviación estándar | 1.63 |
| Mínimo | 2018.00 |
| Máximo | 2025.00 |

### semanas_epidemiologicas

| Estadística | Valor |
|-------------|-------|
| Media | 15.33 |
| Mediana | 14.00 |
| Desviación estándar | 8.98 |
| Mínimo | 1.00 |
| Máximo | 53.00 |

### grupo_edad_id

| Estadística | Valor |
|-------------|-------|
| Media | 8.08 |
| Mediana | 9.00 |
| Desviación estándar | 2.46 |
| Mínimo | 1.00 |
| Máximo | 11.00 |

### grupo_edad_desc

**Valores únicos:** 11

**Top 5 valores más frecuentes:**

- mayores de 65 anos: 14,700 (21.58%)
- de 35 a 44 anos: 9,990 (14.66%)
- de 45 a 65 anos: 9,434 (13.85%)
- de 25 a 34 anos: 8,179 (12.01%)
- de 20 a 24 anos: 7,260 (10.66%)

### cantidad_casos

| Estadística | Valor |
|-------------|-------|
| Media | 11.24 |
| Mediana | 2.00 |
| Desviación estándar | 41.21 |
| Mínimo | 1.00 |
| Máximo | 2351.00 |

### poblacion

| Estadística | Valor |
|-------------|-------|
| Media | 216042.76 |
| Mediana | 99211.00 |
| Desviación estándar | 328065.34 |
| Mínimo | 313.00 |
| Máximo | 2509547.00 |

