#!/usr/bin/env python3
"""
Setup script for Golett Gateway - A modular, long-term conversational agent framework
"""

from setuptools import setup, find_packages
import os
import re

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read version from __init__.py
def get_version():
    with open("golett/__init__.py", "r", encoding="utf-8") as fh:
        content = fh.read()
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")

# Read requirements from requirements.txt
def read_requirements():
    requirements = []
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                # Remove version pinning for more flexible installation
                if "==" in line:
                    package = line.split("==")[0]
                    requirements.append(package)
                else:
                    requirements.append(line)
    return requirements

# Core dependencies (essential for basic functionality)
CORE_REQUIREMENTS = [
    "crewai>=0.120.0",
    "psycopg2-binary>=2.9.0",
    "qdrant-client>=1.14.0",
    "openai>=1.0.0",
    "pydantic>=2.0.0",
    "sqlalchemy>=2.0.0",
    "python-dotenv>=1.0.0",
    "requests>=2.32.0",
    "numpy>=1.24.0",
    "pandas>=2.0.0",
    "sentence-transformers>=2.2.0",
    "tiktoken>=0.5.0",
    "tenacity>=8.0.0",
    "rich>=13.0.0",
    "typer>=0.9.0",
]

# Optional dependencies for extended functionality
EXTRAS_REQUIRE = {
    "dev": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
        "black>=23.0.0",
        "isort>=5.12.0",
        "flake8>=6.0.0",
        "mypy>=1.0.0",
        "pre-commit>=3.0.0",
    ],
    "docs": [
        "sphinx>=6.0.0",
        "sphinx-rtd-theme>=1.2.0",
        "myst-parser>=1.0.0",
        "sphinx-autodoc-typehints>=1.20.0",
    ],
    "cube": [
        "requests>=2.32.0",
        "pyyaml>=6.0.0",
    ],
    "visualization": [
        "matplotlib>=3.7.0",
        "plotly>=5.15.0",
        "seaborn>=0.12.0",
    ],
    "huggingface": [
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "datasets>=2.12.0",
    ],
    "all": [
        "requests>=2.32.0",
        "pyyaml>=6.0.0",
        "matplotlib>=3.7.0",
        "plotly>=5.15.0",
        "seaborn>=0.12.0",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "datasets>=2.12.0",
    ]
}

setup(
    name="golett-gateway",
    version=get_version(),
    author="Anh Hoang",
    author_email="anhhoangdev@example.com",  # Update with actual email
    description="A modular, long-term conversational agent framework built on CrewAI with enhanced memory and BI capabilities",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/anhhoangdev/Golett-Gateway",  # Update with actual repo URL
    project_urls={
        "Bug Tracker": "https://github.com/anhhoangdev/Golett-Gateway/issues",
        "Documentation": "https://github.com/anhhoangdev/Golett-Gateway/docs",
        "Source Code": "https://github.com/anhhoangdev/Golett-Gateway",
    },
    packages=find_packages(exclude=["tests*", "examples*", "docs*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.8",
    install_requires=CORE_REQUIREMENTS,
    extras_require=EXTRAS_REQUIRE,
    include_package_data=True,
    package_data={
        "golett": [
            "config/*.yaml",
            "config/*.yml",
            "config/*.json",
            "knowledge/schemas/*.yml",
            "knowledge/schemas/*.yaml",
        ],
    },
    entry_points={
        "console_scripts": [
            "golett=golett.cli:main",  # Will be created if CLI is needed
        ],
    },
    keywords=[
        "ai",
        "agents",
        "crewai",
        "business-intelligence",
        "conversational-ai",
        "memory-management",
        "postgresql",
        "qdrant",
        "vector-database",
        "llm",
        "chatbot",
        "bi",
        "data-analysis",
    ],
    zip_safe=False,
    test_suite="tests",
    tests_require=[
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
    ],
) 