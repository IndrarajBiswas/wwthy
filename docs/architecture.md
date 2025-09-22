# Architecture overview

This document captures how Watchworthy is put together and how data flows through the system when a visitor submits either the multi-viewer or single-viewer questionnaire.

## High-level components

| Component | Responsibility |
| --- | --- |
| `base.views` | Presents the landing page and handles form submissions. Sanitises POST data, invokes the TMDB client, surfaces errors to templates, and persists submissions. |
| `base.movie` | Wraps the subset of the TMDB API used by the project. Caches genre metadata, raises friendly exceptions when requests fail, and normalises recommendation payloads. |
| `base.models` | Defines the persistence layer for submissions. Uses JSON fields to retain the selected genres as well as the raw recommendation payloads for later analysis. |
| Templates (`base/templates/...`) | Control the UI for the landing page, questionnaires and result views. They now react to error messages and gracefully handle empty recommendations. |
| `wwthy.settings` | Project-level configuration, including environment-driven secrets and the `TMDB_API_KEY` setting consumed by the TMDB client. |

## Request flow

```
+-------------------+       +---------------------+       +---------------------+
| Questionnaire form| 1.    |  base.views.*       | 2.    | base.movie.TmdbClient|
| (multiple/single) | ----> |  validate and normalise ----> | fetch genres & movies |
+-------------------+       |  persist submission  |       +---------------------+
            |               |  return context      |                 |
            |               +----------+-----------+                 |
            |                          v                             |
            |               +---------------------+                  |
            |               |   Django templates   | 3. Render result |
            +-------------> |   display feedback   | <---------------+
                            +---------------------+
```

1. A visitor submits one of the forms. The POST data includes email, demographics, and up to three genre selections.
2. The corresponding view normalises the payload, calculates the wellbeing score (for the single-viewer flow), and asks the TMDB client for recommendations. On success the submission is saved to the database together with the TMDB response.
3. Templates render the resulting movie list along with any validation or connectivity errors that may have occurred.

## Error handling strategy

- Missing or invalid TMDB credentials raise a `django.core.exceptions.ImproperlyConfigured` error, which is surfaced to the user through the result templates.
- Network errors or TMDB outages raise a `MovieServiceError`. The views log the failure and present a readable message while keeping the UI responsive.
- Form data is normalised but deliberately permissive so that the app remains a lightweight prototype. More robust validation (e.g. via Django forms) can be added if needed.

## Extending the project

- **Add more metadata** – extend `MovieRecommendation` in `base.movie` if you want to surface posters, ratings, or release dates. The dataclass ensures any new fields are easy to serialise.
- **Swap the database** – Django's ORM makes it straightforward to switch from SQLite to PostgreSQL. Update `DATABASES` in `wwthy/settings.py` accordingly.
- **Build an API** – convert the view helpers into Django REST Framework viewsets if you want to expose the recommendation engine programmatically.
- **Improve the questionnaire** – the helper functions in `base.views` centralise language and survey score logic so adding new questions is straightforward.

If you plan to contribute changes, take a look at [`CONTRIBUTING.md`](../CONTRIBUTING.md) for workflow details.
