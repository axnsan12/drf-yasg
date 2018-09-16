import logging
import re
from collections import OrderedDict

from coreapi.compat import urlparse
from django.urls import get_script_prefix
from django.utils.functional import cached_property
from inflection import camelize

from .utils import filter_none

logger = logging.getLogger(__name__)

OAS_VERSION = '3.0.1'  #: the version of the OpenAPI Specification that is implemented by this library

TYPE_OBJECT = "object"  #:
TYPE_STRING = "string"  #:
TYPE_NUMBER = "number"  #:
TYPE_INTEGER = "integer"  #:
TYPE_BOOLEAN = "boolean"  #:
TYPE_ARRAY = "array"  #:
TYPE_FILE = "file"  #:

# officially supported by Swagger 2.0 spec
FORMAT_DATE = "date"  #:
FORMAT_DATETIME = "date-time"  #:
FORMAT_PASSWORD = "password"  #:
FORMAT_BINARY = "binary"  #:
FORMAT_BASE64 = "byte"  #:
FORMAT_FLOAT = "float"  #:
FORMAT_DOUBLE = "double"  #:
FORMAT_INT32 = "int32"  #:
FORMAT_INT64 = "int64"  #:

# defined in JSON-schema
FORMAT_EMAIL = "email"  #:
FORMAT_IPV4 = "ipv4"  #:
FORMAT_IPV6 = "ipv6"  #:
FORMAT_URI = "uri"  #:

# pulled out of my ass
FORMAT_UUID = "uuid"  #:
FORMAT_SLUG = "slug"  #:
FORMAT_DECIMAL = "decimal"

IN_PATH = 'path'  #:
IN_QUERY = 'query'  #:
IN_HEADER = 'header'  #:
IN_COOKIE = 'cookie'  #:

STYLE_MATRIX = 'matrix'  #:
STYLE_LABEL = 'label'  #:
STYLE_FORM = 'form'  #:
STYLE_SIMPLE = 'simple'  #:
STYLE_SPACE_DELIMITED = 'spaceDelimited'  #:
STYLE_PIPE_DELIMITED = 'pipeDelimited'  #:
STYLE_DEEP_OBJECT = 'deepObject'  #:

SECURITY_API_KEY = 'apiKey'  #:
SECURITY_HTTP = 'http'  #:
SECURITY_OAUTH2 = 'oauth2'  #:
SECURITY_OPENID_CONNECT = 'openIdConnect'  #:


def make_swagger_name(attribute_name):
    """
    Convert a python variable name into a Swagger spec attribute name.

    In particular,
     * if name starts with ``x_``, return ``x-{camelCase}``
     * if name is ``ref``, return ``$ref``
     * else return the name converted to camelCase, with trailing underscores stripped

    :param str attribute_name: python attribute name
    :return: swagger name
    """
    if attribute_name == 'ref':
        return "$ref"
    if attribute_name.startswith("x_"):
        return "x-" + camelize(attribute_name[2:], uppercase_first_letter=False)
    return camelize(attribute_name.rstrip('_'), uppercase_first_letter=False)


def _bare_SwaggerDict(cls):
    assert issubclass(cls, SwaggerDict)
    result = cls.__new__(cls)
    OrderedDict.__init__(result)  # no __init__ called for SwaggerDict subclasses!
    return result


class SwaggerDict(OrderedDict):
    """A particular type of OrderedDict, which maps all attribute accesses to dict lookups using
     :func:`.make_swagger_name`. Attribute names starting with ``_`` are set on the object as-is and are not included
     in the specification output.

     Used as a base class for all Swagger helper models.
    """

    def __init__(self, **attrs):
        super(SwaggerDict, self).__init__()
        if type(self) == SwaggerDict:
            self._insert_attrs(attrs)

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super(SwaggerDict, self).__setattr__(key, value)
            return
        if value is not None:
            self[make_swagger_name(key)] = value

    def __getattr__(self, item):
        if item.startswith('_'):
            raise AttributeError
        try:
            return self[make_swagger_name(item)]
        except KeyError:
            # raise_from is EXTREMELY slow, replaced with plain raise
            raise AttributeError("object of class " + type(self).__name__ + " has no attribute " + item)

    def __delattr__(self, item):
        if item.startswith('_'):
            super(SwaggerDict, self).__delattr__(item)
            return
        del self[make_swagger_name(item)]

    def _insert_attrs(self, extras):
        """
        From an ordering perspective, it is desired that extra attributes such as vendor extensions stay at the
        bottom of the object. However, python2.7's OrderdDict craps out if you try to insert into it before calling
        init. This means that subclasses must call super().__init__ as the first statement of their own __init__,
        which would result in the extra attributes being added first. For this reason, we defer the insertion of the
        attributes and require that subclasses call ._insert_extras__ at the end of their __init__ method.

        :param dict[str,any] extras: the extra variables
        """
        # make sure to add extensions after regular attributes
        extra_attrs = []
        extensions = []
        for attr, val in extras.items():
            if attr.startswith('_'):
                setattr(self, attr, val)
            elif attr.startswith('x_') or attr.startswith('x-'):
                extensions.append((attr, val))
            else:
                extra_attrs.append((attr, val))

        for attr, val in sorted(extra_attrs):
            setattr(self, attr, val)
        for attr, val in sorted(extensions):
            setattr(self, attr, val)

    @staticmethod
    def _as_odict(obj, memo):
        """Implementation detail of :meth:`.as_odict`"""
        if id(obj) in memo:
            return memo[id(obj)]

        if isinstance(obj, dict):
            result = OrderedDict()
            memo[id(obj)] = result
            for attr, val in obj.items():
                result[attr] = SwaggerDict._as_odict(val, memo)
            return result
        elif isinstance(obj, (list, tuple)):
            return type(obj)(SwaggerDict._as_odict(elem, memo) for elem in obj)

        return obj

    def as_odict(self):
        """Convert this object into an ``OrderedDict`` instance.

        :rtype: OrderedDict
        """
        return SwaggerDict._as_odict(self, {})

    def __reduce__(self):
        # for pickle supprt; this skips calls to all SwaggerDict __init__ methods and relies
        # on the already set attributes instead
        return _bare_SwaggerDict, (type(self),), vars(self), None, iter(self.items())


class Contact(SwaggerDict):
    def __init__(self, name=None, url=None, email=None, **extra):
        """Swagger Contact object

        At least one of the following fields is required:

        :param str name: contact name
        :param str url: contact url
        :param str email: contact e-mail
        """
        super(Contact, self).__init__()
        if name is None and url is None and email is None:
            raise AssertionError("one of name, url or email is requires for Swagger Contact object")
        self.name = name
        self.url = url
        self.email = email
        self._insert_attrs(extra)


class License(SwaggerDict):
    def __init__(self, name, url=None, **extra):
        """Swagger License object

        :param str name: Required. License name
        :param str url: link to detailed license information
        """
        super(License, self).__init__()
        if name is None:
            raise AssertionError("name is required for Swagger License object")
        self.name = name
        self.url = url
        self._insert_attrs(extra)


class Info(SwaggerDict):
    def __init__(self, title, version, description=None, terms_of_service=None, contact=None, license=None,
                 **extra):
        """Swagger Info object.

        :param str title: Required. API title.
        :param str version: Required. API version string (not to be confused with Swagger spec version)
        :param str description: API description; markdown supported
        :param str terms_of_service: API terms of service; should be a URL
        :param Contact contact: contact object
        :param License license: license object
        """
        super(Info, self).__init__()
        if title is None or version is None:
            raise AssertionError("title and version are required for Swagger info object")
        self.title = title
        self.version = version
        self.description = description
        self.terms_of_service = terms_of_service
        self.contact = contact
        self.license = license
        self._insert_attrs(extra)


class ServerVariable(SwaggerDict):
    def __init__(self, default, description=None, enum=None, **extra):
        """Server Variable object.

        :param str default: variable default value; required
        :param str description: variable description
        :param list[str] enum: a set of substitution options
        """
        super(ServerVariable, self).__init__()
        self.default = default
        self.description = description
        self.enum = filter_none(enum)
        self._insert_attrs(extra)

        if enum and self.default not in enum:
            raise AssertionError("default must respect enum!")


class Server(SwaggerDict):
    def __init__(self, url, description=None, variables=None, **extra):
        """Server object.

        :param str url: the target host url; can be relative to the OpenAPI document location;
            supports variable substitions in both hostname and path
        :param str description: server description
        :param dict[str,ServerVariable] variables: url variable substitutions
        """
        super(Server, self).__init__()
        self.url = url
        self.description = description
        self.variables = filter_none(variables)
        self._insert_attrs(extra)


class Tag(SwaggerDict):
    def __init__(self, name, description, **extra):
        """Tag object.

        :param str name: the name of the tag; required
        :param str description: short description for the tag
        """
        super(Tag, self).__init__()
        self.name = name
        self.description = description
        self._insert_attrs(extra)


class OpenAPI(SwaggerDict):
    def __init__(self, info, paths, servers=None, security=None, components=None, tags=None,
                 _url=None, _prefix=None, _version=None, **extra):
        """Root Swagger object.

        :param Info info: info object
        :param Paths paths: paths object
        :param list[dict[str,list[str]]] security: authentication mechanisms accepted by default;
            can be overriden in Operation; each key MUST match the name of a security scheme which is declared in the
            Security Schemes under the Components object; if the security scheme is of type ``oauth2`` or
            ``openIdConnect``, then the value is a list of required scope names;
            for other security scheme types, the array MUST be empty
        :param list[Tag] tags: tag metadata; it is not required to declare all used tags here
        :param Components components: reusable components
        :param str _url: URL used for setting the API host and scheme
        :param str _prefix: api path prefix to use in setting basePath; this will be appended to the wsgi
            SCRIPT_NAME prefix or Django's FORCE_SCRIPT_NAME if applicable
        :param str _version: version string to override Info
        """
        super(OpenAPI, self).__init__()
        self.openapi = OAS_VERSION
        self.info = info
        if _version is not None:
            self.info.version = _version

        if _url:
            url = urlparse.urlparse(_url)
            assert url.netloc and url.scheme, "if given, url must have both schema and netloc"
            _url = url.scheme + '://' + url.netloc

        if servers is None:
            base_path = self.get_base_path(get_script_prefix(), _prefix or '')
            servers = [Server((_url or '') + base_path)]

        self.servers = servers
        self.paths = paths
        self.components = components
        self.security = filter_none(security) or []
        self.tags = filter_none(tags)
        self._insert_attrs(extra)

    @classmethod
    def get_base_path(cls, script_prefix, api_prefix):
        """Determine an appropriate value for ``basePath`` based on the SCRIPT_NAME and the api common prefix.

        :param str script_prefix: script prefix as defined by django ``get_script_prefix``
        :param str api_prefix: api common prefix
        :return: joined base path
        """
        # avoid double slash when joining script_name with api_prefix
        if script_prefix and script_prefix.endswith('/'):
            script_prefix = script_prefix[:-1]
        if not api_prefix.startswith('/'):
            api_prefix = '/' + api_prefix

        base_path = script_prefix + api_prefix

        # ensure that the base path has a leading slash and no trailing slash
        if base_path and base_path.endswith('/'):
            base_path = base_path[:-1]
        if not base_path.startswith('/'):
            base_path = '/' + base_path

        return base_path


class Paths(SwaggerDict):
    def __init__(self, paths, **extra):
        """A listing of all the paths in the API.

        :param dict[str,.PathItem] paths:
        """
        super(Paths, self).__init__()
        for path, path_obj in paths.items():
            assert path.startswith("/")
            if path_obj is not None:  # pragma: no cover
                self[path] = path_obj
        self._insert_attrs(extra)


class PathItem(SwaggerDict):
    OPERATION_NAMES = ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace']

    def __init__(self, summary=None, description=None, get=None, put=None, post=None, delete=None, options=None,
                 head=None, patch=None, trace=None, servers=None, parameters=None, **extra):
        """Information about a single path

        :param str summary: a summary that applies to all operations in this path
        :param str description: a description that applies to all operations in this path
        :param Operation get: operation for GET
        :param Operation put: operation for PUT
        :param Operation post: operation for POST
        :param Operation delete: operation for DELETE
        :param Operation options: operation for OPTIONS
        :param Operation head: operation for HEAD
        :param Operation patch: operation for PATCH
        :param Operation trace: operation for TRACE
        :param list[Server] servers: an alternative server array to service all operations in this path
        :param list[Parameter] parameters: parameters that apply to all operations in this path
        """
        super(PathItem, self).__init__()
        self.summary = summary
        self.description = description
        self.get = get
        self.head = head
        self.post = post
        self.put = put
        self.patch = patch
        self.delete = delete
        self.options = options
        self.trace = trace
        self.servers = servers
        self.parameters = filter_none(parameters)
        self._insert_attrs(extra)

    @property
    def operations(self):
        """A list of all standard Operations on this PathItem object. See :attr:`.OPERATION_NAMES`.

        :return: list of (method name, Operation) tuples
        :rtype: list[tuple[str,Operation]]
        """
        return [(k, v) for k, v in self.items() if k in PathItem.OPERATION_NAMES and v]


class Operation(SwaggerDict):
    def __init__(self, responses, operation_id=None, tags=None, summary=None, description=None, parameters=None,
                 request_body=None, callbacks=None, deprecated=None, security=None, servers=None, **extra):
        """Information about an API operation (path + http method combination)

        :param str operation_id: operation ID, should be unique across all operations
        :param str summary: operation summary; should be < 120 characters
        :param str description: operation description; can be of any length and supports markdown
        :param list[str] tags: operation tags
        :param list[Parameter|ParameterRef] parameters: parameters accepted
        :param RequestBody|RequestBodyRef request_body: optional request body
        :param Responses responses: possible responses
        :param dict[str,Callback|CallbackRef] callbacks: map of possible callbacks, keyed by callback identifier
        :param bool deprecated: declares this operation to be deprecated
        :param list[dict[str,list[str]]] security: list of security requirements; see :class:`OpenAPI`
        :param list[Server] servers: an alternative server array to service this operation; if a server object is
            specified at the Path Item Object or Root level, it will be overridden by this value
        """
        super(Operation, self).__init__()
        self.operation_id = operation_id
        self.summary = summary
        self.description = description
        self.tags = filter_none(tags)
        self.parameters = filter_none(parameters)
        self.request_body = request_body
        self.responses = responses
        self.callbacks = filter_none(callbacks)
        self.deprecated = deprecated
        self.security = filter_none(security)
        self.servers = servers
        self._insert_attrs(extra)


class Parameter(SwaggerDict):
    def __init__(self, name, in_, description=None, required=None, deprecated=None, allow_empty_value=None, style=None,
                 explode=None, allow_reserved=None, schema=None, content=None, example=None, examples=None, **extra):
        """Describe parameters accepted by an :class:`Operation`. Each parameter should have a unique combination of
        (`name`, `in_`).

        :param str name: parameter name
        :param str in_: parameter location
        :param str description: parameter description
        :param bool required: whether the parameter is required for the operation
        :param bool deprecated: specifies that the parameter is deprecated
        :param bool allow_empty_value: sets the ability to pass empty-valued parameters; valid only for query parameters
        :param str style: describes how the parameter value will be serialized
        :param bool explode: generate separate parameters for array or dict values
        :param bool allow_reserved: allow reserved URL characters without percent encoding
        :param Schema|SchemaRef schema: the schema defining the type used for the parameter
        :param dict[str,MediaType] content: representation for the parameter; there must be a single key
        :param any example: simple example; overrides the example in `schema`
        :param dict[str,Example|ExampleRef] examples: map of media types to examples; overrides the example in `schema`
        """
        super(Parameter, self).__init__()
        assert in_ in (IN_PATH, IN_QUERY, IN_HEADER, IN_COOKIE), "invalid value for Parameter 'in': " + in_
        self.name = name
        self.in_ = in_
        self.description = description
        self.required = required
        self.deprecated = deprecated
        self.allow_empty_value = allow_empty_value
        self.style = style
        self.explode = explode
        self.allow_reserved = allow_reserved
        self.schema = schema
        self.content = content
        self.example = example
        self.examples = examples
        self._insert_attrs(extra)
        assert not (example and examples), "cannot use both `example` and `examples`"
        if allow_empty_value is not None and self['in'] != IN_QUERY:
            raise AssertionError("allow_empty_value is only valid for query parameters")
        if allow_reserved is not None and self['in'] != IN_QUERY:
            raise AssertionError("allow_reserved is only valid for query parameters")
        if self['in'] == IN_PATH:
            # path parameters must always be required
            assert required is not False, "path parameter cannot be optional"
            self.required = True
        assert (content is not None) != (schema is not None), "exactly one of (schema, content) is required"
        if content:
            assert len(content) == 1, "Parameter content must contain exactly one media type"


class RequestBody(SwaggerDict):
    def __init__(self, content, description=None, required=None, **extra):
        """RequestBody object.

        :param dict[str,MediaType] content: request body schemas keyed by media type range
        :param str description: optional request body description
        :param bool required: true if the request body is required; defaults to false
        """
        super(RequestBody, self).__init__()
        self.content = content
        self.description = description
        self.required = required
        self._insert_attrs(extra)


class MediaType(SwaggerDict):
    def __init__(self, schema, encoding=None, example=None, examples=None, **extra):
        """MediaType object.

        :param Schema|SchemaRef schema: request/response body schema
        :param dict[str,Encoding] encoding: specifies schema property encodings for multipart and form requests
        :param any example: simple example; overrides the example in `schema`
        :param dict[str,Example|ExampleRef] examples: map of media types to examples; overrides the example in `schema`
        """
        super(MediaType, self).__init__()
        self.schema = schema
        self.encoding = encoding
        self.example = example
        self.examples = examples
        self._insert_attrs(extra)
        assert not (example and examples), "cannot use both `example` and `examples`"


class Encoding(SwaggerDict):
    def __init__(self, content_type=None, headers=None, style=None, explode=None, allow_reserved=None, **extra):
        """Encoding object.

        The ``style``, ``explode``, and ``allow_reserved`` properties apply only when
        the :class:`Encoding` describes a property of a schema inside an ``application/x-www-form-urlencoded``
        :class:`MediaType`, and have the same semantics as ``query`` :class:`Parameter`\\ s.

        :param str content_type: content type of a :class:`Schema` property; comma separated list of media types
        :param dict[str,Header|HeaderRef] headers: multipart section headers except ``Content-Type``
        :param str style: serialization style for ``x-www-form-urlencoded`` parameters
        :param bool explode: generate separate parameters for array or dict values
        :param bool allow_reserved: allow reserved URL characters without percent encoding
        """
        super(Encoding, self).__init__()
        self.content_type = content_type
        self.headers = headers
        self.style = style
        self.explode = explode
        self.allow_reserved = allow_reserved
        self._insert_attrs(extra)


class Responses(SwaggerDict):
    def __init__(self, responses, default=None, **extra):
        """Describes the expected responses of an :class:`Operation`.

        :param dict[str|int,Response|ResponseRef] responses: mapping of status code to response definition;
            the character ``X`` can be used as a wildcard in the status code: ``2XX``, ``4XX``, etc.
        :param Response|ResponseRef default: response structure for status codes not in `responses`
        """
        super(Responses, self).__init__()
        for status, response in responses.items():
            if status is not None and response is not None:  # pragma: no cover
                self[str(status)] = response
        self.default = default
        self._insert_attrs(extra)


class Response(SwaggerDict):
    def __init__(self, description, headers=None, content=None, links=None, **extra):
        """Describes the structure of an operation's response.

        :param str description: response description; required
        :param dict[str,Header|HeaderRef] headers: map of header names to response header definitions
        :param dict[str,MediaType] content: map of media type range to response structure
        :param dict[str,Link|LinkRef] links: response links
        """
        super(Response, self).__init__()
        self.description = description
        self.headers = headers
        self.content = content
        self.links = links
        self._insert_attrs(extra)


class Header(Parameter):
    def __init__(self, **kwargs):
        """Header object for use in formdata :class:`Encoding` and :class:`Response` headers.

        The same properties as for :class:`Parameter` apply, with the exception that ``name`` and ``in`` are not allowed
            - the name is given by the key in the ``headers`` map, and the location is implicitly ``header``
        """
        super(Header, self).__init__(None, IN_HEADER, **kwargs)
        self.name = None
        self.in_ = IN_HEADER


class Callback(SwaggerDict):
    def __init__(self, callback_paths, **extra):
        """Callback object.

        :param dict[str,PathItem] callback_paths: callback request/response structures, keyed by callback url;
            the url can use values from the request and response via OpenAPI runtime expressions
        """
        super(Callback, self).__init__()
        for expression, path_item in callback_paths.items():
            # use setitem instead of setattr to skip case conversion
            self[expression] = path_item
        self._insert_attrs(extra)


class Example(SwaggerDict):
    def __init__(self, summary=None, description=None, value=None, external_value=None, **extra):
        """Example object.

        :param str summary: short description
        :param str description: long description
        :param value: the example value; can be of any type
        :param str external_value: a url pointing to an external example
        """
        super(Example, self).__init__()
        self.summary = summary
        self.description = description
        self.value = value
        self.external_value = external_value
        self._insert_attrs(extra)
        assert not (value and external_value), "Example cannot contain both value and external_value"


class Link(SwaggerDict):
    def __init__(self, operation_id, parameters=None, request_body=None, description=None, server=None, **extra):
        """Link object.
        
        :param str operation_id: the id of an :class:`Operation` defined in the document
        :param dict[str,any] parameters: map of parameter names to values; value can be either a constant or
            a runtime expression; name can optionally be prefixed with location, i.e. ``path.id``, ``query.id``
        :param request_body: constant value or runtime expression for request body
        :param description description: link description
        :param Server server: server to use for the linked operation
        """
        super(Link, self).__init__()
        self.operation_id = operation_id
        self.parameters = parameters
        self.request_body = request_body
        self.description = description
        self.server = server
        self._insert_attrs(extra)


class Schema(SwaggerDict):
    def __init__(self, title=None, description=None, type=None, format=None, enum=None, pattern=None, properties=None,
                 additional_properties=None, required=None, items=None, default=None, read_only=None, write_only=None,
                 nullable=None, example=None, deprecated=None, one_of=None, all_of=None, any_of=None, not_=None,
                 **extra):
        """Describes a complex object accepted as parameter or returned as a response.

        :param str title: schema title
        :param str description: schema description
        :param str type: value type
        :param str format: value format, see OpenAPI spec
        :param list[any] enum: restrict possible values
        :param str pattern: pattern if type is ``string``
        :param dict[str,Schema|SchemaRef] properties: object properties; required if `type` is ``object``
        :param bool|Schema|SchemaRef additional_properties: allow wildcard properties not listed in `properties`
        :param list[str] required: list of requried property names
        :param Schema|SchemaRef items: type of array items, only valid if `type` is ``array``
        :param Discriminator discriminator: discriminator for polymorphism support, to be used with one_of and any_of
        :param any default: the default value for the schema if it is not provided in the input/output data
        :param bool read_only: declares the property read only, indicating that it must never be sent in a request;
            if the property is also required, the server must always send it in the response
        :param bool write_only: declares the property write only, indicating that it will never be sent in a response;
            if the property is also required, the client must always send it in the request
        :param bool nullable: allows a ``null`` value to be used in place of this :class:`Schema`
        :param bool deprecated: declares this schema as deprecated
        :param any example: simple example of an instance of this schema
        :param list[Schema|SchemaRef] one_of: validates the payload if exactly one of the referenced schemas matches it
        :param list[Schema|SchemaRef] any_of: validates the payload if at least one of the referenced schemas matches it
        :param list[Schema|SchemaRef] all_of: validates the payload if all referenced schemas match it
        :param Schema|SchemaRef not_: validates the payload if the referenced schema does not validate it
        """
        super(Schema, self).__init__()
        if required is True or required is False:
            # common error
            raise AssertionError("the `required` attribute of schema must be an "
                                 "array of required property names, not a boolean!")
        assert type, "type is required!"
        self.title = title
        self.description = description
        self.properties = filter_none(properties)
        self.additional_properties = additional_properties
        self.required = filter_none(required)
        self.type = type
        self.format = format
        self.enum = enum
        self.pattern = pattern
        self.items = items
        self.read_only = read_only
        self.write_only = write_only
        self.nullable = nullable
        self.deprecated = deprecated
        self.default = default
        self.example = example
        self.one_of = one_of
        self.all_of = all_of
        self.any_of = any_of
        self.not_ = not_
        self._insert_attrs(extra)
        if (properties or (additional_properties is not None)) and type != TYPE_OBJECT:
            raise AssertionError("only object Schema can have properties")
        if (format or enum or pattern) and type in (TYPE_OBJECT, TYPE_ARRAY):
            raise AssertionError("[format, enum, pattern] can only be applied to primitive Schema")
        if items and type != TYPE_ARRAY:
            raise AssertionError("items can only be used when type is array")
        if pattern and type != TYPE_STRING:
            raise AssertionError("pattern can only be used when type is string")
        assert not (read_only and write_only), "Schema can be either read_only or write_only, not both"

    def _remove_read_only(self):
        # readOnly is only valid for Schemas inside another Schema's properties;
        # when placing Schema elsewhere we must take care to remove the readOnly flag
        self.pop('readOnly', '')


class Discriminator(SwaggerDict):
    def __init__(self, property_name, mapping=None, **extra):
        """Discriminator object.

        :param str property_name: the name of the discriminator property
        :param dict[str,str] mapping: mapping of payload values to :class:`Schema` names or references
        """
        super(Discriminator, self).__init__()
        self.property_name = property_name
        self.mapping = mapping
        self._insert_attrs(extra)


class SecurityScheme(SwaggerDict):
    def __init__(self, type, description=None, name=None, in_=None, scheme=None, bearer_format=None, flows=None,
                 openid_connect_url=None, **extra):
        """SecurityScheme object.

        :param str type: security scheme type; required
        :param str description: security scheme description
        :param str name: for ``apiKey``, the name of the parameter used to send the API key
        :param str in_: for ``apiKey``, the location of the parameter used to send the API key; cannot be ``path``
        :param str scheme: for ``http``, the RFC7235 authorization scheme to use
        :param str bearer_format: for ``http`` with the ``bearer`` scheme, hints the bearer token format
        :param OAuthFlows flows: for ``oauth2``, describes the available flows
        :param str openid_connect_url: for ``openIdConnect``, the URL for discovering auth configuration values
        """
        super(SecurityScheme, self).__init__()
        self.type = type
        self.description = description
        self.name = name
        self.in_ = in_
        self.scheme = scheme
        self.bearer_format = bearer_format
        self.flows = flows
        self.openid_connect_url = openid_connect_url
        self._insert_attrs(extra)
        if self.type == SECURITY_API_KEY:
            assert 'name' in self and 'in' in self, "apiKey authentication requires the name and in properties"
            assert self['in'] != IN_PATH, "apiKey parameter cannot be a path parameter"
        elif self.type == SECURITY_HTTP:
            assert 'scheme' in self, "http authentication requires the scheme property"
        elif self.type == SECURITY_OAUTH2:
            assert 'flows' in self, "oauth2 authentication requires the flows property"
        elif self.type == SECURITY_OPENID_CONNECT:
            assert 'openIdConnectUrl' in self, "openIdConnect authentication requires the openIdConnectUrl property"


class OAuthFlows(SwaggerDict):
    def __init__(self, implicit, password=None, client_credentials=None, authorization_code=None, **extra):
        """OAuth Flows object.

        :param OAuthFlow implicit: Implicit flow configuration
        :param OAuthFlow password: Resource Owner Password flow configuration
        :param OAuthFlow client_credentials: Client Credentials flow configuration
        :param OAuthFlow authorization_code: Authorization Code flow configuration
        """
        super(OAuthFlows, self).__init__()
        self.implicit = implicit
        self.password = password
        self.client_credentials = client_credentials
        self.authorization_code = authorization_code
        self._insert_attrs(extra)


class OAuthFlow(SwaggerDict):
    def __init__(self, scopes, authorization_url=None, token_url=None, refresh_url=None, **extra):
        """OAuth Flow object.

        :param str authorization_url: required for the 'implicit' and 'authorizationCode' flows
        :param str token_url: required for all flows except 'implicit'
        :param str refresh_url: URL for obtaining refresh tokens
        :param dict[str,str] scopes: map of available scope names to short description; required for all flows
        """
        super(OAuthFlow, self).__init__()
        self.authorization_url = authorization_url
        self.token_url = token_url
        self.refresh_url = refresh_url
        self.scopes = scopes
        self._insert_attrs(extra)


def resolve_ref(ref_or_obj, components):
    """Resolve `ref_or_obj` if it is a reference type. Return it unchaged if not.

    :param SwaggerDict|_Ref ref_or_obj:
    :param Components components: component resolver which must contain the referenced object
    """
    if isinstance(ref_or_obj, _Ref):
        return ref_or_obj.resolve(components)
    return ref_or_obj


class Components(SwaggerDict):
    SCHEMAS = 'schemas'  #:
    RESPONSES = 'responses'  #:
    PARAMETERS = 'parameters'  #:
    EXAMPLES = 'examples'  #:
    REQUEST_BODIES = 'requestBodies'  #:
    HEADERS = 'headers'  #:
    SECURITY_SCHEMES = 'securitySchemes'  #:
    LINKS = 'links'  #:
    CALLBACKS = 'callbacks'  #:

    def __init__(self, schemas=None, responses=None, parameters=None, examples=None, request_bodies=None,
                 headers=None, security_schemes=None, links=None, callbacks=None, **extra):
        """Components object.

        :param dict[str,Schema|SchemaRef] schemas: initial schemes
        :param dict[str,Response|ResponseRef] responses: initial responses
        :param dict[str,Parameter|ParameterRef] parameters: initial parameters
        :param dict[str,Example|ExampleRef] examples: initial examples
        :param dict[str,RequestBody|RequestBodyRef] request_bodies: initial request bodies
        :param dict[str,Header|HeaderRef] headers: initial headers
        :param dict[str,SecurityScheme|SecuritySchemeRef] security_schemes: initial security schemes
        :param dict[str,Link|LinkRef] links: initial links
        :param dict[str,Callback|CallbackRef] callbacks: initial callbacks
        """
        super(Components, self).__init__()
        self.schemas = schemas or OrderedDict()
        self.responses = responses or OrderedDict()
        self.parameters = parameters or OrderedDict()
        self.examples = examples or OrderedDict()
        self.request_bodies = request_bodies or OrderedDict()
        self.headers = headers or OrderedDict()
        self.security_schemes = security_schemes or OrderedDict()
        self.links = links or OrderedDict()
        self.callbacks = callbacks or OrderedDict()
        self._insert_attrs(extra)


class _Ref(SwaggerDict):
    ref_name_re = re.compile(r"#/components/(?P<scope>.+)/(?P<name>[^/]+)$")

    def __init__(self, scope, name, components=None):
        """Base class for all reference types. A reference object has only one property, ``$ref``, which must be a JSON
        reference to a valid object in the specification, e.g. ``#/definitions/Article`` to refer to an article model.

        :param str scope: reference scope, e.g. "definitions"
        :param str name: referenced object name, e.g. "Article"
        :param Components components: component resolver which will be checked to contain the referneced object
        """
        super(_Ref, self).__init__()
        assert not type(self) == _Ref, "do not instantiate _Ref directly"
        ref_name = "#/components/{scope}/{name}".format(scope=scope, name=name)
        if components:
            components[scope].get(name)  # assert presence of component

        self.ref = ref_name

    @cached_property
    def ref_scope(self):
        ref_match = self.ref_name_re.match(self.ref)
        return ref_match.group('scope')

    @cached_property
    def ref_name(self):
        ref_match = self.ref_name_re.match(self.ref)
        return ref_match.group('name')

    def resolve(self, components):
        """Get the object targeted by this reference from the given components resolver.

        :param Components components: component resolver which must contain the referneced object
        :returns: the target object
        """
        return components[self.ref_scope][self.ref_name]

    def bind(self, components, maker_or_obj):
        """Set the target of this reference in the given components resolver

        :param Components components: component resolver
        :param object|()->object maker_or_obj: object or object factory; called only if necessary
        """
        objects = components[self.ref_scope]
        ret = objects.get(self.ref_name, None)
        if ret is None:
            if callable(maker_or_obj):
                ret = maker_or_obj()
            else:
                ret = maker_or_obj

            value = objects.get(self.ref_name, None)
            assert ret is not None, "maker returned None; referenced objects cannot be None/null"
            if value is None:
                objects[self.ref_name] = None
            elif value != ret:
                logger.debug("maker for %s inserted a value into components; ignoring its return value", self.ref)
                ret = value

        return ret

    def __setitem__(self, key, value):
        if key == "$ref":
            if key in self:
                raise NotImplementedError("Reference object is immutable")
            return super(_Ref, self).__setitem__(key, value)
        raise NotImplementedError("only $ref can be set on Reference objects (not %s)" % key)

    def __delitem__(self, key):
        raise NotImplementedError("cannot delete property of Reference object")


class SchemaRef(_Ref):
    def __init__(self, components, schema_name):
        """Adds a reference to a named Schema defined in the ``components`` object.

        :param Components components: components resolver
        :param str schema_name: referenced schema name
        """
        super(SchemaRef, self).__init__(Components.SCHEMAS, schema_name, components)


class ResponseRef(_Ref):
    def __init__(self, components, response_name):
        """Adds a reference to a named Response defined in the ``components`` object.

        :param Components components: components resolver
        :param str response_name: name of the referenced response
        """
        super(ResponseRef, self).__init__(Components.RESPONSES, response_name, components)


class ParameterRef(_Ref):
    def __init__(self, components, parameter_name):
        """Adds a reference to a named Parameter defined in the ``components`` object.

        :param Components components: components resolver
        :param str parameter_name: name of the referenced parameter
        """
        super(ParameterRef, self).__init__(Components.PARAMETERS, parameter_name, components)


class ExampleRef(_Ref):
    def __init__(self, components, example_name):
        """Adds a reference to a named Example defined in the ``components`` object.

        :param Components components: components resolver
        :param str example_name: name of the referenced example
        """
        super(ExampleRef, self).__init__(Components.EXAMPLES, example_name, components)


class RequestBodyRef(_Ref):
    def __init__(self, components, request_body_name):
        """Adds a reference to a named Request Body defined in the ``components`` object.

        :param Components components: components resolver
        :param str request_body_name: name of the referenced request_body
        """
        super(RequestBodyRef, self).__init__(Components.REQUEST_BODIES, request_body_name, components)


class HeaderRef(_Ref):
    def __init__(self, components, header_name):
        """Adds a reference to a named Header defined in the ``components`` object.

        :param Components components: components resolver
        :param str header_name: name of the referenced header
        """
        super(HeaderRef, self).__init__(Components.HEADERS, header_name, components)


class SecuritySchemeRef(_Ref):
    def __init__(self, components, security_scheme_name):
        """Adds a reference to a named SecurityScheme defined in the ``components`` object.

        :param Components components: components resolver
        :param str security_scheme_name: name of the referenced security_scheme
        """
        super(SecuritySchemeRef, self).__init__(Components.SECURITY_SCHEMES, security_scheme_name, components)


class LinkRef(_Ref):
    def __init__(self, components, link_name):
        """Adds a reference to a named Link defined in the ``components`` object.

        :param Components components: components resolver
        :param str link_name: name of the referenced link
        """
        super(LinkRef, self).__init__(Components.LINKS, link_name, components)


class CallbackRef(_Ref):
    def __init__(self, components, callback_name):
        """Adds a reference to a named Callback defined in the ``components`` object.

        :param Components components: components resolver
        :param str callback_name: name of the referenced callback
        """
        super(CallbackRef, self).__init__(Components.CALLBACKS, callback_name, components)
