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
        parts_amount AS parts_amount
    FROM public.dnm_ro_data
    WHERE vehicle_report_date != '0'
      AND EXTRACT(YEAR FROM ro_close_date::DATE) IN (%(selected_year)s)
),
/* агрегат UIO по коду модели */
sales_uio AS (
    SELECT
      s.model_code,
      COUNT(
        DATE_PART(
          'year',
          AGE(
            CASE
              WHEN %(selected_year)s::int = EXTRACT(YEAR FROM CURRENT_DATE)::int
                THEN CURRENT_DATE
              ELSE MAKE_DATE(%(selected_year)s::int, 12, 31)
            END,
            s.warranty_start_date::date
          )
        )::int
      ) FILTER (
        WHERE DATE_PART(
          'year',
          AGE(
            CASE
              WHEN %(selected_year)s::int = EXTRACT(YEAR FROM CURRENT_DATE)::int
                THEN CURRENT_DATE
              ELSE MAKE_DATE(%(selected_year)s::int, 12, 31)
            END,
            s.warranty_start_date::date
          )
        )::int BETWEEN 0 AND 10
      ) AS uio_10y
    FROM public.sales s
    GROUP BY s.model_code
),
base AS (
    SELECT 
        vm.model,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age = 0), 0)  AS age_0,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age = 1), 0)  AS age_1,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age = 2), 0)  AS age_2,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age = 3), 0)  AS age_3,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age = 4), 0)  AS age_4,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age = 5), 0)  AS age_5,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age = 6), 0)  AS age_6,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age = 7), 0)  AS age_7,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age = 8), 0)  AS age_8,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age = 9), 0)  AS age_9,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age = 10), 0) AS age_10,
		COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age BETWEEN 0 AND 10), 0)  AS total_0_10,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age BETWEEN 0 AND 3), 0)   AS age_0_3,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age BETWEEN 4 AND 5), 0)   AS age_4_5,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age BETWEEN 6 AND 10), 0)  AS age_6_10,
        COALESCE(SUM(dd.labor_hours)  FILTER (WHERE dd.vehicle_age BETWEEN 0 AND 10), 0) AS labor_hours_0_10,
        COALESCE(SUM(dd.labor_amount) FILTER (WHERE dd.vehicle_age BETWEEN 0 AND 10), 0) AS labor_amount_0_10,
        COALESCE(SUM(dd.parts_amount) FILTER (WHERE dd.vehicle_age BETWEEN 0 AND 10), 0) AS parts_amount_0_10
    FROM dnm_data dd
    LEFT JOIN public.vin_model vm ON dd.vin_mask = vm.vin45678
    GROUP BY vm.model
)
SELECT 
    b.model,
    /* UIO по model через model_code из vin_model */
    COALESCE(MAX(su.uio_10y), 0) AS uio_10y,
    age_0, age_1, age_2, age_3, age_4, age_5, age_6, age_7, age_8, age_9, age_10,
    age_0_3, age_4_5, age_6_10, total_0_10,
    /* проценты по интервалам от total_0_10 */
    COALESCE(ROUND(100 * age_0_3::numeric / NULLIF(total_0_10, 0), 2), 0) AS pct_age_0_3,
    COALESCE(ROUND(100 * age_4_5::numeric / NULLIF(total_0_10, 0), 2), 0) AS pct_age_4_5,
    COALESCE(ROUND(100 * age_6_10::numeric / NULLIF(total_0_10, 0), 2), 0) AS pct_age_6_10,
	COALESCE(ROUND(100 * total_0_10::numeric / NULLIF(COALESCE(MAX(su.uio_10y), 0), 0), 2), 0) AS ro_ratio_of_uio_10y,
    labor_hours_0_10,
    labor_amount_0_10,
    parts_amount_0_10,
    (labor_amount_0_10 + parts_amount_0_10) AS total_ro_cost,
    COALESCE(ROUND(labor_hours_0_10::numeric / NULLIF(total_0_10, 0), 2), 0) AS aver_labor_hours_per_vhc,
    COALESCE(ROUND(labor_amount_0_10::numeric / NULLIF(total_0_10, 0), 2), 0) AS avg_ro_labor_cost,
    COALESCE(ROUND(parts_amount_0_10::numeric / NULLIF(total_0_10, 0), 2), 0) AS avg_ro_part_cost,
    COALESCE(ROUND((labor_amount_0_10 + parts_amount_0_10)::numeric / NULLIF(total_0_10, 0), 2), 0) AS avg_ro_cost
FROM base b
LEFT JOIN public.vin_model vm2 ON vm2.model = b.model
LEFT JOIN sales_uio su ON su.model_code = vm2.model
GROUP BY 
    b.model,
    age_0, age_1, age_2, age_3, age_4, age_5, age_6, age_7, age_8, age_9, age_10,
    age_0_3, age_4_5, age_6_10,
    total_0_10,
    labor_hours_0_10,
    labor_amount_0_10,
    parts_amount_0_10
ORDER BY b.model;