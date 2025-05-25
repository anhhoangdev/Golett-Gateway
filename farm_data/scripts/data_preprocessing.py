#!/usr/bin/env python3
"""
Farm Data Preprocessing Script
Cleans, deduplicates, and normalizes TSV data for PostgreSQL insertion
"""

import pandas as pd
import numpy as np
import os
import glob
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import warnings
warnings.filterwarnings('ignore')

class FarmDataPreprocessor:
    def __init__(self, data_dir: str = "raw_data", output_dir: str = "processed_data"):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.files = glob.glob(os.path.join(data_dir, "*.tsv"))
        self.dataframes = {}
        self.processed_data = {}
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Company mapping
        self.company_mapping = {
            'tai_chinh_ke_toan': {'name': 'Tài chính kế toán', 'code': 'TCKT', 'type': 'Finance'},
            'phap_ly': {'name': 'Phòng pháp lý', 'code': 'PL', 'type': 'Legal'},
            'nhan_su': {'name': 'Phòng nhân sự', 'code': 'NS', 'type': 'HR'},
            'thu_mua_cung_ung': {'name': 'Thu mua cung ứng', 'code': 'TMCU', 'type': 'Procurement'},
            'rnd': {'name': 'Nghiên cứu phát triển', 'code': 'RND', 'type': 'R&D'},
            'inter_b2b': {'name': 'Inter B2B', 'code': 'IB2B', 'type': 'Sales'},
            'local_b2b': {'name': 'Local B2B', 'code': 'LB2B', 'type': 'Sales'},
            'sun_wind': {'name': 'Sun Wind', 'code': 'SW', 'type': 'Production'},
            'vncc': {'name': 'VNCC', 'code': 'VNCC', 'type': 'Production'},
            'mui_dinh': {'name': 'Mũi Dinh', 'code': 'MD', 'type': 'Production'},
            'viet_farm': {'name': 'Viet Farm', 'code': 'VF', 'type': 'Production'}
        }
    
    def load_data(self) -> None:
        """Load all TSV files into dataframes"""
        print("Loading TSV files for preprocessing...")
        for file_path in self.files:
            file_name = os.path.basename(file_path).replace('.tsv', '')
            try:
                # Try different encodings
                for encoding in ['utf-8', 'utf-8-sig', 'latin-1']:
                    try:
                        df = pd.read_csv(file_path, sep='\t', encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                self.dataframes[file_name] = df
                print(f"✓ Loaded {file_name}: {df.shape[0]} rows, {df.shape[1]} columns")
            except Exception as e:
                print(f"✗ Error loading {file_name}: {e}")
    
    def clean_date_columns(self, df: pd.DataFrame, date_columns: List[str]) -> pd.DataFrame:
        """Clean and standardize date columns"""
        df_clean = df.copy()
        
        for col in date_columns:
            if col in df_clean.columns:
                # Convert to string first
                df_clean[col] = df_clean[col].astype(str)
                
                # Handle different date formats
                def parse_date(date_str):
                    if pd.isna(date_str) or date_str == 'nan' or date_str == '':
                        return None
                    
                    date_str = str(date_str).strip()
                    
                    # Handle Excel serial dates (5-digit numbers)
                    if date_str.replace('.', '').replace(',', '').isdigit():
                        try:
                            # Remove commas and convert to float
                            serial_date = float(date_str.replace(',', ''))
                            if 40000 <= serial_date <= 50000:  # Reasonable range for Excel dates
                                # Excel epoch starts from 1900-01-01, but with a bug (1900 is not a leap year)
                                base_date = datetime(1899, 12, 30)
                                return base_date + timedelta(days=serial_date)
                        except:
                            pass
                    
                    # Try standard date parsing
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except:
                            continue
                    
                    return None
                
                df_clean[col] = df_clean[col].apply(parse_date)
        
        return df_clean
    
    def clean_numeric_columns(self, df: pd.DataFrame, numeric_columns: List[str]) -> pd.DataFrame:
        """Clean and standardize numeric columns"""
        df_clean = df.copy()
        
        for col in numeric_columns:
            if col in df_clean.columns:
                def clean_numeric(value):
                    if pd.isna(value) or value == '' or value == 'nan':
                        return None
                    
                    # Convert to string and clean
                    value_str = str(value).strip()
                    
                    # Remove common non-numeric characters
                    value_str = re.sub(r'[,\s]', '', value_str)
                    
                    # Handle negative values in parentheses
                    if value_str.startswith('(') and value_str.endswith(')'):
                        value_str = '-' + value_str[1:-1]
                    
                    # Try to convert to float
                    try:
                        return float(value_str)
                    except:
                        # If it contains letters, it might be text data
                        if any(c.isalpha() for c in value_str):
                            return None
                        return None
                
                df_clean[col] = df_clean[col].apply(clean_numeric)
        
        return df_clean
    
    def remove_duplicates(self, df: pd.DataFrame, date_columns: List[str]) -> pd.DataFrame:
        """Remove duplicate rows based on date columns and other criteria"""
        df_clean = df.copy()
        
        # Remove completely empty rows
        df_clean = df_clean.dropna(how='all')
        
        # Remove exact duplicates
        df_clean = df_clean.drop_duplicates()
        
        # Remove duplicates based on date columns if available
        if date_columns:
            primary_date_col = date_columns[0]
            if primary_date_col in df_clean.columns:
                # Keep the last occurrence for each date (most recent data)
                df_clean = df_clean.drop_duplicates(subset=[primary_date_col], keep='last')
        
        return df_clean
    
    def identify_column_types(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Identify column types based on content and names"""
        column_types = {
            'date': [],
            'numeric': [],
            'text': [],
            'issues': []
        }
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Identify date columns
            if any(keyword in col_lower for keyword in ['ngày', 'date', 'tạo', 'báo cáo']):
                column_types['date'].append(col)
            # Identify issue/problem columns
            elif any(keyword in col_lower for keyword in ['vấn đề', 'issue', 'problem', 'xảy ra']):
                column_types['issues'].append(col)
            # Identify text columns
            elif any(keyword in col_lower for keyword in ['mô tả', 'description', 'ghi chú', 'note']):
                column_types['text'].append(col)
            else:
                # Check if column contains mostly numeric data
                sample_values = df[col].dropna().head(20)
                if len(sample_values) > 0:
                    numeric_count = 0
                    for val in sample_values:
                        val_str = str(val).strip()
                        # Remove commas and check if it's numeric
                        clean_val = re.sub(r'[,\s]', '', val_str)
                        try:
                            float(clean_val)
                            numeric_count += 1
                        except:
                            pass
                    
                    if numeric_count / len(sample_values) > 0.7:
                        column_types['numeric'].append(col)
                    else:
                        column_types['text'].append(col)
        
        return column_types
    
    def process_file(self, file_name: str, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Process a single file and return normalized data"""
        print(f"\n🔄 Processing {file_name}...")
        
        # Identify column types
        column_types = self.identify_column_types(df)
        
        # Clean date columns
        df_clean = self.clean_date_columns(df, column_types['date'])
        
        # Clean numeric columns
        df_clean = self.clean_numeric_columns(df_clean, column_types['numeric'])
        
        # Remove duplicates
        df_clean = self.remove_duplicates(df_clean, column_types['date'])
        
        # Extract company information
        company_info = self.company_mapping.get(file_name, {
            'name': file_name.replace('_', ' ').title(),
            'code': file_name.upper()[:10],
            'type': 'Unknown'
        })
        
        # Create normalized tables
        processed_tables = {}
        
        # 1. Company table entry
        company_df = pd.DataFrame([{
            'company_name': company_info['name'],
            'company_code': company_info['code'],
            'department_type': company_info['type']
        }])
        processed_tables['companies'] = company_df
        
        # 2. Daily reports table
        if column_types['date']:
            primary_date_col = column_types['date'][0]
            secondary_date_col = column_types['date'][1] if len(column_types['date']) > 1 else None
            
            reports_data = []
            for _, row in df_clean.iterrows():
                if pd.notna(row[primary_date_col]):
                    report_entry = {
                        'company_code': company_info['code'],
                        'report_date': row[primary_date_col],
                        'created_date': row[secondary_date_col] if secondary_date_col else None,
                        'report_type': file_name
                    }
                    reports_data.append(report_entry)
            
            if reports_data:
                reports_df = pd.DataFrame(reports_data)
                processed_tables['daily_reports'] = reports_df
        
        # 3. Metrics table based on file type
        metrics_data = []
        
        if column_types['date'] and len(df_clean) > 0:
            primary_date_col = column_types['date'][0]
            
            for _, row in df_clean.iterrows():
                if pd.notna(row[primary_date_col]):
                    metric_entry = {'report_date': row[primary_date_col]}
                    
                    # Add all numeric columns
                    for col in column_types['numeric']:
                        if col in df_clean.columns and pd.notna(row[col]):
                            # Clean column name for database
                            clean_col_name = re.sub(r'[^\w]', '_', col.lower())
                            clean_col_name = re.sub(r'_+', '_', clean_col_name).strip('_')
                            metric_entry[clean_col_name] = row[col]
                    
                    if len(metric_entry) > 1:  # More than just the date
                        metrics_data.append(metric_entry)
        
        if metrics_data:
            metrics_df = pd.DataFrame(metrics_data)
            table_name = f"{file_name}_metrics"
            processed_tables[table_name] = metrics_df
        
        # 4. Issues table
        if column_types['issues']:
            issues_data = []
            primary_date_col = column_types['date'][0] if column_types['date'] else None
            
            for _, row in df_clean.iterrows():
                for issue_col in column_types['issues']:
                    if pd.notna(row[issue_col]) and str(row[issue_col]).strip():
                        issue_entry = {
                            'report_date': row[primary_date_col] if primary_date_col else None,
                            'issue_description': str(row[issue_col]).strip(),
                            'severity': 'medium',  # Default severity
                            'status': 'open'
                        }
                        issues_data.append(issue_entry)
            
            if issues_data:
                issues_df = pd.DataFrame(issues_data)
                processed_tables['issues_log'] = issues_df
        
        print(f"  ✓ Created {len(processed_tables)} normalized tables")
        for table_name, table_df in processed_tables.items():
            print(f"    - {table_name}: {len(table_df)} rows")
        
        return processed_tables
    
    def process_all_files(self) -> None:
        """Process all files and create normalized datasets"""
        print("\n" + "="*60)
        print("DATA PREPROCESSING")
        print("="*60)
        
        all_companies = []
        all_reports = []
        all_issues = []
        all_metrics = {}
        
        for file_name, df in self.dataframes.items():
            processed_tables = self.process_file(file_name, df)
            
            # Collect data for master tables
            if 'companies' in processed_tables:
                all_companies.append(processed_tables['companies'])
            
            if 'daily_reports' in processed_tables:
                all_reports.append(processed_tables['daily_reports'])
            
            if 'issues_log' in processed_tables:
                all_issues.append(processed_tables['issues_log'])
            
            # Collect metrics tables
            for table_name, table_df in processed_tables.items():
                if table_name.endswith('_metrics'):
                    if table_name not in all_metrics:
                        all_metrics[table_name] = []
                    all_metrics[table_name].append(table_df)
        
        # Combine and save master tables
        if all_companies:
            companies_df = pd.concat(all_companies, ignore_index=True)
            companies_df = companies_df.drop_duplicates(subset=['company_code'])
            self.save_processed_data('companies', companies_df)
        
        if all_reports:
            reports_df = pd.concat(all_reports, ignore_index=True)
            reports_df = reports_df.drop_duplicates()
            self.save_processed_data('daily_reports', reports_df)
        
        if all_issues:
            issues_df = pd.concat(all_issues, ignore_index=True)
            self.save_processed_data('issues_log', issues_df)
        
        # Save metrics tables
        for table_name, table_list in all_metrics.items():
            if table_list:
                metrics_df = pd.concat(table_list, ignore_index=True)
                self.save_processed_data(table_name, metrics_df)
    
    def save_processed_data(self, table_name: str, df: pd.DataFrame) -> None:
        """Save processed data to CSV files"""
        output_path = os.path.join(self.output_dir, f"{table_name}.csv")
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"💾 Saved {table_name}: {len(df)} rows -> {output_path}")
    
    def generate_summary_report(self) -> None:
        """Generate a summary report of the preprocessing"""
        print("\n" + "="*60)
        print("PREPROCESSING SUMMARY")
        print("="*60)
        
        # Count processed files
        csv_files = glob.glob(os.path.join(self.output_dir, "*.csv"))
        
        print(f"\n📊 PROCESSING RESULTS:")
        print(f"  - Input TSV files: {len(self.files)}")
        print(f"  - Output CSV files: {len(csv_files)}")
        
        print(f"\n📁 OUTPUT FILES:")
        for csv_file in csv_files:
            file_name = os.path.basename(csv_file)
            try:
                df = pd.read_csv(csv_file)
                print(f"  - {file_name}: {len(df)} rows, {len(df.columns)} columns")
            except:
                print(f"  - {file_name}: Error reading file")
        
        print(f"\n📂 Files saved to: {os.path.abspath(self.output_dir)}")
        
        # Data quality summary
        print(f"\n🔍 DATA QUALITY IMPROVEMENTS:")
        total_original_rows = sum(len(df) for df in self.dataframes.values())
        total_processed_rows = 0
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                total_processed_rows += len(df)
            except:
                pass
        
        print(f"  - Original total rows: {total_original_rows}")
        print(f"  - Processed total rows: {total_processed_rows}")
        print(f"  - Data normalization: Complete")
        print(f"  - Duplicate removal: Applied")
        print(f"  - Date standardization: Applied")
        print(f"  - Numeric cleaning: Applied")
    
    def run_preprocessing(self) -> None:
        """Run the complete preprocessing pipeline"""
        print("🚀 Starting Farm Data Preprocessing")
        print("="*60)
        
        self.load_data()
        self.process_all_files()
        self.generate_summary_report()
        
        print("\n" + "="*60)
        print("✅ PREPROCESSING COMPLETE")
        print("="*60)
        print("\nNext steps:")
        print("1. Review the processed CSV files")
        print("2. Create PostgreSQL database schema")
        print("3. Load data into PostgreSQL")
        print("4. Set up data validation and monitoring")

if __name__ == "__main__":
    preprocessor = FarmDataPreprocessor()
    preprocessor.run_preprocessing() 