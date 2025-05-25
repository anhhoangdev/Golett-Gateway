from typing import Any, Dict, List, Optional, Union, Type
import json

from crewai.tools import BaseTool
from pydantic import Field, BaseModel, field_validator
from golett.tools.cube.client import CubeJsClient
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class BuildCubeQuerySchema(BaseModel):
    """Schema for BuildCubeQueryTool parameters"""
    measures: List[str] = Field(description="List of measures to include (e.g., ['Orders.count', 'Orders.totalAmount'])")
    dimensions: Optional[List[str]] = Field(default=None, description="Optional list of dimensions (e.g., ['Orders.status', 'Orders.userId'])")
    filters: Optional[List[Dict[str, Any]]] = Field(default=None, description="Optional list of filters")
    time_dimensions: Optional[List[Dict[str, Any]]] = Field(default=None, description="Optional list of time dimensions with granularity and date range")
    limit: Optional[int] = Field(default=None, description="Optional maximum number of rows to return")
    offset: Optional[int] = Field(default=0, description="Optional number of rows to skip")
    order: Optional[List[Dict[str, str]]] = Field(default=None, description="Optional sorting specifications")
    
    @field_validator('dimensions', mode='before')
    @classmethod
    def validate_dimensions(cls, v):
        """Convert string 'None' to actual None"""
        if v == "None" or v == ["None"] or v == []:
            return None
        return v
    
    @field_validator('filters', mode='before')
    @classmethod
    def validate_filters(cls, v):
        """Convert string 'None' to actual None"""
        if v == "None" or v == ["None"] or v == []:
            return None
        return v
    
    @field_validator('time_dimensions', mode='before')
    @classmethod
    def validate_time_dimensions(cls, v):
        """Convert string 'None' to actual None"""
        if v == "None" or v == ["None"] or v == []:
            return None
        return v
    
    @field_validator('order', mode='before')
    @classmethod
    def validate_order(cls, v):
        """Convert string 'None' to actual None and validate CubeJS order format"""
        if v == "None" or v == ["None"] or v == []:
            return None
        
        # If it's a string, try to parse it as JSON
        if isinstance(v, str) and v != "None":
            try:
                import json
                v = json.loads(v)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid order format: {v}. Must be valid JSON array.")
        
        # Validate CubeJS order format
        if isinstance(v, list):
            for i, item in enumerate(v):
                if not isinstance(item, dict):
                    raise ValueError(f"Order item {i} must be an object with 'id' and 'desc' fields")
                
                if 'id' not in item:
                    raise ValueError(f"Order item {i} missing required 'id' field")
                
                # Fix desc field if it's boolean instead of string
                if 'desc' in item:
                    if isinstance(item['desc'], bool):
                        item['desc'] = "desc" if item['desc'] else "asc"
                    elif item['desc'] not in ['asc', 'desc']:
                        raise ValueError(f"Order item {i} 'desc' field must be 'asc' or 'desc', got: {item['desc']}")
                else:
                    # Default to ascending if desc not specified
                    item['desc'] = 'asc'
        
        elif v is not None:
            raise ValueError(f"Order must be an array of objects, got: {type(v)}")
        
        return v
    
    @field_validator('limit', mode='before')
    @classmethod
    def validate_limit(cls, v):
        """Convert string 'None' to actual None"""
        if v == "None":
            return None
        return v

class CubeJsMetadataTool(BaseTool):
    """Tool for retrieving Cube.js metadata."""
    
    name: str = "CubeJsMetadata"
    description: str = "Get metadata about available cubes, measures, and dimensions from Cube.js"
    
    # Declare Pydantic fields
    client: CubeJsClient = Field(default=None, description="CubeJS client instance")
    
    def __init__(
        self, 
        api_url: str,
        api_token: Optional[str] = None,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize the Cube.js metadata tool.
        
        Args:
            api_url: Base URL of the Cube.js API
            api_token: Optional API token for authentication
            timeout: Request timeout in seconds
        """
        # Create client and set it in kwargs
        kwargs['client'] = CubeJsClient(api_url, api_token, timeout)
        super().__init__(**kwargs)
        logger.info("Initialized Cube.js metadata tool")
        
    def _run(self, cube_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metadata about available cubes, measures, and dimensions.
        
        Args:
            cube_name: Optional specific cube name to get metadata for
            
        Returns:
            Metadata about cubes, measures, and dimensions
        """
        try:
            # Handle string "None" values from CrewAI agents
            if cube_name == "None":
                cube_name = None
                
            # Get metadata for all cubes (meta() doesn't accept parameters)
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
    """Tool for executing pre-built Cube.js queries."""
    
    name: str = "ExecuteCubeQuery"
    description: str = "Execute a pre-built Cube.js query to retrieve BI data. Use this after BuildCubeQuery."
    
    # Declare Pydantic fields
    client: CubeJsClient = Field(default=None, description="CubeJS client instance")
    
    def __init__(
        self, 
        api_url: str,
        api_token: Optional[str] = None,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize the execute query tool.
        
        Args:
            api_url: Base URL of the Cube.js API
            api_token: Optional API token for authentication
            timeout: Request timeout in seconds
        """
        # Create client and set it in kwargs
        kwargs['client'] = CubeJsClient(api_url, api_token, timeout)
        super().__init__(**kwargs)
        logger.info("Initialized Cube.js query execution tool")
        
    def _preprocess_data_for_analysis(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess CubeJS response data to make it more analysis-friendly.
        
        Args:
            result: Raw CubeJS response
            
        Returns:
            Processed result with structured data and metadata
        """
        if "error" in result or "data" not in result:
            return result
            
        raw_data = result["data"]
        annotation = result.get("annotation", {})
        
        # Extract metadata about measures and dimensions
        measures_info = annotation.get("measures", {})
        dimensions_info = annotation.get("dimensions", {})
        
        # Process the data into a more structured format
        processed_data = {
            "records": [],
            "summary": {},
            "metadata": {
                "total_records": len(raw_data),
                "measures": {},
                "dimensions": {},
                "data_types": {}
            }
        }
        
        if not raw_data:
            processed_data["summary"]["message"] = "No data returned from query"
            return {**result, "processed_data": processed_data}
        
        # Process each record
        for record in raw_data:
            processed_record = {}
            for key, value in record.items():
                # Convert string numbers to actual numbers where possible
                if isinstance(value, str) and value.isdigit():
                    processed_record[key] = int(value)
                elif isinstance(value, str):
                    try:
                        # Try to convert to float
                        processed_record[key] = float(value)
                    except ValueError:
                        # Keep as string if not a number
                        processed_record[key] = value
                else:
                    processed_record[key] = value
                    
            processed_data["records"].append(processed_record)
        
        # Generate summary statistics
        if processed_data["records"]:
            first_record = processed_data["records"][0]
            
            for key in first_record.keys():
                values = [record.get(key) for record in processed_data["records"]]
                
                # Determine data type and collect metadata
                if key in measures_info:
                    measure_info = measures_info[key]
                    processed_data["metadata"]["measures"][key] = {
                        "title": measure_info.get("title", key),
                        "short_title": measure_info.get("shortTitle", key),
                        "type": measure_info.get("type", "unknown")
                    }
                    processed_data["metadata"]["data_types"][key] = "measure"
                elif key in dimensions_info:
                    dimension_info = dimensions_info[key]
                    processed_data["metadata"]["dimensions"][key] = {
                        "title": dimension_info.get("title", key),
                        "short_title": dimension_info.get("shortTitle", key),
                        "type": dimension_info.get("type", "unknown")
                    }
                    processed_data["metadata"]["data_types"][key] = "dimension"
                
                # Calculate statistics for numeric values
                numeric_values = [v for v in values if isinstance(v, (int, float)) and v is not None]
                if numeric_values:
                    processed_data["summary"][key] = {
                        "count": len(numeric_values),
                        "sum": sum(numeric_values),
                        "avg": sum(numeric_values) / len(numeric_values),
                        "min": min(numeric_values),
                        "max": max(numeric_values),
                        "non_zero_count": len([v for v in numeric_values if v != 0])
                    }
                else:
                    # For non-numeric data
                    unique_values = list(set([v for v in values if v is not None]))
                    processed_data["summary"][key] = {
                        "count": len([v for v in values if v is not None]),
                        "unique_values": len(unique_values),
                        "sample_values": unique_values[:5]  # First 5 unique values
                    }
        
        # Add processed data to the result
        return {**result, "processed_data": processed_data}

    def _run(
        self, 
        query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a pre-built Cube.js query.
        
        Args:
            query: The complete Cube.js query object (from BuildCubeQuery tool)
            
        Returns:
            Clean, concise query results optimized for LLM analysis
        """
        try:
            # If the input is from BuildCubeQuery tool, extract the actual query
            if isinstance(query, dict) and "query" in query:
                actual_query = query["query"]
                validation_info = query.get("validation_info", {})
            else:
                actual_query = query
                validation_info = {}
            
            # Execute the query
            result = self.client.load(actual_query)
            
            # Preprocess data for better analysis
            result = self._preprocess_data_for_analysis(result)
            
            # Return ONLY the essential data for LLM analysis (remove massive metadata)
            clean_result = {
                "status": "success",
                "query_executed": {
                    "measures": actual_query.get("measures", []),
                    "dimensions": actual_query.get("dimensions", []),
                    "time_dimensions": actual_query.get("timeDimensions", []),
                    "filters": actual_query.get("filters", [])
                },
                "data": result.get("data", []),
                "processed_data": result.get("processed_data", {}),
                "total_records": len(result.get("data", [])),
                "execution_time": result.get("lastRefreshTime", "unknown")
            }
            
            # Add validation info if available (but keep it minimal)
            if validation_info:
                clean_result["validation_info"] = {
                    "target_cube": validation_info.get("target_cube"),
                    "validated_measures": validation_info.get("validated_measures", []),
                    "validated_dimensions": validation_info.get("validated_dimensions", [])
                }
            
            return clean_result
            
        except Exception as e:
            logger.error(f"Error executing Cube.js query: {e}")
            
            # Parse CubeJS validation errors for actionable feedback
            error_message = str(e)
            actionable_feedback = self._parse_cubejs_error(error_message, actual_query)
            
            return {
                "status": "error", 
                "error": error_message,
                "actionable_feedback": actionable_feedback,
                "query_attempted": actual_query,
                "retry_suggestions": self._generate_retry_suggestions(error_message, actual_query)
            }
    
    def _parse_cubejs_error(self, error_message: str, query: Dict[str, Any]) -> str:
        """
        Parse CubeJS error messages and provide actionable feedback.
        
        Args:
            error_message: The raw error message from CubeJS
            query: The query that caused the error
            
        Returns:
            Actionable feedback for the agent
        """
        error_lower = error_message.lower()
        
        # Common CubeJS validation errors and their fixes
        if "order[0]" in error_message and "must be an array" in error_message:
            return ("ORDER FORMAT ERROR: The 'order' parameter must be an array of objects. "
                   "Correct format: [{\"id\": \"measure_name\", \"desc\": \"asc\"}] or [{\"id\": \"dimension_name\", \"desc\": \"desc\"}]")
        
        elif "invalid query format" in error_lower:
            return ("QUERY FORMAT ERROR: The query structure is invalid. Check that all parameters follow CubeJS JSON format.")
        
        elif "unknown measure" in error_lower or "measure not found" in error_lower:
            return ("MEASURE ERROR: One or more measures don't exist. Use BuildCubeQuery tool to validate available measures.")
        
        elif "unknown dimension" in error_lower or "dimension not found" in error_lower:
            return ("DIMENSION ERROR: One or more dimensions don't exist. Use BuildCubeQuery tool to validate available dimensions.")
        
        elif "time dimension" in error_lower and "invalid" in error_lower:
            return ("TIME DIMENSION ERROR: Time dimension format is invalid. Use format: [{\"dimension\": \"Cube.timeField\", \"granularity\": \"day\", \"dateRange\": [\"start\", \"end\"]}]")
        
        elif "filter" in error_lower and "invalid" in error_lower:
            return ("FILTER ERROR: Filter format is invalid. Use format: [{\"member\": \"Cube.field\", \"operator\": \"equals\", \"values\": [\"value\"]}]")
        
        elif "400" in error_message or "bad request" in error_lower:
            return ("BAD REQUEST: The query parameters are malformed. Check field names, operators, and data types.")
        
        elif "401" in error_message or "unauthorized" in error_lower:
            return ("AUTHENTICATION ERROR: Invalid or missing API token.")
        
        elif "403" in error_message or "forbidden" in error_lower:
            return ("PERMISSION ERROR: Access denied to requested data.")
        
        elif "404" in error_message or "not found" in error_lower:
            return ("ENDPOINT ERROR: CubeJS API endpoint not found. Check the API URL.")
        
        elif "timeout" in error_lower or "connection" in error_lower:
            return ("CONNECTION ERROR: Unable to connect to CubeJS server. Check if the server is running.")
        
        else:
            return f"UNKNOWN ERROR: {error_message}. Please check the query format and try again."
    
    def _generate_retry_suggestions(self, error_message: str, query: Dict[str, Any]) -> List[str]:
        """
        Generate specific retry suggestions based on the error.
        
        Args:
            error_message: The raw error message from CubeJS
            query: The query that caused the error
            
        Returns:
            List of specific retry suggestions
        """
        suggestions = []
        error_lower = error_message.lower()
        
        if "order[0]" in error_message and "must be an array" in error_message:
            suggestions.extend([
                "Fix the 'order' parameter format:",
                "- For ascending: [{\"id\": \"measure_name\", \"desc\": \"asc\"}]",
                "- For descending: [{\"id\": \"measure_name\", \"desc\": \"desc\"}]",
                "- Remove 'order' parameter if sorting is not needed"
            ])
        
        elif "measure" in error_lower and ("unknown" in error_lower or "not found" in error_lower):
            suggestions.extend([
                "Validate measure names using BuildCubeQuery tool",
                "Ensure measures use format: 'CubeName.measureName'",
                "Check available measures in the schema"
            ])
        
        elif "dimension" in error_lower and ("unknown" in error_lower or "not found" in error_lower):
            suggestions.extend([
                "Validate dimension names using BuildCubeQuery tool", 
                "Ensure dimensions use format: 'CubeName.dimensionName'",
                "Check available dimensions in the schema"
            ])
        
        elif "time dimension" in error_lower:
            suggestions.extend([
                "Fix time dimension format:",
                "- Use 'dimension' instead of 'member'",
                "- Include 'granularity': 'day'|'month'|'year'",
                "- Include 'dateRange': ['start_date', 'end_date']"
            ])
        
        elif "filter" in error_lower:
            suggestions.extend([
                "Fix filter format:",
                "- Use 'member' instead of 'dimension'", 
                "- Use valid operators: 'equals', 'gt', 'lt', 'contains'",
                "- Ensure 'values' is an array: ['value1', 'value2']"
            ])
        
        else:
            suggestions.extend([
                "Rebuild the query using BuildCubeQuery tool",
                "Validate all field names against the schema",
                "Check CubeJS server status and connectivity"
            ])
        
        return suggestions


class ExecuteSqlTool(BaseTool):
    """Tool for executing SQL queries against Cube.js."""
    
    name: str = "ExecuteCubeSql"
    description: str = "Execute a SQL query against Cube.js"
    
    # Declare Pydantic fields
    client: CubeJsClient = Field(default=None, description="CubeJS client instance")
    
    def __init__(
        self, 
        api_url: str,
        api_token: Optional[str] = None,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize the SQL execution tool.
        
        Args:
            api_url: Base URL of the Cube.js API
            api_token: Optional API token for authentication
            timeout: Request timeout in seconds
        """
        # Create client and set it in kwargs
        kwargs['client'] = CubeJsClient(api_url, api_token, timeout)
        super().__init__(**kwargs)
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
    """Tool for building Cube.js queries with smart validation."""
    
    name: str = "BuildCubeQuery"
    description: str = "Build a Cube.js query with measures, dimensions, filters, and time dimensions. Returns a validated query object."
    args_schema: Type[BaseModel] = BuildCubeQuerySchema
    
    # Declare Pydantic fields
    client: CubeJsClient = Field(default=None, description="CubeJS client instance")
    
    def __init__(
        self, 
        api_url: str,
        api_token: Optional[str] = None,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize the query builder tool.
        
        Args:
            api_url: Base URL of the Cube.js API
            api_token: Optional API token for authentication
            timeout: Request timeout in seconds
        """
        # Create client and set it in kwargs
        kwargs['client'] = CubeJsClient(api_url, api_token, timeout)
        super().__init__(**kwargs)
        logger.info("Initialized Cube.js query builder tool")
        
    def _validate_and_fix_filters_and_time_dims(
        self, 
        filters: Optional[List[Dict[str, Any]]], 
        time_dimensions: Optional[List[Dict[str, Any]]],
        available_dimensions: List[str]
    ) -> tuple[Optional[List[Dict[str, Any]]], Optional[List[Dict[str, Any]]]]:
        """
        Validate and fix filters and time dimensions format for CubeJS API.
        
        Args:
            filters: List of filter objects
            time_dimensions: List of time dimension objects
            available_dimensions: List of available dimensions for validation
            
        Returns:
            Tuple of (validated_filters, validated_time_dimensions)
        """
        # Operator mapping from common names to CubeJS format
        operator_mapping = {
            "equals": "equals",
            "notEquals": "notEquals", 
            "contains": "contains",
            "notContains": "notContains",
            "startsWith": "startsWith",
            "endsWith": "endsWith",
            "greaterThan": "gt",
            "greaterThanOrEqual": "gte", 
            "lessThan": "lt",
            "lessThanOrEqual": "lte",
            "inDateRange": "inDateRange",
            "notInDateRange": "notInDateRange",
            "beforeDate": "beforeDate",
            "afterDate": "afterDate",
            "set": "set",
            "notSet": "notSet"
        }
        
        validated_filters = None
        if filters:
            validated_filters = []
            for filter_obj in filters:
                fixed_filter = filter_obj.copy()
                
                # Fix dimension -> member
                if "dimension" in fixed_filter:
                    fixed_filter["member"] = fixed_filter.pop("dimension")
                
                # Fix operator names
                if "operator" in fixed_filter:
                    operator = fixed_filter["operator"]
                    if operator in operator_mapping:
                        fixed_filter["operator"] = operator_mapping[operator]
                        logger.info(f"Fixed filter operator: {operator} -> {operator_mapping[operator]}")
                
                validated_filters.append(fixed_filter)
        
        validated_time_dimensions = None
        if time_dimensions:
            validated_time_dimensions = []
            for time_dim in time_dimensions:
                fixed_time_dim = time_dim.copy()
                
                # Fix dimension -> member
                if "dimension" in fixed_time_dim:
                    fixed_time_dim["member"] = fixed_time_dim.pop("dimension")
                    logger.info(f"Fixed time dimension: dimension -> member")
                
                validated_time_dimensions.append(fixed_time_dim)
        
        return validated_filters, validated_time_dimensions

    def _run(
        self,
        measures: List[str],
        dimensions: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        time_dimensions: Optional[List[Dict[str, Any]]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = 0,
        order: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Build a validated Cube.js query.
        
        Args:
            measures: List of measures to include (e.g., ["Orders.count", "Orders.totalAmount"])
            dimensions: Optional list of dimensions (e.g., ["Orders.status", "Orders.userId"])
            filters: Optional list of filters
            time_dimensions: Optional list of time dimensions with granularity and date range
            limit: Optional maximum number of rows to return
            offset: Optional number of rows to skip (defaults to 0)
            order: Optional sorting specifications
            
        Returns:
            A validated query object ready for execution
        """
        try:
            # Handle string "None" values from CrewAI agents
            if dimensions == "None" or dimensions == ["None"]:
                dimensions = None
            if filters == "None" or filters == ["None"]:
                filters = None
            if time_dimensions == "None" or time_dimensions == ["None"]:
                time_dimensions = None
            if order == "None" or order == ["None"]:
                order = None
            if limit == "None":
                limit = None
                
            # Get metadata to validate field names
            try:
                meta = self.client.meta()
                available_cubes = {cube["name"]: cube for cube in meta.get("cubes", [])}
            except Exception as meta_error:
                logger.warning(f"Could not retrieve metadata for validation: {meta_error}")
                available_cubes = {}
            
            if not available_cubes:
                return {"error": "No cubes available"}
            
            # Determine target cube from existing prefixed fields
            target_cube = None
            all_fields = measures.copy()
            if dimensions:
                all_fields.extend(dimensions)
            
            # Find target cube from prefixed fields
            for field in all_fields:
                if "." in field:
                    cube_name = field.split(".")[0]
                    if cube_name in available_cubes:
                        target_cube = cube_name
                        break
            
            # If no target cube found, use the first cube that has any of the requested measures
            if not target_cube:
                for cube_name, cube_info in available_cubes.items():
                    cube_measures = [m["name"] for m in cube_info.get("measures", [])]
                    for measure in measures:
                        measure_name = measure.split(".")[-1]  # Get just the measure name
                        full_measure = f"{cube_name}.{measure_name}"
                        if full_measure in cube_measures:
                            target_cube = cube_name
                            break
                    if target_cube:
                        break
            
            # If still no target cube, use the first available cube
            if not target_cube:
                target_cube = list(available_cubes.keys())[0]
                logger.info(f"No matching cube found, using first available: {target_cube}")
            
            target_cube_info = available_cubes[target_cube]
            available_measures = [m["name"] for m in target_cube_info.get("measures", [])]
            available_dimensions = [d["name"] for d in target_cube_info.get("dimensions", [])]
            
            logger.info(f"Using target cube: {target_cube}")
            
            # Validate and fix measures
            validated_measures = []
            for measure in measures:
                if "." in measure:
                    # Already has cube prefix
                    if measure in available_measures:
                        validated_measures.append(measure)
                    else:
                        # Try to find in target cube
                        measure_name = measure.split(".")[-1]
                        target_measure = f"{target_cube}.{measure_name}"
                        if target_measure in available_measures:
                            validated_measures.append(target_measure)
                            logger.info(f"Redirected measure: {measure} -> {target_measure}")
                        else:
                            # Use first available measure as fallback
                            if available_measures:
                                fallback = available_measures[0]
                                validated_measures.append(fallback)
                                logger.warning(f"Measure '{measure}' not found, using fallback: {fallback}")
                else:
                    # No cube prefix - add target cube prefix
                    target_measure = f"{target_cube}.{measure}"
                    if target_measure in available_measures:
                        validated_measures.append(target_measure)
                        logger.info(f"Added cube prefix: {measure} -> {target_measure}")
                    else:
                        # Use first available measure as fallback
                        if available_measures:
                            fallback = available_measures[0]
                            validated_measures.append(fallback)
                            logger.warning(f"Measure '{measure}' not found, using fallback: {fallback}")
            
            if not validated_measures:
                return {"error": "No valid measures found"}
            
            # Validate and fix dimensions
            validated_dimensions = None
            if dimensions:
                validated_dimensions = []
                for dimension in dimensions:
                    if "." in dimension:
                        # Already has cube prefix
                        if dimension in available_dimensions:
                            validated_dimensions.append(dimension)
                        else:
                            # Try to find in target cube
                            dimension_name = dimension.split(".")[-1]
                            target_dimension = f"{target_cube}.{dimension_name}"
                            if target_dimension in available_dimensions:
                                validated_dimensions.append(target_dimension)
                                logger.info(f"Redirected dimension: {dimension} -> {target_dimension}")
                            else:
                                # Use first available dimension as fallback
                                if available_dimensions:
                                    fallback = available_dimensions[0]
                                    validated_dimensions.append(fallback)
                                    logger.warning(f"Dimension '{dimension}' not found, using fallback: {fallback}")
                    else:
                        # No cube prefix - add target cube prefix
                        target_dimension = f"{target_cube}.{dimension}"
                        if target_dimension in available_dimensions:
                            validated_dimensions.append(target_dimension)
                            logger.info(f"Added cube prefix: {dimension} -> {target_dimension}")
                        else:
                            # Use first available dimension as fallback
                            if available_dimensions:
                                fallback = available_dimensions[0]
                                validated_dimensions.append(fallback)
                                logger.warning(f"Dimension '{dimension}' not found, using fallback: {fallback}")
            
            # Validate and fix filters and time dimensions
            validated_filters, validated_time_dimensions = self._validate_and_fix_filters_and_time_dims(filters, time_dimensions, available_dimensions)
            
            # Build the query object (don't execute it)
            query = self.client.build_query(
                measures=validated_measures,
                dimensions=validated_dimensions,
                filters=validated_filters,
                time_dimensions=validated_time_dimensions,
                limit=limit,
                offset=offset,
                order=None  # Remove order for now as it's causing issues
            )
            
            # Return the query object with validation info
            return {
                "query": query,
                "validation_info": {
                    "target_cube": target_cube,
                    "original_measures": measures,
                    "validated_measures": validated_measures,
                    "original_dimensions": dimensions,
                    "validated_dimensions": validated_dimensions,
                    "available_measures": available_measures,
                    "available_dimensions": available_dimensions
                },
                "status": "query_built_successfully"
            }
            
        except Exception as e:
            logger.error(f"Error building Cube.js query: {e}")
            return {"error": str(e)}


class AnalyzeDataPointToolSchema(BaseModel):
    """Schema for AnalyzeDataPointTool parameters"""
    query_result: Dict[str, Any] = Field(description="The result from ExecuteCubeQuery tool containing data to analyze")
    analysis_type: str = Field(default="summary", description="Type of analysis: 'summary', 'trend', 'comparison', or 'detailed'")


class AnalyzeDataPointTool(BaseTool):
    """Tool for analyzing query results and providing insights."""
    
    name: str = "AnalyzeDataPoint"
    description: str = "Analyze query results to provide insights, trends, and business intelligence. Use this after ExecuteCubeQuery."
    args_schema: Type[BaseModel] = AnalyzeDataPointToolSchema
    
    # Declare Pydantic fields
    client: CubeJsClient = Field(default=None, description="CubeJS client instance")
    
    def __init__(
        self, 
        api_url: str,
        api_token: Optional[str] = None,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize the data point analysis tool.
        
        Args:
            api_url: Base URL of the Cube.js API
            api_token: Optional API token for authentication
            timeout: Request timeout in seconds
        """
        # Create client and set it in kwargs
        kwargs['client'] = CubeJsClient(api_url, api_token, timeout)
        super().__init__(**kwargs)
        logger.info("Initialized Cube.js data point analysis tool")
        
    def _run(
        self,
        query_result: Dict[str, Any],
        analysis_type: str = "summary"
    ) -> Dict[str, Any]:
        """
        Analyze query results to provide business insights.
        
        Args:
            query_result: The result from ExecuteCubeQuery tool
            analysis_type: Type of analysis ("summary", "trend", "comparison", "detailed")
            
        Returns:
            Analysis insights and recommendations
        """
        try:
            if "error" in query_result:
                return {"error": f"Cannot analyze query with error: {query_result['error']}"}
            
            # Use processed data if available, otherwise fall back to raw data
            if "processed_data" in query_result:
                processed_data = query_result["processed_data"]
                data = processed_data["records"]
                summary = processed_data["summary"]
                metadata = processed_data["metadata"]
            else:
                # Fallback to raw data format
                if "data" not in query_result:
                    return {"error": "No data found in query result"}
                data = query_result["data"]
                summary = {}
                metadata = {}
            
            validation_info = query_result.get("validation_info", {})
            
            if not data:
                return {
                    "analysis": "No data returned from query",
                    "insights": ["The query returned no results", "Consider adjusting filters or time range"],
                    "data_points": 0,
                    "summary": summary
                }
            
            # Enhanced analysis with processed data
            analysis = {
                "data_points": len(data),
                "measures_analyzed": list(metadata.get("measures", {}).keys()) or validation_info.get("validated_measures", []),
                "dimensions_analyzed": list(metadata.get("dimensions", {}).keys()) or validation_info.get("validated_dimensions", []),
                "target_cube": validation_info.get("target_cube", "unknown"),
                "data_summary": summary
            }
            
            insights = []
            recommendations = []
            
            # Analyze based on type with enhanced data
            if analysis_type == "summary":
                insights.extend(self._generate_enhanced_summary_insights(data, summary, metadata))
            elif analysis_type == "trend":
                insights.extend(self._generate_enhanced_trend_insights(data, summary, metadata))
            elif analysis_type == "comparison":
                insights.extend(self._generate_enhanced_comparison_insights(data, summary, metadata))
            elif analysis_type == "detailed":
                insights.extend(self._generate_enhanced_detailed_insights(data, summary, metadata))
            else:
                insights.extend(self._generate_enhanced_summary_insights(data, summary, metadata))
            
            # Generate enhanced recommendations
            recommendations.extend(self._generate_enhanced_recommendations(data, summary, metadata))
            
            return {
                "analysis": analysis,
                "insights": insights,
                "recommendations": recommendations,
                "analysis_type": analysis_type,
                "status": "analysis_completed"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing data point: {e}")
            return {"error": str(e)}
    
    def _generate_enhanced_summary_insights(self, data: List[Dict], summary: Dict, metadata: Dict) -> List[str]:
        """Generate enhanced summary insights from processed data"""
        insights = []
        
        # Basic data overview
        insights.append(f"📊 Dataset contains {len(data)} records")
        
        # Analyze measures
        measures = metadata.get("measures", {})
        if measures:
            insights.append(f"📈 Analyzing {len(measures)} measures:")
            for measure_key, measure_info in measures.items():
                if measure_key in summary:
                    stats = summary[measure_key]
                    title = measure_info.get("short_title", measure_key)
                    if "sum" in stats:
                        insights.append(f"  • {title}: Total = {stats['sum']:,}, Average = {stats['avg']:.2f}")
                        if stats['non_zero_count'] < stats['count']:
                            insights.append(f"    ⚠️  {stats['count'] - stats['non_zero_count']} zero values detected")
        
        # Analyze dimensions
        dimensions = metadata.get("dimensions", {})
        if dimensions:
            insights.append(f"🏷️  Analyzing {len(dimensions)} dimensions:")
            for dim_key, dim_info in dimensions.items():
                if dim_key in summary:
                    stats = summary[dim_key]
                    title = dim_info.get("short_title", dim_key)
                    if "unique_values" in stats:
                        insights.append(f"  • {title}: {stats['unique_values']} unique values")
                        if "sample_values" in stats and stats["sample_values"]:
                            sample = ", ".join(str(v) for v in stats["sample_values"][:3])
                            insights.append(f"    Examples: {sample}")
        
        return insights
    
    def _generate_enhanced_trend_insights(self, data: List[Dict], summary: Dict, metadata: Dict) -> List[str]:
        """Generate enhanced trend insights from processed data"""
        insights = []
        
        if len(data) > 1:
            insights.append("📈 Trend Analysis:")
            
            # Analyze trends for measures
            measures = metadata.get("measures", {})
            for measure_key in measures.keys():
                values = [record.get(measure_key) for record in data if isinstance(record.get(measure_key), (int, float))]
                if len(values) > 1:
                    title = measures[measure_key].get("short_title", measure_key)
                    change = values[-1] - values[0]
                    change_pct = (change / values[0] * 100) if values[0] != 0 else 0
                    
                    if change > 0:
                        insights.append(f"  📈 {title}: +{change:,.2f} ({change_pct:+.1f}%)")
                    elif change < 0:
                        insights.append(f"  📉 {title}: {change:,.2f} ({change_pct:+.1f}%)")
                    else:
                        insights.append(f"  ➡️  {title}: No change")
        else:
            insights.append("📊 Trend analysis requires multiple data points")
            insights.append("💡 Consider adding time dimensions or multiple dimension values")
        
        return insights
    
    def _generate_enhanced_comparison_insights(self, data: List[Dict], summary: Dict, metadata: Dict) -> List[str]:
        """Generate enhanced comparison insights from processed data"""
        insights = []
        
        if len(data) > 1:
            insights.append("🔍 Comparison Analysis:")
            
            # Compare measures across records
            measures = metadata.get("measures", {})
            for measure_key in measures.keys():
                if measure_key in summary and "min" in summary[measure_key]:
                    stats = summary[measure_key]
                    title = measures[measure_key].get("short_title", measure_key)
                    
                    range_val = stats["max"] - stats["min"]
                    if range_val > 0:
                        insights.append(f"  📊 {title}: Range {stats['min']:,} to {stats['max']:,} (spread: {range_val:,})")
                        
                        # Find records with min/max values
                        for i, record in enumerate(data):
                            if record.get(measure_key) == stats["max"]:
                                insights.append(f"    🔝 Highest in record {i+1}")
                                break
                        for i, record in enumerate(data):
                            if record.get(measure_key) == stats["min"]:
                                insights.append(f"    🔻 Lowest in record {i+1}")
                                break
        else:
            insights.append("🔍 Comparison analysis requires multiple data points")
        
        return insights
    
    def _generate_enhanced_detailed_insights(self, data: List[Dict], summary: Dict, metadata: Dict) -> List[str]:
        """Generate enhanced detailed insights from processed data"""
        insights = []
        
        insights.append("🔬 Detailed Analysis:")
        
        # Show detailed breakdown for each record
        for i, record in enumerate(data[:5]):  # Limit to first 5 records
            record_insights = []
            
            # Group by measures and dimensions
            measures = metadata.get("measures", {})
            dimensions = metadata.get("dimensions", {})
            
            measure_parts = []
            dimension_parts = []
            
            for key, value in record.items():
                if key in measures:
                    title = measures[key].get("short_title", key)
                    if isinstance(value, (int, float)):
                        measure_parts.append(f"{title}: {value:,}")
                    else:
                        measure_parts.append(f"{title}: {value}")
                elif key in dimensions:
                    title = dimensions[key].get("short_title", key)
                    dimension_parts.append(f"{title}: {value}")
                else:
                    # Unknown field
                    if isinstance(value, (int, float)):
                        measure_parts.append(f"{key}: {value:,}")
                    else:
                        dimension_parts.append(f"{key}: {value}")
            
            # Combine insights
            if dimension_parts:
                insights.append(f"  📋 Record {i+1} - {', '.join(dimension_parts)}")
            else:
                insights.append(f"  📋 Record {i+1}:")
                
            if measure_parts:
                insights.append(f"    📊 {', '.join(measure_parts)}")
        
        if len(data) > 5:
            insights.append(f"  ... and {len(data) - 5} more records")
        
        return insights
    
    def _generate_enhanced_recommendations(self, data: List[Dict], summary: Dict, metadata: Dict) -> List[str]:
        """Generate enhanced business recommendations based on processed data"""
        recommendations = []
        
        if len(data) == 0:
            recommendations.append("🔍 No data found - consider adjusting query filters or date ranges")
            return recommendations
        
        # Analyze data quality
        measures = metadata.get("measures", {})
        zero_measures = []
        
        for measure_key in measures.keys():
            if measure_key in summary and "non_zero_count" in summary[measure_key]:
                stats = summary[measure_key]
                if stats["non_zero_count"] == 0:
                    zero_measures.append(measures[measure_key].get("short_title", measure_key))
                elif stats["non_zero_count"] < stats["count"]:
                    title = measures[measure_key].get("short_title", measure_key)
                    zero_pct = (stats["count"] - stats["non_zero_count"]) / stats["count"] * 100
                    recommendations.append(f"⚠️  {title} has {zero_pct:.1f}% zero values - investigate data quality")
        
        if zero_measures:
            recommendations.append(f"❌ These measures have only zero values: {', '.join(zero_measures)}")
        
        # Analysis recommendations
        if len(data) == 1:
            recommendations.append("📈 Add time dimensions for trend analysis")
            recommendations.append("🔍 Add more dimensions for comparative analysis")
        elif len(data) < 10:
            recommendations.append("📊 Consider expanding date range or reducing filters for more data points")
        else:
            recommendations.append("✅ Good data volume for comprehensive analysis")
        
        # Dimension recommendations
        dimensions = metadata.get("dimensions", {})
        for dim_key in dimensions.keys():
            if dim_key in summary and "unique_values" in summary[dim_key]:
                stats = summary[dim_key]
                if stats["unique_values"] == 1:
                    title = dimensions[dim_key].get("short_title", dim_key)
                    recommendations.append(f"🔍 {title} has only one value - consider removing or changing filters")
        
        return recommendations


class PreviewQuerySqlTool(BaseTool):
    """Tool for previewing the SQL generated for a Cube.js query."""
    
    name: str = "PreviewQuerySql"
    description: str = "Preview the SQL that would be generated for a Cube.js query without executing it"
    
    # Declare Pydantic fields
    client: CubeJsClient = Field(default=None, description="CubeJS client instance")
    
    def __init__(
        self, 
        api_url: str,
        api_token: Optional[str] = None,
        timeout: int = 30,
        **kwargs
    ):
        """
        Initialize the SQL preview tool.
        
        Args:
            api_url: Base URL of the Cube.js API
            api_token: Optional API token for authentication
            timeout: Request timeout in seconds
        """
        # Create client and set it in kwargs
        kwargs['client'] = CubeJsClient(api_url, api_token, timeout)
        super().__init__(**kwargs)
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