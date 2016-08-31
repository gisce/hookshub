from setuptools import setup

setup(name='hookshub',
      version='0.1',
      description='A module for parsing and acting against JSON hooks',
      url='https://github.com/gisce/github-hooks',
      author='Jaume Florez',
      author_email='jflorez@gisce.net',
      license='MIT',
      packages=[
          'hookshub', 'hookshub/hooks', 'hookshub/hooks/github/',
          'hookshub/hooks/gitlab/', 'hookshub/hooks/webhook/',
      ],
      zip_safe=False)
