from setuptools import setup

setup(name='minio_etl_connector',
      version='2.0',
      description='minio_connector for etl',
      url='',
      author='Gabe McWilliams',
      author_email='gmcwilliams@example.co',
      install_requires=['minio', 'hvac', 'io', 're', 'traceback'],
      license='MIT',
      packages=['minio_connector'],
      zip_safe=False)
