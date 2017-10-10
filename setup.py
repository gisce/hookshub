from setuptools import setup

requirements = [
      'requests',
      'osconf',
      'flask',
      'raven==5.0.0',
      'blinker',
      'virtualenv'
]

setup(name='hookshub',
      version='1.0',
      description='A module for parsing and acting against JSON hooks',
      url='git@github.com:gisce/hookshub.git',
      author='Jaume Florez',
      author_email='jflorez@gisce.net',
      license='MIT',
      install_requires=requirements,
      packages=[
          'hookshub', 'hookshub/hooks', 'hookshub/hooks/webhook_hooks/',
      ],
      zip_safe=False)
