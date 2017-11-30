import warnings
from collections import OrderedDict

import coreapi


class Contact(object):
    def __init__(self, name=None, url=None, email=None):
        self.name = name
        self.url = url
        self.email = email
        if name is None and url is None and email is None:
            raise ValueError("one of name, url or email is requires for Swagger Contact object")

    def to_swagger(self):
        contact = OrderedDict()
        if self.name is not None:
            contact['name'] = self.name
        if self.url is not None:
            contact['url'] = self.url
        if self.email is not None:
            contact['email'] = self.email

        return contact


class License(object):
    def __init__(self, name, url=None):
        self.name = name
        self.url = url
        if name is None:
            raise ValueError("name is required for Swagger License object")

    def to_swagger(self):
        license = OrderedDict()
        license['name'] = self.name
        if self.url is not None:
            license['url'] = self.url

        return license


class Info(object):
    def __init__(self, title, default_version, description=None, terms_of_service=None, contact=None, license=None):
        if title is None or default_version is None:
            raise ValueError("title and version are required for Swagger info object")
        if contact is not None and not isinstance(contact, Contact):
            raise ValueError("contact must be a Contact object")
        if license is not None and not isinstance(license, License):
            raise ValueError("license must be a License object")
        self.title = title
        self.default_version = default_version
        self.description = description
        self.terms_of_service = terms_of_service
        self.contact = contact
        self.license = license

    def to_swagger(self, version):
        info = OrderedDict()
        info['title'] = self.title
        if self.description is not None:
            info['description'] = self.description
        if self.terms_of_service is not None:
            info['termsOfService'] = self.terms_of_service
        if self.contact is not None:
            info['contact'] = self.contact.to_swagger()
        if self.license is not None:
            info['license'] = self.license.to_swagger()
        info['version'] = version or self.default_version
        return info


class Swagger(coreapi.Document):
    @classmethod
    def from_coreapi(cls, document, info, version):
        """
        Create an openapi.Swagger from the fields of a coreapi.Document.

        :param coreapi.Document document: source coreapi.Document
        :param openapi.Info info: Swagger info object
        :param string version: API version string
        :return: an openapi.Swagger
        """
        if document.title != info.title:
            warnings.warn("document title is overriden by Swagger Info")
        if document.description != info.description:
            warnings.warn("document description is overriden by Swagger Info")
        return Swagger(
            info=info,
            version=version,
            url=document.url,
            media_type=document.media_type,
            content=document.data
        )

    def __init__(self, info=None, version=None, url=None, media_type=None, content=None):
        super(Swagger, self).__init__(url, info.title, info.description, media_type, content)
        self._info = info
        self._version = version

    @property
    def info(self):
        return self._info

    @property
    def version(self):
        return self._version


class Field(coreapi.Field):
    pass


class Link(coreapi.Link):
    pass
