from setuptools import setup, find_packages

setup(
    name="mi_mcp_gemini",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "google-genai>=1.0.0",
        "cryptography>=41.0",
        "python-dotenv>=1.0.0",
        "PyGithub>=2.0.0"
    ],
    python_requires=">=3.10",
    url="https://github.com/tu_usuario/mi_mcp_gemini",
    author="Alberto",
    author_email="tu_email@example.com",
    description="MCP profesional con Google Gemini, gestión de múltiples API Keys cifradas y agente autónomo.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "mi-mcp-gemini=ia_core.main:main",
        ],
    },
)
