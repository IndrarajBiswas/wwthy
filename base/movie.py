"""Utilities for interacting with The Movie Database (TMDB) API."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import Dict, Iterable, List

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

TMDB_API_BASE_URL = "https://api.themoviedb.org/3"
DEFAULT_LANGUAGE = "en-US"
TIMEOUT_SECONDS = 10


class MovieServiceError(RuntimeError):
    """Raised when TMDB cannot be reached or returns an unexpected response."""


@dataclass
class MovieRecommendation:
    """Simple representation of a recommended movie."""

    title: str
    genres: List[str]
    overview: str | None
    poster_path: str | None


class TmdbClient:
    """Small wrapper around the TMDB API endpoints the app relies on."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ImproperlyConfigured(
                "TMDB_API_KEY is not configured. Set it in your environment to enable recommendations."
            )
        self.api_key = api_key

    @cached_property
    def _genre_maps(self) -> tuple[Dict[str, int], Dict[int, str]]:
        """Return mappings of genre names to ids and vice versa."""

        payload = self._get("genre/movie/list", language=DEFAULT_LANGUAGE)
        name_to_id: Dict[str, int] = {}
        id_to_name: Dict[int, str] = {}
        for genre in payload.get("genres", []):
            genre_id = genre.get("id")
            genre_name = genre.get("name")
            if genre_id is None or genre_name is None:
                continue
            name_to_id[str(genre_name)] = int(genre_id)
            id_to_name[int(genre_id)] = str(genre_name)
        return name_to_id, id_to_name

    def discover_movies(self, *, language: str, genre_names: Iterable[str]) -> List[MovieRecommendation]:
        """Return a list of movies for the supplied language and genres."""

        params = {
            "language": language or DEFAULT_LANGUAGE,
            "include_adult": "false",
            "sort_by": "popularity.desc",
            "page": 1,
        }

        genre_ids = self._resolve_genre_ids(genre_names)
        if genre_ids:
            params["with_genres"] = ",".join(str(genre_id) for genre_id in genre_ids)

        payload = self._get("discover/movie", **params)
        recommendations: List[MovieRecommendation] = []
        for result in payload.get("results", []):
            recommendations.append(
                MovieRecommendation(
                    title=result.get("title", "Untitled"),
                    genres=self._resolve_genre_names(result.get("genre_ids", [])),
                    overview=result.get("overview"),
                    poster_path=result.get("poster_path"),
                )
            )
        return recommendations

    def _resolve_genre_ids(self, genre_names: Iterable[str]) -> List[int]:
        name_to_id, _ = self._genre_maps
        seen: Dict[str, None] = {}
        genre_ids: List[int] = []
        for genre_name in genre_names:
            if not genre_name or genre_name == "none" or genre_name in seen:
                continue
            seen[genre_name] = None
            genre_id = name_to_id.get(genre_name)
            if genre_id is not None:
                genre_ids.append(genre_id)
        return genre_ids

    def _resolve_genre_names(self, genre_ids: Iterable[int]) -> List[str]:
        _, id_to_name = self._genre_maps
        return [id_to_name.get(int(genre_id), str(genre_id)) for genre_id in genre_ids]

    def _get(self, path: str, **params) -> dict:
        params.setdefault("api_key", self.api_key)
        url = f"{TMDB_API_BASE_URL}/{path}"
        try:
            response = requests.get(url, params=params, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("TMDB request failed: %s", exc)
            raise MovieServiceError("Unable to communicate with The Movie Database.") from exc
        return response.json()


@lru_cache(maxsize=1)
def get_tmdb_client() -> TmdbClient:
    """Return a cached TMDB client instance."""

    return TmdbClient(getattr(settings, "TMDB_API_KEY", ""))


def fetch_recommendations(*, language: str, genre_names: Iterable[str]) -> List[MovieRecommendation]:
    """Convenience wrapper around :meth:`TmdbClient.discover_movies`."""

    client = get_tmdb_client()
    return client.discover_movies(language=language, genre_names=genre_names)
