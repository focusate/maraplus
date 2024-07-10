from setuptools import setup, find_packages

with open('README.rst', encoding='utf-8') as f:
    readme = f.read()

test_deps = [
    "pytest",
    "mock",
]

extras = {
    'test': test_deps,
}

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
    install_requires=[
        'marabunta>=0.12.0',
        'mergedeep>=1.3.4',
        'PyYAML>=6.0.1',
        # marabunta uses distutils, but it was removed in 3.12, so
        # we must install setuptools manually, before marabunta fixes
        # this themselves.
        'setuptools>=70.3.0',
    ],
    tests_require=test_deps,
    extras_require=extras,
    setup_requires=[
        'setuptools_scm',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: '
        + 'GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    entry_points={
        'console_scripts': ['maraplus = maraplus.core:main']
    },
)
