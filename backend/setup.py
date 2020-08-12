from setuptools import find_packages, setup

setup(
    name="labyrinth",
    version="0.1.6",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask", "requests"],
)
