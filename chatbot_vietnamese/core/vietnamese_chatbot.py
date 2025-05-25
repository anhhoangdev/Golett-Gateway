#!/usr/bin/env python3
"""
Vietnamese Business Intelligence Chatbot with Dynamic CubeJS Integration
"""

import os
import sys
from typing import Dict, Any, List

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewai import Agent, Task, Crew, Process
from golett.tools.cube.query_tools import BuildCubeQueryTool, ExecuteCubeQueryTool, AnalyzeDataPointTool
from chatbot_vietnamese.utils.dynamic_schema_mapper import DynamicCubeJSSchemaMapper
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class VietnameseCubeJSChatbot:
    """
    Vietnamese Business Intelligence Chatbot with Dynamic CubeJS Schema Integration
    """
    
    def __init__(self, cubejs_api_url: str = "http://localhost:4000", cubejs_api_token: str = None):
        """
        Initialize the Vietnamese CubeJS Chatbot with dynamic schema mapping
        
        Args:
            cubejs_api_url: CubeJS API URL
            cubejs_api_token: Optional API token
        """
        self.cubejs_api_url = cubejs_api_url
        self.cubejs_api_token = cubejs_api_token
        
        # Initialize dynamic schema mapper
        self.schema_mapper = DynamicCubeJSSchemaMapper(cubejs_api_url, cubejs_api_token)
        
        # Initialize CubeJS tools
        self.build_query_tool = BuildCubeQueryTool(
            api_url=cubejs_api_url,
            api_token=cubejs_api_token
        )
        
        self.execute_query_tool = ExecuteCubeQueryTool(
            api_url=cubejs_api_url,
            api_token=cubejs_api_token
        )
        
        self.analyze_tool = AnalyzeDataPointTool(
            api_url=cubejs_api_url,
            api_token=cubejs_api_token
        )
        
        # Load fresh schema
        self.schema_info = self.schema_mapper.refresh_schema()
        
        logger.info("✅ Vietnamese CubeJS Chatbot initialized with dynamic schema")
    
    def _create_data_analyst_agent(self) -> Agent:
        """Create the Vietnamese data analyst agent with ultra-simple instructions"""
        
        # Generate clean schema context
        schema_context = self._generate_schema_context()
        
        return Agent(
            role="Vietnamese Data Analyst",
            goal="Answer Vietnamese business questions using data",
            backstory=f"""
You are a data analyst who answers Vietnamese business questions.

AVAILABLE DATA:
{schema_context}

TOOLS AVAILABLE:
1. BuildCubeQuery - Creates a data query
2. ExecuteCubeQuery - Runs the query to get data  
3. AnalyzeDataPoint - Analyzes the data results

WORKFLOW:
Step 1: Use BuildCubeQuery with appropriate measures and cube
Step 2: Use ExecuteCubeQuery with the query from step 1
Step 3: Use AnalyzeDataPoint with the results from step 2
Step 4: Answer in Vietnamese with specific data

CUBE SELECTION:
- Companies questions → companies cube
- Sales questions → sales_metrics cube  
- Financial questions → financial_metrics cube
- Production questions → production_metrics cube

IMPORTANT: Always use the exact tool names and pass results between tools.
            """,
            tools=[self.build_query_tool, self.execute_query_tool, self.analyze_tool],
            verbose=True,
            allow_delegation=False,
            llm="gpt-4o-mini"
        )
    
    def _generate_schema_context(self) -> str:
        """Generate comprehensive schema context for the agent"""
        return """
## CUBEJS SCHEMA DOCUMENTATION

### AVAILABLE CUBES AND FIELDS

**PRODUCTION METRICS** (production_metrics)
- Measures: production_metrics.count, production_metrics.raw_material_volume, production_metrics.finished_product_volume, production_metrics.product_10kg_volume, production_metrics.product_5kg_volume
- Dimensions: production_metrics.metric_id, production_metrics.company_code, production_metrics.created_at

**SALES METRICS** (sales_metrics)  
- Measures: sales_metrics.count, sales_metrics.total_revenue, sales_metrics.total_orders, sales_metrics.new_customers, sales_metrics.customer_visits
- Dimensions: sales_metrics.metric_id, sales_metrics.sales_channel, sales_metrics.created_at

**FINANCIAL METRICS** (financial_metrics)
- Measures: financial_metrics.count, financial_metrics.bank_inflow, financial_metrics.bank_outflow, financial_metrics.cash_balance, financial_metrics.debt_ratio
- Dimensions: financial_metrics.metric_id, financial_metrics.created_at

**HR METRICS** (hr_metrics)
- Measures: hr_metrics.count, hr_metrics.applications_received, hr_metrics.interviews_completed, hr_metrics.new_hires, hr_metrics.total_employees
- Dimensions: hr_metrics.metric_id, hr_metrics.created_at

**EXECUTIVE DASHBOARD** (executive_dashboard)
- Measures: executive_dashboard.total_daily_revenue, executive_dashboard.total_costs, executive_dashboard.total_labor, executive_dashboard.operational_efficiency, executive_dashboard.cash_flow_ratio
- Dimensions: executive_dashboard.report_date, executive_dashboard.report_type, executive_dashboard.company_name, executive_dashboard.department_type

**FINANCIAL PERFORMANCE** (financial_performance)
- Measures: financial_performance.bank_inflow, financial_performance.bank_outflow, financial_performance.cash_balance, financial_performance.debt_ratio, financial_performance.management_cost
- Dimensions: financial_performance.metric_id, financial_performance.created_at, financial_performance.report_date, financial_performance.report_type, financial_performance.company_name

**COMPANIES** (companies)
- Measures: companies.count
- Dimensions: companies.company_id, companies.company_name, companies.company_code, companies.department_type, companies.created_at

### CRITICAL FIELD NAMING RULES
1. **ALWAYS use cube prefix**: production_metrics.count (✓) NOT count (✗)
2. **Exact field names**: Use exactly as shown above
3. **Case sensitive**: production_metrics.count (✓) NOT Production_Metrics.Count (✗)

### QUERY CONSTRUCTION EXAMPLES

**Simple Count Query:**
{{
  "measures": ["companies.count"],
  "dimensions": ["companies.company_name"]
}}

**Production Analysis:**
{{
  "measures": ["production_metrics.raw_material_volume", "production_metrics.finished_product_volume"],
  "dimensions": ["production_metrics.company_code"],
  "time_dimensions": [{{
    "dimension": "production_metrics.created_at",
    "granularity": "day"
  }}]
}}

**Financial Performance:**
{{
  "measures": ["financial_performance.bank_inflow", "financial_performance.bank_outflow"],
  "dimensions": ["financial_performance.company_name"],
  "filters": [{{
    "member": "financial_performance.report_date",
    "operator": "inDateRange",
    "values": ["2024-01-01", "2024-12-31"]
  }}]
}}

### SUPPORTED OPERATORS
- equals, notEquals
- gt, gte, lt, lte  
- contains, notContains
- inDateRange, notInDateRange
- set, notSet

### TIME GRANULARITIES
- second, minute, hour, day, week, month, quarter, year

### VIETNAMESE BUSINESS QUERIES MAPPING
- "doanh thu" → sales_metrics.total_revenue
- "đơn hàng" → sales_metrics.total_orders  
- "khách hàng mới" → sales_metrics.new_customers
- "sản xuất" → production_metrics.finished_product_volume
- "nguyên liệu" → production_metrics.raw_material_volume
- "tiền mặt" → financial_metrics.cash_balance
- "dòng tiền vào" → financial_metrics.bank_inflow
- "dòng tiền ra" → financial_metrics.bank_outflow
- "nhân viên" → hr_metrics.total_employees
- "tuyển dụng" → hr_metrics.new_hires
"""
    
    def _create_analysis_task(self, question: str) -> Task:
        """Create analysis task with simplified instructions"""
        
        return Task(
            description=f"""
            Answer this Vietnamese business question: "{question}"
            
            Follow these steps:
            1. Use BuildCubeQuery to create a query for the relevant data
            2. Use ExecuteCubeQuery to get the data
            3. Use AnalyzeDataPoint to analyze the results
            4. Provide a comprehensive answer in Vietnamese
            
            Remember:
            - Use appropriate cube based on the question topic
            - Include specific numbers and insights
            - Explain business implications
            """,
            expected_output="Detailed Vietnamese business analysis with specific data points and insights",
            agent=self._create_data_analyst_agent()
        )
    
    def ask(self, question: str) -> str:
        """
        Ask a business question in Vietnamese and get analysis
        
        Args:
            question: Vietnamese business question
            
        Returns:
            Detailed analysis in Vietnamese
        """
        try:
            logger.info(f"🤔 Processing Vietnamese question: {question}")
            
            # Refresh schema if needed
            if not self.schema_info or "error" in self.schema_info:
                logger.info("🔄 Refreshing schema...")
                self.schema_info = self.schema_mapper.refresh_schema()
            
            # Create and execute analysis task
            task = self._create_analysis_task(question)
            
            crew = Crew(
                agents=[self._create_data_analyst_agent()],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            
            logger.info("✅ Analysis completed successfully")
            return str(result)
            
        except Exception as e:
            error_msg = f"❌ Lỗi khi phân tích câu hỏi: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def chat(self, message: str) -> str:
        """
        Chat interface method - alias for ask() method
        Compatible with Ollama-style chat interfaces
        
        Args:
            message: Vietnamese business question or message
            
        Returns:
            Detailed analysis in Vietnamese
        """
        return self.ask(message)
    
    def get_schema_summary(self) -> str:
        """Get a summary of available data cubes in Vietnamese"""
        if "error" in self.schema_info:
            return f"❌ Không thể tải thông tin schema: {self.schema_info['error']}"
        
        summary_parts = [
            "📊 **TỔNG QUAN DỮ LIỆU KINH DOANH**\n",
            f"🔢 Tổng số cube: {self.schema_info['total_cubes']}",
            f"🕐 Cập nhật: {self.schema_info['last_updated']}\n"
        ]
        
        for cube_name, cube_info in self.schema_info["cubes"].items():
            vietnamese_mappings = self.schema_info["vietnamese_mappings"].get(cube_name, {})
            
            summary_parts.append(f"### 🔹 {cube_name}")
            summary_parts.append(f"- **Chỉ số**: {len(cube_info['measures'])} measures")
            summary_parts.append(f"- **Chiều dữ liệu**: {len(cube_info['dimensions'])} dimensions")
            
            if vietnamese_mappings.get("keywords"):
                summary_parts.append(f"- **Từ khóa**: {', '.join(vietnamese_mappings['keywords'][:3])}")
            
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def test_connection(self) -> Dict[str, Any]:
        """Test CubeJS connection and schema loading"""
        try:
            schema = self.schema_mapper.refresh_schema()
            
            if "error" in schema:
                return {
                    "status": "error",
                    "message": f"Không thể kết nối CubeJS: {schema['error']}"
                }
            
            return {
                "status": "success",
                "message": f"✅ Kết nối thành công! Đã tải {schema['total_cubes']} cubes",
                "cubes": list(schema["cubes"].keys()),
                "last_updated": schema["last_updated"]
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"❌ Lỗi kết nối: {str(e)}"
            }

def main():
    """Test the Vietnamese chatbot"""
    print("🇻🇳 Vietnamese Business Intelligence Chatbot")
    print("=" * 50)
    
    # Initialize chatbot
    chatbot = VietnameseCubeJSChatbot()
    
    # Test connection
    connection_test = chatbot.test_connection()
    print(f"📡 {connection_test['message']}")
    
    if connection_test["status"] == "error":
        return
    
    # Show schema summary
    print("\n" + chatbot.get_schema_summary())
    
    # Test questions
    test_questions = [
        "Doanh thu tháng này như thế nào?",
        "Chi phí năng lượng tuần trước bao nhiêu?",
        "Số lượng nhân viên hiện tại?",
        "Hiệu suất sản xuất hôm nay ra sao?"
    ]
    
    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"❓ **CÂUHỎI**: {question}")
        print("="*60)
        
        try:
            answer = chatbot.ask(question)
            print(answer)
        except Exception as e:
            print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main() 