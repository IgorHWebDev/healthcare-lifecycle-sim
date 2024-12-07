from setuptools import setup, find_packages

setup(
    name="healthcare_sim",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit>=1.24.0",
        "plotly>=5.14.0",
        "python-dateutil>=2.8.2",
        "typing-extensions>=4.6.3",
        "dataclasses>=0.6",
        "python-dotenv>=1.0.0",
        "watchdog>=3.0.0"
    ],
    author="Healthcare Sim Team",
    description="Healthcare Lifecycle Simulation",
    python_requires=">=3.8",
    package_dir={"": "."},
    package_data={
        "healthcare_sim": ["*.py", "*/*.py", "*/*/*.py"]
    }
)
