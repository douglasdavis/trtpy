from setuptools import setup

setup(name='trtpy',
      version='0.0.1alpha',
      description='TRT Python Toolkit',
      url='https://gitlab.cern.ch/atlas-trt-software/trtpy',
      author='Doug Davis',
      author_email='ddavis@cern.ch',
      license='MIT',
      install_requires=[
          'numpy',
          'scipy',
          'pyyaml',
      ],
      packages=[
          'trtpy',
          'trtpy.pid'
      ]
)
