"""Test suite for the base application."""

from __future__ import annotations

from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings

from . import movie
from .views import _calculate_survey_score, _clean_genre_selection, SURVEY_FIELD_NAMES


def _mock_response(payload: dict):
    response = mock.Mock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


class TmdbClientTests(SimpleTestCase):
    def setUp(self) -> None:
        movie.get_tmdb_client.cache_clear()

    def tearDown(self) -> None:
        movie.get_tmdb_client.cache_clear()

    @override_settings(TMDB_API_KEY="example-key")
    def test_fetch_recommendations_returns_movies(self):
        genre_payload = {"genres": [{"id": 1, "name": "Action"}]}
        discover_payload = {
            "results": [
                {
                    "title": "Edge of Tomorrow",
                    "genre_ids": [1],
                    "overview": "A reluctant soldier relives the same day over and over.",
                    "poster_path": "/poster.jpg",
                }
            ]
        }

        with mock.patch("base.movie.requests.get") as mock_get:
            mock_get.side_effect = [
                _mock_response(genre_payload),
                _mock_response(discover_payload),
            ]
            recommendations = movie.fetch_recommendations(language="en", genre_names=["Action"])

        self.assertEqual(len(recommendations), 1)
        first = recommendations[0]
        self.assertEqual(first.title, "Edge of Tomorrow")
        self.assertEqual(first.genres, ["Action"])
        self.assertEqual(first.overview, "A reluctant soldier relives the same day over and over.")

    def test_fetch_recommendations_without_api_key_raises(self):
        movie.get_tmdb_client.cache_clear()
        with self.assertRaises(ImproperlyConfigured):
            movie.fetch_recommendations(language="en", genre_names=["Action"])

    @override_settings(TMDB_API_KEY="another-key")
    def test_tmdb_errors_raise_domain_specific_exception(self):
        with mock.patch("base.movie.requests.get", side_effect=movie.requests.RequestException("Boom")):
            with self.assertRaises(movie.MovieServiceError):
                movie.fetch_recommendations(language="en", genre_names=["Action"])


class ViewHelperTests(SimpleTestCase):
    def test_clean_genre_selection_filters_none_values(self):
        cleaned = _clean_genre_selection(["Action", "none", "Comedy", ""])
        self.assertEqual(cleaned, ["Action", "Comedy"])

    def test_calculate_survey_score_handles_missing_values(self):
        data = {name: "1" for name in SURVEY_FIELD_NAMES[:3]}
        score = _calculate_survey_score(data)
        self.assertEqual(score, 3)
