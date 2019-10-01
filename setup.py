import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gabriel-server",
    version="0.0.2",
    author="Roger Iyengar",
    author_email="ri@rogeriyengar.com",
    description="Server for Wearable Cognitive Assistance Applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cmusatyalab/gabriel-server-common",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "protobuf>=3.9.1",
        "websockets==8.0.2",
        "zmq>=0.0.0",
    ],
)
