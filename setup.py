#!/usr/bin/env python3
"""
Setup script for the Ubiwell Study Framework Core package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Ubiwell Study Framework Core"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="study-framework-core",
    version="1.0.0",
    description="Core framework for Ubiwell study deployments",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Ubiwell Team",
    author_email="team@ubiwell.com",
    url="https://github.com/your-org/ubiwell-study-backend-core",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "console_scripts": [
            "setup-study=study_framework_core.setup_study:main",
            "update-core=study_framework_core.update_core:main",
        ],
    },
)



