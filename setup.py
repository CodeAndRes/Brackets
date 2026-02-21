#!/usr/bin/env python3
"""Setup para Brackets - Sistema de Gestión de Bitácoras y Notas."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="brackets",
    version="3.0.0",
    author="Tu Nombre",
    description="Sistema modular de gestión de bitácoras semanales y notas organizadas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tuusuario/brackets",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Scheduling",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "brackets=brackets.main:main",
        ],
    },
)
