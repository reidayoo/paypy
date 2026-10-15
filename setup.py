from setuptools import setup, find_packages

setup(
    name="paypaypay",
    version="4.5.0",
    packages=find_packages(),
    install_requires=["requests", "pkce", "curl_cffi", "cryptography"],
    python_requires=">=3.10",
)
