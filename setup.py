from setuptools import setup, find_packages

setup(
    name="foxtronpi_client",
    version="0.1.0",
    description="Python diagnostic and control client package for FoxtronPi (D31x model)",
    author="Foxtron",
    packages=find_packages(),
    python_requires=">=3.10",
    package_data={
        "foxtronpi_client": ["*.so"],
    },
    install_requires=[
        "cffi>=1.17.1",
        "cryptography>=45.0.6",
        "doipclient>=1.1.7",
        "pycparser>=2.22",
        "PySide6>=6.8.2",
        "udsoncan>=1.25.0",
        "pyqtgraph>=0.13.7",
        "numpy>=2.2.3",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Operating System :: POSIX :: Linux",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
