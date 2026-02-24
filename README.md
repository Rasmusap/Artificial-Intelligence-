# Artificial-Intelligence-

Python starter scaffold for building a turn-based game with:
- game logic (`src/game`)
- UI layer (`src/ui`)
- AI agents (`src/agent`)

The app now runs in a separate window using `pygame`.

## Virtual environment (Windows / PowerShell)

Create a virtual environment in the repo root:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, allow scripts for your current session and try again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Upgrade packaging tools (recommended):

```powershell
python -m pip install --upgrade pip
```

## Project structure

```text
.
|-- assets/
|   `-- .gitkeep
|-- scripts/
|   `-- run.ps1
|-- src/
|   |-- agent/
|   |   |-- __init__.py
|   |   |-- base.py
|   |   |-- minimax_agent.py
|   |   `-- random_agent.py
|   |-- common/
|   |   |-- __init__.py
|   |   `-- types.py
|   |-- game/
|   |   |-- __init__.py
|   |   |-- engine.py
|   |   |-- rules.py
|   |   `-- state.py
|   |-- ui/
|   |   |-- __init__.py
|   |   |-- cli.py
|   |   |-- pygame_ui.py
|   |   `-- renderer.py
|   `-- main.py
|-- tests/
|   |-- test_agents.py
|   `-- test_engine.py
|-- .gitignore
|-- pyproject.toml
`-- requirements.txt
```

## Install dependencies

```powershell
python -m pip install -r requirements.txt
```

Or (without activation):

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
```

Troubleshooting: if you see `No module named pip`, run:

```powershell
python -m ensurepip --upgrade
python -m pip --version
```

## Run

```powershell
python -m src.main
```

Or you can run with the venv interpreter directly:

```powershell
.\.venv\Scripts\python -m src.main
```

## Test

```powershell
python -m pytest -q
```

Or:

```powershell
.\.venv\Scripts\python -m pytest -q
```
