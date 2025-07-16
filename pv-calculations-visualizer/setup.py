from setuptools import setup, find_packages

setup(
    name='pv-calculations-visualizer',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A project for visualizing photovoltaic calculations and generating PDF reports.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/pv-calculations-visualizer',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'reportlab',  # For PDF generation
        'matplotlib',  # For visualizations
        'numpy',      # For numerical calculations
        'pandas',     # For data manipulation
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)