#!/usr/bin/env python3
"""
Farm Data Database Testing Script
Tests database connectivity and runs sample queries
"""

import psycopg2
import psycopg2.extras
import pandas as pd
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseTester:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """Connect to the database"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            logger.info("✓ Connected to database successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            return False
    
    def test_tables_exist(self) -> bool:
        """Test that all required tables exist"""
        try:
            expected_tables = [
                'companies', 'daily_reports', 'financial_metrics', 
                'production_metrics', 'hr_metrics', 'legal_metrics',
                'procurement_metrics', 'sales_metrics', 'rnd_metrics',
                'metric_types', 'issues_log'
            ]
            
            self.cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            existing_tables = [row['table_name'] for row in self.cursor.fetchall()]
            
            logger.info("📊 Checking database tables:")
            all_exist = True
            for table in expected_tables:
                if table in existing_tables:
                    logger.info(f"  ✓ {table}")
                else:
                    logger.error(f"  ❌ {table} - MISSING")
                    all_exist = False
            
            return all_exist
            
        except Exception as e:
            logger.error(f"Error checking tables: {e}")
            return False
    
    def test_views_exist(self) -> bool:
        """Test that all views exist"""
        try:
            expected_views = ['daily_summary', 'production_summary', 'financial_summary']
            
            self.cursor.execute("""
                SELECT table_name 
                FROM information_schema.views 
                WHERE table_schema = 'public'
            """)
            
            existing_views = [row['table_name'] for row in self.cursor.fetchall()]
            
            logger.info("📈 Checking database views:")
            all_exist = True
            for view in expected_views:
                if view in existing_views:
                    logger.info(f"  ✓ {view}")
                else:
                    logger.error(f"  ❌ {view} - MISSING")
                    all_exist = False
            
            return all_exist
            
        except Exception as e:
            logger.error(f"Error checking views: {e}")
            return False
    
    def test_data_counts(self) -> bool:
        """Test data counts in main tables"""
        try:
            tables = ['companies', 'daily_reports', 'financial_metrics', 'production_metrics', 'hr_metrics']
            
            logger.info("📊 Data counts:")
            for table in tables:
                self.cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = self.cursor.fetchone()['count']
                logger.info(f"  {table}: {count:,} records")
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking data counts: {e}")
            return False
    
    def test_sample_queries(self) -> bool:
        """Run sample queries to test functionality"""
        try:
            logger.info("🔍 Running sample queries:")
            
            # Test 1: Companies query
            self.cursor.execute("SELECT COUNT(*) as count FROM companies")
            company_count = self.cursor.fetchone()['count']
            logger.info(f"  ✓ Found {company_count} companies")
            
            # Test 2: Date range query
            self.cursor.execute("""
                SELECT MIN(report_date) as min_date, MAX(report_date) as max_date, COUNT(*) as count
                FROM daily_reports
            """)
            date_info = self.cursor.fetchone()
            if date_info['count'] > 0:
                logger.info(f"  ✓ Date range: {date_info['min_date']} to {date_info['max_date']} ({date_info['count']} reports)")
            else:
                logger.warning("  ⚠️ No daily reports found")
            
            # Test 3: Production summary view
            self.cursor.execute("SELECT COUNT(*) as count FROM production_summary")
            prod_count = self.cursor.fetchone()['count']
            logger.info(f"  ✓ Production summary: {prod_count} records")
            
            # Test 4: Financial summary view
            self.cursor.execute("SELECT COUNT(*) as count FROM financial_summary")
            fin_count = self.cursor.fetchone()['count']
            logger.info(f"  ✓ Financial summary: {fin_count} records")
            
            # Test 5: Join query
            self.cursor.execute("""
                SELECT c.department_type, COUNT(*) as report_count
                FROM companies c
                JOIN daily_reports dr ON c.company_id = dr.company_id
                GROUP BY c.department_type
                ORDER BY report_count DESC
            """)
            
            dept_stats = self.cursor.fetchall()
            if dept_stats:
                logger.info("  ✓ Reports by department:")
                for row in dept_stats:
                    logger.info(f"    - {row['department_type']}: {row['report_count']} reports")
            
            return True
            
        except Exception as e:
            logger.error(f"Error running sample queries: {e}")
            return False
    
    def test_data_integrity(self) -> bool:
        """Test data integrity constraints"""
        try:
            logger.info("🔒 Testing data integrity:")
            
            # Test foreign key constraints
            self.cursor.execute("""
                SELECT COUNT(*) as orphaned_reports
                FROM daily_reports dr
                LEFT JOIN companies c ON dr.company_id = c.company_id
                WHERE c.company_id IS NULL
            """)
            orphaned = self.cursor.fetchone()['orphaned_reports']
            
            if orphaned == 0:
                logger.info("  ✓ No orphaned daily reports")
            else:
                logger.warning(f"  ⚠️ Found {orphaned} orphaned daily reports")
            
            # Test for null critical fields
            self.cursor.execute("""
                SELECT COUNT(*) as null_dates
                FROM daily_reports
                WHERE report_date IS NULL
            """)
            null_dates = self.cursor.fetchone()['null_dates']
            
            if null_dates == 0:
                logger.info("  ✓ No null report dates")
            else:
                logger.warning(f"  ⚠️ Found {null_dates} records with null report dates")
            
            return True
            
        except Exception as e:
            logger.error(f"Error testing data integrity: {e}")
            return False
    
    def run_performance_test(self) -> bool:
        """Run basic performance tests"""
        try:
            logger.info("⚡ Running performance tests:")
            
            import time
            
            # Test 1: Simple aggregation
            start_time = time.time()
            self.cursor.execute("""
                SELECT 
                    DATE_TRUNC('month', report_date) as month,
                    COUNT(*) as report_count
                FROM daily_reports
                GROUP BY DATE_TRUNC('month', report_date)
                ORDER BY month DESC
            """)
            results = self.cursor.fetchall()
            elapsed = time.time() - start_time
            logger.info(f"  ✓ Monthly aggregation: {len(results)} months in {elapsed:.3f}s")
            
            # Test 2: Complex join
            start_time = time.time()
            self.cursor.execute("""
                SELECT 
                    dr.report_date,
                    c.company_name,
                    pm.finished_product_volume
                FROM daily_reports dr
                JOIN companies c ON dr.company_id = c.company_id
                LEFT JOIN production_metrics pm ON dr.report_id = pm.report_id
                WHERE dr.report_date >= CURRENT_DATE - INTERVAL '30 days'
                ORDER BY dr.report_date DESC
                LIMIT 100
            """)
            results = self.cursor.fetchall()
            elapsed = time.time() - start_time
            logger.info(f"  ✓ Complex join query: {len(results)} records in {elapsed:.3f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"Error running performance tests: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Disconnected from database")
    
    def run_all_tests(self) -> bool:
        """Run all database tests"""
        logger.info("🧪 Starting Farm Data Database Tests")
        logger.info("=" * 50)
        
        if not self.connect():
            return False
        
        try:
            tests = [
                ("Table Structure", self.test_tables_exist),
                ("View Structure", self.test_views_exist),
                ("Data Counts", self.test_data_counts),
                ("Sample Queries", self.test_sample_queries),
                ("Data Integrity", self.test_data_integrity),
                ("Performance", self.run_performance_test)
            ]
            
            all_passed = True
            for test_name, test_function in tests:
                logger.info(f"\n🔬 {test_name}")
                logger.info("-" * 30)
                if not test_function():
                    logger.error(f"❌ {test_name} test failed")
                    all_passed = False
                else:
                    logger.info(f"✅ {test_name} test passed")
            
            logger.info("\n" + "=" * 50)
            if all_passed:
                logger.info("🎉 ALL TESTS PASSED - Database is ready!")
            else:
                logger.error("❌ Some tests failed - Check the logs")
            logger.info("=" * 50)
            
            return all_passed
            
        except Exception as e:
            logger.error(f"Unexpected error during testing: {e}")
            return False
        finally:
            self.disconnect()

def main():
    """Main testing function"""
    # Database configuration
    db_config = {
        'host': 'localhost',
        'database': 'vietfarm_db',  # Connect to default database first
        'user': 'golett_user',      # PostgreSQL admin user
        'password': 'golett_password',  # UPDATE THIS
        'port': 5432
    }
    # Prompt for password if not set
    if db_config['password'] == 'your_password':
        import getpass
        db_config['password'] = getpass.getpass("Enter PostgreSQL password: ")
    
    # Run tests
    tester = DatabaseTester(db_config)
    success = tester.run_all_tests()
    
    if success:
        print("\n🌾 Your farm data system is ready for use!")
        print("\nSuggested next steps:")
        print("1. Connect with your favorite SQL client")
        print("2. Explore the data using the sample queries in README.md")
        print("3. Create dashboards and reports")
        print("4. Set up automated data updates")
    else:
        print("\n🔧 Please fix the issues above before proceeding.")
    
    return success

if __name__ == "__main__":
    main() 