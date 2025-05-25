#!/usr/bin/env python3
"""
Farm Data Database Setup Script
Creates PostgreSQL database and runs schema creation
"""

import psycopg2
import psycopg2.extras
import os
import sys
import logging
from typing import Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseSetup:
    def __init__(self, admin_config: Dict[str, str], target_db: str = "farm_data"):
        self.admin_config = admin_config
        self.target_db = target_db
        self.connection = None
        self.cursor = None
    
    def connect_as_admin(self) -> bool:
        """Connect to PostgreSQL as admin user"""
        try:
            # Connect to default postgres database first
            admin_config = self.admin_config.copy()
            admin_config['database'] = 'postgres'
            
            self.connection = psycopg2.connect(**admin_config)
            self.connection.autocommit = True  # Required for CREATE DATABASE
            self.cursor = self.connection.cursor()
            logger.info("Connected to PostgreSQL as admin")
            return True
        except Exception as e:
            logger.error(f"Failed to connect as admin: {e}")
            return False
    
    def create_database(self) -> bool:
        """Create the farm_data database"""
        try:
            # Check if database exists
            self.cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.target_db,)
            )
            
            if self.cursor.fetchone():
                logger.info(f"Database '{self.target_db}' already exists")
                return True
            
            # Create database
            self.cursor.execute(f'CREATE DATABASE "{self.target_db}"')
            logger.info(f"✓ Created database '{self.target_db}'")
            return True
            
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            return False
    
    def run_schema(self) -> bool:
        """Run the schema creation script"""
        try:
            # Connect to the target database
            if self.connection:
                self.connection.close()
            
            target_config = self.admin_config.copy()
            target_config['database'] = self.target_db
            
            self.connection = psycopg2.connect(**target_config)
            self.cursor = self.connection.cursor()
            
            # Read and execute schema file
            schema_file = "create_database_schema.sql"
            if not os.path.exists(schema_file):
                logger.error(f"Schema file not found: {schema_file}")
                return False
            
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Execute schema
            self.cursor.execute(schema_sql)
            self.connection.commit()
            
            logger.info("✓ Database schema created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error running schema: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def verify_setup(self) -> bool:
        """Verify the database setup"""
        try:
            # Check tables exist
            self.cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            
            tables = [row[0] for row in self.cursor.fetchall()]
            expected_tables = [
                'companies', 'daily_reports', 'financial_metrics', 
                'production_metrics', 'hr_metrics', 'legal_metrics',
                'procurement_metrics', 'sales_metrics', 'rnd_metrics',
                'metric_types', 'issues_log'
            ]
            
            logger.info("Database tables created:")
            for table in tables:
                status = "✓" if table in expected_tables else "?"
                logger.info(f"  {status} {table}")
            
            missing_tables = set(expected_tables) - set(tables)
            if missing_tables:
                logger.warning(f"Missing tables: {missing_tables}")
                return False
            
            # Check views exist
            self.cursor.execute("""
                SELECT table_name 
                FROM information_schema.views 
                WHERE table_schema = 'public'
            """)
            
            views = [row[0] for row in self.cursor.fetchall()]
            logger.info(f"Database views created: {views}")
            
            logger.info("✓ Database setup verification completed")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying setup: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Disconnected from database")
    
    def setup_database(self) -> bool:
        """Run complete database setup"""
        logger.info("🚀 Starting Farm Data Database Setup")
        logger.info("=" * 50)
        
        if not self.connect_as_admin():
            return False
        
        try:
            steps = [
                ("Create Database", self.create_database),
                ("Run Schema", self.run_schema),
                ("Verify Setup", self.verify_setup)
            ]
            
            for step_name, step_function in steps:
                logger.info(f"\n📊 {step_name}")
                logger.info("-" * 30)
                if not step_function():
                    logger.error(f"Failed at step: {step_name}")
                    return False
            
            logger.info("\n" + "=" * 50)
            logger.info("✅ DATABASE SETUP COMPLETED SUCCESSFULLY")
            logger.info("=" * 50)
            return True
            
        except Exception as e:
            logger.error(f"Unexpected error during setup: {e}")
            return False
        finally:
            self.disconnect()

def print_instructions():
    """Print setup instructions"""
    print("""
🌾 Farm Data Management System - Database Setup
===============================================

PREREQUISITES:
1. PostgreSQL server running
2. Admin access to PostgreSQL
3. Python packages: psycopg2-binary, pandas

SETUP STEPS:
1. Update database credentials in this script
2. Run: python setup_database.py
3. Run: python import_data.py

DATABASE CONFIGURATION:
- Database name: farm_data
- Tables: 11 main tables + 2 lookup tables
- Views: 3 summary views for common queries
- Indexes: Optimized for reporting queries

NEXT STEPS AFTER SETUP:
1. Import your processed CSV data
2. Create database users with appropriate permissions
3. Set up backup procedures
4. Configure monitoring and alerts

SAMPLE QUERIES:
-- View all companies
SELECT * FROM companies;

-- Daily production summary
SELECT * FROM production_summary 
WHERE report_date >= '2025-01-01' 
ORDER BY report_date DESC;

-- Financial overview
SELECT * FROM financial_summary 
WHERE report_date >= '2025-01-01';
""")

def main():
    """Main setup function"""
    print_instructions()
    
    # Database configuration - UPDATE THESE VALUES
    admin_config = {
        'host': 'localhost',
        'database': 'vietfarm_db',  # Connect to default database first
        'user': 'golett_user',      # PostgreSQL admin user
        'password': 'golett_password',  # UPDATE THIS
        'port': 5432
    }
    
    # Prompt for password if not set
    if admin_config['password'] == 'your_password':
        import getpass
        admin_config['password'] = getpass.getpass("Enter PostgreSQL admin password: ")
    
    # Run setup
    setup = DatabaseSetup(admin_config)
    success = setup.setup_database()
    
    if success:
        print("\n🎉 Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Update database credentials in import_data.py")
        print("2. Run: python import_data.py")
        print("3. Start querying your farm data!")
    else:
        print("\n❌ Database setup failed. Check the logs for details.")
        print("\nTroubleshooting:")
        print("1. Verify PostgreSQL is running")
        print("2. Check database credentials")
        print("3. Ensure admin user has CREATE DATABASE privileges")
    
    return success

if __name__ == "__main__":
    main() 