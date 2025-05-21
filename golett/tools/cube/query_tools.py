from typing import Any, Dict, List, Optional, Union
import json

from crewai.tools import BaseTool
from golett.tools.cube.client import CubeJsClient
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class CubeJsMetadataTool(BaseTool):
    """Tool for retrieving Cube.js metadata."""
    
    name: str = "CubeJsMetadata"
    description: str = "Get metadata about available cubes, measures, and dimensions from Cube.js"
    
    def __init__(
        self, 
        api_url: str,
        api_token: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize the Cube.js metadata tool.
        
        Args:
            api_url: Base URL of the Cube.js API
            api_token: Optional API token for authentication
            timeout: Request timeout in seconds
        """
        super().__init__()
        self.client = CubeJsClient(api_url, api_token, timeout)
        logger.info("Initialized Cube.js metadata tool")
        
    def _run(self, cube_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metadata from Cube.js.
        
        Args:
            cube_name: Optional specific cube to get metadata for
            
        Returns:
            Metadata about cubes, measures, and dimensions
        """
        try:
            meta = self.client.meta()
            
            if cube_name:
                # Filter to just the requested cube
                cubes = [cube for cube in meta.get("cubes", []) if cube.get("name") == cube_name]
                if not cubes:
                    return {"error": f"Cube '{cube_name}' not found"}
                meta["cubes"] = cubes
                
            return meta
        except Exception as e:
            logger.error(f"Error retrieving Cube.js metadata: {e}")
            return {"error": str(e)}


class ExecuteCubeQueryTool(BaseTool):
    """Tool for executing queries against Cube.js."""
    
    name: str = "ExecuteCubeQuery"
    description: str = "Execute a query against Cube.js to retrieve BI data"
    
    def __init__(
        self, 
        api_url: str,
        api_token: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize the execute query tool.
        
        Args:
            api_url: Base URL of the Cube.js API
            api_token: Optional API token for authentication
            timeout: Request timeout in seconds
        """
        super().__init__()
        self.client = CubeJsClient(api_url, api_token, timeout)
        logger.info("Initialized Cube.js query execution tool")
        
    def _run(
        self, 
        query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a query against Cube.js.
        
        Args:
            query: The complete Cube.js query object
            
        Returns:
            The query results
        """
        try:
            return self.client.load(query)
        except Exception as e:
            logger.error(f"Error executing Cube.js query: {e}")
            return {"error": str(e)}


class ExecuteSqlTool(BaseTool):
    """Tool for executing SQL queries against Cube.js."""
    
    name: str = "ExecuteCubeSql"
    description: str = "Execute a SQL query against Cube.js"
    
    def __init__(
        self, 
        api_url: str,
        api_token: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize the SQL execution tool.
        
        Args:
            api_url: Base URL of the Cube.js API
            api_token: Optional API token for authentication
            timeout: Request timeout in seconds
        """
        super().__init__()
        self.client = CubeJsClient(api_url, api_token, timeout)
        logger.info("Initialized Cube.js SQL execution tool")
        
    def _run(self, sql: str) -> Dict[str, Any]:
        """
        Execute a SQL query against Cube.js.
        
        Args:
            sql: The SQL query string
            
        Returns:
            The query results
        """
        try:
            return self.client.sql(sql)
        except Exception as e:
            logger.error(f"Error executing Cube.js SQL query: {e}")
            return {"error": str(e)}


class BuildCubeQueryTool(BaseTool):
    """Tool for building and executing Cube.js queries."""
    
    name: str = "BuildCubeQuery"
    description: str = "Build and execute a Cube.js query with measures, dimensions, filters, and time dimensions"
    
    def __init__(
        self, 
        api_url: str,
        api_token: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize the query builder tool.
        
        Args:
            api_url: Base URL of the Cube.js API
            api_token: Optional API token for authentication
            timeout: Request timeout in seconds
        """
        super().__init__()
        self.client = CubeJsClient(api_url, api_token, timeout)
        logger.info("Initialized Cube.js query builder tool")
        
    def _run(
        self,
        measures: List[str],
        dimensions: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        time_dimensions: Optional[List[Dict[str, Any]]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Build and execute a Cube.js query.
        
        Args:
            measures: List of measures to include (e.g., ["Orders.count", "Orders.totalAmount"])
            dimensions: Optional list of dimensions (e.g., ["Orders.status", "Orders.userId"])
            filters: Optional list of filters
            time_dimensions: Optional list of time dimensions with granularity and date range
            limit: Optional maximum number of rows to return
            offset: Optional number of rows to skip
            order: Optional sorting specifications
            
        Returns:
            The query results
        """
        try:
            # Build the query
            query = self.client.build_query(
                measures=measures,
                dimensions=dimensions,
                filters=filters,
                time_dimensions=time_dimensions,
                limit=limit,
                offset=offset,
                order=order
            )
            
            # Execute the query
            return self.client.load(query)
        except Exception as e:
            logger.error(f"Error building and executing Cube.js query: {e}")
            return {"error": str(e)}


class AnalyzeDataPointTool(BaseTool):
    """Tool for analyzing specific data points in Cube.js."""
    
    name: str = "AnalyzeDataPoint"
    description: str = "Analyze a specific measure or metric with optional dimensions and filters"
    
    def __init__(
        self, 
        api_url: str,
        api_token: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize the data point analysis tool.
        
        Args:
            api_url: Base URL of the Cube.js API
            api_token: Optional API token for authentication
            timeout: Request timeout in seconds
        """
        super().__init__()
        self.client = CubeJsClient(api_url, api_token, timeout)
        logger.info("Initialized Cube.js data point analysis tool")
        
    def _run(
        self,
        cube_name: str,
        measure: str,
        dimensions: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        time_dimension: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a specific data point with optional dimensions and filters.
        
        Args:
            cube_name: Name of the cube (e.g., "Orders")
            measure: The measure to analyze (e.g., "count", "totalAmount")
            dimensions: Optional dimensions to group by (e.g., ["status", "userId"])
            filters: Optional filters to apply
            time_dimension: Optional time dimension with granularity and date range
            
        Returns:
            The analysis results
        """
        try:
            # Build query
            query = {}
            
            # Add measure with cube prefix
            full_measure = f"{cube_name}.{measure}"
            query["measures"] = [full_measure]
            
            # Add dimensions with cube prefix
            if dimensions:
                query["dimensions"] = [f"{cube_name}.{dim}" for dim in dimensions]
            
            # Add filters
            if filters:
                # Ensure each filter has cube prefix for member
                for filter_item in filters:
                    if "member" in filter_item and "." not in filter_item["member"]:
                        filter_item["member"] = f"{cube_name}.{filter_item['member']}"
                query["filters"] = filters
            
            # Add time dimension
            if time_dimension:
                dimension = time_dimension.get("dimension")
                if dimension and "." not in dimension:
                    time_dimension["dimension"] = f"{cube_name}.{dimension}"
                query["timeDimensions"] = [time_dimension]
            
            # Execute the query
            return self.client.load(query)
        except Exception as e:
            logger.error(f"Error analyzing data point: {e}")
            return {"error": str(e)}


class PreviewQuerySqlTool(BaseTool):
    """Tool for previewing the SQL generated for a Cube.js query."""
    
    name: str = "PreviewQuerySql"
    description: str = "Preview the SQL that would be generated for a Cube.js query without executing it"
    
    def __init__(
        self, 
        api_url: str,
        api_token: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize the SQL preview tool.
        
        Args:
            api_url: Base URL of the Cube.js API
            api_token: Optional API token for authentication
            timeout: Request timeout in seconds
        """
        super().__init__()
        self.client = CubeJsClient(api_url, api_token, timeout)
        logger.info("Initialized Cube.js SQL preview tool")
        
    def _run(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preview the SQL for a Cube.js query.
        
        Args:
            query: The Cube.js query object
            
        Returns:
            The SQL that would be generated
        """
        try:
            result = self.client.dry_run(query)
            sql = result.get("sql", {}).get("sql", "SQL not available")
            return {
                "sql": sql,
                "dialect": result.get("sql", {}).get("dialect", "unknown"),
                "external": result.get("external", False)
            }
        except Exception as e:
            logger.error(f"Error previewing query SQL: {e}")
            return {"error": str(e)} 