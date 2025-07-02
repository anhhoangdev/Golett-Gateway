import os
from typing import Type, Any
from pydantic import BaseModel, Field, ConfigDict

from golett_core.tools.tool_interface import Tool
from golett_core.settings import settings

class FileToolSchema(BaseModel):
    """Input schema for the FileTool."""
    operation: str = Field(description="The operation to perform: 'read' or 'write'.")
    path: str = Field(description="The relative path to the file.")
    content: str | None = Field(default=None, description="The content to write to the file (required for 'write' operation).")

    model_config = ConfigDict(
        extra="forbid" if settings.pydantic_mode == "strict" else "allow",
    )

class FileTool(Tool):
    name: str = "File I/O Tool"
    description: str = "A tool to read from and write to files in the local filesystem."
    args_schema: Type[BaseModel] = FileToolSchema

    model_config = ConfigDict(
        extra="forbid" if settings.pydantic_mode == "strict" else "allow",
        arbitrary_types_allowed=True,
    )

    def _run(
        self,
        operation: str,
        path: str,
        content: str | None = None,
    ) -> str:
        try:
            if operation == "read":
                if not os.path.exists(path):
                    return f"Error: File not found at {path}"
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            elif operation == "write":
                if content is None:
                    return "Error: 'content' is required for the 'write' operation."
                
                dir_name = os.path.dirname(path)
                if dir_name:
                    os.makedirs(dir_name, exist_ok=True)
                
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return f"Successfully wrote {len(content)} characters to {path}"
            else:
                return f"Error: Unknown operation '{operation}'. Valid operations are 'read' and 'write'."
        except Exception as e:
            return f"An unexpected error occurred: {e}" 