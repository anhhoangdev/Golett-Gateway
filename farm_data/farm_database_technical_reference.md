# Farm Database Technical Reference

## Quick Reference for LLMs

This document provides practical SQL examples and patterns for working with the Farm Data Management System database.

## Database Connection

```sql
-- Database: farm_data_management
-- Schema: public (default)
-- Required Extensions: uuid-ossp
-- Character Set: UTF-8
```

## Table Relationships

```
companies (1) ←→ (many) daily_reports (1) ←→ (many) [metrics_tables]
                                      ↓
                                 issues_log
```

## Common Query Patterns

### 1. Daily Operations Dashboard

```sql
-- Get today's metrics across all departments
SELECT 
    c.company_name,
    c.department_type,
    dr.report_date,
    CASE 
        WHEN c.department_type = 'Finance' THEN 'Financial Data Available'
        WHEN c.department_type = 'Production' THEN 'Production Data Available'
        WHEN c.department_type = 'HR' THEN 'HR Data Available'
        ELSE 'Other Data Available'
    END as data_status
FROM companies c
JOIN daily_reports dr ON c.company_id = dr.company_id
WHERE dr.report_date = CURRENT_DATE
ORDER BY c.department_type, c.company_name;
```

### 2. Production Performance Analysis

```sql
-- Production efficiency trends over last 30 days
SELECT 
    dr.report_date,
    c.company_name,
    pm.efficiency_cut,
    pm.efficiency_aseptic,
    pm.error_rate,
    pm.finished_product_volume,
    pm.downtime_minutes
FROM daily_reports dr
JOIN companies c ON dr.company_id = c.company_id
JOIN production_metrics pm ON dr.report_id = pm.report_id
WHERE dr.report_date >= CURRENT_DATE - INTERVAL '30 days'
    AND c.department_type = 'Production'
ORDER BY dr.report_date DESC, c.company_name;
```

### 3. Financial Summary

```sql
-- Monthly financial overview
SELECT 
    DATE_TRUNC('month', dr.report_date) as month,
    SUM(fm.bank_inflow) as total_inflow,
    SUM(fm.bank_outflow) as total_outflow,
    SUM(fm.bank_inflow - fm.bank_outflow) as net_flow,
    AVG(fm.debt_ratio) as avg_debt_ratio,
    SUM(fm.leaf_revenue + fm.seedling_revenue) as total_revenue
FROM daily_reports dr
JOIN financial_metrics fm ON dr.report_id = fm.report_id
WHERE dr.report_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '6 months'
GROUP BY DATE_TRUNC('month', dr.report_date)
ORDER BY month DESC;
```

### 4. Cross-Department KPI Dashboard

```sql
-- Key metrics from all departments for a specific date
WITH daily_kpis AS (
    SELECT 
        dr.report_date,
        c.company_name,
        c.department_type,
        -- Financial KPIs
        fm.bank_inflow,
        fm.cash_balance,
        -- Production KPIs
        pm.finished_product_volume,
        pm.efficiency_cut,
        -- HR KPIs
        hm.total_employees,
        hm.absent_employees,
        -- Sales KPIs
        sm.total_revenue as sales_revenue,
        sm.new_customers
    FROM daily_reports dr
    JOIN companies c ON dr.company_id = c.company_id
    LEFT JOIN financial_metrics fm ON dr.report_id = fm.report_id
    LEFT JOIN production_metrics pm ON dr.report_id = pm.report_id
    LEFT JOIN hr_metrics hm ON dr.report_id = hm.report_id
    LEFT JOIN sales_metrics sm ON dr.report_id = sm.report_id
    WHERE dr.report_date = '2024-01-15'  -- Replace with desired date
)
SELECT * FROM daily_kpis
ORDER BY department_type, company_name;
```

### 5. Issue Tracking and Resolution

```sql
-- Active issues by severity and department
SELECT 
    c.department_type,
    c.company_name,
    il.severity,
    COUNT(*) as issue_count,
    AVG(EXTRACT(days FROM (COALESCE(il.resolved_at, CURRENT_TIMESTAMP) - il.created_at))) as avg_resolution_days
FROM issues_log il
JOIN companies c ON il.company_id = c.company_id
WHERE il.status IN ('open', 'in_progress')
GROUP BY c.department_type, c.company_name, il.severity
ORDER BY 
    CASE il.severity 
        WHEN 'critical' THEN 1 
        WHEN 'high' THEN 2 
        WHEN 'medium' THEN 3 
        WHEN 'low' THEN 4 
    END,
    issue_count DESC;
```

## Data Insertion Patterns

### 1. Adding a New Company/Department

```sql
INSERT INTO companies (company_name, company_code, department_type)
VALUES ('New Production Unit', 'NPU', 'Production')
RETURNING company_id;
```

### 2. Creating Daily Report Entry

```sql
-- Insert daily report
INSERT INTO daily_reports (company_id, report_date, created_date, report_type)
VALUES (1, '2024-01-15', '2024-01-15', 'daily_operations')
RETURNING report_id;

-- Insert corresponding metrics (example for production)
INSERT INTO production_metrics (
    report_id, company_code, raw_material_volume, 
    finished_product_volume, efficiency_cut, direct_labor_count
)
VALUES (
    123, 'VIET_FARM', 1500.50, 1200.75, 85.5, 25
);
```

### 3. Logging Issues

```sql
INSERT INTO issues_log (
    report_id, company_id, issue_description, 
    severity, status, assigned_to
)
VALUES (
    123, 1, 'Equipment malfunction in production line 2', 
    'high', 'open', 'maintenance_team'
);
```

## Data Analysis Queries

### 1. Trend Analysis

```sql
-- Production efficiency trends with moving averages
SELECT 
    dr.report_date,
    c.company_name,
    pm.efficiency_cut,
    AVG(pm.efficiency_cut) OVER (
        PARTITION BY c.company_id 
        ORDER BY dr.report_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as efficiency_7day_avg
FROM daily_reports dr
JOIN companies c ON dr.company_id = c.company_id
JOIN production_metrics pm ON dr.report_id = pm.report_id
WHERE c.department_type = 'Production'
    AND dr.report_date >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY c.company_name, dr.report_date;
```

### 2. Performance Benchmarking

```sql
-- Compare department performance against averages
WITH dept_averages AS (
    SELECT 
        c.department_type,
        AVG(pm.efficiency_cut) as avg_efficiency,
        AVG(pm.error_rate) as avg_error_rate
    FROM daily_reports dr
    JOIN companies c ON dr.company_id = c.company_id
    JOIN production_metrics pm ON dr.report_id = pm.report_id
    WHERE dr.report_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY c.department_type
)
SELECT 
    c.company_name,
    pm.efficiency_cut,
    da.avg_efficiency,
    pm.efficiency_cut - da.avg_efficiency as efficiency_variance,
    pm.error_rate,
    da.avg_error_rate,
    pm.error_rate - da.avg_error_rate as error_variance
FROM daily_reports dr
JOIN companies c ON dr.company_id = c.company_id
JOIN production_metrics pm ON dr.report_id = pm.report_id
JOIN dept_averages da ON c.department_type = da.department_type
WHERE dr.report_date = CURRENT_DATE - INTERVAL '1 day';
```

### 3. Resource Utilization

```sql
-- Labor utilization across production facilities
SELECT 
    c.company_name,
    dr.report_date,
    pm.direct_labor_count,
    pm.indirect_labor_count,
    pm.direct_labor_count + pm.indirect_labor_count as total_labor,
    pm.finished_product_volume,
    CASE 
        WHEN pm.direct_labor_count + pm.indirect_labor_count > 0 
        THEN pm.finished_product_volume / (pm.direct_labor_count + pm.indirect_labor_count)
        ELSE 0 
    END as productivity_per_worker
FROM daily_reports dr
JOIN companies c ON dr.company_id = c.company_id
JOIN production_metrics pm ON dr.report_id = pm.report_id
WHERE c.department_type = 'Production'
    AND dr.report_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY dr.report_date DESC, productivity_per_worker DESC;
```

## Reporting Views Usage

### 1. Using Built-in Views

```sql
-- Daily summary for executive dashboard
SELECT * FROM daily_summary 
WHERE report_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY report_date DESC, department_type;

-- Production performance overview
SELECT * FROM production_summary 
WHERE report_date = CURRENT_DATE - INTERVAL '1 day'
ORDER BY efficiency_cut DESC;

-- Financial overview
SELECT * FROM financial_summary 
WHERE report_date >= DATE_TRUNC('month', CURRENT_DATE)
ORDER BY report_date DESC;
```

### 2. Custom Aggregation Views

```sql
-- Create custom view for weekly summaries
CREATE VIEW weekly_production_summary AS
SELECT 
    DATE_TRUNC('week', dr.report_date) as week_start,
    c.company_name,
    AVG(pm.efficiency_cut) as avg_efficiency,
    SUM(pm.finished_product_volume) as total_production,
    AVG(pm.error_rate) as avg_error_rate,
    SUM(pm.downtime_minutes) as total_downtime
FROM daily_reports dr
JOIN companies c ON dr.company_id = c.company_id
JOIN production_metrics pm ON dr.report_id = pm.report_id
WHERE c.department_type = 'Production'
GROUP BY DATE_TRUNC('week', dr.report_date), c.company_name;
```

## Data Validation Queries

### 1. Data Quality Checks

```sql
-- Check for missing daily reports
SELECT 
    c.company_name,
    generate_series(
        CURRENT_DATE - INTERVAL '30 days',
        CURRENT_DATE - INTERVAL '1 day',
        INTERVAL '1 day'
    )::date as expected_date
FROM companies c
WHERE NOT EXISTS (
    SELECT 1 FROM daily_reports dr 
    WHERE dr.company_id = c.company_id 
    AND dr.report_date = generate_series::date
);

-- Identify outliers in production data
SELECT 
    c.company_name,
    dr.report_date,
    pm.efficiency_cut,
    pm.error_rate
FROM daily_reports dr
JOIN companies c ON dr.company_id = c.company_id
JOIN production_metrics pm ON dr.report_id = pm.report_id
WHERE pm.efficiency_cut > 100 OR pm.efficiency_cut < 0
   OR pm.error_rate > 50 OR pm.error_rate < 0;
```

### 2. Consistency Checks

```sql
-- Verify referential integrity
SELECT 'Orphaned financial metrics' as issue, COUNT(*) as count
FROM financial_metrics fm
LEFT JOIN daily_reports dr ON fm.report_id = dr.report_id
WHERE dr.report_id IS NULL

UNION ALL

SELECT 'Reports without companies' as issue, COUNT(*) as count
FROM daily_reports dr
LEFT JOIN companies c ON dr.company_id = c.company_id
WHERE c.company_id IS NULL;
```

## Performance Optimization

### 1. Index Usage Verification

```sql
-- Check index usage for common queries
EXPLAIN (ANALYZE, BUFFERS) 
SELECT c.company_name, dr.report_date, pm.efficiency_cut
FROM daily_reports dr
JOIN companies c ON dr.company_id = c.company_id
JOIN production_metrics pm ON dr.report_id = pm.report_id
WHERE dr.report_date >= CURRENT_DATE - INTERVAL '30 days'
    AND c.department_type = 'Production';
```

### 2. Table Statistics

```sql
-- Get table sizes and row counts
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public' 
    AND tablename IN ('daily_reports', 'companies', 'production_metrics')
ORDER BY tablename, attname;
```

## Common Data Patterns

### 1. Vietnamese Date Handling

```sql
-- Handle Excel serial dates (if still present in data)
SELECT 
    report_date,
    CASE 
        WHEN report_date::text ~ '^\d{5}$' 
        THEN ('1900-01-01'::date + (report_date::text::integer - 2)::integer)::date
        ELSE report_date
    END as corrected_date
FROM daily_reports;
```

### 2. Numeric Data Cleaning

```sql
-- Clean numeric fields with commas or parentheses
UPDATE financial_metrics 
SET bank_inflow = REPLACE(REPLACE(bank_inflow::text, ',', ''), '(', '-')::decimal
WHERE bank_inflow::text LIKE '%,%' OR bank_inflow::text LIKE '%(%';
```

### 3. Text Processing for Issues

```sql
-- Extract and categorize issues
SELECT 
    issue_description,
    CASE 
        WHEN issue_description ILIKE '%equipment%' OR issue_description ILIKE '%máy%' THEN 'Equipment'
        WHEN issue_description ILIKE '%quality%' OR issue_description ILIKE '%chất lượng%' THEN 'Quality'
        WHEN issue_description ILIKE '%delay%' OR issue_description ILIKE '%trễ%' THEN 'Scheduling'
        ELSE 'Other'
    END as issue_category
FROM issues_log;
```

## API Integration Patterns

### 1. REST API Endpoints (Conceptual)

```sql
-- GET /api/companies
SELECT company_id, company_name, company_code, department_type FROM companies;

-- GET /api/reports/daily/{date}
SELECT * FROM daily_summary WHERE report_date = $1;

-- GET /api/metrics/production/{company_id}/{start_date}/{end_date}
SELECT dr.report_date, pm.* 
FROM daily_reports dr
JOIN production_metrics pm ON dr.report_id = pm.report_id
WHERE dr.company_id = $1 AND dr.report_date BETWEEN $2 AND $3;
```

### 2. Bulk Data Operations

```sql
-- Bulk insert pattern for daily data
WITH new_reports AS (
    INSERT INTO daily_reports (company_id, report_date, created_date, report_type)
    SELECT company_id, $1, $2, 'daily_operations'
    FROM companies
    WHERE department_type = 'Production'
    RETURNING report_id, company_id
)
INSERT INTO production_metrics (report_id, company_code, raw_material_volume, finished_product_volume)
SELECT nr.report_id, c.company_code, $3, $4
FROM new_reports nr
JOIN companies c ON nr.company_id = c.company_id;
```

## Maintenance Queries

### 1. Regular Cleanup

```sql
-- Archive old data (example: move data older than 2 years)
CREATE TABLE daily_reports_archive AS
SELECT * FROM daily_reports 
WHERE report_date < CURRENT_DATE - INTERVAL '2 years';

DELETE FROM daily_reports 
WHERE report_date < CURRENT_DATE - INTERVAL '2 years';
```

### 2. Performance Maintenance

```sql
-- Update table statistics
ANALYZE companies;
ANALYZE daily_reports;
ANALYZE production_metrics;
ANALYZE financial_metrics;

-- Reindex for performance
REINDEX TABLE daily_reports;
REINDEX TABLE production_metrics;
```

This technical reference provides practical examples for working with the Farm Data Management System database. Use these patterns as templates for building queries, reports, and integrations. 