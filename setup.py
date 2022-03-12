from setuptools import setup, find_packages

setup(name='TeleDjan_Auth',
      version='0.1',
      url='https://github.com/rouelboom/TeleDjan_Auth',
      license='MIT',
      author='Pavel Senokosov',
      author_email='rouel.boom@gmail.com',
      description='Lib for auth to djoser by telegram bot with using of Django ORM',
      packages=find_packages(exclude=['tests']),
      long_description=open('README.md').read(),
      zip_safe=False)


#
# with open("README.md", "r") as readme_file:
#     readme = readme_file.read()
#
# requirements = ["ipython>=6", "nbformat>=4", "nbconvert>=5", "requests>=2"]
#
# setup(
#     name="notebookc",
#     version="0.0.1",
#     author="Jeff Hale",
#     author_email="jeffmshale@gmail.com",
#     description="A package to convert your Jupyter Notebook",
#     long_description=readme,
#     long_description_content_type="text/markdown",
#     url="https://github.com/your_package/homepage/",
#     packages=find_packages(),
#     install_requires=requirements,
#     classifiers=[
#         "Programming Language :: Python :: 3.7",
#         "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
#     ],
# )
