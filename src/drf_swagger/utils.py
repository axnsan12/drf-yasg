from rest_framework.mixins import RetrieveModelMixin, DestroyModelMixin

no_body = object()


class UpdateModelMixing(object):
    pass


def is_list_view(path, method, view):
    """Return True if the given path/method appears to represent a list view (as opposed to a detail/instance view)."""
    # for ViewSets, it could be the default 'list' view, or a list_route
    action = getattr(view, 'action', '')
    method = getattr(view, action, None)
    detail = getattr(method, 'detail', None)
    suffix = getattr(view, 'suffix', None)
    if action == 'list' or detail is False or suffix == 'List':
        return True

    if action in ('retrieve', 'update', 'partial_update', 'destroy') or detail is True or suffix == 'Instance':
        # a detail_route is surely not a list route
        return False

    # for APIView, if it's a detail view it can't also be a list view
    if isinstance(view, (RetrieveModelMixin, UpdateModelMixing, DestroyModelMixin)):
        return False

    # if the last component in the path is parameterized it's probably not a list view
    path_components = path.strip('/').split('/')
    if path_components and '{' in path_components[-1]:
        return False

    # otherwise assume it's a list route
    return True


def swagger_auto_schema(method=None, methods=None, auto_schema=None, request_body=None, manual_parameters=None,
                        operation_description=None, responses=None):
    def decorator(view_method):
        data = {
            'auto_schema': auto_schema,
            'request_body': request_body,
            'manual_parameters': manual_parameters,
            'operation_description': operation_description,
            'responses': responses,
        }
        data = {k: v for k, v in data.items() if v is not None}

        bind_to_methods = getattr(view_method, 'bind_to_methods', [])
        # if the method is actually a function based view
        view_cls = getattr(view_method, 'cls', None)
        http_method_names = getattr(view_cls, 'http_method_names', [])
        if bind_to_methods or http_method_names:
            # detail_route, list_route or api_view
            assert bool(http_method_names) != bool(bind_to_methods), "this should never happen"
            available_methods = http_method_names + bind_to_methods
            existing_data = getattr(view_method, 'swagger_auto_schema', {})

            if http_method_names:
                _route = "api_view"
            else:
                _route = "detail_route" if view_method.detail else "list_route"

            _methods = methods
            if len(available_methods) > 1:
                assert methods or method, \
                    "on multi-method %s, you must specify swagger_auto_schema on a per-method basis " \
                    "using one of the `method` or `methods` arguments" % _route
                assert bool(methods) != bool(method), "specify either method or methods"
                if method:
                    _methods = [method.lower()]
                else:
                    _methods = [mth.lower() for mth in methods]
                assert not isinstance(_methods, str)
                assert not any(mth in existing_data for mth in _methods), "method defined multiple times"
                assert all(mth in available_methods for mth in _methods), "method not bound to %s" % _route

                existing_data.update((mth.lower(), data) for mth in _methods)
            else:
                existing_data[available_methods[0]] = data
            view_method.swagger_auto_schema = existing_data
        else:
            assert methods is None, \
                "the methods argument should only be specified when decorating a detail_route or list_route; you " \
                "should also ensure that you put the swagger_auto_schema decorator AFTER (above) the _route decorator"
            view_method.swagger_auto_schema = data

        return view_method

    return decorator
