import setuptools


DESCRIPTION = ("Standalone Engine Runner for Gabriel Server. This must be used "
               "with gabriel-server.")


setuptools.setup(
    name="gabriel-standalone-engine",
    version="0.0.2",
    author="Roger Iyengar",
    author_email="ri@rogeriyengar.com",
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    long_description_content_type="text/markdown",
    url="http://gabriel.cs.cmu.edu",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    license="Apache",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "gabriel-protocol==0.0.4",
        "pyzmq==18.1",
    ],
)
