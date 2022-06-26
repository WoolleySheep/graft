# graft

## Graph-based task management

Graft seeks to solve the two problems I run into when deciding what to work on:
1. What is the most important task I have to do?
2. What should I be working on right now to do that most important task ASAP?

## Installation instructions
TODO

## How to run
    python -m main.py

## For developers
### Install developer dependencies
    pip install -r requirements-dev.txt
### Sort imports
    isort .
### Format code
    black .
### Run tests
    pytest
### Lint code
    pylama graft tests
### Generate & view code coverage report
    pytest --cov-report html --cov=graft
Open htmlcov/index.html in a browser to view the report
### Run mypy
    mypy graft --strict
