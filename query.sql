WITH contagios_semanal AS (
    -- 1️⃣ Agrupo contagios por provincia, departamento, año y semana
    SELECT
        c.id_provincia,
        c.departamento,
        c.provincia,
        c.ano,
        c.semanas_epidemiologicas AS semana,
        SUM(c.cantidad_casos) AS total_casos
    FROM contagios AS c
    GROUP BY c.id_provincia, c.departamento, c.provincia, c.ano, c.semanas_epidemiologicas
),

clima_semanal AS (
    -- 2️⃣ Agrupo clima por estación y semana (con promedio de variables)
    SELECT
        e.id_provincia,
        e.id_departamento,
        e.id_estacion,
        strftime('%Y', cl.fecha) AS ano,
        CAST(strftime('%W', cl.fecha) AS INTEGER) AS semana,
        AVG(cl.precipitacion_pluviometrica) AS precip_prom,
        AVG(cl.temperatura_minima) AS temp_min_prom,
        AVG(cl.temperatura_maxima) AS temp_max_prom,
        AVG(cl.temperatura_media) AS temp_med_prom,
        AVG(cl.humedad_media) AS humedad_prom,
        AVG(cl.rocio_medio) AS rocio_prom,
        AVG(cl.tesion_vapor_media) AS vapor_prom,
        AVG(cl.radiacion_global) AS radiacion_prom,
        AVG(cl.heliofania_efectiva) AS heliofania_prom,
        AVG(cl.heliofania_relativa) AS heliofania_rel_prom
    FROM clima AS cl
    JOIN estaciones AS e ON cl.id_estacion = e.id_interno
    GROUP BY e.id_provincia, e.id_departamento, e.id_estacion, ano, semana
),

base_unificada AS (
    -- 3️⃣ Relaciono contagios con clima por provincia, departamento, año y semana
    SELECT
        cs.id_provincia,
        cs.departamento,
        cs.provincia,
        cs.ano,
        cs.semana,
        cs.total_casos,
        AVG(cl.precip_prom) AS precip_prom,
        AVG(cl.temp_min_prom) AS temp_min_prom,
        AVG(cl.temp_max_prom) AS temp_max_prom,
        AVG(cl.temp_med_prom) AS temp_med_prom,
        AVG(cl.humedad_prom) AS humedad_prom,
        AVG(cl.rocio_prom) AS rocio_prom,
        AVG(cl.vapor_prom) AS vapor_prom,
        AVG(cl.radiacion_prom) AS radiacion_prom,
        AVG(cl.heliofania_prom) AS heliofania_prom,
        AVG(cl.heliofania_rel_prom) AS heliofania_rel_prom
    FROM contagios_semanal cs
    LEFT JOIN clima_semanal cl
        ON cs.id_provincia = cl.id_provincia
        AND cs.ano = cl.ano
        AND cs.semana = cl.semana
    GROUP BY cs.id_provincia, cs.departamento, cs.provincia, cs.ano, cs.semana
),

lags AS (
    -- 4️⃣ Creo variables "lag" (1 a 4 semanas anteriores) usando ventanas
    SELECT
        b.*,
        LAG(b.total_casos, 1) OVER (PARTITION BY b.departamento ORDER BY b.ano, b.semana) AS lag1_casos,
        LAG(b.total_casos, 2) OVER (PARTITION BY b.departamento ORDER BY b.ano, b.semana) AS lag2_casos,
        LAG(b.total_casos, 3) OVER (PARTITION BY b.departamento ORDER BY b.ano, b.semana) AS lag3_casos,
        LAG(b.total_casos, 4) OVER (PARTITION BY b.departamento ORDER BY b.ano, b.semana) AS lag4_casos,

        LAG(b.precip_prom, 1) OVER (PARTITION BY b.departamento ORDER BY b.ano, b.semana) AS lag1_precip,
        LAG(b.precip_prom, 2) OVER (PARTITION BY b.departamento ORDER BY b.ano, b.semana) AS lag2_precip,
        LAG(b.precip_prom, 3) OVER (PARTITION BY b.departamento ORDER BY b.ano, b.semana) AS lag3_precip,
        LAG(b.precip_prom, 4) OVER (PARTITION BY b.departamento ORDER BY b.ano, b.semana) AS lag4_precip,

        LAG(b.temp_med_prom, 1) OVER (PARTITION BY b.departamento ORDER BY b.ano, b.semana) AS lag1_temp,
        LAG(b.temp_med_prom, 2) OVER (PARTITION BY b.departamento ORDER BY b.ano, b.semana) AS lag2_temp,
        LAG(b.temp_med_prom, 3) OVER (PARTITION BY b.departamento ORDER BY b.ano, b.semana) AS lag3_temp,
        LAG(b.temp_med_prom, 4) OVER (PARTITION BY b.departamento ORDER BY b.ano, b.semana) AS lag4_temp,

        LAG(b.humedad_prom, 1) OVER (PARTITION BY b.departamento ORDER BY b.ano, b.semana) AS lag1_humedad,
        LAG(b.humedad_prom, 2) OVER (PARTITION BY b.departamento ORDER BY b.ano, b.semana) AS lag2_humedad,
        LAG(b.humedad_prom, 3) OVER (PARTITION BY b.departamento ORDER BY b.ano, b.semana) AS lag3_humedad,
        LAG(b.humedad_prom, 4) OVER (PARTITION BY b.departamento ORDER BY b.ano, b.semana) AS lag4_humedad
    FROM base_unificada b
)

-- 5️⃣ Creo la variable target de clasificación (rango de contagios)
SELECT
    *,
    CASE
        WHEN total_casos BETWEEN 0 AND 5 THEN '0-5'
        WHEN total_casos BETWEEN 6 AND 10 THEN '6-10'
        WHEN total_casos BETWEEN 11 AND 15 THEN '11-15'
        ELSE '16+'
    END AS rango_contagios
FROM lags
WHERE total_casos IS NOT NULL;
