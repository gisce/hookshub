from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
    INSTALL_REQUIRES = f.readlines()

with open('requirements-dev.txt', 'r') as f:
    TESTS_REQUIRE = f.readlines()

setup(name='hookshub',
      version='0.1',
      description='A module for parsing and acting against JSON hooks',
      url='git@github.com:gisce/hookshub.git',
      author='Jaume Florez',
      author_email='jflorez@gisce.net',
      license='MIT',
      install_requires=INSTALL_REQUIRES,
      tests_require=TESTS_REQUIRE,
      packages=find_packages(),
      zip_safe=False)
