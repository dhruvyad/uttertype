# UtterType Project Guidelines

## Running the Application
- Module run: `python -m uttertype.main` (most reliable method)
- Wrapper script: `python main.py` (simplest option)
- After installation: `uttertype` (requires activated venv)
- With tmux: `./start_uttertype.sh` (starts in background)
- Install dependencies: `uv sync` or `pip install -e .`

## Code Style Guidelines
- **Imports**: Standard library first, third-party second, local imports last
- **Naming**: 
  - snake_case for functions/variables
  - PascalCase for classes
  - UPPERCASE for constants
- **Type Hints**: Required for all function parameters and return values
- **Formatting**: 
  - 4-space indentation
  - Max line length ~88 characters
  - Blank lines between logical sections
- **Error Handling**: Use try/except with specific exceptions, include original exception in messages
- **Docstrings**: Required for classes and non-trivial functions
- **Architecture**: Maintain clear separation of concerns between modules

## Development Notes
- Environment variables configured in `.env` (see README for required settings)
- Async programming with asyncio
- Use context managers (with statements) for resource management
- Follow factory method pattern for object creation when appropriate