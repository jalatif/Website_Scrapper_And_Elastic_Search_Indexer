__author__ = 'manshu'

from setuptools import setup, find_packages

setup(
    name='cs410_hw2_scraper',
    version='1.0',
    packages=find_packages(),
    entry_points={'scrapy': ['settings = cs410_hw2_scraper.settings']},
)