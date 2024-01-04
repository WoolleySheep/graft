# graft

## Graph-based task management

Graft seeks to solve the two problems I run into when deciding what to work on:
1. What is the most important task I have to do?
2. What should I be working on right now to do that most important task ASAP?

## Installation instructions
TODO

## How to run app
### Run as CLI
Activate CLI by uncommenting `graft.run_cli()`
```python main.py --help```

### Run as GUI
activate GUI by uncommenting `graft.run_gui()`
```python main.py```

## For developers
### Install developer dependencies
```poetry install```

### Launch poetry environment
```poetry shell```

### Format
```
ruff format graft tests
pydocstringformatter graft tests
```

### Type-check
```
pyright graft tests
```

### Lint
```
ruff --fix graft tests
pylint graft tests
vulture graft tests
autoflake -r graft tests
```

### Run tests
```pytest```
### Generate & view code coverage report
```pytest --cov-report html --cov=graft```

Open htmlcov/index.html in a browser to view the report
