#!/usr/bin/env python3
"""
Script to check actual CubeJS schema vs hardcoded mappings
"""

import os
import sys

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from golett.tools.cube.client import CubeJsClient
from core.query_mapper import CubeJSQueryMapper
import json

def check_schema_vs_mappings():
    """Check actual CubeJS schema vs hardcoded mappings"""
    
    # Get actual schema
    client = CubeJsClient("http://localhost:4000")
    meta = client.meta()
    
    # Get hardcoded mappings
    mapper = CubeJSQueryMapper()
    
    print("🔍 COMPARING ACTUAL SCHEMA VS HARDCODED MAPPINGS")
    print("=" * 60)
    
    print("\n📊 ACTUAL CUBES IN CUBEJS:")
    actual_cubes = {}
    for cube in meta.get('cubes', []):
        cube_name = cube["name"]
        actual_cubes[cube_name] = {
            "measures": [m["name"] for m in cube.get('measures', [])],
            "dimensions": [d["name"] for d in cube.get('dimensions', [])]
        }
        print(f"\n🔹 Cube: {cube_name}")
        print(f"   Measures: {actual_cubes[cube_name]['measures']}")
        print(f"   Dimensions: {actual_cubes[cube_name]['dimensions']}")
    
    print("\n📝 HARDCODED MAPPINGS:")
    print(f"   Cube mappings: {list(mapper.cube_mapping.values())}")
    print(f"   Measure mappings: {list(mapper.measure_mapping.keys())}")
    print(f"   Dimension mappings: {list(mapper.dimension_mapping.keys())}")
    
    print("\n❌ MISMATCHES FOUND:")
    
    # Check cube mismatches
    mapped_cubes = set(mapper.cube_mapping.values())
    actual_cube_names = set(actual_cubes.keys())
    
    missing_cubes = mapped_cubes - actual_cube_names
    extra_cubes = actual_cube_names - mapped_cubes
    
    if missing_cubes:
        print(f"   🚫 Mapped cubes not in actual schema: {missing_cubes}")
    if extra_cubes:
        print(f"   ➕ Actual cubes not in mappings: {extra_cubes}")
    
    # Check measure mismatches for each cube
    for cube_name in mapped_cubes.intersection(actual_cube_names):
        if cube_name in mapper.measure_mapping:
            mapped_measures = set(mapper.measure_mapping[cube_name].values())
            actual_measures = set(actual_cubes[cube_name]["measures"])
            
            missing_measures = mapped_measures - actual_measures
            extra_measures = actual_measures - mapped_measures
            
            if missing_measures or extra_measures:
                print(f"\n   🔹 {cube_name}:")
                if missing_measures:
                    print(f"      🚫 Mapped measures not in schema: {missing_measures}")
                if extra_measures:
                    print(f"      ➕ Actual measures not in mappings: {extra_measures}")
    
    # Check dimension mismatches
    for cube_name in mapped_cubes.intersection(actual_cube_names):
        if cube_name in mapper.dimension_mapping:
            mapped_dimensions = set(mapper.dimension_mapping[cube_name].values())
            actual_dimensions = set(actual_cubes[cube_name]["dimensions"])
            
            missing_dimensions = mapped_dimensions - actual_dimensions
            extra_dimensions = actual_dimensions - mapped_dimensions
            
            if missing_dimensions or extra_dimensions:
                print(f"\n   🔹 {cube_name} dimensions:")
                if missing_dimensions:
                    print(f"      🚫 Mapped dimensions not in schema: {missing_dimensions}")
                if extra_dimensions:
                    print(f"      ➕ Actual dimensions not in mappings: {extra_dimensions}")
    
    print("\n" + "=" * 60)
    print("✅ Schema comparison completed!")

if __name__ == "__main__":
    check_schema_vs_mappings() 