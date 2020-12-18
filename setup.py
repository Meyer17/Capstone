import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="shtmkr",
    version="1.0.0",
    entry_points={
        'console_scripts': [
            'shtmkr=runner:run'
        ]
    },
    author="Max Coy, Bridgette Meyer, Benigno Chihuahua, Jacob Tycko",
    author_email="benignovc@berkeley.edu",
    description="Music Transcription Software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Meyer17/Capstone",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)