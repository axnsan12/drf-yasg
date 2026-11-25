import importlib
import sys
import types
from contextlib import contextmanager

import pytest
from django.urls import path
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.fields import Field
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework_recursive.fields import (
    RecursiveField as RestFrameworkRecursiveField,
)

from drf_yasg import inspectors as inspectors_module
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.inspectors import NotHandled
from drf_yasg.inspectors import field as field_module
from drf_yasg.utils import swagger_auto_schema


def _make_drf_recursive_modules():
    """Build standalone modules mimicking the `drf-recursive` package."""

    class DrfRecursiveField(Field):
        def __init__(self, to=None, **kwargs):
            self.to = to
            self.init_kwargs = kwargs
            self._proxied = None
            super_kwargs = {
                k: v for k, v in kwargs.items() if k in ("read_only", "allow_null")
            }
            super().__init__(**super_kwargs)

        def bind(self, field_name, parent):
            self.bind_args = (field_name, parent)

        @property
        def proxied(self):
            if not self._proxied and self.bind_args:
                field_name, parent = self.bind_args
                if hasattr(parent, "child") and parent.child is self:
                    parent_class = parent.parent.__class__
                else:
                    parent_class = parent.__class__
                assert issubclass(parent_class, BaseSerializer)
                proxied = parent_class(**self.init_kwargs)
                proxied.bind(field_name, parent)
                self._proxied = proxied
            return self._proxied

    pkg = types.ModuleType("django_rest_framework_recursive")
    fields_mod = types.ModuleType("django_rest_framework_recursive.fields")
    fields_mod.RecursiveField = DrfRecursiveField
    pkg.fields = fields_mod
    return {
        "django_rest_framework_recursive": pkg,
        "django_rest_framework_recursive.fields": fields_mod,
    }, DrfRecursiveField


@contextmanager
def _reloaded_field_inspectors(sys_modules_overrides):
    with pytest.MonkeyPatch.context() as mp:
        for name, mod in sys_modules_overrides.items():
            mp.setitem(sys.modules, name, mod)
        try:
            importlib.reload(field_module)
            importlib.reload(inspectors_module)
            yield field_module.RecursiveFieldInspector
        finally:
            mp.undo()
            importlib.reload(field_module)
            importlib.reload(inspectors_module)


def _generate_schema_for_serializer(serializer_cls, url_path="recursive/"):
    @swagger_auto_schema(
        method="get",
        responses={200: openapi.Response("OK", serializer_cls)},
    )
    @api_view(["GET"])
    def view(request):
        return Response({})

    generator = OpenAPISchemaGenerator(
        info=openapi.Info(title="Test recursive field", default_version="v1"),
        patterns=[path(url_path, view)],
    )
    return generator.get_schema(public=True)


def test_drf_recursive_only_installed(swagger_settings):
    swagger_settings["SECURITY_DEFINITIONS"] = None
    drf_recursive_modules, DrfRecursiveField = _make_drf_recursive_modules()
    overrides = {
        **drf_recursive_modules,
        "rest_framework_recursive": None,
        "rest_framework_recursive.fields": None,
    }

    with _reloaded_field_inspectors(overrides):

        class DrfRecursiveNodeSerializer(serializers.Serializer):
            name = serializers.CharField()
            parent = DrfRecursiveField(read_only=True)
            children = serializers.ListField(child=DrfRecursiveField())
            many_children = DrfRecursiveField(many=True)

        swagger = _generate_schema_for_serializer(DrfRecursiveNodeSerializer)
        props = swagger["definitions"]["DrfRecursiveNode"]["properties"]

        assert props["parent"] == {"$ref": "#/definitions/DrfRecursiveNode"}
        assert props["children"] == {
            "type": openapi.TYPE_ARRAY,
            "items": {"$ref": "#/definitions/DrfRecursiveNode"},
        }
        assert props["many_children"] == {
            "type": openapi.TYPE_ARRAY,
            "items": {"$ref": "#/definitions/DrfRecursiveNode"},
        }


def test_both_recursive_packages_installed():
    drf_recursive_modules, DrfRecursiveField = _make_drf_recursive_modules()

    with _reloaded_field_inspectors(drf_recursive_modules):

        class MixedRecursiveSerializer(serializers.Serializer):
            legacy_parent = RestFrameworkRecursiveField(read_only=True)
            drf_recursive_parent = DrfRecursiveField(read_only=True)
            drf_recursive_many = DrfRecursiveField(many=True)

        swagger = _generate_schema_for_serializer(MixedRecursiveSerializer)
        props = swagger["definitions"]["MixedRecursive"]["properties"]

        assert props["legacy_parent"] == {"$ref": "#/definitions/MixedRecursive"}
        assert props["drf_recursive_parent"] == {"$ref": "#/definitions/MixedRecursive"}
        assert props["drf_recursive_many"] == {
            "type": openapi.TYPE_ARRAY,
            "items": {"$ref": "#/definitions/MixedRecursive"},
        }


def test_no_recursive_package_installed():
    overrides = {
        "rest_framework_recursive": None,
        "rest_framework_recursive.fields": None,
        "django_rest_framework_recursive": None,
        "django_rest_framework_recursive.fields": None,
    }

    with _reloaded_field_inspectors(overrides) as inspector_cls:
        inspector = inspector_cls(
            view=None,
            path="/",
            method="GET",
            components=openapi.ReferenceResolver("definitions", force_init=True),
            request=None,
            field_inspectors=[],
        )
        result = inspector.field_to_swagger_object(
            serializers.CharField(),
            openapi.Schema,
            use_references=True,
        )
        assert result is NotHandled
