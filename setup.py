"""
Setup configuration for Vibify
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setup(
    name="vibify",
    version="1.0.0",
    author="Vibify Team",
    author_email="team@vibify.com",
    description="AI-powered music recommendation system using musical DNA analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourname/vibify",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "basic-pitch>=1.0.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "openai>=1.0.0",
        "librosa>=0.9.0",
        "soundfile>=0.12.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
        "advanced": [
            "essentia>=2.1b6.dev374",
            "madmom>=0.16.1",
        ]
    },
    entry_points={
        "console_scripts": [
            "vibify=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)