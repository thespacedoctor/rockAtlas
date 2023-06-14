from setuptools import setup, find_packages
import os

moduleDirectory = os.path.dirname(os.path.realpath(__file__))
exec(open(moduleDirectory + "/rockAtlas/__version__.py").read())


def readme():
    with open(moduleDirectory + '/README.rst') as f:
        return f.read()


install_requires = [
    'pyyaml',
    'rockAtlas',
    'fundamentals',
    'hmpty',
    'pymysql',
    'astrocalc',
    'pyephem',
    'healpy',
    'scipy',
    'multiprocess'
]

# READ THE DOCS SERVERS
exists = os.path.exists("/home/docs/")
if exists:
    c_exclude_list = ['healpy', 'astropy',
                      'numpy', 'sherlock', 'wcsaxes', 'HMpTy', 'ligo-gracedb']
    for e in c_exclude_list:
        try:
            install_requires.remove(e)
        except:
            pass

setup(name="rockAtlas",
      version=__version__,
      description="A python package and command-line tools to A suite of tools to pull known solar-system small-body detections out of ATLAS data",
      long_description=readme(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Utilities',
      ],

      keywords=['atlas, asteroid, astronomy'],
      url='https://github.com/thespacedoctor/rockAtlas',
      download_url='https://github.com/thespacedoctor/rockAtlas/archive/v%(__version__)s.zip' % locals(
      ),
      author='David Young',
      author_email='davidrobertyoung@gmail.com',
      license='MIT',
      packages=find_packages(exclude=["*tests*"]),
      include_package_data=True,
      install_requires=install_requires,
      test_suite='nose2.collector.collector',
      tests_require=['nose2', 'cov-core'],
      entry_points={
          'console_scripts': ['rockAtlas=rockAtlas.cl_utils:main'],
      },
      zip_safe=False)
