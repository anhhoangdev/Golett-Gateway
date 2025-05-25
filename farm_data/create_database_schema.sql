-- Farm Data Management System - PostgreSQL Schema
-- Created for normalized farm data from 11 departments
-- Supports daily reporting, metrics tracking, and data analysis

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS issues_log CASCADE;
DROP TABLE IF EXISTS financial_metrics CASCADE;
DROP TABLE IF EXISTS production_metrics CASCADE;
DROP TABLE IF EXISTS hr_metrics CASCADE;
DROP TABLE IF EXISTS legal_metrics CASCADE;
DROP TABLE IF EXISTS procurement_metrics CASCADE;
DROP TABLE IF EXISTS sales_metrics CASCADE;
DROP TABLE IF EXISTS rnd_metrics CASCADE;
DROP TABLE IF EXISTS daily_reports CASCADE;
DROP TABLE IF EXISTS companies CASCADE;
DROP TABLE IF EXISTS metric_types CASCADE;

-- Create extension for UUID generation if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Companies/Departments table
CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    company_code VARCHAR(20) UNIQUE NOT NULL,
    department_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily reports table (central reporting table)
CREATE TABLE daily_reports (
    report_id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(company_id),
    report_date DATE NOT NULL,
    created_date DATE,
    report_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, report_date, report_type)
);

-- ============================================================================
-- METRICS TABLES
-- ============================================================================

-- Financial metrics (from tai_chinh_ke_toan)
CREATE TABLE financial_metrics (
    metric_id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES daily_reports(report_id),
    bank_inflow DECIMAL(15,2),
    bank_outflow DECIMAL(15,2),
    cash_balance DECIMAL(15,2),
    debt_ratio DECIMAL(5,2),
    management_cost DECIMAL(15,2),
    energy_cost DECIMAL(15,2),
    labor_cost_cut DECIMAL(15,2),
    labor_cost_aseptic DECIMAL(15,2),
    material_cost DECIMAL(15,2),
    bank_inflow_2 DECIMAL(15,2),
    bank_outflow_2 DECIMAL(15,2),
    cash_balance_2 DECIMAL(15,2),
    material_cost_2 DECIMAL(15,2),
    bank_inflow_3 DECIMAL(15,2),
    bank_outflow_3 DECIMAL(15,2),
    cash_balance_3 DECIMAL(15,2),
    labor_cost DECIMAL(15,2),
    leaf_revenue DECIMAL(15,2),
    seedling_revenue DECIMAL(15,2),
    fertilizer_cost DECIMAL(15,2),
    material_cost_3 DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Production metrics (from viet_farm, sun_wind, vncc, mui_dinh)
CREATE TABLE production_metrics (
    metric_id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES daily_reports(report_id),
    company_code VARCHAR(20) NOT NULL,
    raw_material_volume DECIMAL(15,2),
    finished_product_volume DECIMAL(15,2),
    product_10kg_volume DECIMAL(15,2),
    product_5kg_volume DECIMAL(15,2),
    product_small_volume DECIMAL(15,2),
    aseptic_volume DECIMAL(15,2),
    total_consumption DECIMAL(15,2),
    consumption_kdqt DECIMAL(15,2),
    consumption_kdnd DECIMAL(15,2),
    consumption_b2c DECIMAL(15,2),
    efficiency_cut DECIMAL(10,2),
    efficiency_aseptic DECIMAL(10,2),
    error_rate DECIMAL(8,4),
    complaint_rate DECIMAL(8,4),
    direct_labor_count INTEGER,
    indirect_labor_count INTEGER,
    aloe_seedling_a1_count INTEGER,
    aloe_seedling_sa01_count INTEGER,
    cluster_production_count INTEGER,
    downtime_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- HR metrics (from nhan_su)
CREATE TABLE hr_metrics (
    metric_id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES daily_reports(report_id),
    applications_received INTEGER,
    interviews_completed INTEGER,
    new_hires INTEGER,
    total_employees INTEGER,
    late_employees INTEGER,
    absent_employees INTEGER,
    overtime_employees INTEGER,
    training_sessions INTEGER,
    training_participants INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Legal metrics (from phap_ly)
CREATE TABLE legal_metrics (
    metric_id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES daily_reports(report_id),
    contracts_under_review INTEGER,
    contract_amendments_review INTEGER,
    new_contracts_stored INTEGER,
    new_contracts_received INTEGER,
    contracts_need_negotiation INTEGER,
    contract_disputes INTEGER,
    compliance_rate DECIMAL(5,2),
    regulatory_warnings INTEGER,
    legal_consultation_hours DECIMAL(5,2),
    document_processing_count INTEGER,
    legal_training_sessions INTEGER,
    policy_updates INTEGER,
    audit_findings INTEGER,
    risk_assessments INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Procurement metrics (from thu_mua_cung_ung)
CREATE TABLE procurement_metrics (
    metric_id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES daily_reports(report_id),
    total_suppliers INTEGER,
    main_suppliers INTEGER,
    evaluated_suppliers INTEGER,
    planned_orders INTEGER,
    new_planned_orders INTEGER,
    emergency_orders INTEGER,
    on_time_deliveries INTEGER,
    late_deliveries INTEGER,
    returned_items INTEGER,
    cost_savings DECIMAL(15,2),
    total_procurement_cost DECIMAL(15,2),
    supplier_performance_score DECIMAL(5,2),
    quality_issues INTEGER,
    delivery_performance DECIMAL(5,2),
    price_variance DECIMAL(15,2),
    inventory_turnover DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sales metrics (from inter_b2b, local_b2b)
CREATE TABLE sales_metrics (
    metric_id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES daily_reports(report_id),
    sales_channel VARCHAR(20) NOT NULL, -- 'inter_b2b' or 'local_b2b'
    total_revenue DECIMAL(15,2),
    total_orders INTEGER,
    new_customers INTEGER,
    customer_visits INTEGER,
    quotations_sent INTEGER,
    contracts_signed INTEGER,
    payment_received DECIMAL(15,2),
    outstanding_receivables DECIMAL(15,2),
    customer_complaints INTEGER,
    market_share DECIMAL(5,2),
    sales_target_achievement DECIMAL(5,2),
    average_order_value DECIMAL(15,2),
    customer_retention_rate DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- R&D metrics (from rnd)
CREATE TABLE rnd_metrics (
    metric_id SERIAL PRIMARY KEY,
    report_id INTEGER NOT NULL REFERENCES daily_reports(report_id),
    research_projects INTEGER,
    experiments_conducted INTEGER,
    samples_tested INTEGER,
    quality_tests INTEGER,
    new_formulations INTEGER,
    patent_applications INTEGER,
    research_hours DECIMAL(8,2),
    equipment_utilization DECIMAL(5,2),
    research_budget_used DECIMAL(15,2),
    collaboration_meetings INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- LOOKUP AND SUPPORT TABLES
-- ============================================================================

-- Metric types for categorization
CREATE TABLE metric_types (
    type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    unit VARCHAR(20),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Issues log for tracking daily problems
CREATE TABLE issues_log (
    issue_id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES daily_reports(report_id),
    company_id INTEGER REFERENCES companies(company_id),
    issue_description TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    assigned_to VARCHAR(100),
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Primary indexes on foreign keys
CREATE INDEX idx_daily_reports_company_id ON daily_reports(company_id);
CREATE INDEX idx_daily_reports_date ON daily_reports(report_date);
CREATE INDEX idx_daily_reports_type ON daily_reports(report_type);

-- Metrics table indexes
CREATE INDEX idx_financial_metrics_report_id ON financial_metrics(report_id);
CREATE INDEX idx_production_metrics_report_id ON production_metrics(report_id);
CREATE INDEX idx_production_metrics_company ON production_metrics(company_code);
CREATE INDEX idx_hr_metrics_report_id ON hr_metrics(report_id);
CREATE INDEX idx_legal_metrics_report_id ON legal_metrics(report_id);
CREATE INDEX idx_procurement_metrics_report_id ON procurement_metrics(report_id);
CREATE INDEX idx_sales_metrics_report_id ON sales_metrics(report_id);
CREATE INDEX idx_sales_metrics_channel ON sales_metrics(sales_channel);
CREATE INDEX idx_rnd_metrics_report_id ON rnd_metrics(report_id);

-- Issues log indexes
CREATE INDEX idx_issues_log_report_id ON issues_log(report_id);
CREATE INDEX idx_issues_log_company_id ON issues_log(company_id);
CREATE INDEX idx_issues_log_status ON issues_log(status);
CREATE INDEX idx_issues_log_severity ON issues_log(severity);

-- Composite indexes for common queries
CREATE INDEX idx_daily_reports_company_date ON daily_reports(company_id, report_date);
CREATE INDEX idx_daily_reports_date_type ON daily_reports(report_date, report_type);

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC TIMESTAMPS
-- ============================================================================

-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at columns
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_reports_updated_at BEFORE UPDATE ON daily_reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Daily summary view
CREATE VIEW daily_summary AS
SELECT 
    dr.report_date,
    c.company_name,
    c.company_code,
    c.department_type,
    dr.report_type,
    dr.created_date,
    dr.report_id
FROM daily_reports dr
JOIN companies c ON dr.company_id = c.company_id
ORDER BY dr.report_date DESC, c.company_name;

-- Production summary view
CREATE VIEW production_summary AS
SELECT 
    ds.report_date,
    ds.company_name,
    ds.company_code,
    pm.raw_material_volume,
    pm.finished_product_volume,
    pm.total_consumption,
    pm.efficiency_cut,
    pm.efficiency_aseptic,
    pm.error_rate,
    pm.direct_labor_count + pm.indirect_labor_count as total_labor,
    pm.downtime_minutes
FROM daily_summary ds
JOIN production_metrics pm ON ds.report_id = pm.report_id
WHERE ds.department_type = 'Production'
ORDER BY ds.report_date DESC, ds.company_name;

-- Financial summary view
CREATE VIEW financial_summary AS
SELECT 
    ds.report_date,
    ds.company_name,
    fm.bank_inflow,
    fm.bank_outflow,
    fm.cash_balance,
    fm.debt_ratio,
    fm.energy_cost,
    fm.labor_cost,
    fm.material_cost
FROM daily_summary ds
JOIN financial_metrics fm ON ds.report_id = fm.report_id
WHERE ds.department_type = 'Finance'
ORDER BY ds.report_date DESC;

-- ============================================================================
-- INITIAL DATA SETUP
-- ============================================================================

-- Insert metric types
INSERT INTO metric_types (type_name, category, unit, description) VALUES
('Production Volume', 'Production', 'kg', 'Daily production volume in kilograms'),
('Efficiency Rate', 'Production', '%', 'Production efficiency percentage'),
('Error Rate', 'Quality', '%', 'Production error rate percentage'),
('Employee Count', 'HR', 'count', 'Number of employees'),
('Revenue', 'Finance', 'VND', 'Revenue in Vietnamese Dong'),
('Cost', 'Finance', 'VND', 'Cost in Vietnamese Dong'),
('Supplier Count', 'Procurement', 'count', 'Number of suppliers'),
('Contract Count', 'Legal', 'count', 'Number of contracts'),
('Research Hours', 'R&D', 'hours', 'Research and development hours'),
('Customer Count', 'Sales', 'count', 'Number of customers');

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO farm_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO farm_user;

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE companies IS 'Master table for all departments and companies in the farm system';
COMMENT ON TABLE daily_reports IS 'Central table for all daily reports from different departments';
COMMENT ON TABLE financial_metrics IS 'Financial data from accounting department';
COMMENT ON TABLE production_metrics IS 'Production data from all production facilities';
COMMENT ON TABLE hr_metrics IS 'Human resources metrics and KPIs';
COMMENT ON TABLE legal_metrics IS 'Legal department metrics and compliance data';
COMMENT ON TABLE procurement_metrics IS 'Procurement and supply chain metrics';
COMMENT ON TABLE sales_metrics IS 'Sales performance data from B2B channels';
COMMENT ON TABLE rnd_metrics IS 'Research and development metrics';
COMMENT ON TABLE issues_log IS 'Daily issues and problems tracking';

COMMENT ON COLUMN daily_reports.report_date IS 'The date this report covers';
COMMENT ON COLUMN daily_reports.created_date IS 'The date this report was created';
COMMENT ON COLUMN production_metrics.efficiency_cut IS 'Efficiency rate for cut products (%)';
COMMENT ON COLUMN production_metrics.efficiency_aseptic IS 'Efficiency rate for aseptic products (%)';
COMMENT ON COLUMN financial_metrics.debt_ratio IS 'Debt ratio percentage';
COMMENT ON COLUMN procurement_metrics.cost_savings IS 'Cost savings from negotiations';

-- Schema creation completed
SELECT 'Farm Data Management System schema created successfully!' as status; 