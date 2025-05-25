import json
import os
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import requests
import time

from golett.utils.logger import get_logger

logger = get_logger(__name__)

class CubeJsClient:
    """
    Client for interacting with the Cube.js REST API.
    
    This class provides methods to query and interact with a Cube.js server,
    allowing agents to retrieve and analyze BI data.
    """
    
    def __init__(
        self,
        api_url: str,
        api_token: Optional[str] = None,
        timeout: int = 30
    ) -> None:
        """
        Initialize the Cube.js client.
        
        Args:
            api_url: Base URL of the Cube.js API (e.g., "http://localhost:4000")
            api_token: Optional API token for authentication
            timeout: Request timeout in seconds
        """
        # Ensure proper API URL format
        self.base_url = api_url.rstrip('/')
        
        # Add the standard Cube.js API path if not already present
        if not self.base_url.endswith('/cubejs-api/v1'):
            if self.base_url.endswith('/cubejs-api'):
                self.base_url += '/v1'
            else:
                self.base_url += '/cubejs-api/v1'
        
        self.api_token = api_token or os.getenv("CUBEJS_API_TOKEN")
        self.timeout = timeout
        
        if not self.api_token:
            logger.warning("No Cube.js API token provided. Some requests may fail.")
            
        logger.info(f"Initialized Cube.js client for {self.base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_token:
            # Use Authorization header as per Cube.js documentation
            headers["Authorization"] = self.api_token
            
        return headers
    
    def load(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a query and load data from Cube.js.
        
        Args:
            query: The Cube.js query object (measures, dimensions, etc.)
            
        Returns:
            The query result data
        """
        url = f"{self.base_url}/load"
        headers = self._get_headers()
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json={"query": query},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error executing Cube.js query: {e}")
            raise
    
    def sql(self, query: str) -> Dict[str, Any]:
        """
        Execute a SQL query against Cube.js.
        
        Args:
            query: SQL query string
            
        Returns:
            The query result data
        """
        url = f"{self.base_url}/sql"
        headers = self._get_headers()
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json={"query": query},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error executing Cube.js SQL query: {e}")
            raise
    
    def meta(self) -> Dict[str, Any]:
        """
        Get Cube.js metadata.
        
        Returns:
            The metadata for all available cubes and their measures/dimensions
        """
        url = f"{self.base_url}/meta"
        headers = self._get_headers()
        
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error retrieving Cube.js metadata: {e}")
            raise
    
    def dry_run(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a dry run of a query without executing it.
        
        Args:
            query: The Cube.js query object
            
        Returns:
            The SQL query that would be generated
        """
        url = f"{self.base_url}/dry-run"
        headers = self._get_headers()
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json={"query": query},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error performing Cube.js dry run: {e}")
            raise
    
    def run_scheduled_refresh(
        self, 
        query_id: str, 
        wait_for_completion: bool = False,
        wait_timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Run a scheduled refresh for pre-aggregations.
        
        Args:
            query_id: The ID of the query to refresh
            wait_for_completion: Whether to wait for refresh completion
            wait_timeout: Maximum time to wait (in seconds)
            
        Returns:
            The refresh status
        """
        url = f"{self.base_url}/pre-aggregations/jobs/{query_id}"
        headers = self._get_headers()
        
        try:
            response = requests.post(
                url,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            if wait_for_completion:
                start_time = time.time()
                job_id = result.get("id")
                
                if not job_id:
                    logger.warning("No job ID returned, cannot wait for completion")
                    return result
                
                status = "created"
                while status not in ["finished", "failure"] and (time.time() - start_time) < wait_timeout:
                    time.sleep(5)  # Poll every 5 seconds
                    status_result = self.get_refresh_status(job_id)
                    status = status_result.get("status", "unknown")
                    
                    if status in ["finished", "failure"]:
                        result = status_result
                        break
                
                if status not in ["finished", "failure"]:
                    logger.warning(f"Refresh job {job_id} did not complete within timeout")
            
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Error running Cube.js scheduled refresh: {e}")
            raise
    
    def get_refresh_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a refresh job.
        
        Args:
            job_id: The ID of the job to check
            
        Returns:
            The job status
        """
        url = f"{self.base_url}/pre-aggregations/jobs/{job_id}"
        headers = self._get_headers()
        
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking Cube.js refresh status: {e}")
            raise
    
    def cancel_refresh(self, job_id: str) -> Dict[str, Any]:
        """
        Cancel a refresh job.
        
        Args:
            job_id: The ID of the job to cancel
            
        Returns:
            The cancellation status
        """
        url = f"{self.base_url}/pre-aggregations/jobs/{job_id}/cancel"
        headers = self._get_headers()
        
        try:
            response = requests.post(
                url,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error canceling Cube.js refresh job: {e}")
            raise
    
    def build_query(
        self,
        measures: Optional[List[str]] = None,
        dimensions: Optional[List[str]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        time_dimensions: Optional[List[Dict[str, Any]]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Build a Cube.js query object from parameters.
        
        Args:
            measures: List of measures to include
            dimensions: List of dimensions to include
            filters: List of filters to apply
            time_dimensions: List of time dimensions with granularity/date range
            limit: Maximum number of rows to return
            offset: Number of rows to skip
            order: Sorting specifications
            
        Returns:
            A complete query object for the Cube.js API
        """
        query = {}
        
        if measures:
            query["measures"] = measures
            
        if dimensions:
            query["dimensions"] = dimensions
            
        if filters:
            query["filters"] = filters
            
        if time_dimensions:
            query["timeDimensions"] = time_dimensions
            
        if limit is not None:
            query["limit"] = limit
            
        if offset is not None:
            query["offset"] = offset
            
        if order:
            query["order"] = order
            
        return query 