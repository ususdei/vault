
from distutils.core import setup

setup(  name='vault',
        version='0.9',
        description='python interface to pass',
        author='Markus Blöchl',
        author_email='ususdei@googlemail.com',
        packages=['vault', 'vault.init', 'vault.backend'],
        scripts=['bin/vault'],
     )
