from collections import OrderedDict

from coreapi.compat import urlparse
from inflection import camelize


TYPE_OBJECT = "object"
TYPE_STRING = "string"
TYPE_NUMBER = "number"
TYPE_INTEGER = "integer"
TYPE_BOOLEAN = "boolean"
TYPE_ARRAY = "array"
TYPE_FILE = "file"

# officially supported by Swagger 2.0 spec
FORMAT_DATE = "date"
FORMAT_DATETIME = "date-time"
FORMAT_PASSWORD = "password"
FORMAT_BINARY = "binary"
FORMAT_BASE64 = "bytes"
FORMAT_FLOAT = "float"
FORMAT_DOUBLE = "double"
FORMAT_INT32 = "int32"
FORMAT_INT64 = "int64"

# defined in JSON-schema
FORMAT_EMAIL = "email"
FORMAT_IPV4 = "ipv4"
FORMAT_IPV6 = "ipv6"
FORMAT_URI = "uri"

# pulled out of my ass
FORMAT_UUID = "uuid"
FORMAT_SLUG = "slug"


def make_swagger_name(attribute_name):
    """
    Convert a python variable name into a Swagger spec attribute name.

    In particular,
     * if name starts with x_, return "x-{camelCase}"
     * if name is 'ref', return "$ref"
     * else return the name converted to camelCase, with trailing underscores stripped

    :param str attribute_name: python attribute name
    :return: swagger name
    """
    if attribute_name == 'ref':
        return "$ref"
    if attribute_name.startswith("x_"):
        return "x-" + camelize(attribute_name, uppercase_first_letter=False)
    return camelize(attribute_name.strip('_'), uppercase_first_letter=False)


class SwaggerDict(OrderedDict):
    def __init__(self, **attrs):
        super().__init__()
        for attr, val in attrs:
            setattr(self, attr, val)

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super().__setattr__(key, value)
            return
        if value is not None:
            self[make_swagger_name(key)] = value

    def __getattr__(self, item):
        if item.startswith('_'):
            raise AttributeError
        try:
            return self[make_swagger_name(item)]
        except KeyError as e:
            raise AttributeError("no attribute " + item) from e

    def __delattr__(self, item):
        if item.startswith('_'):
            super().__delattr__(item)
            return
        del self[make_swagger_name(item)]


class Contact(SwaggerDict):
    """Swagger Contact object
    At least one of the following fields is required:

    :param str name: contact name
    :param str url: contact url
    :param str email: contact e-mail
    """

    def __init__(self, *, name=None, url=None, email=None, **extra):
        if name is None and url is None and email is None:
            raise ValueError("one of name, url or email is requires for Swagger Contact object")
        self.name = name
        self.url = url
        self.email = email
        super().__init__(**extra)


class License(SwaggerDict):
    """Swagger License object

    :param str name: Requird. License name
    :param str url: link to detailed license information
    """

    def __init__(self, *, name, url=None, **extra):
        if name is None:
            raise ValueError("name is required for Swagger License object")
        self.name = name
        self.url = url
        super().__init__(**extra)


class Info(SwaggerDict):
    """Swagger Info object

    :param str title: Required. API title.
    :param str default_version: Required. API version string (not to be confused with Swagger spec version)
    :param str description: API description; markdown supported
    :param str terms_of_service: API terms of service; should be a URL
    :param Contact contact: contact object
    :param License license: license object
    """

    def __init__(self, *, title, default_version, description=None, terms_of_service=None, contact=None, license=None,
                 **extra):
        if title is None or default_version is None:
            raise ValueError("title and version are required for Swagger info object")
        if contact is not None and not isinstance(contact, Contact):
            raise ValueError("contact must be a Contact object")
        if license is not None and not isinstance(license, License):
            raise ValueError("license must be a License object")
        self.title = title
        self._default_version = default_version
        self.description = description
        self.terms_of_service = terms_of_service
        self.contact = contact
        self.license = license
        super().__init__(**extra)


class Swagger(SwaggerDict):
    def __init__(self, *, info=None, _url=None, _version=None, paths=None, **extra):
        self.swagger = '2.0'
        self.info = info
        self.info.version = _version or info._default_version
        self.paths = paths

        url = urlparse.urlparse(_url)
        if url.netloc:
            self.host = url.netloc
        if url.scheme:
            self.schemes = [url.scheme]

        self.base_path = '/'
        super().__init__(**extra)


class Paths(SwaggerDict):
    def __init__(self, paths, **extra):
        for path, path_obj in paths.items():
            assert path.startswith("/")
            self[path] = path_obj
        super().__init__(**extra)


class PathItem(SwaggerDict):
    def __init__(self, *, get=None, put=None, post=None, delete=None, options=None,
                 head=None, patch=None, parameters=None, **extra):
        self.get = get
        self.put = put
        self.post = post
        self.delete = delete
        self.options = options
        self.head = head
        self.patch = patch
        self.parameters = parameters
        super().__init__(**extra)


class Operation(SwaggerDict):
    def __init__(self, *, operation_id, responses, consumes=None, produces=None, description=None, tags=None, **extra):
        self.operation_id = operation_id
        self.responses = responses
        self.consumes = consumes
        self.produces = produces
        self.description = description
        self.tags = tags
        super().__init__(**extra)


class Items(SwaggerDict):
    def __init__(self, *, type=None, format=None, enum=None, pattern=None, items=None, **extra):
        self.type = type
        self.format = format
        self.enum = enum
        self.pattern = pattern
        self.items = items
        super().__init__(**extra)


class Parameter(SwaggerDict):
    def __init__(self, *, name, in_, description, required, schema=None,
                 type=None, format=None, enum=None, pattern=None, items=None, **extra):
        if not schema and not type:
            raise ValueError("either schema or type are required for Parameter object!")
        self.name = name
        self.in_ = in_
        self.description = description
        self.required = required
        self.schema = schema
        self.type = type
        self.format = format
        self.enum = enum
        self.pattern = pattern
        self.items = items
        super().__init__(**extra)


class Schema(SwaggerDict):
    def __init__(self, *, description=None, required=None, type=None, properties=None, additional_properties=None,
                 format=None, enum=None, pattern=None, items=None, **extra):
        self.description = description
        self.required = required
        self.type = type
        self.properties = properties
        self.additional_properties = additional_properties
        self.format = format
        self.enum = enum
        self.pattern = pattern
        self.items = items
        super().__init__(**extra)


class Ref(SwaggerDict):
    def __init__(self, ref):
        self.ref = ref
        super().__init__()


class Responses(SwaggerDict):
    def __init__(self, responses, default=None, **extra):
        for status, response in responses.items():
            self[str(status)] = response
        self.default = default
        super().__init__(**extra)


class Response(SwaggerDict):
    def __init__(self, description, schema=None, examples=None, **extra):
        self.description = description
        self.schema = schema
        self.examples = examples
        super().__init__(**extra)
