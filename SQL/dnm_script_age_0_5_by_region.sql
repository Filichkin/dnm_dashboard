WITH dnm_data AS (
    SELECT 
        vin AS vin,
        SUBSTRING(vin, 4, 5) AS vin_mask,
        EXTRACT(YEAR FROM vehicle_report_date::DATE) AS sales_year,
        EXTRACT(YEAR FROM ro_close_date::DATE) AS repair_year,
        (EXTRACT(YEAR FROM ro_close_date::DATE) 
         - EXTRACT(YEAR FROM vehicle_report_date::DATE)) AS vehicle_age,
        labor_hours_total AS labor_hours,
        labor_amount AS labor_amount,
        parts_amount AS parts_amount,
        drd.mobis_code,
        drd.holding,
        COALESCE(dd.region, 'Unknown') AS region
    FROM public.dnm_ro_data drd
    LEFT JOIN public.dealers_data dd ON drd.mobis_code = dd.mobis_code
    WHERE vehicle_report_date != '0'
      AND EXTRACT(YEAR FROM ro_close_date::DATE) IN (%(selected_year)s)
      AND (EXTRACT(YEAR FROM ro_close_date::DATE) 
           - EXTRACT(YEAR FROM vehicle_report_date::DATE)) BETWEEN 0 AND 5
      AND (%(selected_region)s = 'All' OR dd.region = %(selected_region)s)
),
/* агрегат UIO по коду модели для возрастных групп 0-5 лет */
sales_uio AS (
  WITH s AS (
    SELECT
      sbd.vin,
      sbd.sales_date,
      sbd.sap_code,
      SUBSTRING(sbd.sap_code FROM 6 FOR 5)              AS dealer_code_txt,
      CAST(SUBSTRING(sbd.sap_code FROM 6 FOR 5) AS INT) AS dealer_code_num,
      SUBSTRING(sbd.vin FROM 4 FOR 5)                   AS vin_mask
    FROM sales_by_dealer sbd
    -- убираем фильтр по году продажи, берём все автомобили
  )
  SELECT
      vm.model,
      COUNT(DISTINCT s.vin) AS uio_5y
  FROM s
  LEFT JOIN dealers_data dd
    ON dd.warranty_code = s.dealer_code_num
  LEFT JOIN vin_model vm
    ON s.vin_mask = CAST(vm.vin45678 AS TEXT)
  WHERE s.sales_date::date IS NOT NULL
    AND AGE(
      CASE
        WHEN %(selected_year)s::int = EXTRACT(YEAR FROM CURRENT_DATE)::int
          THEN CURRENT_DATE
        ELSE MAKE_DATE(%(selected_year)s::int, 12, 31)
      END,
      s.sales_date::date
    ) <= INTERVAL '5 years'
    AND (%(selected_region)s = 'All' OR dd.region = %(selected_region)s)
  GROUP BY vm.model
),
/* Агрегация данных по дилерам (mobis_code) для каждой модели в регионе */
dealer_aggregates AS (
    SELECT 
        vm.model,
        dd.region,
        dd.mobis_code,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age = 0), 0)  AS age_0,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age = 1), 0)  AS age_1,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age = 2), 0)  AS age_2,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age = 3), 0)  AS age_3,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age = 4), 0)  AS age_4,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age = 5), 0)  AS age_5,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age BETWEEN 0 AND 5), 0)  AS total_0_5,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age BETWEEN 0 AND 3), 0)   AS age_0_3,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age BETWEEN 4 AND 5), 0)   AS age_4_5,
        COALESCE(SUM(dd.labor_hours)  FILTER (WHERE dd.vehicle_age BETWEEN 0 AND 5), 0) AS labor_hours_0_5,
        COALESCE(SUM(dd.labor_amount) FILTER (WHERE dd.vehicle_age BETWEEN 0 AND 5), 0) AS labor_amount_0_5,
        COALESCE(SUM(dd.parts_amount) FILTER (WHERE dd.vehicle_age BETWEEN 0 AND 5), 0) AS parts_amount_0_5
    FROM dnm_data dd
    LEFT JOIN public.vin_model vm ON dd.vin_mask = vm.vin45678
    GROUP BY vm.model, dd.region, dd.mobis_code
),
/* Агрегация данных по модели и региону (средние по дилерам) */
base AS (
    SELECT 
        model,
        region,
        AVG(age_0) AS age_0,
        AVG(age_1) AS age_1,
        AVG(age_2) AS age_2,
        AVG(age_3) AS age_3,
        AVG(age_4) AS age_4,
        AVG(age_5) AS age_5,
        AVG(total_0_5) AS total_0_5,
        AVG(age_0_3) AS age_0_3,
        AVG(age_4_5) AS age_4_5,
        AVG(labor_hours_0_5) AS labor_hours_0_5,
        AVG(labor_amount_0_5) AS labor_amount_0_5,
        AVG(parts_amount_0_5) AS parts_amount_0_5
    FROM dealer_aggregates
    GROUP BY model, region
),
/* Дополнительные средние значения по дилерам в регионе */
region_averages AS (
    SELECT 
        model,
        region,
        AVG(CASE WHEN total_0_5 > 0 THEN labor_hours_0_5::numeric / total_0_5 ELSE 0 END) AS avg_labor_hours_per_vhc_by_dealers,
        AVG(CASE WHEN total_0_5 > 0 THEN (labor_amount_0_5 + parts_amount_0_5)::numeric / total_0_5 ELSE 0 END) AS avg_ro_cost_per_vhc_by_dealers,
        COUNT(DISTINCT mobis_code) AS dealer_count_in_region
    FROM dealer_aggregates
    GROUP BY model, region
)
SELECT 
    b.model,
    b.region,
    /* UIO по model через model_code из vin_model для возрастных групп 0-5 лет */
    COALESCE(MAX(su.uio_5y), 0) AS uio_5y,
    age_0, age_1, age_2, age_3, age_4, age_5,
    age_0_3, age_4_5, total_0_5,
    /* проценты по интервалам от total_0_5 */
    COALESCE(ROUND(100 * age_0_3::numeric / NULLIF(total_0_5, 0), 2), 0) AS pct_age_0_3,
    COALESCE(ROUND(100 * age_4_5::numeric / NULLIF(total_0_5, 0), 2), 0) AS pct_age_4_5,
    COALESCE(ROUND(100 * total_0_5::numeric / NULLIF(COALESCE(MAX(su.uio_5y), 0), 0), 2), 0) AS ro_ratio_of_uio_5y,
    labor_hours_0_5,
    labor_amount_0_5,
    parts_amount_0_5,
    (labor_amount_0_5 + parts_amount_0_5) AS total_ro_cost,
    COALESCE(ROUND(labor_hours_0_5::numeric / NULLIF(total_0_5, 0), 2), 0) AS aver_labor_hours_per_vhc,
    COALESCE(ROUND(labor_amount_0_5::numeric / NULLIF(total_0_5, 0), 2), 0) AS avg_ro_labor_cost,
    COALESCE(ROUND(parts_amount_0_5::numeric / NULLIF(total_0_5, 0), 2), 0) AS avg_ro_part_cost,
    COALESCE(ROUND((labor_amount_0_5 + parts_amount_0_5)::numeric / NULLIF(total_0_5, 0), 2), 0) AS avg_ro_cost,
    /* дополнительные средние значения по дилерам в регионе */
    ra.avg_labor_hours_per_vhc_by_dealers,
    ra.avg_ro_cost_per_vhc_by_dealers,
    ra.dealer_count_in_region
FROM base b
LEFT JOIN public.vin_model vm2 ON vm2.model = b.model
LEFT JOIN sales_uio su ON su.model = vm2.model
LEFT JOIN region_averages ra ON ra.model = b.model AND ra.region = b.region
GROUP BY 
    b.model,
    b.region,
    age_0, age_1, age_2, age_3, age_4, age_5,
    age_0_3, age_4_5,
    total_0_5,
    labor_hours_0_5,
    labor_amount_0_5,
    parts_amount_0_5,
    ra.avg_labor_hours_per_vhc_by_dealers,
    ra.avg_ro_cost_per_vhc_by_dealers,
    ra.dealer_count_in_region
ORDER BY b.model, b.region;
