"""URL patterns for the base application."""

from django.urls import path

from . import views

app_name = "base"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("multiple/", views.multiple, name="multiple"),
    path("single/", views.single, name="single"),
    path("submitform/", views.form_submit, name="submit_form"),
    path("submitformsingle/", views.single_form, name="submit_form_single"),
]
