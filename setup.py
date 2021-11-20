from setuptools import setup, find_packages

with open('README.rst', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='maraplus',
    use_scm_version=True,
    description="Migration and setup tool for Odoo",
    long_description=readme,
    author="Focusate (Andrius Laukavičius)",
    author_email='dev@focusate.eu',
    url="https://github.com/focusate/maraplus",
    license='AGPLv3+',
    packages=find_packages(),
    install_requires=['marabunta>=0.10.6'],
    setup_requires=[
        'setuptools_scm',
    ],
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: '
        'GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ),
    entry_points={
        'console_scripts': ['maraplus = marabunta.main:main']
    },
)