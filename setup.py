from setuptools import setup, find_packages

setup(
    name="powerbi-embedded-sample",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "powerbi-embedded-sample = powerbi_embedded_sample.main:main"
        ]
    },
    install_requires=["adal==1.1.0", "sanic==0.7.0", "Jinja2==2.10"],
)
