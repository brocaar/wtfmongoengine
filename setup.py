from setuptools import setup


setup(
    name='WTFMongoengine',
    version='0.1',
    url='http://github.com/brocaar/wtfmongoengine',
    license='BSD',
    author='Orne Brocaar',
    author_email='info@brocaar.com',
    description='WTForms for Mongoengine documents',
    long_description=open('README.rst').read(),
    packages=[
        'wtfmongoengine',
    ],
    tests_require=[
        'mock',
        'wtforms',
        'mongoengine',
        'unittest2',
    ],
    test_suite='wtfmongoengine.tests.suite',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
