#!/usr/bin/env python3
"""
Farm Data Analysis and Preprocessing Script
Analyzes TSV files for data quality, duplicates, and prepares for normalization
"""

import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime
import re
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

class FarmDataAnalyzer:
    def __init__(self, data_dir: str = "raw_data"):
        self.data_dir = data_dir
        self.files = glob.glob(os.path.join(data_dir, "*.tsv"))
        self.dataframes = {}
        self.analysis_results = {}
        
    def load_data(self) -> None:
        """Load all TSV files into dataframes"""
        print("Loading TSV files...")
        for file_path in self.files:
            file_name = os.path.basename(file_path).replace('.tsv', '')
            try:
                # Read with different encodings to handle Vietnamese characters
                try:
                    df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(file_path, sep='\t', encoding='utf-8-sig')
                except UnicodeDecodeError:
                    df = pd.read_csv(file_path, sep='\t', encoding='latin-1')
                
                self.dataframes[file_name] = df
                print(f"✓ Loaded {file_name}: {df.shape[0]} rows, {df.shape[1]} columns")
            except Exception as e:
                print(f"✗ Error loading {file_name}: {e}")
    
    def analyze_data_quality(self) -> None:
        """Analyze data quality issues across all files"""
        print("\n" + "="*60)
        print("DATA QUALITY ANALYSIS")
        print("="*60)
        
        for name, df in self.dataframes.items():
            print(f"\n📊 Analyzing {name.upper()}")
            print("-" * 40)
            
            analysis = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'empty_rows': 0,
                'duplicate_rows': 0,
                'missing_values': {},
                'data_types': {},
                'date_issues': [],
                'numeric_issues': [],
                'column_duplicates': []
            }
            
            # Check for empty rows
            empty_rows = df.isnull().all(axis=1).sum()
            analysis['empty_rows'] = empty_rows
            
            # Check for duplicate rows
            duplicate_rows = df.duplicated().sum()
            analysis['duplicate_rows'] = duplicate_rows
            
            # Check for missing values
            missing_counts = df.isnull().sum()
            analysis['missing_values'] = missing_counts[missing_counts > 0].to_dict()
            
            # Analyze data types
            for col in df.columns:
                analysis['data_types'][col] = str(df[col].dtype)
            
            # Check for date column issues
            date_columns = [col for col in df.columns if any(keyword in col.lower() 
                           for keyword in ['ngày', 'date', 'tạo', 'báo cáo'])]
            
            for col in date_columns:
                if col in df.columns:
                    # Check for inconsistent date formats
                    non_null_values = df[col].dropna().astype(str)
                    if len(non_null_values) > 0:
                        # Look for different date patterns
                        patterns = set()
                        for val in non_null_values.head(20):
                            if ',' in val:
                                patterns.add('comma_format')
                            elif '.' in val:
                                patterns.add('dot_format')
                            elif len(val) == 5 and val.isdigit():
                                patterns.add('excel_serial')
                        
                        if len(patterns) > 1:
                            analysis['date_issues'].append(f"{col}: Multiple formats detected")
            
            # Check for numeric columns with text values
            for col in df.columns:
                if col not in date_columns:
                    sample_values = df[col].dropna().astype(str).head(10)
                    has_numbers = any(any(c.isdigit() for c in str(val)) for val in sample_values)
                    has_text = any(any(c.isalpha() for c in str(val)) for val in sample_values)
                    
                    if has_numbers and has_text:
                        analysis['numeric_issues'].append(f"{col}: Mixed numeric/text data")
            
            # Check for duplicate column names or similar columns
            columns = list(df.columns)
            for i, col1 in enumerate(columns):
                for j, col2 in enumerate(columns[i+1:], i+1):
                    if col1 == col2:
                        analysis['column_duplicates'].append(f"Exact duplicate: {col1}")
                    elif col1.strip() == col2.strip():
                        analysis['column_duplicates'].append(f"Whitespace difference: '{col1}' vs '{col2}'")
            
            self.analysis_results[name] = analysis
            
            # Print summary
            print(f"Total rows: {analysis['total_rows']}")
            print(f"Total columns: {analysis['total_columns']}")
            print(f"Empty rows: {analysis['empty_rows']}")
            print(f"Duplicate rows: {analysis['duplicate_rows']}")
            print(f"Columns with missing values: {len(analysis['missing_values'])}")
            
            if analysis['date_issues']:
                print(f"Date issues: {len(analysis['date_issues'])}")
                for issue in analysis['date_issues']:
                    print(f"  - {issue}")
            
            if analysis['numeric_issues']:
                print(f"Numeric issues: {len(analysis['numeric_issues'])}")
                for issue in analysis['numeric_issues'][:3]:  # Show first 3
                    print(f"  - {issue}")
            
            if analysis['column_duplicates']:
                print(f"Column duplicates: {len(analysis['column_duplicates'])}")
                for dup in analysis['column_duplicates']:
                    print(f"  - {dup}")
    
    def identify_common_fields(self) -> Dict[str, List[str]]:
        """Identify common fields across all datasets"""
        print("\n" + "="*60)
        print("COMMON FIELDS ANALYSIS")
        print("="*60)
        
        all_columns = {}
        for name, df in self.dataframes.items():
            for col in df.columns:
                clean_col = col.strip().lower()
                if clean_col not in all_columns:
                    all_columns[clean_col] = []
                all_columns[clean_col].append(name)
        
        # Group by frequency
        common_fields = {
            'universal': [],  # In all datasets
            'frequent': [],   # In most datasets
            'occasional': [], # In some datasets
            'unique': []      # In one dataset only
        }
        
        total_datasets = len(self.dataframes)
        
        for col, datasets in all_columns.items():
            count = len(datasets)
            if count == total_datasets:
                common_fields['universal'].append((col, datasets))
            elif count >= total_datasets * 0.7:
                common_fields['frequent'].append((col, datasets))
            elif count >= 2:
                common_fields['occasional'].append((col, datasets))
            else:
                common_fields['unique'].append((col, datasets))
        
        # Print results
        for category, fields in common_fields.items():
            print(f"\n{category.upper()} FIELDS ({len(fields)}):")
            for field, datasets in fields[:10]:  # Show first 10
                print(f"  - {field} (in: {', '.join(datasets)})")
            if len(fields) > 10:
                print(f"  ... and {len(fields) - 10} more")
        
        return common_fields
    
    def detect_duplicates(self) -> None:
        """Detect and analyze duplicate records"""
        print("\n" + "="*60)
        print("DUPLICATE DETECTION")
        print("="*60)
        
        for name, df in self.dataframes.items():
            print(f"\n🔍 Analyzing duplicates in {name.upper()}")
            print("-" * 40)
            
            # Check for exact duplicates
            exact_duplicates = df.duplicated().sum()
            print(f"Exact duplicate rows: {exact_duplicates}")
            
            # Check for duplicates based on date columns
            date_cols = [col for col in df.columns if any(keyword in col.lower() 
                        for keyword in ['ngày', 'date'])]
            
            if date_cols:
                for date_col in date_cols[:2]:  # Check first 2 date columns
                    if date_col in df.columns:
                        date_duplicates = df[date_col].duplicated().sum()
                        print(f"Duplicate {date_col}: {date_duplicates}")
            
            # Show sample duplicates if any
            if exact_duplicates > 0:
                duplicate_rows = df[df.duplicated(keep=False)]
                print(f"Sample duplicate rows (showing first 3):")
                print(duplicate_rows.head(3).to_string())
    
    def suggest_normalization_schema(self) -> Dict[str, Any]:
        """Suggest a normalized database schema"""
        print("\n" + "="*60)
        print("NORMALIZATION SCHEMA SUGGESTION")
        print("="*60)
        
        schema = {
            'core_tables': {},
            'lookup_tables': {},
            'relationships': []
        }
        
        # Core entity tables
        schema['core_tables'] = {
            'companies': {
                'description': 'Company/Department information',
                'columns': [
                    'company_id SERIAL PRIMARY KEY',
                    'company_name VARCHAR(100) NOT NULL',
                    'company_code VARCHAR(20) UNIQUE',
                    'department_type VARCHAR(50)',
                    'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                ]
            },
            'daily_reports': {
                'description': 'Main daily report entries',
                'columns': [
                    'report_id SERIAL PRIMARY KEY',
                    'company_id INTEGER REFERENCES companies(company_id)',
                    'report_date DATE NOT NULL',
                    'created_date DATE',
                    'report_type VARCHAR(50)',
                    'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                    'UNIQUE(company_id, report_date, report_type)'
                ]
            },
            'financial_metrics': {
                'description': 'Financial data from tai_chinh_ke_toan',
                'columns': [
                    'metric_id SERIAL PRIMARY KEY',
                    'report_id INTEGER REFERENCES daily_reports(report_id)',
                    'total_revenue DECIMAL(15,2)',
                    'total_expenses DECIMAL(15,2)',
                    'bank_inflow DECIMAL(15,2)',
                    'bank_outflow DECIMAL(15,2)',
                    'cash_balance DECIMAL(15,2)',
                    'gross_profit DECIMAL(15,2)',
                    'debt_ratio DECIMAL(5,2)',
                    'material_cost DECIMAL(15,2)',
                    'energy_cost DECIMAL(15,2)',
                    'labor_cost DECIMAL(15,2)'
                ]
            },
            'production_metrics': {
                'description': 'Production data from viet_farm and other production units',
                'columns': [
                    'production_id SERIAL PRIMARY KEY',
                    'report_id INTEGER REFERENCES daily_reports(report_id)',
                    'raw_material_volume DECIMAL(12,2)',
                    'finished_product_volume DECIMAL(12,2)',
                    'product_10kg_volume DECIMAL(12,2)',
                    'product_5kg_volume DECIMAL(12,2)',
                    'product_small_volume DECIMAL(12,2)',
                    'aseptic_volume DECIMAL(12,2)',
                    'total_consumption DECIMAL(12,2)',
                    'efficiency_cut DECIMAL(5,2)',
                    'efficiency_aseptic DECIMAL(5,2)',
                    'error_rate DECIMAL(5,4)',
                    'complaint_rate DECIMAL(5,4)',
                    'downtime_minutes INTEGER'
                ]
            },
            'hr_metrics': {
                'description': 'Human resources data',
                'columns': [
                    'hr_id SERIAL PRIMARY KEY',
                    'report_id INTEGER REFERENCES daily_reports(report_id)',
                    'applications_received INTEGER',
                    'interviews_completed INTEGER',
                    'new_hires INTEGER',
                    'total_employees INTEGER',
                    'late_employees INTEGER',
                    'absent_employees INTEGER',
                    'overtime_employees INTEGER',
                    'training_sessions INTEGER',
                    'training_participants INTEGER'
                ]
            },
            'legal_metrics': {
                'description': 'Legal and compliance data',
                'columns': [
                    'legal_id SERIAL PRIMARY KEY',
                    'report_id INTEGER REFERENCES daily_reports(report_id)',
                    'contracts_under_review INTEGER',
                    'contract_amendments INTEGER',
                    'new_contracts_stored INTEGER',
                    'new_contracts_received INTEGER',
                    'contracts_need_negotiation INTEGER',
                    'contract_disputes INTEGER',
                    'compliance_rate DECIMAL(5,2)',
                    'regulatory_warnings INTEGER'
                ]
            },
            'procurement_metrics': {
                'description': 'Procurement and supply chain data',
                'columns': [
                    'procurement_id SERIAL PRIMARY KEY',
                    'report_id INTEGER REFERENCES daily_reports(report_id)',
                    'total_suppliers INTEGER',
                    'main_suppliers INTEGER',
                    'evaluated_suppliers INTEGER',
                    'planned_orders INTEGER',
                    'new_planned_orders INTEGER',
                    'emergency_orders INTEGER',
                    'on_time_deliveries INTEGER',
                    'late_deliveries INTEGER',
                    'returned_items INTEGER',
                    'cost_savings DECIMAL(15,2)',
                    'total_procurement_cost DECIMAL(15,2)'
                ]
            }
        }
        
        # Lookup tables
        schema['lookup_tables'] = {
            'metric_types': {
                'description': 'Types of metrics being tracked',
                'columns': [
                    'type_id SERIAL PRIMARY KEY',
                    'type_name VARCHAR(100) NOT NULL',
                    'category VARCHAR(50)',
                    'unit VARCHAR(20)',
                    'description TEXT'
                ]
            },
            'issues_log': {
                'description': 'Daily issues and problems reported',
                'columns': [
                    'issue_id SERIAL PRIMARY KEY',
                    'report_id INTEGER REFERENCES daily_reports(report_id)',
                    'issue_description TEXT',
                    'severity VARCHAR(20)',
                    'status VARCHAR(20) DEFAULT \'open\'',
                    'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                ]
            }
        }
        
        # Print schema
        print("\n🏗️  SUGGESTED DATABASE SCHEMA:")
        print("\nCORE TABLES:")
        for table_name, table_info in schema['core_tables'].items():
            print(f"\n📋 {table_name.upper()}")
            print(f"   Description: {table_info['description']}")
            print("   Columns:")
            for col in table_info['columns']:
                print(f"     - {col}")
        
        print("\nLOOKUP TABLES:")
        for table_name, table_info in schema['lookup_tables'].items():
            print(f"\n📋 {table_name.upper()}")
            print(f"   Description: {table_info['description']}")
            print("   Columns:")
            for col in table_info['columns']:
                print(f"     - {col}")
        
        return schema
    
    def generate_data_mapping(self) -> Dict[str, Dict[str, str]]:
        """Generate mapping from source columns to target schema"""
        print("\n" + "="*60)
        print("DATA MAPPING GENERATION")
        print("="*60)
        
        mapping = {}
        
        # Define mappings for each source file
        file_mappings = {
            'tai_chinh_ke_toan': {
                'target_table': 'financial_metrics',
                'column_mapping': {
                    'Tổng doanh thu trong ngày (theo nguồn: bán hàng, dịch vụ, khác)': 'total_revenue',
                    'Tổng chi phí phát sinh trong ngày': 'total_expenses',
                    'Chi tiết giao dịch ngân hàng (tiền vào)': 'bank_inflow',
                    'Chi tiết giao dịch ngân hàng (tiền ra)': 'bank_outflow',
                    'Số dư tiền mặt tại quỹ': 'cash_balance',
                    'Lợi nhuận gộp theo ngày ĐVT': 'gross_profit',
                    'Tỷ lệ nợ trễ hạn thanh toán trên tổng công nợ': 'debt_ratio',
                    'Giá nguyên liệu': 'material_cost',
                    'Chi phí năng lượng (điện, củi, nước)': 'energy_cost',
                    'Chi phí nhân công': 'labor_cost'
                }
            },
            'viet_farm': {
                'target_table': 'production_metrics',
                'column_mapping': {
                    'Sản lượng nguyên liệu sản xuất (kg)': 'raw_material_volume',
                    'Sản lượng thành phẩm sản xuất (kg)': 'finished_product_volume',
                    'Sản lượng hàng túi 10kg (kg)': 'product_10kg_volume',
                    'Sản lượng hàng túi 5kg (kg)': 'product_5kg_volume',
                    'Sản lượng hàng túi nhỏ (kg)': 'product_small_volume',
                    'Sản lượng hàng aseptic (kg)': 'aseptic_volume',
                    'Sản lượng thành phẩm tiêu thụ (tổng sản lượng) (Kg)': 'total_consumption',
                    'Hiệu suất thu hồi hàng cắt (%)': 'efficiency_cut',
                    'Hiệu suất thu hồi hàng aseptic (%)': 'efficiency_aseptic',
                    '% lỗi sản xuất/tổng sản xuất': 'error_rate',
                    '% lỗi khiếu nại/tổng xuất hàng': 'complaint_rate',
                    'Sự cố dừng máy ngưng sản xuất ( phút)': 'downtime_minutes'
                }
            },
            'nhan_su': {
                'target_table': 'hr_metrics',
                'column_mapping': {
                    'Hồ sơ ứng viên nhận được': 'applications_received',
                    'Lịch phỏng vấn hoàn thành': 'interviews_completed',
                    'Số nhân viên tuyển dụng': 'new_hires',
                    'Tổng số nhân viên đi làm': 'total_employees',
                    'Tổng số NV đi trễ': 'late_employees',
                    'Tổng số NV vắng không phép': 'absent_employees',
                    'Tổng số NV OT': 'overtime_employees',
                    'Số khóa đào tạo trong ngày': 'training_sessions',
                    'Tổng số NV tham gia': 'training_participants'
                }
            },
            'phap_ly': {
                'target_table': 'legal_metrics',
                'column_mapping': {
                    'Số hợp đồng đang rà soát': 'contracts_under_review',
                    'Số phụ lục hợp đồng đang rà soát': 'contract_amendments',
                    'Số hợp đồng, phụ lục mới được lưu trữ': 'new_contracts_stored',
                    'Số hợp đồng mới nhận từ các phòng/ban': 'new_contracts_received',
                    'Số hợp đồng có điều khoản cần đàm phán lại': 'contracts_need_negotiation',
                    'Số hợp đồng có tranh chấp phát sinh': 'contract_disputes',
                    'Tỷ lệ báo cáo gửi đúng hạn': 'compliance_rate',
                    'Số lần bị nhắc nhở từ cơ quan quản lý': 'regulatory_warnings'
                }
            },
            'thu_mua_cung_ung': {
                'target_table': 'procurement_metrics',
                'column_mapping': {
                    'Tổng số NCC hiện tại': 'total_suppliers',
                    'Tổng số NCC chính': 'main_suppliers',
                    'Tổng số NCC đã đánh giá': 'evaluated_suppliers',
                    'Số lượng kế hoạch theo tháng': 'planned_orders',
                    'Số đơn hàng mới có kế hoạch': 'new_planned_orders',
                    'Số đơn hàng mới phát sinh': 'emergency_orders',
                    'Số đơn giao đúng tiến độ': 'on_time_deliveries',
                    'Số đơn giao trễ hạn': 'late_deliveries',
                    'Số lượng hàng trả lại': 'returned_items',
                    'Chi phí tiết kiệm nhờ thương lượng giá': 'cost_savings',
                    'Tổng chi phí mua NVL': 'total_procurement_cost'
                }
            }
        }
        
        # Print mappings
        for file_name, mapping_info in file_mappings.items():
            if file_name in self.dataframes:
                print(f"\n📄 {file_name.upper()} -> {mapping_info['target_table'].upper()}")
                print("-" * 50)
                df = self.dataframes[file_name]
                available_columns = set(df.columns)
                
                for source_col, target_col in mapping_info['column_mapping'].items():
                    status = "✓" if source_col in available_columns else "✗"
                    print(f"  {status} {source_col[:50]}... -> {target_col}")
        
        return file_mappings
    
    def run_full_analysis(self) -> None:
        """Run complete analysis pipeline"""
        print("🚀 Starting Farm Data Analysis")
        print("="*60)
        
        self.load_data()
        self.analyze_data_quality()
        self.identify_common_fields()
        self.detect_duplicates()
        schema = self.suggest_normalization_schema()
        mapping = self.generate_data_mapping()
        
        print("\n" + "="*60)
        print("✅ ANALYSIS COMPLETE")
        print("="*60)
        print("\nNext steps:")
        print("1. Review the suggested schema")
        print("2. Run the data preprocessing script")
        print("3. Create the PostgreSQL database")
        print("4. Load the cleaned data")

if __name__ == "__main__":
    analyzer = FarmDataAnalyzer()
    analyzer.run_full_analysis() 