WITH
-- 0) Calendario semanal: lunes como inicio de semana
cal_sem AS (
  SELECT
    fecha,
    anio,
    semana,
    diaNumeroSemana,
    DATE(fecha) AS semana_inicio
  FROM calendario
  WHERE diaNumeroSemana = 0          -- Lunes
),

-- 1) Clima diario normalizado
clima_d AS (
  SELECT
    DATE(c.fecha)                       AS fecha,
    c.id_estacion                       AS id_interno,   -- A872xxx
    c.precipitacion_pluviometrica       AS precip,
    c.temperatura_media                 AS t_media,
    c.humedad_media                     AS h_media,
    c.temperatura_minima                AS t_min,
    c.temperatura_maxima                AS t_max
  FROM clima c
),

-- 2) Mapeo estación -> departamento
est_dep AS (
  SELECT
    e.id_interno,                       -- A872xxx
    e.id_estacion,                      -- id numérico si lo necesitás
    e.id_departamento
  FROM estaciones e
),

-- 3) Clima semanal por departamento
clima_sem AS (
  SELECT
    cs.semana_inicio,
    ed.id_departamento,
    AVG(cd.t_media)  AS t_media_sem,
    AVG(cd.h_media)  AS h_media_sem,
    AVG(cd.t_min)    AS t_min_sem,
    AVG(cd.t_max)    AS t_max_sem,
    SUM(cd.precip)   AS precip_sem
  FROM clima_d cd
  JOIN cal_sem cs   ON cd.fecha = cs.fecha
  JOIN est_dep ed   ON ed.id_interno = cd.id_interno
  GROUP BY cs.semana_inicio, ed.id_departamento
),

-- 4) Dim de departamentos
dep_dim AS (
  SELECT
    d.id_departamento,
    UPPER(TRIM(d.departamento)) AS dep_name_u,
    d.id_provincia
  FROM departamentos d
),

-- 5) Contagios semanales (por texto + provincia)
contagios_sem_raw AS (
  SELECT
    CAST(co.ano AS INT)                                 AS anio,
    CAST(co.semanas_epidemiologicas AS INT)             AS semana,
    UPPER(TRIM(co.departamento))                        AS dep_name_u,
    co.id_provincia,
    SUM(COALESCE(co.cantidad_casos,0))                  AS y_cont_sem
  FROM contagios co
  GROUP BY anio, semana, dep_name_u, id_provincia
),

-- 6) Índice (anio, semana) -> semana_inicio (desde cal_sem)  ⬅️ AQUÍ EL FIX
sem_idx AS (
  SELECT DISTINCT
    anio,
    semana,
    semana_inicio
  FROM cal_sem
),

-- 7) Labels con id_departamento
label_sem AS (
  SELECT
    si.semana_inicio,
    dd.id_departamento,
    csr.y_cont_sem AS y
  FROM contagios_sem_raw csr
  JOIN dep_dim dd
       ON dd.dep_name_u   = csr.dep_name_u
      AND dd.id_provincia = csr.id_provincia
  JOIN sem_idx si
       ON si.anio   = csr.anio
      AND si.semana = csr.semana
),

-- 8) Universo base
base AS (
  SELECT DISTINCT
    ls.semana_inicio,
    ls.id_departamento
  FROM label_sem ls
),

-- 9) Features climáticas semana t
feat_sem AS (
  SELECT
    b.semana_inicio,
    b.id_departamento,
    cs.t_media_sem,
    cs.h_media_sem,
    cs.t_min_sem,
    cs.t_max_sem,
    cs.precip_sem
  FROM base b
  LEFT JOIN clima_sem cs
    ON cs.semana_inicio = b.semana_inicio
   AND cs.id_departamento = b.id_departamento
),

-- 10) Lags/rolling sin fuga (hasta t-1)
feat_lags AS (
  SELECT
    f.*,
    LAG(t_media_sem,1)  OVER (PARTITION BY id_departamento ORDER BY semana_inicio) AS lag1_t_media,
    LAG(h_media_sem,1)  OVER (PARTITION BY id_departamento ORDER BY semana_inicio) AS lag1_h_media,
    LAG(t_min_sem,1)    OVER (PARTITION BY id_departamento ORDER BY semana_inicio) AS lag1_t_min,
    LAG(t_max_sem,1)    OVER (PARTITION BY id_departamento ORDER BY semana_inicio) AS lag1_t_max,
    LAG(precip_sem,1)   OVER (PARTITION BY id_departamento ORDER BY semana_inicio) AS lag1_precip,
    AVG(t_media_sem)    OVER (PARTITION BY id_departamento ORDER BY semana_inicio ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING) AS roll4_t_media,
    SUM(precip_sem)     OVER (PARTITION BY id_departamento ORDER BY semana_inicio ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING) AS roll4_precip
  FROM feat_sem f
),

-- 11) Lags del target
label_lags AS (
  SELECT
    ls.*,
    LAG(y,1) OVER (PARTITION BY id_departamento ORDER BY semana_inicio) AS lag1_y,
    SUM(y)   OVER (PARTITION BY id_departamento ORDER BY semana_inicio ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING) AS roll4_y
  FROM label_sem ls
)

-- 12) Salida final
SELECT
  fl.semana_inicio,
  fl.id_departamento,
  fl.lag1_t_media,
  fl.lag1_h_media,
  fl.lag1_t_min,
  fl.lag1_t_max,
  fl.lag1_precip,
  fl.roll4_t_media,
  fl.roll4_precip,
  ll.lag1_y,
  ll.roll4_y,
  ll.y AS y
FROM feat_lags fl
LEFT JOIN label_lags ll
  ON ll.semana_inicio = fl.semana_inicio
 AND ll.id_departamento = fl.id_departamento
WHERE fl.lag1_t_media IS NOT NULL
  AND ll.lag1_y IS NOT NULL
;
