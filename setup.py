from setuptools import setup, find_namespace_packages

setup(
    name="ultron",
    version="1.0.0",
    # The backend is laid out as a namespace package (no __init__.py in most
    # subpackages). find_namespace_packages() discovers ALL of backend.app.*,
    # so the built wheel actually contains the code (find_packages() was
    # returning an empty list and shipping an empty wheel).
    packages=find_namespace_packages(include=["backend*"], exclude=["*.test*"]),
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
        "edge-tts>=6.1.0",   # TTS provider (was missing -> voice broke after install)
    ],
    entry_points={
        "console_scripts": [
            "ultron=backend.app.cli:main",
        ],
    },
    author="Arena AI & Debjeet",
    description="Ultron V1: Personal Developer Partner & Emotional Companion.",
    python_requires=">=3.9",
)
