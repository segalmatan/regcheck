import setuptools


README = open("README.md", "r", encoding="utf-8").read()

setuptools.setup(
    name="regcheck",
    version="1.0.0",
    author="Matan Segal",
    description="Regex-like python objects sequence checker",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/segalmatan/regcheck",
    project_urls={
        "Bug Tracker": "https://github.com/segalmatan/regcheck/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(exclude=["test*"]),
    python_requires=">=2.7",
)