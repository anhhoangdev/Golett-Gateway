# 🌾 Farm Data Management System

A comprehensive PostgreSQL-based data management system for farm operations, designed to handle daily reporting, metrics tracking, and data analysis across multiple departments and production facilities.

## 📊 Overview

This system processes and normalizes farm data from 11 different departments:
- **Production Units**: Viet Farm, Sun Wind, VNCC, Mui Dinh
- **Business Units**: Financial/Accounting, HR, Legal, Procurement, R&D, International B2B, Local B2B

## 🏗️ Database Schema

### Core Tables
- **`companies`** - Master table for departments and facilities
- **`daily_reports`** - Central reporting table linking all daily data
- **`financial_metrics`** - Financial and accounting data
- **`production_metrics`** - Production volumes, efficiency, and quality metrics
- **`hr_metrics`** - Human resources KPIs and metrics
- **`legal_metrics`** - Legal compliance and contract management
- **`procurement_metrics`** - Supply chain and procurement data
- **`sales_metrics`** - B2B sales performance (international and local)
- **`rnd_metrics`** - Research and development metrics

### Support Tables
- **`metric_types`** - Lookup table for metric categorization
- **`issues_log`** - Daily issues and problem tracking

### Views
- **`daily_summary`** - Overview of all daily reports
- **`production_summary`** - Production metrics summary
- **`financial_summary`** - Financial metrics overview

## 🚀 Quick Start

### Prerequisites
```bash
# Install required packages
pip install pandas psycopg2-binary

# Ensure PostgreSQL is running
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS
```

### Setup Process

1. **Prepare Your Data**
   ```bash
   # Run data preprocessing (if not already done)
   python data_preprocessing.py
   ```

2. **Setup Database**
   ```bash
   # Create database and schema
   python setup_database.py
   ```

3. **Import Data**
   ```bash
   # Import processed CSV data
   python import_data.py
   ```

### Configuration

Update database credentials in the setup scripts:

```python
# In setup_database.py and import_data.py
db_config = {
    'host': 'localhost',
    'database': 'farm_data',
    'user': 'postgres',
    'password': 'your_password',
    'port': 5432
}
```

## 📈 Data Structure

### Companies Table
```sql
CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    company_code VARCHAR(20) UNIQUE NOT NULL,
    department_type VARCHAR(50) NOT NULL
);
```

### Daily Reports Table
```sql
CREATE TABLE daily_reports (
    report_id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(company_id),
    report_date DATE NOT NULL,
    created_date DATE,
    report_type VARCHAR(50) NOT NULL
);
```

### Production Metrics Table
```sql
CREATE TABLE production_metrics (
    metric_id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES daily_reports(report_id),
    company_code VARCHAR(20) NOT NULL,
    raw_material_volume DECIMAL(12,2),
    finished_product_volume DECIMAL(12,2),
    efficiency_cut DECIMAL(5,2),
    efficiency_aseptic DECIMAL(5,2),
    error_rate DECIMAL(5,4),
    direct_labor_count INTEGER,
    indirect_labor_count INTEGER
    -- ... additional production metrics
);
```

## 🔍 Sample Queries

### Basic Data Exploration

```sql
-- View all companies and their types
SELECT company_name, company_code, department_type 
FROM companies 
ORDER BY department_type, company_name;

-- Check data coverage by date range
SELECT 
    MIN(report_date) as earliest_date,
    MAX(report_date) as latest_date,
    COUNT(*) as total_reports
FROM daily_reports;

-- Reports by department type
SELECT 
    c.department_type,
    COUNT(*) as report_count,
    MIN(dr.report_date) as first_report,
    MAX(dr.report_date) as last_report
FROM daily_reports dr
JOIN companies c ON dr.company_id = c.company_id
GROUP BY c.department_type
ORDER BY report_count DESC;
```

### Production Analysis

```sql
-- Daily production summary for all facilities
SELECT 
    report_date,
    company_name,
    raw_material_volume,
    finished_product_volume,
    efficiency_cut,
    efficiency_aseptic,
    direct_labor_count + indirect_labor_count as total_workers
FROM production_summary
WHERE report_date >= '2025-01-01'
ORDER BY report_date DESC, company_name;

-- Production efficiency trends
SELECT 
    company_code,
    DATE_TRUNC('week', ps.report_date) as week,
    AVG(efficiency_cut) as avg_efficiency_cut,
    AVG(efficiency_aseptic) as avg_efficiency_aseptic,
    AVG(error_rate) as avg_error_rate
FROM production_summary ps
WHERE report_date >= '2025-01-01'
GROUP BY company_code, DATE_TRUNC('week', ps.report_date)
ORDER BY week DESC, company_code;

-- Top performing production days
SELECT 
    report_date,
    company_name,
    finished_product_volume,
    efficiency_cut,
    efficiency_aseptic
FROM production_summary
WHERE finished_product_volume > 0
ORDER BY finished_product_volume DESC
LIMIT 10;
```

### Financial Analysis

```sql
-- Daily financial overview
SELECT 
    report_date,
    bank_inflow,
    bank_outflow,
    cash_balance,
    debt_ratio,
    energy_cost,
    material_cost
FROM financial_summary
WHERE report_date >= '2025-01-01'
ORDER BY report_date DESC;

-- Monthly financial aggregation
SELECT 
    DATE_TRUNC('month', report_date) as month,
    SUM(bank_inflow) as total_inflow,
    SUM(bank_outflow) as total_outflow,
    AVG(cash_balance) as avg_cash_balance,
    AVG(debt_ratio) as avg_debt_ratio
FROM financial_summary
GROUP BY DATE_TRUNC('month', report_date)
ORDER BY month DESC;
```

### HR Analysis

```sql
-- HR metrics overview
SELECT 
    dr.report_date,
    hr.total_employees,
    hr.new_hires,
    hr.late_employees,
    hr.absent_employees,
    hr.training_sessions,
    hr.training_participants
FROM daily_reports dr
JOIN hr_metrics hr ON dr.report_id = hr.report_id
JOIN companies c ON dr.company_id = c.company_id
WHERE c.company_code = 'NS'
ORDER BY dr.report_date DESC;

-- Employee attendance trends
SELECT 
    DATE_TRUNC('week', dr.report_date) as week,
    AVG(hr.total_employees) as avg_employees,
    AVG(CASE WHEN hr.total_employees > 0 
        THEN (hr.late_employees::float / hr.total_employees) * 100 
        ELSE 0 END) as late_percentage,
    AVG(CASE WHEN hr.total_employees > 0 
        THEN (hr.absent_employees::float / hr.total_employees) * 100 
        ELSE 0 END) as absent_percentage
FROM daily_reports dr
JOIN hr_metrics hr ON dr.report_id = hr.report_id
JOIN companies c ON dr.company_id = c.company_id
WHERE c.company_code = 'NS'
GROUP BY DATE_TRUNC('week', dr.report_date)
ORDER BY week DESC;
```

### Cross-Department Analysis

```sql
-- Daily operations dashboard
SELECT 
    dr.report_date,
    -- Production metrics
    SUM(pm.finished_product_volume) as total_production,
    AVG(pm.efficiency_cut) as avg_efficiency,
    SUM(pm.direct_labor_count + pm.indirect_labor_count) as total_production_workers,
    -- Financial metrics
    MAX(fm.cash_balance) as cash_balance,
    MAX(fm.debt_ratio) as debt_ratio,
    -- HR metrics
    MAX(hr.total_employees) as total_employees
FROM daily_reports dr
LEFT JOIN production_metrics pm ON dr.report_id = pm.report_id
LEFT JOIN financial_metrics fm ON dr.report_id = fm.report_id
LEFT JOIN hr_metrics hr ON dr.report_id = hr.report_id
WHERE dr.report_date >= '2025-01-01'
GROUP BY dr.report_date
ORDER BY dr.report_date DESC;

-- Performance correlation analysis
WITH daily_stats AS (
    SELECT 
        dr.report_date,
        SUM(pm.finished_product_volume) as daily_production,
        AVG(pm.efficiency_cut) as avg_efficiency,
        MAX(fm.energy_cost) as energy_cost,
        MAX(hr.total_employees) as workforce_size
    FROM daily_reports dr
    LEFT JOIN production_metrics pm ON dr.report_id = pm.report_id
    LEFT JOIN financial_metrics fm ON dr.report_id = fm.report_id
    LEFT JOIN hr_metrics hr ON dr.report_id = hr.report_id
    WHERE dr.report_date >= '2025-01-01'
    GROUP BY dr.report_date
)
SELECT 
    report_date,
    daily_production,
    avg_efficiency,
    energy_cost,
    workforce_size,
    CASE 
        WHEN daily_production > 0 AND workforce_size > 0 
        THEN daily_production / workforce_size 
        ELSE 0 
    END as productivity_per_worker
FROM daily_stats
WHERE daily_production > 0
ORDER BY productivity_per_worker DESC;
```

## 📊 Data Quality Features

### Duplicate Removal
- Automatic detection and removal of duplicate records
- Date-based deduplication keeping the latest entries

### Data Validation
- Foreign key constraints ensure data integrity
- Check constraints for valid status values
- Automatic timestamp tracking for audit trails

### Error Handling
- Comprehensive logging for import processes
- Data validation with detailed error reporting
- Rollback capabilities for failed imports

## 🔧 Maintenance

### Regular Tasks

```sql
-- Check data freshness
SELECT 
    c.company_name,
    MAX(dr.report_date) as last_report_date,
    COUNT(*) as total_reports
FROM companies c
LEFT JOIN daily_reports dr ON c.company_id = dr.company_id
GROUP BY c.company_id, c.company_name
ORDER BY last_report_date DESC;

-- Identify data gaps
SELECT 
    company_code,
    report_date,
    LAG(report_date) OVER (PARTITION BY company_code ORDER BY report_date) as prev_date,
    report_date - LAG(report_date) OVER (PARTITION BY company_code ORDER BY report_date) as gap_days
FROM daily_summary
WHERE report_date >= '2025-01-01'
HAVING report_date - LAG(report_date) OVER (PARTITION BY company_code ORDER BY report_date) > 1
ORDER BY company_code, report_date;
```

### Performance Optimization

```sql
-- Analyze table statistics
ANALYZE companies;
ANALYZE daily_reports;
ANALYZE production_metrics;
ANALYZE financial_metrics;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## 🔒 Security Considerations

1. **User Management**: Create specific database users with limited permissions
2. **Data Encryption**: Enable encryption at rest and in transit
3. **Backup Strategy**: Implement regular automated backups
4. **Access Logging**: Monitor database access and modifications

## 📝 File Structure

```
farm_data/
├── raw_data/                    # Original TSV files
├── processed_data/              # Cleaned CSV files
├── data_analysis.py            # Data quality analysis
├── data_preprocessing.py       # Data cleaning and normalization
├── create_database_schema.sql  # PostgreSQL schema
├── setup_database.py          # Database creation script
├── import_data.py             # Data import script
├── README.md                  # This documentation
└── logs/                      # Processing logs
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the logs in the `logs/` directory
2. Verify database connectivity and permissions
3. Ensure all prerequisites are installed
4. Review the sample queries for usage examples

---

**Happy farming! 🌱** 