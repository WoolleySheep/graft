# graft

## Graph-based task management

Graft seeks to solve the two problems I run into when deciding what to work on:
1. What is the most important task I have to do?
2. What should I be working on right now to do that most important task ASAP?

## Installation instructions
TODO

## How to run
```python -m main.py```

## For developers
### Install developer dependencies
```poetry install```
### Format
```
isort graft
black graft
```
### Lint
```
mypy --strict graft
pylint graft
ruff --fix graft
vulture graft
autoflake -r graft
pydocstringformatter graft
```
