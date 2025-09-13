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
      AND (EXTRACT(YEAR FROM ro_close_date::DATE) 
           - EXTRACT(YEAR FROM vehicle_report_date::DATE)) BETWEEN 0 AND 5
      AND (%(selected_mobis_code)s = 'All' OR mobis_code = %(selected_mobis_code)s)
),
/* агрегат UIO по коду модели для возрастных групп 0-5 лет */
sales_uio AS (
    SELECT
      s.model_code,
      COUNT(
        EXTRACT(
          'year' FROM AGE(
            CASE
              WHEN %(selected_year)s::int = EXTRACT(YEAR FROM CURRENT_DATE)::int
                THEN CURRENT_DATE
              ELSE MAKE_DATE(%(selected_year)s::int, 12, 31)
            END,
            s.warranty_start_date::date
          )
        ) + 
        EXTRACT(
          'month' FROM AGE(
            CASE
              WHEN %(selected_year)s::int = EXTRACT(YEAR FROM CURRENT_DATE)::int
                THEN CURRENT_DATE
              ELSE MAKE_DATE(%(selected_year)s::int, 12, 31)
            END,
            s.warranty_start_date::date
          )
        ) / 12.0
      ) FILTER (
        WHERE EXTRACT(
          'year' FROM AGE(
            CASE
              WHEN %(selected_year)s::int = EXTRACT(YEAR FROM CURRENT_DATE)::int
                THEN CURRENT_DATE
              ELSE MAKE_DATE(%(selected_year)s::int, 12, 31)
            END,
            s.warranty_start_date::date
          )
        ) + 
        EXTRACT(
          'month' FROM AGE(
            CASE
              WHEN %(selected_year)s::int = EXTRACT(YEAR FROM CURRENT_DATE)::int
                THEN CURRENT_DATE
              ELSE MAKE_DATE(%(selected_year)s::int, 12, 31)
            END,
            s.warranty_start_date::date
          )
        ) / 12.0 <= 5.0
      ) AS uio_5y
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
		COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age BETWEEN 0 AND 5), 0)  AS total_0_5,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age BETWEEN 0 AND 3), 0)   AS age_0_3,
        COALESCE(COUNT(dd.vin) FILTER (WHERE dd.vehicle_age BETWEEN 4 AND 5), 0)   AS age_4_5,
        COALESCE(SUM(dd.labor_hours)  FILTER (WHERE dd.vehicle_age BETWEEN 0 AND 5), 0) AS labor_hours_0_5,
        COALESCE(SUM(dd.labor_amount) FILTER (WHERE dd.vehicle_age BETWEEN 0 AND 5), 0) AS labor_amount_0_5,
        COALESCE(SUM(dd.parts_amount) FILTER (WHERE dd.vehicle_age BETWEEN 0 AND 5), 0) AS parts_amount_0_5
    FROM dnm_data dd
    LEFT JOIN public.vin_model vm ON dd.vin_mask = vm.vin45678
    GROUP BY vm.model
)
SELECT 
    b.model,
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
    COALESCE(ROUND((labor_amount_0_5 + parts_amount_0_5)::numeric / NULLIF(total_0_5, 0), 2), 0) AS avg_ro_cost
FROM base b
LEFT JOIN public.vin_model vm2 ON vm2.model = b.model
LEFT JOIN sales_uio su ON su.model_code = vm2.model
GROUP BY 
    b.model,
    age_0, age_1, age_2, age_3, age_4, age_5,
    age_0_3, age_4_5,
    total_0_5,
    labor_hours_0_5,
    labor_amount_0_5,
    parts_amount_0_5
ORDER BY b.model;
