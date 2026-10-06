-- =====================================================================
-- views.sql
-- Views SQL que resumem os dados de temperatura IoT para o dashboard.
-- Executar no banco iot_db.
-- =====================================================================

-- ---------------------------------------------------------------------
-- View 1: Média de temperatura por dispositivo
-- Mostra a temperatura média de cada device_id.
-- Usada no Gráfico 2 (gráfico de barras) do dashboard.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW avg_temp_por_dispositivo AS
SELECT
    device_id,
    ROUND(AVG(temperature)::numeric, 2) AS avg_temp
FROM temperature_readings
GROUP BY device_id
ORDER BY avg_temp DESC;


-- ---------------------------------------------------------------------
-- View 2: Contagem de leituras por hora do dia
-- Mostra quantas leituras foram feitas em cada hora (0 a 23).
-- Usada no Gráfico 3 (gráfico de linha) do dashboard.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW leituras_por_hora AS
SELECT
    EXTRACT(HOUR FROM reading_datetime)::int AS hora,
    COUNT(*) AS contagem
FROM temperature_readings
GROUP BY hora
ORDER BY hora;


-- ---------------------------------------------------------------------
-- View 3: Temperatura máxima e mínima por dia
-- Mostra a temp. máxima e a mínima registradas em cada dia.
-- Usada no Gráfico 4 (gráfico de linha) do dashboard.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW temp_max_min_por_dia AS
SELECT
    DATE(reading_datetime) AS data,
    MAX(temperature) AS temp_max,
    MIN(temperature) AS temp_min
FROM temperature_readings
GROUP BY data
ORDER BY data;


-- ---------------------------------------------------------------------
-- View 4 (extra): Média de temperatura por localização (in / out)
-- Mostra a temperatura média dentro e fora do ambiente, com o total
-- de leituras em cada caso.
-- Usada no Gráfico 1 (gráfico de barras) do dashboard.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW avg_temp_por_localizacao AS
SELECT
    location,
    ROUND(AVG(temperature)::numeric, 2) AS avg_temp,
    COUNT(*) AS total_leituras
FROM temperature_readings
GROUP BY location
ORDER BY avg_temp DESC;