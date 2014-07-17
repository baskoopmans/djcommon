from setuptools import setup, find_packages

setup(
    name='djcommon',
    version=__import__('djcommon').__version__,
    description='Django Common (djcommon) - A set of project independent reusable features while developing with the Django Framework - https://www.djangoproject.com/ ',
    long_description=open('README.rst').read(),
    # Get more strings from http://www.python.org/pypi?:action=list_classifiers
    author='Bas Koopmans',
    author_email='django@baskoopmans.nl',
    url='http://github.com/baskoopmans/djcommon/',
    download_url='http://github.com/baskoopmans/djcommon/downloads',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False, # because we're including media that Django needs
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
