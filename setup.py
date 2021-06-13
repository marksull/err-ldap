from setuptools import setup, find_packages

setup(
    name='errldap',
    version='1.0.0',
    author="Mark Sullivan",
    packages=find_packages(),
    author_email="mark@sullivans.id.au",
    url="http://github.com/marksull/errldap",
    install_requires=["errbot", "python-ldap"],
    description="Decorator to limit Errbot commands to specific LDAP groups",
)

