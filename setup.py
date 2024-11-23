from setuptools import setup, find_packages

setup(
    name="mechsys_uav",
    py_modules=["mechsys_uav"],
    version="0.1.1",
    description="PX4 UAV handling wrapper for Mechsys",
    author="Leon Seidel",
    url="https://github.com/leon-seidel/mechsys_uav",
    packages=find_packages(),
    install_requires=["mavsdk", "shapely"],
    include_package_data=True,
)