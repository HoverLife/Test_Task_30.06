WITH earliest_defaults AS (
    SELECT
        inn,
        MIN("defaultdate") AS default_date
    FROM defaults
    WHERE "defaultdate" <= DATE '2021-09-09'
    GROUP BY inn
),

clients_tagged AS (
    SELECT
        c.inn,
        c."reportdate",
        CASE
            WHEN d.default_date IS NOT NULL
                 AND d.default_date > c."reportdate"
                 AND d.default_date <= c."reportdate" + INTERVAL '365 days'
            THEN 1
            ELSE 0
        END AS default_flag
    FROM clients c
    LEFT JOIN earliest_defaults d ON c.inn = d.inn
    WHERE c."reportdate" <= DATE '2021-09-09' - INTERVAL '365 days'
),

def_only AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY inn ORDER BY "reportdate") AS rn
    FROM clients_tagged
    WHERE default_flag = 1
),

final_selection AS (
    SELECT inn, "reportdate", default_flag
    FROM def_only
    WHERE rn = 1
    UNION ALL
    SELECT inn, "reportdate", default_flag
    FROM clients_tagged
    WHERE default_flag = 0
)

SELECT *
FROM final_selection
ORDER BY inn, "reportdate";