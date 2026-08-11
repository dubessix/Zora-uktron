from setuptools import setup, find_packages

setup(
    name="ultron",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.111.0",
        "uvicorn>=0.30.0",
        "websockets>=12.0",
        "python-dotenv>=1.0.0",
        "PyYAML>=6.0.0",
        "pydantic>=2.8.0",
        "pydantic-settings>=2.3.0",
        "numpy>=2.1.0",
        "httpx>=0.27.0",
        "click>=8.1.0",
        "psutil>=6.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ultron=backend.app.cli:main",
        ],
    },
    author="Arena AI & Debjeet",
    description="Ultron V1: Personal Developer Partner & Emotional Companion.",
)
