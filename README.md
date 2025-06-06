# graft

## Graph-based task management

Graft seeks to solve the two problems I run into when deciding what to work on:
1. What is the most important task I have to do?
2. What should I be working on right now to do that most important task ASAP?

## Installation instructions
TODO

## How to run GUI app
```
python main.py
```

## For developers
### Install developer dependencies
```
poetry install
```

### Launch poetry environment
```
poetry env activate
```

### Update dependencies
```
poetry update
```

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
ruff check --unsafe-fixes --show-fixes --fix graft tests
pylint graft tests
vulture graft tests
autoflake -r graft tests
```

### Run tests
```
pytest tests
```
### Generate code coverage report
```
pytest tests --cov-report html --cov=graft
```
Open htmlcov/index.html in a browser to view the report

### Build executable
```
pyinstaller main.py --onefile --noconsole --name graft
```
After building is complete, `graft.exe` can be found in the `dist` directory
