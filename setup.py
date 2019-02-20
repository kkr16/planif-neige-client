import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="planif-neige-client",
    version="0.0.4",
    author="Karim Roukoz",
    author_email="roukoz@gmail.com",
    description="A python client for Montreal's Planif-Neige snow removal API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords = ['montreal','snow removal','neige','deneigement','quebec'],
    install_requires = ['zeep'],
    url="https://github.com/kkr16/planif-neige-client",
    packages=setuptools.find_packages(),
)

