from typing import Any, Dict, List, Optional, Union
import os

from crewai import Agent
from crewai.tools import BaseTool
from golett.tools.cube import (
    CubeJsMetadataTool,
    ExecuteCubeQueryTool,
    BuildCubeQueryTool,
    AnalyzeDataPointTool,
    LoadCubeSchemasTool,
    AnalyzeCubeSchemasTool
)
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class BiQueryAgent:
    """
    Agent specialized in handling BI queries using Cube.js.
    
    This agent is equipped with Cube.js tools for querying and analyzing
    business intelligence data.
    """
    
    def __init__(
        self,
        api_url: str,
        api_token: Optional[str] = None,
        schemas_path: Optional[str] = None,
        llm_model: str = "gpt-4o",
        verbose: bool = False
    ):
        """
        Initialize the BI query agent.
        
        Args:
            api_url: Base URL of the Cube.js API
            api_token: Optional API token for authentication
            schemas_path: Path to Cube.js schema files
            llm_model: LLM model to use for the agent
            verbose: Whether to enable verbose logging
        """
        self.api_url = api_url
        self.api_token = api_token or os.environ.get("CUBEJS_API_TOKEN")
        self.schemas_path = schemas_path or os.environ.get("CUBEJS_SCHEMAS_PATH", "schemas")
        self.llm_model = llm_model
        self.verbose = verbose
        
        # Initialize the agent and tools
        self._initialize_tools()
        self._create_agent()
        
        logger.info(f"BI Query Agent initialized with Cube.js API: {api_url}")
    
    def _initialize_tools(self):
        """Initialize the CrewAI tools for Cube.js."""
        self.tools = [
            CubeJsMetadataTool(
                api_url=self.api_url,
                api_token=self.api_token
            ),
            ExecuteCubeQueryTool(
                api_url=self.api_url,
                api_token=self.api_token
            ),
            BuildCubeQueryTool(
                api_url=self.api_url,
                api_token=self.api_token
            ),
            AnalyzeDataPointTool(
                api_url=self.api_url,
                api_token=self.api_token
            ),
            LoadCubeSchemasTool(
                schemas_path=self.schemas_path
            ),
            AnalyzeCubeSchemasTool(
                schemas_path=self.schemas_path
            )
        ]
        
        logger.info(f"Initialized {len(self.tools)} Cube.js tools for the BI agent")
    
    def _create_agent(self):
        """Create the CrewAI agent with tools."""
        self.agent = Agent(
            role="Business Intelligence Analyst",
            goal="Extract actionable insights from BI data using Cube.js queries",
            backstory="""You are an expert Business Intelligence analyst with deep knowledge of 
                      data analysis, SQL, and business metrics. You're skilled at understanding 
                      complex data models and translating business questions into precise queries.
                      You use Cube.js to analyze data and extract meaningful insights.""",
            verbose=self.verbose,
            allow_delegation=False,
            tools=self.tools,
            llm_model=self.llm_model
        )
        
        logger.info("Created BI Query Agent with CrewAI")
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Execute a business intelligence query based on a natural language question.
        
        Args:
            question: The business question to answer
            
        Returns:
            The query results and analysis
        """
        task_description = f"""
        Answer the following business intelligence question by:
        1. Reviewing available data models and schemas using the LoadCubeSchemas tool
        2. Understanding the available measures and dimensions using the CubeJsMetadata tool
        3. Building and executing appropriate Cube.js queries
        4. Analyzing the results to provide insights
        
        Question: {question}
        
        Return both the data and your analysis of what it means in business terms.
        """
        
        try:
            # Execute the task
            result = self.agent.execute_task(task_description)
            return {
                "success": True,
                "result": result,
                "question": question
            }
        except Exception as e:
            logger.error(f"Error executing BI query: {e}")
            return {
                "success": False,
                "error": str(e),
                "question": question
            }
    
    def analyze_trend(self, metric: str, time_period: str, dimensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze a trend for a specific metric over time.
        
        Args:
            metric: The metric to analyze (e.g., "Orders.count")
            time_period: Time period for analysis (e.g., "last 6 months", "2023")
            dimensions: Optional dimensions to break down the analysis by
            
        Returns:
            Trend analysis results
        """
        dimensions_text = ", ".join(dimensions) if dimensions else "none"
        
        task_description = f"""
        Analyze the trend for the metric '{metric}' over the time period '{time_period}' 
        with dimensions: {dimensions_text}.
        
        1. Determine the appropriate time dimension and granularity
        2. Build a query to analyze the trend
        3. Execute the query and retrieve the data
        4. Analyze if the trend is increasing, decreasing, or stable
        5. Identify any notable patterns, seasonality, or anomalies
        
        Provide a detailed analysis of the trend with supporting data.
        """
        
        try:
            # Execute the task
            result = self.agent.execute_task(task_description)
            return {
                "success": True,
                "result": result,
                "metric": metric,
                "time_period": time_period,
                "dimensions": dimensions
            }
        except Exception as e:
            logger.error(f"Error analyzing trend: {e}")
            return {
                "success": False,
                "error": str(e),
                "metric": metric,
                "time_period": time_period,
                "dimensions": dimensions
            }
    
    def compare_metrics(self, metrics: List[str], filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Compare multiple metrics with optional filters.
        
        Args:
            metrics: List of metrics to compare
            filters: Optional filters to apply
            
        Returns:
            Comparison analysis results
        """
        metrics_text = ", ".join(metrics)
        filters_text = str(filters) if filters else "none"
        
        task_description = f"""
        Compare the following metrics: {metrics_text} with filters: {filters_text}.
        
        1. Build queries to retrieve data for each metric
        2. Apply the specified filters to ensure consistent comparison
        3. Compare the metrics in terms of absolute values and relative performance
        4. Identify correlations or relationships between the metrics
        
        Provide a detailed comparison with insights about how these metrics relate to each other.
        """
        
        try:
            # Execute the task
            result = self.agent.execute_task(task_description)
            return {
                "success": True,
                "result": result,
                "metrics": metrics,
                "filters": filters
            }
        except Exception as e:
            logger.error(f"Error comparing metrics: {e}")
            return {
                "success": False,
                "error": str(e),
                "metrics": metrics,
                "filters": filters
            }
    
    def generate_dashboard_data(self, dashboard_name: str, metrics: List[str]) -> Dict[str, Any]:
        """
        Generate data for a dashboard with multiple metrics.
        
        Args:
            dashboard_name: Name of the dashboard
            metrics: List of metrics to include in the dashboard
            
        Returns:
            Dashboard data and insights
        """
        metrics_text = ", ".join(metrics)
        
        task_description = f"""
        Generate data for the '{dashboard_name}' dashboard with the following metrics: {metrics_text}.
        
        1. For each metric, determine the most appropriate visualization type
        2. Build and execute queries to retrieve the necessary data
        3. Structure the data in a format suitable for visualization
        4. Provide insights for each metric and the dashboard as a whole
        
        Return the query results and analysis for each component of the dashboard.
        """
        
        try:
            # Execute the task
            result = self.agent.execute_task(task_description)
            return {
                "success": True,
                "result": result,
                "dashboard_name": dashboard_name,
                "metrics": metrics
            }
        except Exception as e:
            logger.error(f"Error generating dashboard data: {e}")
            return {
                "success": False,
                "error": str(e),
                "dashboard_name": dashboard_name,
                "metrics": metrics
            } 