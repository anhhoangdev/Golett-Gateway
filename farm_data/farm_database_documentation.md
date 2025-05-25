# Farm Data Management System - Database Documentation

## Overview

The Farm Data Management System is a PostgreSQL database designed to normalize and manage daily operational data from 11 different departments/units within a Vietnamese agricultural enterprise. The system consolidates data from various TSV files into a structured, relational database that supports comprehensive reporting, analytics, and operational monitoring.

## System Architecture

### Data Sources
The database consolidates data from 11 original TSV files:
- **tai_chinh_ke_toan.tsv** - Financial/Accounting department (1008 records)
- **phap_ly.tsv** - Legal department (69 records)
- **nhan_su.tsv** - Human Resources (69 records)
- **thu_mua_cung_ung.tsv** - Procurement/Supply Chain (69 records)
- **rnd.tsv** - Research & Development (69 records)
- **inter_b2b.tsv** - International B2B Sales (69 records)
- **local_b2b.tsv** - Local B2B Sales (69 records)
- **sun_wind.tsv** - Production Unit (69 records)
- **vncc.tsv** - Production Unit (67 records)
- **mui_dinh.tsv** - Production Unit (67 records)
- **viet_farm.tsv** - Main Production Facility (67 records)

### Database Design Principles
- **Normalization**: Data is normalized to 3NF to eliminate redundancy
- **Centralized Reporting**: All departments report through a central `daily_reports` table
- **Modular Metrics**: Department-specific metrics are stored in dedicated tables
- **Audit Trail**: Automatic timestamps and change tracking
- **Data Integrity**: Foreign key constraints and check constraints ensure data quality

## Database Schema

### Core Tables

#### 1. companies
**Purpose**: Master table for all departments and organizational units

| Column | Type | Description |
|--------|------|-------------|
| company_id | SERIAL PRIMARY KEY | Unique identifier |
| company_name | VARCHAR(100) | Full department/company name |
| company_code | VARCHAR(20) UNIQUE | Short code (TCKT, PL, NS, etc.) |
| department_type | VARCHAR(50) | Category (Finance, Production, HR, etc.) |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Last update time |

**Sample Data Mapping**:
- TCKT → Tài Chính Kế Toán (Finance/Accounting)
- PL → Pháp Lý (Legal)
- NS → Nhân Sự (Human Resources)
- TMCU → Thu Mua Cung Ứng (Procurement)
- RND → Research & Development
- VIET_FARM → Main Production Facility

#### 2. daily_reports
**Purpose**: Central reporting table linking all daily reports

| Column | Type | Description |
|--------|------|-------------|
| report_id | SERIAL PRIMARY KEY | Unique report identifier |
| company_id | INTEGER | Foreign key to companies |
| report_date | DATE | Date the report covers |
| created_date | DATE | Date the report was created |
| report_type | VARCHAR(50) | Type of report |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Last update time |

**Constraints**: 
- Unique constraint on (company_id, report_date, report_type)
- Foreign key to companies table

### Metrics Tables

#### 3. financial_metrics
**Purpose**: Financial and accounting data from tai_chinh_ke_toan.tsv

**Key Metrics**:
- Bank flows (inflow/outflow) across multiple accounts
- Cash balances and debt ratios
- Cost breakdowns (management, energy, labor, materials)
- Revenue streams (leaf, seedling)
- Cost centers (fertilizer, materials)

**Notable Features**:
- Supports multiple bank accounts (bank_inflow_2, bank_inflow_3)
- Separate cost tracking for different production processes
- Revenue tracking by product type

#### 4. production_metrics
**Purpose**: Production data from all manufacturing facilities

**Key Metrics**:
- Volume tracking (raw materials, finished products)
- Product-specific volumes (10kg, 5kg, small packages, aseptic)
- Consumption metrics by category (KDQT, KDND, B2C)
- Efficiency rates for different processes
- Quality metrics (error rate, complaint rate)
- Labor allocation (direct/indirect)
- Specialized production (aloe seedlings, clusters)
- Downtime tracking

**Multi-Facility Support**:
- company_code field distinguishes between facilities
- Standardized metrics across all production units

#### 5. hr_metrics
**Purpose**: Human resources and workforce management

**Key Metrics**:
- Recruitment pipeline (applications, interviews, hires)
- Workforce size and attendance
- Performance tracking (late, absent, overtime)
- Training and development activities

#### 6. legal_metrics
**Purpose**: Legal compliance and contract management

**Key Metrics**:
- Contract lifecycle management
- Compliance monitoring
- Risk assessment and audit findings
- Legal consultation tracking
- Policy and regulatory updates

#### 7. procurement_metrics
**Purpose**: Supply chain and procurement operations

**Key Metrics**:
- Supplier management and evaluation
- Order processing and delivery performance
- Cost optimization and savings tracking
- Quality and performance monitoring
- Inventory management

#### 8. sales_metrics
**Purpose**: Sales performance for B2B channels

**Key Metrics**:
- Revenue and order tracking
- Customer acquisition and retention
- Sales process metrics (visits, quotations, contracts)
- Financial performance (payments, receivables)
- Market performance indicators

**Channel Support**:
- sales_channel field distinguishes between 'inter_b2b' and 'local_b2b'

#### 9. rnd_metrics
**Purpose**: Research and development activities

**Key Metrics**:
- Research project and experiment tracking
- Testing and quality assurance
- Innovation metrics (formulations, patents)
- Resource utilization (hours, budget, equipment)
- Collaboration activities

### Support Tables

#### 10. metric_types
**Purpose**: Metadata for metric categorization and standardization

**Structure**:
- type_name: Descriptive name
- category: Grouping (Production, Finance, etc.)
- unit: Measurement unit
- description: Detailed explanation

#### 11. issues_log
**Purpose**: Daily problem and issue tracking

**Features**:
- Severity levels (low, medium, high, critical)
- Status tracking (open, in_progress, resolved, closed)
- Assignment and resolution tracking
- Links to specific reports and companies

## Database Features

### Indexing Strategy
- **Primary Indexes**: All foreign keys are indexed
- **Date Indexes**: Optimized for date-range queries
- **Composite Indexes**: Common query patterns optimized
- **Category Indexes**: Department and type-based filtering

### Automatic Features
- **Timestamps**: Automatic creation and update timestamps
- **Triggers**: Auto-updating of updated_at columns
- **UUID Support**: Extension enabled for unique identifiers

### Data Views

#### daily_summary
Provides a consolidated view of all daily reports with company information.

#### production_summary
Aggregates production metrics with key performance indicators.

#### financial_summary
Consolidates financial data for reporting and analysis.

## Data Quality and Constraints

### Data Validation
- **Check Constraints**: Severity and status fields have predefined values
- **Unique Constraints**: Prevent duplicate reports for same date/company
- **Foreign Keys**: Ensure referential integrity
- **NOT NULL**: Critical fields are required

### Data Types
- **DECIMAL**: Financial and measurement data with appropriate precision
- **INTEGER**: Count-based metrics
- **DATE**: Separate date and timestamp handling
- **TEXT**: Flexible text fields for descriptions and issues

## Usage Patterns

### Common Queries
1. **Daily Operations**: Current day metrics across all departments
2. **Trend Analysis**: Time-series data for performance tracking
3. **Department Comparison**: Cross-departmental performance analysis
4. **Issue Tracking**: Problem identification and resolution monitoring
5. **Financial Reporting**: Revenue, cost, and profitability analysis

### Reporting Capabilities
- **Operational Dashboards**: Real-time department performance
- **Executive Reports**: High-level KPIs and trends
- **Compliance Reports**: Legal and regulatory compliance tracking
- **Production Reports**: Manufacturing efficiency and quality
- **Financial Reports**: P&L, cash flow, and cost analysis

## Data Integration

### ETL Process
The database is designed to receive data from:
1. **Cleaned CSV files** (output from preprocessing pipeline)
2. **Direct API integration** (for real-time data)
3. **Batch imports** (for historical data migration)

### Data Mapping
Original Vietnamese column headers are mapped to standardized English column names:
- "Ngày báo cáo" → report_date
- "Ngày tạo" → created_date
- "Vấn đề xảy ra trong ngày" → issues_log entries

## Performance Considerations

### Optimization Features
- **Partitioning Ready**: Tables can be partitioned by date for large datasets
- **Index Coverage**: All common query patterns are indexed
- **View Materialization**: Views can be materialized for heavy reporting
- **Connection Pooling**: Designed for concurrent access

### Scalability
- **Horizontal Scaling**: Read replicas for reporting workloads
- **Vertical Scaling**: Optimized for memory and CPU usage
- **Archive Strategy**: Historical data can be archived by date ranges

## Security and Access Control

### Permission Structure
- **Role-Based Access**: Different roles for different departments
- **Row-Level Security**: Can be implemented for data isolation
- **Audit Logging**: All changes are timestamped and traceable

### Data Privacy
- **Sensitive Data**: Financial and HR data properly secured
- **Compliance**: Designed for Vietnamese data protection requirements
- **Backup Strategy**: Regular backups with point-in-time recovery

## Maintenance and Monitoring

### Regular Tasks
- **Index Maintenance**: Regular REINDEX and VACUUM operations
- **Statistics Updates**: ANALYZE for query optimization
- **Backup Verification**: Regular backup testing
- **Performance Monitoring**: Query performance tracking

### Health Checks
- **Data Quality**: Regular validation of data integrity
- **Constraint Violations**: Monitoring for data quality issues
- **Performance Metrics**: Query execution time monitoring
- **Storage Usage**: Disk space and growth monitoring

## Extension Points

### Future Enhancements
- **Real-time Analytics**: Integration with streaming data platforms
- **Machine Learning**: Predictive analytics on operational data
- **Mobile Access**: API development for mobile applications
- **Integration**: ERP and other business system integration

### Customization
- **Additional Metrics**: Easy addition of new metric types
- **Department Expansion**: Simple addition of new departments
- **Reporting Extensions**: Custom views and stored procedures
- **Data Export**: Flexible export capabilities for external systems

## Technical Specifications

### Database Requirements
- **PostgreSQL Version**: 12+ (for advanced features)
- **Extensions**: uuid-ossp for UUID generation
- **Character Set**: UTF-8 for Vietnamese language support
- **Timezone**: Configurable for local time handling

### Hardware Recommendations
- **CPU**: Multi-core for concurrent processing
- **Memory**: Sufficient for index caching
- **Storage**: SSD for optimal performance
- **Network**: High bandwidth for data loading

This documentation serves as a comprehensive guide for understanding, maintaining, and extending the Farm Data Management System database. 