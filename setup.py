from setuptools import setup, find_packages

setup(
    name="paypaypay",
    version="4.3.0",
    packages=find_packages(),
    install_requires=["requests", "pkce"],
    python_requires=">=3.10",
)
