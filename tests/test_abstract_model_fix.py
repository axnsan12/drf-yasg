"""Test for abstract model handling fix in drf-yasg"""
import pytest
from django.db import models
from rest_framework import serializers, viewsets
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator


# Test models
class AbstractActivity(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    class Meta:
        abstract = True
        app_label = 'tests'


class VideoActivity(AbstractActivity):
    video_url = models.URLField()
    
    class Meta:
        app_label = 'tests'


class TextActivity(AbstractActivity):
    content = models.TextField()
    
    class Meta:
        app_label = 'tests'


# Test serializers
class AbstractActivitySerializer(serializers.ModelSerializer):
    """This serializer should not cause errors even though it references an abstract model"""
    class Meta:
        model = AbstractActivity
        fields = '__all__'


class VideoActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoActivity
        fields = '__all__'


class TextActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = TextActivity
        fields = '__all__'


# Test viewsets
class BaseActivityViewSet(viewsets.ModelViewSet):
    """Base viewset with abstract model reference"""
    activity_model = AbstractActivity
    
    def get_queryset(self):
        if hasattr(self, 'queryset') and self.queryset is not None:
            return self.queryset.all()
        return self.activity_model.objects.all()


class VideoActivityViewSet(BaseActivityViewSet):
    activity_model = VideoActivity
    serializer_class = VideoActivitySerializer


class TextActivityViewSet(BaseActivityViewSet):
    queryset = TextActivity.objects.all()
    serializer_class = TextActivitySerializer


# Integration test
def test_abstract_model_in_viewset_does_not_raise_error(mock_schema_request):
    """Test that viewsets with abstract models in base classes don't cause errors during schema generation"""
    generator = OpenAPISchemaGenerator(
        info=openapi.Info(title="Test abstract models", default_version="v1"),
        version="v1",
        patterns=[],
    )
    
    # Mock the get_endpoints to include our viewset
    def get_test_endpoints(request):
        factory = APIRequestFactory()
        view = VideoActivityViewSet()
        view.request = request
        view.format_kwarg = None
        view.action = 'list'
        view.action_map = {'get': 'list'}
        return {
            '/videos/': (VideoActivityViewSet, [('GET', view)]),
        }
    
    # Monkey patch get_endpoints
    original_get_endpoints = generator.get_endpoints
    generator.get_endpoints = get_test_endpoints
    
    try:
        # This should not raise ValueError about abstract models
        schema = generator.get_schema(mock_schema_request, public=True)
        
        # Verify the schema was generated
        assert schema is not None
        assert isinstance(schema, openapi.Swagger)
        assert '/videos/' in schema.paths
    finally:
        # Restore original method
        generator.get_endpoints = original_get_endpoints


# Unit tests for the fix
def test_abstract_model_serializer_field_to_swagger():
    """Test that field inspector handles abstract model serializers"""
    from drf_yasg.inspectors.field import InlineSerializerInspector
    from drf_yasg.app_settings import swagger_settings
    
    # Create a fake view and components
    factory = APIRequestFactory()
    request = factory.get('/')
    request = APIView().initialize_request(request)
    components = openapi.ReferenceResolver('definitions', 'parameters', 'responses', force_init=True)
    
    # Create inspector with default field inspectors
    inspector = InlineSerializerInspector(
        view=None,
        path='/test/',
        method='GET',
        components=components,
        request=request,
        field_inspectors=swagger_settings.DEFAULT_FIELD_INSPECTORS,
    )
    
    # Test with abstract model serializer
    serializer = AbstractActivitySerializer()
    schema = inspector.field_to_swagger_object(
        serializer,
        openapi.Schema,
        use_references=False
    )
    
    # Should return a schema with empty properties
    assert schema is not None
    assert schema.type == openapi.TYPE_OBJECT
    assert schema.properties == {}
    assert 'required' not in schema  # required should not be present
    
    # Test with concrete model serializer
    serializer = VideoActivitySerializer()
    schema = inspector.field_to_swagger_object(
        serializer,
        openapi.Schema,
        use_references=False
    )
    
    # Should return a schema with all properties
    assert schema is not None
    assert schema.type == openapi.TYPE_OBJECT
    assert 'title' in schema.properties
    assert 'description' in schema.properties
    assert 'video_url' in schema.properties


def test_abstract_model_request_parameters():
    """Test that get_request_parameters handles abstract model serializers"""
    from drf_yasg.inspectors.field import InlineSerializerInspector
    from drf_yasg.app_settings import swagger_settings
    
    # Create a fake view and components
    factory = APIRequestFactory()
    request = factory.get('/')
    request = APIView().initialize_request(request)
    components = openapi.ReferenceResolver('definitions', 'parameters', 'responses', force_init=True)
    
    # Create inspector with default field inspectors
    inspector = InlineSerializerInspector(
        view=None,
        path='/test/',
        method='POST',
        components=components,
        request=request,
        field_inspectors=swagger_settings.DEFAULT_FIELD_INSPECTORS,
    )
    
    # Test with abstract model serializer
    serializer = AbstractActivitySerializer()
    parameters = inspector.get_request_parameters(serializer, openapi.IN_FORM)
    
    # Should return empty parameters for abstract model
    assert parameters == []
    
    # Test with concrete model serializer
    serializer = VideoActivitySerializer()
    parameters = inspector.get_request_parameters(serializer, openapi.IN_FORM)
    
    # Should return parameters for all fields
    assert len(parameters) == 3
    param_names = [p.name for p in parameters]
    assert 'title' in param_names
    assert 'description' in param_names
    assert 'video_url' in param_names