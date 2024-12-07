from setuptools import setup, find_packages

setup(
    name="healthcare_sim",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.24.0",
        "plotly>=5.14.0",
        "python-dateutil>=2.8.2",
        "typing-extensions>=4.6.3",
        "dataclasses>=0.6"
    ],
    author="Cursor AI",
    description="Healthcare Lifecycle Simulation",
    python_requires=">=3.8",
)
