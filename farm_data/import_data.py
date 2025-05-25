#!/usr/bin/env python3
"""
Farm Data Import Script
Imports processed CSV data into PostgreSQL database
Handles data mapping, validation, and error reporting
"""

import pandas as pd
import psycopg2
import psycopg2.extras
import os
import glob
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_import.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class FarmDataImporter:
    def __init__(self, db_config: Dict[str, str], data_dir: str = "processed_data"):
        self.db_config = db_config
        self.data_dir = data_dir
        self.connection = None
        self.cursor = None
        
        # Column mappings for each metrics table
        self.column_mappings = {
            'financial_metrics': {
                'chi_tiết_giao_dịch_ngân_hàng_tiền_vào': 'bank_inflow',
                'chi_tiết_giao_dịch_ngân_hàng_tiền_ra': 'bank_outflow',
                'số_dư_tiền_mặt_tại_quỹ': 'cash_balance',
                'tỷ_lệ_nợ_trễ_hạn_thanh_toán_trên_tổng_công_nợ': 'debt_ratio',
                'chi_phí_quản_lý_chi_phí_hoạt_động': 'management_cost',
                'chi_phí_năng_lượng_điện_củi_nước': 'energy_cost',
                'chi_phí_nhân_công_hàng_cắt': 'labor_cost_cut',
                'chi_phí_nhân_công_hàng_aseptic': 'labor_cost_aseptic',
                'giá_nguyên_liệu': 'material_cost',
                'chi_tiết_giao_dịch_ngân_hàng_tiền_vào_1': 'bank_inflow_2',
                'chi_tiết_giao_dịch_ngân_hàng_tiền_ra_1': 'bank_outflow_2',
                'số_dư_tiền_mặt_tại_quỹ_1': 'cash_balance_2',
                'giá_nguyên_liệu_1': 'material_cost_2',
                'chi_tiết_giao_dịch_ngân_hàng_tiền_vào_2': 'bank_inflow_3',
                'chi_tiết_giao_dịch_ngân_hàng_tiền_ra_2': 'bank_outflow_3',
                'số_dư_tiền_mặt_tại_quỹ_2': 'cash_balance_3',
                'chi_phí_nhân_công': 'labor_cost',
                'doanh_thu_lá': 'leaf_revenue',
                'doanh_thu_cây_con': 'seedling_revenue',
                'chi_phí_phân_bón': 'fertilizer_cost',
                'giá_nguyên_liệu_2': 'material_cost_3'
            },
            'production_metrics': {
                'sản_lượng_nguyên_liệu_sản_xuất_kg': 'raw_material_volume',
                'sản_lượng_thành_phẩm_sản_xuất_kg': 'finished_product_volume',
                'sản_lượng_hàng_túi_10kg_kg': 'product_10kg_volume',
                'sản_lượng_hàng_túi_5kg_kg': 'product_5kg_volume',
                'sản_lượng_hàng_túi_nhỏ_kg': 'product_small_volume',
                'sản_lượng_hàng_aseptic_kg': 'aseptic_volume',
                'sản_lượng_thành_phẩm_tiêu_thụ_tổng_sản_lượng_kg': 'total_consumption',
                'sản_lượng_thành_phẩm_tiêu_thụ_khối_kdqt_kg': 'consumption_kdqt',
                'sản_lượng_thành_phẩm_tiêu_thụ_khối_kdnđ_kg': 'consumption_kdnd',
                'sản_lượng_thành_phẩm_tiêu_thụ_b2c_kg': 'consumption_b2c',
                'hiệu_suất_thu_hồi_hàng_cắt': 'efficiency_cut',
                'hiệu_suất_thu_hồi_hàng_aseptic': 'efficiency_aseptic',
                'lỗi_sản_xuất_tổng_sản_xuất': 'error_rate',
                'lỗi_khiếu_nại_tổng_xuất_hàng': 'complaint_rate',
                'số_lao_động_sản_xuất_trực_tiếp': 'direct_labor_count',
                'số_lao_động_sản_xuất_gián_tiếp': 'indirect_labor_count',
                'số_lượng_cây_giống_nha_đam_thái_gc_a1_sản_xuất': 'aloe_seedling_a1_count',
                'số_lượng_cây_giống_nha_đam_sâm_gc_sa01_sản_xuất': 'aloe_seedling_sa01_count',
                'số_lượng_cụm_nhân_sản_xuất_bao_gồm_tất_cả_các_giống': 'cluster_production_count',
                'sự_cố_dừng_máy_ngưng_sản_xuất_phút': 'downtime_minutes'
            }
        }
        
        # Company code mapping
        self.company_codes = {
            'tai_chinh_ke_toan': 'TCKT',
            'phap_ly': 'PL',
            'nhan_su': 'NS',
            'thu_mua_cung_ung': 'TMCU',
            'rnd': 'RND',
            'inter_b2b': 'IB2B',
            'local_b2b': 'LB2B',
            'sun_wind': 'SW',
            'vncc': 'VNCC',
            'mui_dinh': 'MD',
            'viet_farm': 'VF'
        }
    
    def connect_database(self) -> bool:
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            logger.info("Successfully connected to PostgreSQL database")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def disconnect_database(self):
        """Disconnect from database"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Disconnected from database")
    
    def load_companies(self) -> bool:
        """Load companies data"""
        try:
            companies_file = os.path.join(self.data_dir, "companies.csv")
            if not os.path.exists(companies_file):
                logger.error(f"Companies file not found: {companies_file}")
                return False
            
            df = pd.read_csv(companies_file)
            logger.info(f"Loading {len(df)} companies...")
            
            # Clear existing companies
            self.cursor.execute("DELETE FROM companies")
            
            for _, row in df.iterrows():
                insert_query = """
                INSERT INTO companies (company_name, company_code, department_type)
                VALUES (%s, %s, %s)
                ON CONFLICT (company_code) DO UPDATE SET
                    company_name = EXCLUDED.company_name,
                    department_type = EXCLUDED.department_type,
                    updated_at = CURRENT_TIMESTAMP
                """
                self.cursor.execute(insert_query, (
                    row['company_name'],
                    row['company_code'],
                    row['department_type']
                ))
            
            self.connection.commit()
            logger.info("✓ Companies loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading companies: {e}")
            self.connection.rollback()
            return False
    
    def load_daily_reports(self) -> bool:
        """Load daily reports data"""
        try:
            reports_file = os.path.join(self.data_dir, "daily_reports.csv")
            if not os.path.exists(reports_file):
                logger.error(f"Daily reports file not found: {reports_file}")
                return False
            
            df = pd.read_csv(reports_file)
            logger.info(f"Loading {len(df)} daily reports...")
            
            # Clear existing reports
            self.cursor.execute("DELETE FROM daily_reports")
            
            # Get company IDs mapping
            self.cursor.execute("SELECT company_id, company_code FROM companies")
            company_mapping = {row['company_code']: row['company_id'] for row in self.cursor.fetchall()}
            
            for _, row in df.iterrows():
                company_id = company_mapping.get(row['company_code'])
                if not company_id:
                    logger.warning(f"Company code not found: {row['company_code']}")
                    continue
                
                # Handle date conversion
                report_date = pd.to_datetime(row['report_date']).date() if pd.notna(row['report_date']) else None
                created_date = pd.to_datetime(row['created_date']).date() if pd.notna(row['created_date']) else None
                
                insert_query = """
                INSERT INTO daily_reports (company_id, report_date, created_date, report_type)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (company_id, report_date, report_type) DO UPDATE SET
                    created_date = EXCLUDED.created_date,
                    updated_at = CURRENT_TIMESTAMP
                """
                self.cursor.execute(insert_query, (
                    company_id,
                    report_date,
                    created_date,
                    row['report_type']
                ))
            
            self.connection.commit()
            logger.info("✓ Daily reports loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading daily reports: {e}")
            self.connection.rollback()
            return False
    
    def get_report_id_mapping(self) -> Dict[Tuple, int]:
        """Get mapping of (company_code, report_date, report_type) to report_id"""
        query = """
        SELECT dr.report_id, c.company_code, dr.report_date, dr.report_type
        FROM daily_reports dr
        JOIN companies c ON dr.company_id = c.company_id
        """
        self.cursor.execute(query)
        
        mapping = {}
        for row in self.cursor.fetchall():
            key = (row['company_code'], row['report_date'], row['report_type'])
            mapping[key] = row['report_id']
        
        return mapping
    
    def load_financial_metrics(self) -> bool:
        """Load financial metrics data"""
        try:
            file_path = os.path.join(self.data_dir, "tai_chinh_ke_toan_metrics.csv")
            if not os.path.exists(file_path):
                logger.warning(f"Financial metrics file not found: {file_path}")
                return True
            
            df = pd.read_csv(file_path)
            logger.info(f"Loading {len(df)} financial metrics records...")
            
            # Clear existing financial metrics
            self.cursor.execute("DELETE FROM financial_metrics")
            
            # Get report ID mapping
            report_mapping = self.get_report_id_mapping()
            
            for _, row in df.iterrows():
                report_date = pd.to_datetime(row['report_date']).date()
                report_key = ('TCKT', report_date, 'tai_chinh_ke_toan')
                report_id = report_mapping.get(report_key)
                
                if not report_id:
                    logger.warning(f"Report ID not found for financial metrics: {report_key}")
                    continue
                
                # Map columns and prepare data
                data = {'report_id': report_id}
                for source_col, target_col in self.column_mappings['financial_metrics'].items():
                    if source_col in df.columns and pd.notna(row[source_col]):
                        data[target_col] = float(row[source_col])
                
                if len(data) > 1:  # More than just report_id
                    columns = list(data.keys())
                    values = list(data.values())
                    placeholders = ', '.join(['%s'] * len(values))
                    
                    insert_query = f"""
                    INSERT INTO financial_metrics ({', '.join(columns)})
                    VALUES ({placeholders})
                    """
                    self.cursor.execute(insert_query, values)
            
            self.connection.commit()
            logger.info("✓ Financial metrics loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading financial metrics: {e}")
            self.connection.rollback()
            return False
    
    def load_production_metrics(self) -> bool:
        """Load production metrics data from all production units"""
        try:
            production_files = [
                'viet_farm_metrics.csv',
                'sun_wind_metrics.csv',
                'vncc_metrics.csv',
                'mui_dinh_metrics.csv'
            ]
            
            # Clear existing production metrics
            self.cursor.execute("DELETE FROM production_metrics")
            
            # Get report ID mapping
            report_mapping = self.get_report_id_mapping()
            total_records = 0
            
            for file_name in production_files:
                file_path = os.path.join(self.data_dir, file_name)
                if not os.path.exists(file_path):
                    logger.warning(f"Production metrics file not found: {file_path}")
                    continue
                
                df = pd.read_csv(file_path)
                company_key = file_name.replace('_metrics.csv', '')
                company_code = self.company_codes.get(company_key)
                
                if not company_code:
                    logger.warning(f"Company code not found for: {company_key}")
                    continue
                
                logger.info(f"Loading {len(df)} records from {file_name}...")
                
                for _, row in df.iterrows():
                    report_date = pd.to_datetime(row['report_date']).date()
                    report_key = (company_code, report_date, company_key)
                    report_id = report_mapping.get(report_key)
                    
                    if not report_id:
                        logger.warning(f"Report ID not found for production metrics: {report_key}")
                        continue
                    
                    # Map columns and prepare data
                    data = {'report_id': report_id, 'company_code': company_code}
                    for source_col, target_col in self.column_mappings['production_metrics'].items():
                        if source_col in df.columns and pd.notna(row[source_col]):
                            data[target_col] = float(row[source_col])
                    
                    if len(data) > 2:  # More than just report_id and company_code
                        columns = list(data.keys())
                        values = list(data.values())
                        placeholders = ', '.join(['%s'] * len(values))
                        
                        insert_query = f"""
                        INSERT INTO production_metrics ({', '.join(columns)})
                        VALUES ({placeholders})
                        """
                        self.cursor.execute(insert_query, values)
                        total_records += 1
            
            self.connection.commit()
            logger.info(f"✓ Production metrics loaded successfully ({total_records} records)")
            return True
            
        except Exception as e:
            logger.error(f"Error loading production metrics: {e}")
            self.connection.rollback()
            return False
    
    def load_hr_metrics(self) -> bool:
        """Load HR metrics data"""
        try:
            file_path = os.path.join(self.data_dir, "nhan_su_metrics.csv")
            if not os.path.exists(file_path):
                logger.warning(f"HR metrics file not found: {file_path}")
                return True
            
            df = pd.read_csv(file_path)
            logger.info(f"Loading {len(df)} HR metrics records...")
            
            # Clear existing HR metrics
            self.cursor.execute("DELETE FROM hr_metrics")
            
            # Get report ID mapping
            report_mapping = self.get_report_id_mapping()
            
            # HR column mapping
            hr_columns = {
                'hồ_sơ_ứng_viên_nhận_được': 'applications_received',
                'lịch_phỏng_vấn_hoàn_thành': 'interviews_completed',
                'số_nhân_viên_tuyển_dụng': 'new_hires',
                'tổng_số_nhân_viên_đi_làm': 'total_employees',
                'tổng_số_nv_đi_trễ': 'late_employees',
                'tổng_số_nv_vắng_không_phép': 'absent_employees',
                'tổng_số_nv_ot': 'overtime_employees',
                'số_khóa_đào_tạo_trong_ngày': 'training_sessions',
                'tổng_số_nv_tham_gia': 'training_participants'
            }
            
            for _, row in df.iterrows():
                report_date = pd.to_datetime(row['report_date']).date()
                report_key = ('NS', report_date, 'nhan_su')
                report_id = report_mapping.get(report_key)
                
                if not report_id:
                    logger.warning(f"Report ID not found for HR metrics: {report_key}")
                    continue
                
                # Map columns and prepare data
                data = {'report_id': report_id}
                for source_col, target_col in hr_columns.items():
                    if source_col in df.columns and pd.notna(row[source_col]):
                        data[target_col] = int(float(row[source_col]))
                
                if len(data) > 1:  # More than just report_id
                    columns = list(data.keys())
                    values = list(data.values())
                    placeholders = ', '.join(['%s'] * len(values))
                    
                    insert_query = f"""
                    INSERT INTO hr_metrics ({', '.join(columns)})
                    VALUES ({placeholders})
                    """
                    self.cursor.execute(insert_query, values)
            
            self.connection.commit()
            logger.info("✓ HR metrics loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading HR metrics: {e}")
            self.connection.rollback()
            return False
    
    def load_other_metrics(self) -> bool:
        """Load other metrics (legal, procurement, sales, R&D)"""
        try:
            # For now, we'll create placeholder records for these tables
            # since the column mappings are complex and would need detailed analysis
            
            logger.info("Creating placeholder records for other metrics tables...")
            
            # Clear existing records
            self.cursor.execute("DELETE FROM legal_metrics")
            self.cursor.execute("DELETE FROM procurement_metrics") 
            self.cursor.execute("DELETE FROM sales_metrics")
            self.cursor.execute("DELETE FROM rnd_metrics")
            
            self.connection.commit()
            logger.info("✓ Other metrics tables cleared (ready for future data)")
            return True
            
        except Exception as e:
            logger.error(f"Error with other metrics: {e}")
            self.connection.rollback()
            return False
    
    def validate_data_integrity(self) -> bool:
        """Validate data integrity after import"""
        try:
            logger.info("Validating data integrity...")
            
            # Check record counts
            tables = ['companies', 'daily_reports', 'financial_metrics', 'production_metrics', 'hr_metrics']
            for table in tables:
                self.cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = self.cursor.fetchone()['count']
                logger.info(f"  {table}: {count} records")
            
            # Check for orphaned records
            self.cursor.execute("""
                SELECT COUNT(*) as orphaned_reports
                FROM daily_reports dr
                LEFT JOIN companies c ON dr.company_id = c.company_id
                WHERE c.company_id IS NULL
            """)
            orphaned = self.cursor.fetchone()['orphaned_reports']
            if orphaned > 0:
                logger.warning(f"Found {orphaned} orphaned daily reports")
            
            # Check date ranges
            self.cursor.execute("""
                SELECT MIN(report_date) as min_date, MAX(report_date) as max_date
                FROM daily_reports
            """)
            date_range = self.cursor.fetchone()
            logger.info(f"  Date range: {date_range['min_date']} to {date_range['max_date']}")
            
            logger.info("✓ Data integrity validation completed")
            return True
            
        except Exception as e:
            logger.error(f"Error validating data integrity: {e}")
            return False
    
    def run_import(self) -> bool:
        """Run the complete data import process"""
        logger.info("🚀 Starting Farm Data Import Process")
        logger.info("=" * 60)
        
        if not self.connect_database():
            return False
        
        try:
            # Import data in order of dependencies
            steps = [
                ("Companies", self.load_companies),
                ("Daily Reports", self.load_daily_reports),
                ("Financial Metrics", self.load_financial_metrics),
                ("Production Metrics", self.load_production_metrics),
                ("HR Metrics", self.load_hr_metrics),
                ("Other Metrics", self.load_other_metrics),
                ("Data Validation", self.validate_data_integrity)
            ]
            
            for step_name, step_function in steps:
                logger.info(f"\n📊 {step_name}")
                logger.info("-" * 40)
                if not step_function():
                    logger.error(f"Failed at step: {step_name}")
                    return False
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ FARM DATA IMPORT COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            return True
            
        except Exception as e:
            logger.error(f"Unexpected error during import: {e}")
            return False
        finally:
            self.disconnect_database()

def main():
    """Main function to run the import"""
    # Database configuration
    db_config = {
        'host': 'localhost',
        'database': 'farm_data',  # Connect to default database first
        'user': 'golett_user',      # PostgreSQL admin user
        'password': 'golett_password',  # UPDATE THIS
        'port': 5432
    }
    
    # Check if processed data directory exists
    if not os.path.exists("processed_data"):
        logger.error("Processed data directory not found. Please run data preprocessing first.")
        return False
    
    # Create importer and run
    importer = FarmDataImporter(db_config)
    success = importer.run_import()
    
    if success:
        logger.info("\n🎉 Data import completed successfully!")
        logger.info("You can now query your farm data using SQL.")
    else:
        logger.error("\n❌ Data import failed. Check the logs for details.")
    
    return success

if __name__ == "__main__":
    main() 