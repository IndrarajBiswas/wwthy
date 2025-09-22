"""Django views for rendering pages and handling form submissions."""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Iterable, List

from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render

from base.models import forminput, singleforminput
from .movie import MovieServiceError, fetch_recommendations

logger = logging.getLogger(__name__)

DEFAULT_LANGUAGE = "en"
SURVEY_FIELD_NAMES: List[str] = ["radio"] + [f"radio{i}" for i in range(1, 13)]


def landing(request):
    return render(request, "base/landing.html")


def multiple(request):
    return render(request, "base/multiple.html")


def single(request):
    return render(request, "base/single.html")


def form_submit(request):
    recommendations: List[dict] = []
    error_message: str | None = None

    if request.method == "POST":
        email = (request.POST.get("mail") or "").strip()
        audiences = _safe_int(request.POST.get("audiences"), default=1)
        ageranges = (request.POST.get("age-ranges") or "-1").strip()
        genre_preferences = _clean_genre_selection(request.POST.getlist("gp"))
        language = _normalise_language(request.POST.get("Languages"))

        try:
            raw_recommendations = fetch_recommendations(
                language=language, genre_names=genre_preferences
            )
            recommendations = [asdict(movie) for movie in raw_recommendations]
        except (MovieServiceError, ImproperlyConfigured) as exc:
            error_message = str(exc)
            logger.warning("Unable to fetch recommendations: %s", exc)
        else:
            forminput.objects.create(
                email=email,
                audiences=audiences,
                ageranges=ageranges,
                gp=genre_preferences,
                recommendations=recommendations,
            )

    context = {
        "recommendations": recommendations,
        "error_message": error_message,
    }
    return render(request, "base/display.html", context)


def single_form(request):
    recommendations: List[dict] = []
    error_message: str | None = None
    score: int | None = None

    if request.method == "POST":
        email = (request.POST.get("mail") or "").strip()
        age = _safe_int(request.POST.get("age"), default=0)
        genre_preferences = _clean_genre_selection(request.POST.getlist("gp"))
        language = _normalise_language(request.POST.get("Languages"))
        score = _calculate_survey_score(request.POST)

        try:
            raw_recommendations = fetch_recommendations(
                language=language, genre_names=genre_preferences
            )
            recommendations = [asdict(movie) for movie in raw_recommendations]
        except (MovieServiceError, ImproperlyConfigured) as exc:
            error_message = str(exc)
            logger.warning("Unable to fetch recommendations: %s", exc)
        else:
            singleforminput.objects.create(
                email=email,
                age=age,
                sum=score or 0,
                gp=genre_preferences,
                recommendations=recommendations,
            )

    context = {
        "recommendations": recommendations,
        "sum": score,
        "error_message": error_message,
    }
    return render(request, "base/displaysingle.html", context)


def _clean_genre_selection(raw_selection: Iterable[str]) -> List[str]:
    return [value for value in raw_selection if value and value.lower() != "none"]


def _safe_int(value: str | None, *, default: int = 0) -> int:
    try:
        return int(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def _normalise_language(language: str | None) -> str:
    language = (language or "").strip()
    if not language or language.lower() == "none":
        return DEFAULT_LANGUAGE
    return language


def _calculate_survey_score(data) -> int:
    total = 0
    for field_name in SURVEY_FIELD_NAMES:
        total += _safe_int(data.get(field_name), default=0)
    return total
