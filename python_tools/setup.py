from setuptools import setup

setup(name='SBISToolkit',
      version='1.4',
      description='SBIS Python dev toolkit.',
      author='Vladislav Vasyuk',
      author_email='nazgarth@gmail.com',
      packages=[
         'sbis_toolkit',
         'sbis_toolkit.git_sbis',
         'sbis_toolkit.bl_methods',
         'sbis_toolkit.utils'
      ],
      install_requires=[
         'gitpython'
      ],
      package_data={
          'sbis_toolkit': ['config.ini'],
      }
     )
