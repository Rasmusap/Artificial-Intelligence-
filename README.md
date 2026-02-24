# Artificial-Intelligence-

Python starter scaffold for building a turn-based game with:
- game logic (`src/game`)
- UI layer (`src/ui`)
- AI agents (`src/agent`)

The app now runs in a separate window using `pygame`.

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

## Run

```powershell
python -m src.main
```

## Test

```powershell
python -m pytest -q
```
