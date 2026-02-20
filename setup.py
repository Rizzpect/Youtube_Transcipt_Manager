from setuptools import setup, find_packages

setup(
    name="youtube-transcript-manager",
    version="2.0.0",
    description="Fetch, search, organize, and manage YouTube video transcripts",
    author="Rizzpect",
    author_email="",
    url="https://github.com/Rizzpect/Youtube_Transcipt_Manager",
    packages=find_packages(),
    install_requires=[
        "scrapetube>=2.5.0",
        "google-api-python-client>=2.0.0",
        "youtube-transcript-api>=0.6.0",
        "tqdm>=4.60.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ytm=ytm.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
