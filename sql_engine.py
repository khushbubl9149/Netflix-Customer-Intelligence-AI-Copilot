from sqlalchemy import text
from src.copilot.database import engine


# ==========================================
# BUSINESS SQL QUERIES
# ==========================================

QUERIES = {

    "overall_churn": """
        SELECT
            COUNT(*) AS total_customers,
            SUM(CASE WHEN churned = TRUE THEN 1 ELSE 0 END) AS churned_customers,
            SUM(CASE WHEN churned = FALSE THEN 1 ELSE 0 END) AS active_customers,
            ROUND(
                100.0 * SUM(CASE WHEN churned = TRUE THEN 1 ELSE 0 END)
                / COUNT(*),
                2
            ) AS churn_rate
        FROM churn_labels;
    """,

    "total_customers": """
        SELECT COUNT(*) AS total_customers
        FROM customers;
    """,
    "q01_active_customers_by_country": """
    SELECT
        c.country,
        COUNT(*) AS active_customers
    FROM customers c
    JOIN churn_labels cl
        ON c.customer_id = cl.customer_id
    WHERE cl.churned = FALSE
    GROUP BY c.country
    ORDER BY active_customers DESC;
""",
"q02_revenue_by_subscription_plan": """
    SELECT
        sp.plan_name,
        COUNT(s.subscription_id) AS subscription_count,
        ROUND(
            SUM(s.monthly_price)::numeric,
            2
        ) AS total_monthly_revenue,
        ROUND(
            AVG(s.monthly_price)::numeric,
            2
        ) AS average_monthly_revenue
    FROM subscriptions s
    JOIN subscription_plans sp
        ON s.plan_id = sp.plan_id
    GROUP BY sp.plan_name
    ORDER BY total_monthly_revenue DESC;
""",
"q03_overall_churn_rate": """
    SELECT
        COUNT(*) AS total_customers,
        SUM(
            CASE
                WHEN churned = TRUE THEN 1
                ELSE 0
            END
        ) AS churned_customers,
        ROUND(
            100.0 * SUM(
                CASE
                    WHEN churned = TRUE THEN 1
                    ELSE 0
                END
            ) / COUNT(*),
            2
        ) AS churn_rate
    FROM churn_labels;
""",
"q04_churn_by_acquisition_channel": """
    SELECT
        c.acquisition_channel,
        COUNT(*) AS total_customers,
        SUM(
            CASE
                WHEN cl.churned = TRUE THEN 1
                ELSE 0
            END
        ) AS churned_customers,
        ROUND(
            100.0 * SUM(
                CASE
                    WHEN cl.churned = TRUE THEN 1
                    ELSE 0
                END
            ) / COUNT(*),
            2
        ) AS churn_rate
    FROM customers c
    JOIN churn_labels cl
        ON c.customer_id = cl.customer_id
    GROUP BY c.acquisition_channel
    ORDER BY total_customers DESC;
""",

    "churn_by_gender": """
        SELECT
            c.gender,
            COUNT(*) AS customers,
            SUM(
                CASE WHEN cl.churned = TRUE THEN 1 ELSE 0 END
            ) AS churned_customers,
            ROUND(
                100.0 *
                SUM(CASE WHEN cl.churned = TRUE THEN 1 ELSE 0 END)
                / COUNT(*),
                2
            ) AS churn_rate
        FROM customers c
        JOIN churn_labels cl
            ON c.customer_id = cl.customer_id
        GROUP BY c.gender
        ORDER BY churn_rate DESC;
    """,
    "q05_average_age_by_plan": """
    SELECT
        sp.plan_name,
        ROUND(AVG(c.age)::numeric, 2) AS average_customer_age
    FROM customers c
    JOIN subscriptions s
        ON c.customer_id = s.customer_id
    JOIN subscription_plans sp
        ON s.plan_id = sp.plan_id
    WHERE c.age IS NOT NULL
    GROUP BY sp.plan_name
    ORDER BY average_customer_age DESC;
""",
"q06_top_10_most_watched_titles": """
    SELECT
        ct.content_id,
        ct.title,
        ct.content_type,
        SUM(va.watch_duration_minutes) AS total_watch_minutes
    FROM viewing_activity va
    JOIN content ct
        ON va.content_id = ct.content_id
    GROUP BY
        ct.content_id,
        ct.title,
        ct.content_type
    ORDER BY total_watch_minutes DESC
    LIMIT 10;
""",
"q07_average_completion_by_type_genre": """
    SELECT
        c.content_type,
        c.genre,
        ROUND(
            AVG(va.completion_percentage)::numeric,
            2
        ) AS average_completion_percentage
    FROM viewing_activity va
    JOIN content c
        ON va.content_id = c.content_id
    GROUP BY
        c.content_type,
        c.genre
    ORDER BY
        c.content_type,
        average_completion_percentage DESC;
""",
"q08_failed_payments_last_12_months": """
    SELECT
        DATE_TRUNC('month', payment_date) AS payment_month,
        COUNT(*) AS failed_payment_count
    FROM payments
    WHERE payment_status = 'Failed'
      AND payment_date >= CURRENT_DATE - INTERVAL '12 months'
    GROUP BY DATE_TRUNC('month', payment_date)
    ORDER BY payment_month;
""",
"q09_average_resolution_by_issue": """
    SELECT
        issue_category,
        ROUND(
            AVG(resolution_time_hours)::numeric,
            2
        ) AS average_resolution_time_hours
    FROM support_tickets
    GROUP BY issue_category
    ORDER BY average_resolution_time_hours DESC;
""",
"q10_satisfaction_score_distribution": """
    SELECT
        customer_satisfaction_score,
        COUNT(*) AS ticket_count
    FROM support_tickets
    WHERE LOWER(ticket_status) IN ('resolved', 'closed')
      AND customer_satisfaction_score IS NOT NULL
    GROUP BY customer_satisfaction_score
    ORDER BY customer_satisfaction_score;
""",
"q11_viewing_minutes_by_device": """
    SELECT
        device_type,
        SUM(watch_duration_minutes) AS total_viewing_minutes
    FROM viewing_activity
    GROUP BY device_type
    ORDER BY total_viewing_minutes DESC;
""",
"q12_average_rating_by_sentiment": """
    SELECT
        sentiment_label,
        ROUND(
            AVG(rating)::numeric,
            2
        ) AS average_rating
    FROM customer_feedback
    WHERE rating IS NOT NULL
    GROUP BY sentiment_label
    ORDER BY average_rating DESC;
""",
"q13_customers_by_channel_year": """
    SELECT
        EXTRACT(YEAR FROM registration_date)::int AS registration_year,
        acquisition_channel,
        COUNT(*) AS customer_count
    FROM customers
    WHERE registration_date IS NOT NULL
    GROUP BY
        EXTRACT(YEAR FROM registration_date)::int,
        acquisition_channel
    ORDER BY registration_year, customer_count DESC;
""",
"q14_auto_renew_off_percentage": """
    SELECT
        COUNT(*) AS total_customers,
        SUM(
            CASE
                WHEN auto_renew = FALSE THEN 1
                ELSE 0
            END
        ) AS auto_renew_off_customers,
        ROUND(
            100.0 * SUM(
                CASE
                    WHEN auto_renew = FALSE THEN 1
                    ELSE 0
                END
            ) / COUNT(*),
            2
        ) AS auto_renew_off_percentage
    FROM subscriptions;
""",
"q15_customers_more_than_3_tickets": """
    SELECT
        c.customer_id,
        c.first_name,
        c.last_name,
        COUNT(st.ticket_id) AS support_ticket_count
    FROM customers c
    JOIN support_tickets st
        ON c.customer_id = st.customer_id
    GROUP BY
        c.customer_id,
        c.first_name,
        c.last_name
    HAVING COUNT(st.ticket_id) > 3
    ORDER BY support_ticket_count DESC, c.customer_id;
""",
"q16_rank_plans_by_revenue": """
    SELECT
        sp.plan_name,
        COUNT(s.subscription_id) AS active_subscription_count,
        ROUND(
            SUM(s.monthly_price)::numeric,
            2
        ) AS total_revenue,
        RANK() OVER (
            ORDER BY SUM(s.monthly_price) DESC
        ) AS revenue_rank
    FROM subscriptions s
    JOIN subscription_plans sp
        ON s.plan_id = sp.plan_id
    WHERE LOWER(s.subscription_status) = 'active'
    GROUP BY sp.plan_name
    ORDER BY revenue_rank;
""",
"q17_latest_support_ticket_per_customer": """
    WITH ranked_tickets AS (
        SELECT
            st.customer_id,
            st.ticket_id,
            st.ticket_date,
            st.issue_category,
            st.issue_subcategory,
            st.priority,
            st.ticket_status,
            st.resolution_time_hours,
            st.customer_satisfaction_score,
            ROW_NUMBER() OVER (
                PARTITION BY st.customer_id
                ORDER BY st.ticket_date DESC, st.ticket_id DESC
            ) AS rn
        FROM support_tickets st
    )
    SELECT
        customer_id,
        ticket_id,
        ticket_date,
        issue_category,
        issue_subcategory,
        priority,
        ticket_status,
        resolution_time_hours,
        customer_satisfaction_score
    FROM ranked_tickets
    WHERE rn = 1
    ORDER BY customer_id;
""",
"q18_three_month_moving_avg_registrations": """
    WITH monthly_registrations AS (
        SELECT
            DATE_TRUNC('month', registration_date)::date AS registration_month,
            COUNT(*) AS new_customers
        FROM customers
        WHERE registration_date IS NOT NULL
        GROUP BY DATE_TRUNC('month', registration_date)
    )
    SELECT
        registration_month,
        new_customers,
        ROUND(
            AVG(new_customers) OVER (
                ORDER BY registration_month
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            )::numeric,
            2
        ) AS three_month_moving_average
    FROM monthly_registrations
    ORDER BY registration_month;
""",
"q19_monthly_watch_time_decline": """
    WITH monthly_watch AS (
        SELECT
            customer_id,
            DATE_TRUNC('month', viewing_date)::date AS watch_month,
            SUM(watch_duration_minutes) AS monthly_watch_minutes
        FROM viewing_activity
        GROUP BY
            customer_id,
            DATE_TRUNC('month', viewing_date)
    ),
    watch_with_previous AS (
        SELECT
            customer_id,
            watch_month,
            monthly_watch_minutes,
            LAG(monthly_watch_minutes) OVER (
                PARTITION BY customer_id
                ORDER BY watch_month
            ) AS previous_month_watch_minutes
        FROM monthly_watch
    ),
    latest_month AS (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id
                ORDER BY watch_month DESC
            ) AS rn
        FROM watch_with_previous
    )
    SELECT
        customer_id,
        watch_month,
        monthly_watch_minutes,
        previous_month_watch_minutes,
        ROUND(
            (
                100.0
                * (monthly_watch_minutes - previous_month_watch_minutes)
                / NULLIF(previous_month_watch_minutes, 0)
            )::numeric,
            2
        ) AS percentage_change
    FROM latest_month
    WHERE rn = 1
      AND previous_month_watch_minutes IS NOT NULL
      AND monthly_watch_minutes < previous_month_watch_minutes
    ORDER BY percentage_change;
""",
"q20_cohort_retention": """
    WITH customer_cohorts AS (
        SELECT
            c.customer_id,
            DATE_TRUNC('month', c.registration_date)::date AS cohort_month
        FROM customers c
        WHERE c.registration_date IS NOT NULL
    ),
    cohort_activity AS (
        SELECT
            cc.cohort_month,
            cc.customer_id,
            MAX(
                CASE
                    WHEN va.viewing_date >=
                         cc.cohort_month + INTERVAL '1 month'
                    AND va.viewing_date <
                         cc.cohort_month + INTERVAL '2 months'
                    THEN 1 ELSE 0
                END
            ) AS active_1_month,
            MAX(
                CASE
                    WHEN va.viewing_date >=
                         cc.cohort_month + INTERVAL '3 months'
                    AND va.viewing_date <
                         cc.cohort_month + INTERVAL '4 months'
                    THEN 1 ELSE 0
                END
            ) AS active_3_month,
            MAX(
                CASE
                    WHEN va.viewing_date >=
                         cc.cohort_month + INTERVAL '6 months'
                    AND va.viewing_date <
                         cc.cohort_month + INTERVAL '7 months'
                    THEN 1 ELSE 0
                END
            ) AS active_6_month
        FROM customer_cohorts cc
        LEFT JOIN viewing_activity va
            ON va.customer_id = cc.customer_id
        GROUP BY
            cc.cohort_month,
            cc.customer_id
    )
    SELECT
        cohort_month,
        COUNT(*) AS cohort_customers,
        ROUND(
            100.0 * SUM(active_1_month)
            / COUNT(*),
            2
        ) AS retention_1_month_pct,
        ROUND(
            100.0 * SUM(active_3_month)
            / COUNT(*),
            2
        ) AS retention_3_month_pct,
        ROUND(
            100.0 * SUM(active_6_month)
            / COUNT(*),
            2
        ) AS retention_6_month_pct
    FROM cohort_activity
    GROUP BY cohort_month
    ORDER BY cohort_month;
""",
"q21_country_churn_rate_rank": """
    WITH country_churn AS (
        SELECT
            c.country,
            COUNT(*) AS total_customers,
            SUM(
                CASE WHEN cl.churned = TRUE THEN 1 ELSE 0 END
            ) AS churned_customers,
            100.0 * SUM(
                CASE WHEN cl.churned = TRUE THEN 1 ELSE 0 END
            ) / COUNT(*) AS churn_rate
        FROM customers c
        JOIN churn_labels cl
            ON c.customer_id = cl.customer_id
        WHERE c.country IS NOT NULL
        GROUP BY c.country
    ),
    ranked_countries AS (
        SELECT
            country,
            total_customers,
            churned_customers,
            ROUND(churn_rate::numeric, 2) AS churn_rate,
            DENSE_RANK() OVER (
                ORDER BY churn_rate DESC
            ) AS churn_rank
        FROM country_churn
    )
    SELECT
        country,
        total_customers,
        churned_customers,
        churn_rate,
        churn_rank
    FROM ranked_countries
    WHERE churn_rank <= 5
    ORDER BY churn_rank, country;
""",
"q22_customer_running_payment_total": """
    SELECT
        customer_id,
        payment_id,
        payment_date,
        amount,
        SUM(amount) OVER (
            PARTITION BY customer_id
            ORDER BY payment_date, payment_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS running_total
    FROM payments
    WHERE amount IS NOT NULL
    ORDER BY customer_id, payment_date, payment_id;
""",

"q23_three_month_declining_watch_time": """
    WITH monthly_watch_time AS (
        SELECT
            customer_id,
            DATE_TRUNC('month', viewing_date)::date AS watch_month,
            SUM(watch_duration_minutes) AS total_watch_minutes
        FROM viewing_activity
        WHERE viewing_date IS NOT NULL
        GROUP BY
            customer_id,
            DATE_TRUNC('month', viewing_date)::date
    ),
    watch_comparison AS (
        SELECT
            customer_id,
            watch_month,
            total_watch_minutes,
            LAG(total_watch_minutes, 1) OVER (
                PARTITION BY customer_id
                ORDER BY watch_month
            ) AS previous_month_watch,
            LAG(total_watch_minutes, 2) OVER (
                PARTITION BY customer_id
                ORDER BY watch_month
            ) AS two_months_ago_watch
        FROM monthly_watch_time
    )
    SELECT
        customer_id,
        watch_month,
        two_months_ago_watch,
        previous_month_watch,
        total_watch_minutes
    FROM watch_comparison
    WHERE two_months_ago_watch > previous_month_watch
      AND previous_month_watch > total_watch_minutes
    ORDER BY customer_id, watch_month;
""",

"q24_monthly_churn_rate": """
    WITH months AS (
        SELECT generate_series(
            DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months',
            DATE_TRUNC('month', CURRENT_DATE),
            INTERVAL '1 month'
        )::date AS month_start
    ),
    active_at_start AS (
        SELECT
            m.month_start,
            COUNT(DISTINCT s.customer_id) AS active_customers_at_start
        FROM months m
        LEFT JOIN subscriptions s
            ON s.subscription_start_date < m.month_start
           AND (
                s.subscription_end_date IS NULL
                OR s.subscription_end_date >= m.month_start
           )
        GROUP BY m.month_start
    ),
    monthly_churn AS (
        SELECT
            DATE_TRUNC('month', cl.churn_date)::date AS month_start,
            COUNT(DISTINCT cl.customer_id) AS churned_customers
        FROM churn_labels cl
        WHERE cl.churn_date >= (
            DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '11 months'
        )
          AND cl.churn_date < (
            DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month'
        )
        GROUP BY DATE_TRUNC('month', cl.churn_date)::date
    )
    SELECT
        m.month_start,
        COALESCE(ac.active_customers_at_start, 0)
            AS active_customers_at_start,
        COALESCE(mc.churned_customers, 0) AS churned_customers,
        CASE
            WHEN COALESCE(ac.active_customers_at_start, 0) = 0
                THEN NULL
            ELSE ROUND(
                100.0 * COALESCE(mc.churned_customers, 0)
                / ac.active_customers_at_start,
                2
            )
        END AS monthly_churn_rate_pct
    FROM months m
    LEFT JOIN active_at_start ac
        ON m.month_start = ac.month_start
    LEFT JOIN monthly_churn mc
        ON m.month_start = mc.month_start
    ORDER BY m.month_start;
""",

"q25_retention_by_acquisition_channel": """
    SELECT
        c.acquisition_channel,
        COUNT(*) AS total_customers,
        COUNT(*) FILTER (
            WHERE cl.churned = FALSE
        ) AS active_customers,
        COUNT(*) FILTER (
            WHERE cl.churned = TRUE
        ) AS churned_customers,
        ROUND(
            100.0 * COUNT(*) FILTER (
                WHERE cl.churned = FALSE
            ) / NULLIF(COUNT(*), 0),
            2
        ) AS retention_rate_pct
    FROM customers c
    JOIN churn_labels cl
        ON c.customer_id = cl.customer_id
    GROUP BY c.acquisition_channel
    ORDER BY retention_rate_pct DESC;
""",

"q26_customer_lifetime_spend_quartiles": """
    WITH customer_spend AS (
        SELECT
            c.customer_id,
            COALESCE(
                SUM(p.amount) FILTER (
                    WHERE LOWER(p.payment_status) = 'success'
                ),
                0
            ) AS lifetime_spend
        FROM customers c
        LEFT JOIN payments p
            ON c.customer_id = p.customer_id
        GROUP BY c.customer_id
    ),
    ranked_customers AS (
        SELECT
            customer_id,
            lifetime_spend,
            NTILE(4) OVER (
                ORDER BY lifetime_spend DESC
            ) AS spend_quartile
        FROM customer_spend
    )
    SELECT
        customer_id,
        lifetime_spend,
        spend_quartile
    FROM ranked_customers
    ORDER BY spend_quartile, lifetime_spend DESC;
""",

"q27_top3_issues_per_country": """
    WITH issue_counts AS (
        SELECT
            c.country,
            st.issue_subcategory,
            COUNT(*) AS ticket_count
        FROM support_tickets st
        JOIN customers c
            ON st.customer_id = c.customer_id
        WHERE c.country IS NOT NULL
          AND st.issue_subcategory IS NOT NULL
        GROUP BY
            c.country,
            st.issue_subcategory
    ),
    ranked_issues AS (
        SELECT
            country,
            issue_subcategory,
            ticket_count,
            ROW_NUMBER() OVER (
                PARTITION BY country
                ORDER BY ticket_count DESC, issue_subcategory
            ) AS issue_rank
        FROM issue_counts
    )
    SELECT
        country,
        issue_subcategory,
        ticket_count,
        issue_rank
    FROM ranked_issues
    WHERE issue_rank <= 3
    ORDER BY country, issue_rank;
""",

    "q28_failed_payments_high_risk": """
        SELECT
            p.customer_id,
            COUNT(*) AS failed_payment_count,
            sp.plan_name AS current_plan
        FROM payments p
        JOIN subscriptions s
            ON p.subscription_id = s.subscription_id
        JOIN subscription_plans sp
            ON s.plan_id = sp.plan_id
        WHERE LOWER(TRIM(p.payment_status)) = 'failed'
          AND p.payment_date >= CURRENT_DATE - INTERVAL '90 days'
          AND p.payment_date < CURRENT_DATE + INTERVAL '1 day'
          AND LOWER(TRIM(s.subscription_status)) = 'active'
        GROUP BY p.customer_id, sp.plan_name
        HAVING COUNT(*) >= 2
        ORDER BY failed_payment_count DESC;
    """,
        "q29_price_change_engagement": """
        WITH price_changes AS (
            SELECT
                customer_id,
                subscription_id,
                subscription_start_date,
                monthly_price,
                LAG(monthly_price) OVER (
                    PARTITION BY customer_id
                    ORDER BY subscription_start_date, subscription_id
                ) AS previous_price
            FROM subscriptions
        )
        SELECT
            COUNT(*) FILTER (
                WHERE previous_price IS NOT NULL
                  AND monthly_price <> previous_price
            ) AS price_change_events,
            COUNT(DISTINCT customer_id) FILTER (
                WHERE previous_price IS NOT NULL
                  AND monthly_price <> previous_price
            ) AS affected_customers
        FROM price_changes;
    """,
        "q30_country_churn_analysis": """
        WITH customer_base AS (
            SELECT
                c.customer_id,
                COALESCE(NULLIF(TRIM(c.country), ''), 'Unknown') AS country,
                COALESCE(cl.churned, FALSE) AS churned,
                cl.churn_date,
                COALESCE(NULLIF(TRIM(cl.churn_reason), ''), 'Unknown')
                    AS churn_reason
            FROM customers c
            LEFT JOIN churn_labels cl
                ON c.customer_id = cl.customer_id
        ),

        customer_ltv AS (
            SELECT
                cb.customer_id,
                cb.country,
                cb.churned,
                cb.churn_date,
                cb.churn_reason,
                COALESCE(SUM(p.amount), 0)::NUMERIC AS lifetime_value
            FROM customer_base cb
            LEFT JOIN payments p
                ON p.customer_id = cb.customer_id
               AND LOWER(TRIM(p.payment_status)) = 'success'
               AND (
                    cb.churned = FALSE
                    OR cb.churn_date IS NULL
                    OR p.payment_date < cb.churn_date
               )
            GROUP BY
                cb.customer_id,
                cb.country,
                cb.churned,
                cb.churn_date,
                cb.churn_reason
        ),

        country_summary AS (
            SELECT
                country,
                COUNT(*) AS total_customers,
                COUNT(*) FILTER (
                    WHERE churned = TRUE
                ) AS churned_customers,
                ROUND(
                    100.0 * COUNT(*) FILTER (WHERE churned = TRUE)
                    / NULLIF(COUNT(*), 0),
                    2
                ) AS churn_rate_pct,
                ROUND(
                    AVG(lifetime_value) FILTER (WHERE churned = TRUE),
                    2
                ) AS avg_churned_customer_ltv
            FROM customer_ltv
            GROUP BY country
        ),

        reason_counts AS (
            SELECT
                country,
                churn_reason,
                COUNT(*) AS reason_count
            FROM customer_ltv
            WHERE churned = TRUE
            GROUP BY country, churn_reason
        ),

        ranked_reasons AS (
            SELECT
                country,
                churn_reason AS top_churn_reason,
                reason_count,
                ROW_NUMBER() OVER (
                    PARTITION BY country
                    ORDER BY reason_count DESC, churn_reason
                ) AS reason_rank
            FROM reason_counts
        )

        SELECT
            cs.country,
            cs.total_customers,
            cs.churned_customers,
            cs.churn_rate_pct,
            cs.avg_churned_customer_ltv,
            COALESCE(rr.top_churn_reason, 'No churn reason recorded')
                AS top_churn_reason,
            COALESCE(rr.reason_count, 0) AS top_reason_count
        FROM country_summary cs
        LEFT JOIN ranked_reasons rr
            ON cs.country = rr.country
           AND rr.reason_rank = 1
        ORDER BY cs.churn_rate_pct DESC, cs.country;
    """,
        "q31_at_risk_revenue": """
        WITH active_customers AS (
            SELECT DISTINCT ON (s.customer_id)
                s.customer_id,
                s.subscription_id,
                sp.plan_name,
                s.monthly_price
            FROM subscriptions s
            JOIN subscription_plans sp
                ON s.plan_id = sp.plan_id
            WHERE LOWER(TRIM(s.subscription_status)) = 'active'
            ORDER BY
                s.customer_id,
                s.subscription_start_date DESC,
                s.subscription_id DESC
        ),

        last_activity AS (
            SELECT
                customer_id,
                MAX(viewing_date)::DATE AS last_viewing_date
            FROM viewing_activity
            GROUP BY customer_id
        ),

        payment_metrics AS (
            SELECT
                customer_id,
                COUNT(*) AS total_payments,
                COUNT(*) FILTER (
                    WHERE LOWER(TRIM(payment_status)) = 'failed'
                ) AS failed_payments,
                COUNT(*) FILTER (
                    WHERE LOWER(TRIM(payment_status)) = 'failed'
                )::NUMERIC / NULLIF(COUNT(*), 0) AS failed_payment_rate
            FROM payments
            GROUP BY customer_id
        ),

        support_metrics AS (
            SELECT
                customer_id,
                COUNT(*) AS support_ticket_count
            FROM support_tickets
            GROUP BY customer_id
        ),

        customer_metrics AS (
            SELECT
                a.customer_id,
                a.subscription_id,
                a.plan_name,
                a.monthly_price,
                COALESCE(
                    CURRENT_DATE - la.last_viewing_date,
                    3650
                ) AS days_since_last_activity,
                COALESCE(pm.total_payments, 0) AS total_payments,
                COALESCE(pm.failed_payments, 0) AS failed_payments,
                COALESCE(pm.failed_payment_rate, 0) AS failed_payment_rate,
                COALESCE(sm.support_ticket_count, 0) AS support_ticket_count
            FROM active_customers a
            LEFT JOIN last_activity la
                ON a.customer_id = la.customer_id
            LEFT JOIN payment_metrics pm
                ON a.customer_id = pm.customer_id
            LEFT JOIN support_metrics sm
                ON a.customer_id = sm.customer_id
        ),

        normalized_metrics AS (
            SELECT
                *,
                days_since_last_activity::NUMERIC
                    / NULLIF(MAX(days_since_last_activity) OVER (), 0)
                    AS inactivity_score,

                failed_payment_rate AS payment_risk_score,

                support_ticket_count::NUMERIC
                    / NULLIF(MAX(support_ticket_count) OVER (), 0)
                    AS support_risk_score
            FROM customer_metrics
        ),

        risk_scores AS (
            SELECT
                *,
                (
                    0.40 * COALESCE(inactivity_score, 0)
                    + 0.35 * COALESCE(payment_risk_score, 0)
                    + 0.25 * COALESCE(support_risk_score, 0)
                ) AS churn_risk_score
            FROM normalized_metrics
        ),

        ranked_customers AS (
            SELECT
                *,
                monthly_price * churn_risk_score AS at_risk_revenue,
                ROW_NUMBER() OVER (
                    ORDER BY
                        monthly_price * churn_risk_score DESC,
                        customer_id
                ) AS revenue_risk_rank
            FROM risk_scores
        )

        SELECT
            customer_id,
            subscription_id,
            plan_name,
            monthly_price,
            days_since_last_activity,
            total_payments,
            failed_payments,
            ROUND(failed_payment_rate * 100, 2)
                AS failed_payment_rate_pct,
            support_ticket_count,
            ROUND(churn_risk_score * 100, 2)
                AS churn_risk_score_pct,
            ROUND(at_risk_revenue, 2) AS at_risk_revenue,
            revenue_risk_rank
        FROM ranked_customers
        ORDER BY revenue_risk_rank
        LIMIT 50;
    """,
        "q32_top5_complaints_per_country": """
        WITH quarter_tickets AS (
            SELECT
                COALESCE(NULLIF(TRIM(c.country), ''), 'Unknown') AS country,
                COALESCE(NULLIF(TRIM(st.issue_subcategory), ''), 'Unknown')
                    AS issue_subcategory,
                st.resolution_time_hours,
                st.customer_satisfaction_score
            FROM support_tickets st
            JOIN customers c
                ON c.customer_id = st.customer_id
            WHERE st.ticket_date >=
                  DATE_TRUNC('quarter', CURRENT_DATE) - INTERVAL '3 months'
              AND st.ticket_date < DATE_TRUNC('quarter', CURRENT_DATE)
        ),
        complaint_summary AS (
            SELECT
                country,
                issue_subcategory,
                COUNT(*) AS complaint_count,
                ROUND(AVG(resolution_time_hours)::NUMERIC, 2)
                    AS avg_resolution_hours,
                ROUND(AVG(customer_satisfaction_score)::NUMERIC, 2)
                    AS avg_satisfaction_score
            FROM quarter_tickets
            GROUP BY country, issue_subcategory
        ),
        ranked AS (
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY country
                    ORDER BY complaint_count DESC, issue_subcategory
                ) AS complaint_rank
            FROM complaint_summary
        )
        SELECT *
        FROM ranked
        WHERE complaint_rank <= 5
        ORDER BY country, complaint_rank;
    """,
    "q33_winback_candidates":"""

WITH churned_customers AS (
    SELECT customer_id, churn_date, churn_reason
    FROM churn_labels
    WHERE churned = TRUE
      AND churn_date IS NOT NULL
),
lifetime_value AS (
    SELECT
        cc.customer_id,
        cc.churn_date,
        cc.churn_reason,
        COALESCE(SUM(p.amount) FILTER (
            WHERE LOWER(TRIM(p.payment_status)) = 'success'
              AND p.payment_date < cc.churn_date
        ), 0)::NUMERIC AS customer_lifetime_value
    FROM churned_customers cc
    LEFT JOIN payments p ON p.customer_id = cc.customer_id
    GROUP BY cc.customer_id, cc.churn_date, cc.churn_reason
),
quartiles AS (
    SELECT *,
        NTILE(4) OVER (
            ORDER BY customer_lifetime_value
        ) AS ltv_quartile
    FROM lifetime_value
),
engagement AS (
    SELECT
        q.customer_id,
        AVG(va.watch_duration_minutes)::NUMERIC
            AS avg_watch_minutes
    FROM quartiles q
    JOIN viewing_activity va
      ON va.customer_id = q.customer_id
     AND va.viewing_date::DATE >= q.churn_date - 30
     AND va.viewing_date::DATE < q.churn_date
    GROUP BY q.customer_id
)
SELECT
    q.customer_id,
    q.churn_date,
    q.churn_reason,
    q.customer_lifetime_value,
    q.ltv_quartile,
    COALESCE(
        CASE
            WHEN e.avg_watch_minutes >= 60 THEN 'High'
            WHEN e.avg_watch_minutes >= 20 THEN 'Medium'
            WHEN e.avg_watch_minutes IS NOT NULL THEN 'Low'
        END,
        'No recent viewing data'
    ) AS last_known_engagement_level
FROM quartiles q
LEFT JOIN engagement e ON e.customer_id = q.customer_id
WHERE q.ltv_quartile = 4
ORDER BY q.customer_lifetime_value DESC;

    """,
    "q34_plan_migration_analysis":"""

WITH subscription_history AS (
    SELECT
        s.customer_id,
        s.subscription_id,
        s.subscription_start_date,
        sp.plan_name,
        s.monthly_price,
        LAG(sp.plan_name) OVER (
            PARTITION BY s.customer_id
            ORDER BY s.subscription_start_date, s.subscription_id
        ) AS previous_plan,
        LAG(s.monthly_price) OVER (
            PARTITION BY s.customer_id
            ORDER BY s.subscription_start_date, s.subscription_id
        ) AS previous_price
    FROM subscriptions s
    JOIN subscription_plans sp ON sp.plan_id = s.plan_id
),
migrations AS (
    SELECT *,
        CASE
            WHEN monthly_price > previous_price THEN 'Upgrader'
            WHEN monthly_price < previous_price THEN 'Downgrader'
            ELSE 'Same-price migration'
        END AS migration_type,
        previous_plan || ' -> ' || plan_name AS migration_path
    FROM subscription_history
    WHERE previous_plan IS NOT NULL
),
customer_migrations AS (
    SELECT
        m.*,
        COALESCE(cl.churned, FALSE) AS churned
    FROM migrations m
    LEFT JOIN churn_labels cl ON cl.customer_id = m.customer_id
)
SELECT
    migration_path,
    migration_type,
    COUNT(*) AS migration_events,
    COUNT(DISTINCT customer_id) AS customers,
    COUNT(DISTINCT customer_id) FILTER (WHERE churned)
        AS churned_customers,
    ROUND(
        100.0 * COUNT(DISTINCT customer_id) FILTER (WHERE churned)
        / NULLIF(COUNT(DISTINCT customer_id), 0),
        2
    ) AS churn_rate_pct
FROM customer_migrations
GROUP BY migration_path, migration_type
ORDER BY migration_events DESC, migration_path;

""",
    "q35_wau_mau_stickiness":"""

WITH weekly_active AS (
    SELECT
        DATE_TRUNC('week', viewing_date)::DATE AS week_start,
        COUNT(DISTINCT customer_id) AS wau
    FROM viewing_activity
    WHERE viewing_date >=
          DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '5 months'
    GROUP BY DATE_TRUNC('week', viewing_date)::DATE
),
monthly_active AS (
    SELECT
        DATE_TRUNC('month', viewing_date)::DATE AS month_start,
        COUNT(DISTINCT customer_id) AS mau
    FROM viewing_activity
    WHERE viewing_date >=
          DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '5 months'
    GROUP BY DATE_TRUNC('month', viewing_date)::DATE
),
weekly_by_month AS (
    SELECT
        DATE_TRUNC('month', week_start)::DATE AS month_start,
        ROUND(AVG(wau)::NUMERIC, 2) AS avg_wau,
        MAX(wau) AS peak_wau
    FROM weekly_active
    GROUP BY DATE_TRUNC('month', week_start)::DATE
)
SELECT
    m.month_start,
    COALESCE(w.avg_wau, 0) AS avg_weekly_active_users,
    COALESCE(w.peak_wau, 0) AS peak_weekly_active_users,
    m.mau AS monthly_active_users,
    ROUND(
        100.0 * COALESCE(w.avg_wau, 0) / NULLIF(m.mau, 0),
        2
    ) AS wau_mau_stickiness_pct
FROM monthly_active m
LEFT JOIN weekly_by_month w ON w.month_start = m.month_start
ORDER BY m.month_start;

""",
       "q36_negative_feedback_after_payment_or_ticket": """
        WITH failed_payment_matches AS (
            SELECT DISTINCT
                cf.feedback_id
            FROM customer_feedback cf
            JOIN payments p
                ON p.customer_id = cf.customer_id
               AND LOWER(TRIM(p.payment_status)) = 'failed'
               AND cf.feedback_date >= p.payment_date
               AND cf.feedback_date < p.payment_date + INTERVAL '15 days'
        ),
        low_satisfaction_matches AS (
            SELECT DISTINCT
                cf.feedback_id
            FROM customer_feedback cf
            JOIN support_tickets st
                ON st.customer_id = cf.customer_id
               AND st.customer_satisfaction_score <= 2
               AND cf.feedback_date >= st.ticket_date
               AND cf.feedback_date < st.ticket_date + INTERVAL '15 days'
        )
        SELECT
            cf.feedback_id,
            cf.customer_id,
            cf.feedback_date,
            cf.rating,
            cf.sentiment_label,
            cf.feedback_text
        FROM customer_feedback cf
        WHERE (
            LOWER(TRIM(COALESCE(cf.sentiment_label, ''))) = 'negative'
            OR cf.rating <= 2
        )
        AND (
            cf.feedback_id IN (
                SELECT feedback_id FROM failed_payment_matches
            )
            OR cf.feedback_id IN (
                SELECT feedback_id FROM low_satisfaction_matches
            )
        )
        ORDER BY cf.feedback_date DESC, cf.customer_id;
    """,
    "q37_customer_health_score":"""

WITH active_subscriptions AS (
    SELECT DISTINCT ON (s.customer_id)
        s.customer_id,
        s.subscription_id,
        sp.plan_name,
        s.monthly_price
    FROM subscriptions s
    JOIN subscription_plans sp ON sp.plan_id = s.plan_id
    WHERE LOWER(TRIM(s.subscription_status)) = 'active'
    ORDER BY
        s.customer_id,
        s.subscription_start_date DESC,
        s.subscription_id
),
last_viewing AS (
    SELECT
        customer_id,
        MAX(viewing_date)::DATE AS last_viewing_date
    FROM viewing_activity
    GROUP BY customer_id
),
payment_stats AS (
    SELECT
        customer_id,
        COUNT(*) AS payment_count,
        COUNT(*) FILTER (
            WHERE LOWER(TRIM(payment_status)) = 'failed'
        ) AS failed_payment_count,
        COUNT(*) FILTER (
            WHERE LOWER(TRIM(payment_status)) = 'failed'
        )::NUMERIC / NULLIF(COUNT(*), 0) AS failure_rate
    FROM payments
    GROUP BY customer_id
),
support_stats AS (
    SELECT
        customer_id,
        AVG(customer_satisfaction_score)::NUMERIC AS avg_satisfaction
    FROM support_tickets
    WHERE customer_satisfaction_score IS NOT NULL
    GROUP BY customer_id
),
base AS (
    SELECT
        a.customer_id,
        a.subscription_id,
        a.plan_name AS current_plan,
        a.monthly_price,
        lv.last_viewing_date,
        COALESCE(CURRENT_DATE - lv.last_viewing_date, 3650)
            AS days_since_last_viewing,
        COALESCE(ps.payment_count, 0) AS payment_count,
        COALESCE(ps.failed_payment_count, 0)
            AS failed_payment_count,
        COALESCE(ps.failure_rate, 0) AS failure_rate,
        ss.avg_satisfaction,
        GREATEST(CURRENT_DATE - c.registration_date::DATE, 0)
            AS tenure_days
    FROM active_subscriptions a
    JOIN customers c ON c.customer_id = a.customer_id
    LEFT JOIN last_viewing lv ON lv.customer_id = a.customer_id
    LEFT JOIN payment_stats ps ON ps.customer_id = a.customer_id
    LEFT JOIN support_stats ss ON ss.customer_id = a.customer_id
),
normalized AS (
    SELECT *,
        days_since_last_viewing::NUMERIC
            / NULLIF(MAX(days_since_last_viewing) OVER (), 0)
            AS inactivity_score,
        COALESCE(failure_rate, 0) AS payment_risk_score,
        CASE
            WHEN avg_satisfaction IS NULL THEN 0.5
            ELSE (5 - avg_satisfaction) / 4.0
        END AS support_risk_score,
        1 - (
            tenure_days::NUMERIC
            / NULLIF(MAX(tenure_days) OVER (), 0)
        ) AS short_tenure_score
    FROM base
),
scored AS (
    SELECT *,
        100 * (
            0.30 * COALESCE(inactivity_score, 0)
            + 0.30 * COALESCE(payment_risk_score, 0)
            + 0.25 * COALESCE(support_risk_score, 0)
            + 0.15 * COALESCE(short_tenure_score, 0)
        ) AS customer_health_risk_score
    FROM normalized
)
SELECT
    customer_id,
    subscription_id,
    current_plan,
    monthly_price,
    last_viewing_date,
    days_since_last_viewing,
    payment_count,
    failed_payment_count,
    ROUND(failure_rate * 100, 2) AS failed_payment_rate_pct,
    ROUND(avg_satisfaction, 2) AS avg_support_satisfaction,
    tenure_days,
    ROUND(customer_health_risk_score, 2)
        AS customer_health_risk_score
FROM scored
ORDER BY customer_health_risk_score DESC, customer_id;

""",
    




 





    "churn_by_country": """
        SELECT
            c.country,
            COUNT(*) AS customers,
            SUM(
                CASE WHEN cl.churned = TRUE THEN 1 ELSE 0 END
            ) AS churned_customers,
            ROUND(
                100.0 *
                SUM(CASE WHEN cl.churned = TRUE THEN 1 ELSE 0 END)
                / COUNT(*),
                2
            ) AS churn_rate
        FROM customers c
        JOIN churn_labels cl
            ON c.customer_id = cl.customer_id
        GROUP BY c.country
        ORDER BY churn_rate DESC;
    """
    
    
}


# ==========================================
# RUN QUERY
# ==========================================

def run_query(query_name):

    if query_name not in QUERIES:

        print(f"Unknown query: {query_name}")
        return None

    query = QUERIES[query_name]

    with engine.connect() as connection:

        result = connection.execute(
            text(query)
        )

        rows = result.mappings().all()

    return rows


# ==========================================
# TEST
# ==========================================





if __name__ == "__main__":
    for query_name in QUERIES:
        print(f"\nRunning: {query_name}")
        result = run_query(query_name)
        for row in result:
            print(row)



