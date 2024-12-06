from setuptools import setup, find_packages

setup(
    name="healthcare_sim",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'plotly',
        'pandas',
        'numpy',
        'openai',
        'python-dotenv'
    ],
    author="Igor",
    description="A healthcare facility simulation system with generative agents",
    python_requires=">=3.8",
) 