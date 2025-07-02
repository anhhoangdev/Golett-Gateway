from golett_core.interfaces import CrewInterface
from golett_core.crew.spec import CrewSpec, default_specs
from typing import Dict, Any, Optional, List
from crewai import Agent, Task


class CrewManager(CrewInterface):
    def get_crew_spec(self, name: str) -> CrewSpec:
        # This is a basic implementation. A real one would look up specs
        # from a registry or configuration.
        for spec in default_specs():
            if spec.name == name:
                return spec
        raise ValueError(f"Crew spec '{name}' not found.")

    def list_crew_specs(self) -> list[CrewSpec]:
        return default_specs() 