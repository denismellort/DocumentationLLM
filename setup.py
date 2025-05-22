from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="documentationllm",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Processador Inteligente de Documentação para LLMs com Supervisão de IA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/documentationllm",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup :: Markdown",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "gitpython>=3.1.30",
        "pyyaml>=6.0",
        "markdown>=3.4.0",
        "beautifulsoup4>=4.11.0",
        "tqdm>=4.64.0",
        "colorama>=0.4.6",
        "click>=8.1.3",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "docllm=documentationllm.cli:main",
        ],
    },
)
