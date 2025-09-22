# Watchworthy

Watchworthy is a Django web application that curates film recommendations from [The Movie Database (TMDB)](https://www.themoviedb.org/) based on how a visitor answers either a group-focused or single-viewer questionnaire. It was originally created as a hackathon prototype; this refresh makes the codebase easier to understand, configure and extend.

![Watchworthy hero illustration](static/Group.svg)

## Key features

- **Two recommendation flows** – one form captures information about a group of viewers while another includes a short well-being survey for individuals.
- **Live TMDB integration** – genres are resolved dynamically and recommendations are fetched in real time via TMDB's public API.
- **Persistent submissions** – every submission is stored in SQLite via Django models to enable later analysis.
- **Fully documented setup** – environment variables, dependencies, and local development workflows are now captured in this repository.

## Project layout

```
├── base/                 # Django app with models, views, templates and tests
├── static/               # Shared CSS and illustration assets
├── templates/            # Root template directory (extends Django defaults)
├── wwthy/                # Project configuration (settings, URLs, ASGI/WSGI)
├── requirements.txt      # Minimal dependencies needed to run the project
├── .env.example          # Sample environment configuration
└── README.md             # This document
```

## Getting started

### 1. Prerequisites

- Python 3.10 or newer
- A TMDB API key ([request one here](https://developer.themoviedb.org/docs/getting-started))
- `pip`, `virtualenv`, or your preferred environment manager

### 2. Configure your environment

```bash
cp .env.example .env
# Then edit .env and add your unique TMDB and Django secrets
```

The application reads these values at runtime:

| Variable | Description |
| --- | --- |
| `DJANGO_SECRET_KEY` | Secret used by Django for cryptographic signing. Use a long random value in production. |
| `DJANGO_DEBUG` | Set to `1` for development or `0` to disable debug mode. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list of hostnames allowed to serve the app. |
| `TMDB_API_KEY` | API key from TMDB used to fetch genres and movie recommendations. |

### 3. Install dependencies and set up the database

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

### 4. Run the application locally

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000 to explore the landing page and submit either form.

### 5. Running the test suite

Unit tests are written with Django's built-in test runner. They include coverage for the TMDB integration layer and reusable view helpers.

```bash
python manage.py test
```

## Development notes

- **TMDB integration** – the `base.movie` module wraps the limited subset of the TMDB API that the project uses. It caches genre lookups, normalises responses, and raises a friendly exception when the service is unreachable.
- **Form handling** – the `base.views` module now validates and normalises POST data, stores JSON in the database, and surfaces error messages in the UI if recommendations cannot be retrieved.
- **Data storage** – submissions are persisted through Django models defined in `base.models`. JSON fields keep both the selected genres and the returned recommendation payloads structured.

For a deeper dive into how requests flow through the application, see [`docs/architecture.md`](docs/architecture.md).

## Contributing

Contributions are welcome! Please review [`CONTRIBUTING.md`](CONTRIBUTING.md) for details about code style, testing, and pull request expectations.

## License

This project is released under the [MIT License](LICENSE). Feel free to fork, adapt, and share it.
