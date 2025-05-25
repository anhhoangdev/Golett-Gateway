import os
import yaml
import json
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from crewai.tools import BaseTool
from pydantic import Field
from golett.utils.logger import get_logger

logger = get_logger(__name__)

class LoadCubeSchemasTool(BaseTool):
    """Tool for loading Cube.js schema definitions."""
    
    name: str = "LoadCubeSchemas"
    description: str = "Load Cube.js schema definitions from YAML files to understand data models"
    
    # Declare Pydantic fields
    schemas_path: str = Field(default="schemas", description="Directory path containing Cube.js schema files")
    
    def __init__(self, schemas_path: Optional[str] = None, **kwargs):
        """
        Initialize the tool with a path to schema files.
        
        Args:
            schemas_path: Directory path containing Cube.js schema files
        """
        # Set the schemas_path before calling super().__init__()
        if schemas_path is not None:
            kwargs['schemas_path'] = schemas_path
        elif 'schemas_path' not in kwargs:
            kwargs['schemas_path'] = os.environ.get("CUBEJS_SCHEMAS_PATH", "schemas")
            
        super().__init__(**kwargs)
        logger.info(f"Initialized LoadCubeSchemas tool with path: {self.schemas_path}")

    def _run(self, schema_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Load Cube.js schema definitions.
        
        Args:
            schema_name: Optional specific schema name to load
            
        Returns:
            Dictionary of loaded schema definitions
        """
        # Handle string "None" values from CrewAI agents
        if schema_name == "None":
            schema_name = None
            
        schemas_dir = Path(self.schemas_path)
        if not schemas_dir.exists():
            return {"error": f"Schemas directory not found: {self.schemas_path}"}
            
        if schema_name:
            # Load a specific schema
            schema_file = schemas_dir / f"{schema_name}.yml"
            if not schema_file.exists():
                schema_file = schemas_dir / f"{schema_name}.yaml"
                
            if schema_file.exists():
                try:
                    with open(schema_file, 'r') as f:
                        schema = yaml.safe_load(f)
                    return {schema_name: schema}
                except Exception as e:
                    logger.error(f"Error loading schema {schema_name}: {e}")
                    return {"error": f"Failed to load schema {schema_name}: {str(e)}"}
            else:
                return {"error": f"Schema not found: {schema_name}"}
        else:
            # Load all schemas
            schemas = {}
            for file_path in schemas_dir.glob("*.y*ml"):
                schema_name = file_path.stem
                try:
                    with open(file_path, 'r') as f:
                        schema = yaml.safe_load(f)
                    schemas[schema_name] = schema
                except Exception as e:
                    logger.error(f"Error loading schema {schema_name}: {e}")
            
            if not schemas:
                return {"warning": "No schemas found"}
                
            return schemas


class SaveCubeSchemaTool(BaseTool):
    """Tool for saving Cube.js schema definitions."""
    
    name: str = "SaveCubeSchema"
    description: str = "Save or update a Cube.js schema definition to a YAML file"
    
    # Declare Pydantic fields
    schemas_path: str = Field(default="schemas", description="Directory path to save Cube.js schema files")
    
    def __init__(self, schemas_path: Optional[str] = None, **kwargs):
        """
        Initialize the tool with a path to schema files.
        
        Args:
            schemas_path: Directory path to save Cube.js schema files
        """
        # Set the schemas_path before calling super().__init__()
        if schemas_path is not None:
            kwargs['schemas_path'] = schemas_path
        elif 'schemas_path' not in kwargs:
            kwargs['schemas_path'] = os.environ.get("CUBEJS_SCHEMAS_PATH", "schemas")
            
        super().__init__(**kwargs)
        logger.info(f"Initialized SaveCubeSchema tool with path: {self.schemas_path}")

    def _run(self, schema_name: str, schema_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a Cube.js schema definition.
        
        Args:
            schema_name: Name of the schema to save
            schema_definition: The schema definition to save
            
        Returns:
            Result of the save operation
        """
        schemas_dir = Path(self.schemas_path)
        if not schemas_dir.exists():
            schemas_dir.mkdir(parents=True, exist_ok=True)
            
        schema_file = schemas_dir / f"{schema_name}.yml"
        
        try:
            with open(schema_file, 'w') as f:
                yaml.dump(schema_definition, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Saved schema {schema_name} to {schema_file}")
            return {
                "success": True,
                "message": f"Schema {schema_name} saved successfully",
                "path": str(schema_file)
            }
        except Exception as e:
            logger.error(f"Error saving schema {schema_name}: {e}")
            return {
                "success": False,
                "error": f"Failed to save schema {schema_name}: {str(e)}"
            }


class AnalyzeCubeSchemasTool(BaseTool):
    """Tool for analyzing and understanding Cube.js schemas."""
    
    name: str = "AnalyzeCubeSchemas"
    description: str = "Analyze Cube.js schemas to understand data models, relationships, and metrics"
    
    # Declare Pydantic fields
    schemas_path: str = Field(default="schemas", description="Directory path containing Cube.js schema files")
    loader: LoadCubeSchemasTool = Field(default=None, description="Schema loader tool instance")
    
    def __init__(self, schemas_path: Optional[str] = None, **kwargs):
        """
        Initialize the tool.
        
        Args:
            schemas_path: Directory path containing Cube.js schema files
        """
        # Set the schemas_path before calling super().__init__()
        if schemas_path is not None:
            kwargs['schemas_path'] = schemas_path
        elif 'schemas_path' not in kwargs:
            kwargs['schemas_path'] = os.environ.get("CUBEJS_SCHEMAS_PATH", "schemas")
            
        # Create the loader with the same path
        kwargs['loader'] = LoadCubeSchemasTool(kwargs['schemas_path'])
        
        super().__init__(**kwargs)
        logger.info(f"Initialized AnalyzeCubeSchemas tool")

    def _run(self, schema_name: Optional[str] = None, analysis_type: str = "full") -> Dict[str, Any]:
        """
        Analyze Cube.js schemas.
        
        Args:
            schema_name: Optional specific schema to analyze
            analysis_type: Type of analysis to perform (full, measures, dimensions, joins)
            
        Returns:
            Analysis results
        """
        # Handle string "None" values from CrewAI agents
        if schema_name == "None":
            schema_name = None
            
        # Load schemas
        schemas = self.loader._run(schema_name)
        
        if "error" in schemas:
            return schemas
            
        analysis = {}
        
        for name, schema in schemas.items():
            if analysis_type == "full" or analysis_type == "measures":
                # Analyze measures
                measures = self._extract_measures(schema)
                if measures:
                    if "measures" not in analysis:
                        analysis["measures"] = {}
                    analysis["measures"][name] = measures
            
            if analysis_type == "full" or analysis_type == "dimensions":
                # Analyze dimensions
                dimensions = self._extract_dimensions(schema)
                if dimensions:
                    if "dimensions" not in analysis:
                        analysis["dimensions"] = {}
                    analysis["dimensions"][name] = dimensions
            
            if analysis_type == "full" or analysis_type == "joins":
                # Analyze joins
                joins = self._extract_joins(schema)
                if joins:
                    if "joins" not in analysis:
                        analysis["joins"] = {}
                    analysis["joins"][name] = joins
                    
            if analysis_type == "full":
                # Analyze relationships
                relationships = self._analyze_relationships(schema, schemas)
                if relationships:
                    if "relationships" not in analysis:
                        analysis["relationships"] = {}
                    analysis["relationships"][name] = relationships
        
        if not analysis:
            return {"warning": "No analysis could be generated"}
            
        return analysis
    
    def _extract_measures(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract measures from a schema."""
        measures = []
        if "measures" in schema:
            for name, config in schema["measures"].items():
                measures.append({
                    "name": name,
                    "type": config.get("type", "unknown"),
                    "sql": config.get("sql", ""),
                    "description": config.get("description", "")
                })
        return measures
    
    def _extract_dimensions(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract dimensions from a schema."""
        dimensions = []
        if "dimensions" in schema:
            for name, config in schema["dimensions"].items():
                dimensions.append({
                    "name": name,
                    "type": config.get("type", "unknown"),
                    "sql": config.get("sql", ""),
                    "description": config.get("description", "")
                })
        return dimensions
    
    def _extract_joins(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract joins from a schema."""
        joins = []
        if "joins" in schema:
            for name, config in schema["joins"].items():
                joins.append({
                    "name": name,
                    "relationship": config.get("relationship", "unknown"),
                    "sql": config.get("sql", "")
                })
        return joins
    
    def _analyze_relationships(self, schema: Dict[str, Any], all_schemas: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze relationships between schemas."""
        relationships = []
        if "joins" in schema:
            cube_name = schema.get("name", "")
            for join_name, join_config in schema["joins"].items():
                relationship = {
                    "from": cube_name,
                    "to": join_name,
                    "relationship": join_config.get("relationship", "unknown"),
                    "sql_condition": join_config.get("sql", "")
                }
                relationships.append(relationship)
        return relationships 