from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="NeoCompression",
    version="1.0.0",
    author="Fizzolas",
    author_email="",
    description="Adaptive binary compression tool that converts files/folders into highly compressed ASCII representations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Fizzolas/NeoCompression",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Archiving :: Compression",
        "Topic :: Utilities",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "neocompression=neocompression.cli:main",
            "neo=neocompression.cli:main",
        ],
    },
    install_requires=[],
    extras_require={
        "gui": ["tkinter-dragmanager"],
        "dev": ["pyinstaller", "pytest"],
    },
)