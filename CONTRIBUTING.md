# Contributing to Watchworthy

Thanks for your interest in improving Watchworthy! This document outlines how to get set up, the coding conventions we follow, and the steps to submit a helpful pull request.

## Development workflow

1. **Fork and clone** the repository.
2. **Create a virtual environment** and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Configure environment variables** by copying `.env.example` to `.env` and adding your secrets.
4. **Run migrations** before starting work:
   ```bash
   python manage.py migrate
   ```
5. **Start the development server** with `python manage.py runserver` and visit http://127.0.0.1:8000.

## Coding guidelines

- **Python style** – follow [PEP 8](https://peps.python.org/pep-0008/) where practical. Use descriptive names and add docstrings to modules or complex functions.
- **Django conventions** – lean on the framework: prefer class-based models with JSON fields for structured data, use the ORM for database access, and take advantage of settings for environment-specific configuration.
- **Error handling** – surface actionable error messages to end users while logging the root cause with `logging`. Avoid bare `except` blocks.
- **Security** – never commit real API keys or credentials. Secrets belong in `.env`, environment variables, or your deployment platform.
- **Tests** – add or update tests in `base/tests.py` whenever you modify behaviour. Mock network calls so the suite remains deterministic.

## Submitting a pull request

1. Ensure `python manage.py test` passes and that you've run any other relevant checks.
2. Keep commits focused and include clear messages summarising the change.
3. Update documentation (README, architecture notes, etc.) if your change affects the developer experience or application behaviour.
4. Open a pull request describing the motivation and testing performed. Screenshots or GIFs are appreciated for UI updates.

By following these guidelines you help keep Watchworthy friendly for new contributors and maintainers alike. Thank you!
