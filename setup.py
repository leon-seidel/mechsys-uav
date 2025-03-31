from setuptools import setup, find_packages

setup(
    name="mechsys-uav",
    py_modules=["mechsys_uav"],
    version="0.2.0",
    description="PX4 UAV handling wrapper for Mechsys",
    author="Leon Seidel",
    url="https://github.com/leon-seidel/mechsys-uav",
    packages=find_packages(),
    install_requires=["mavsdk", "shapely", "haversine"],
    include_package_data=True,
)
