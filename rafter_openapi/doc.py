from collections import defaultdict
from datetime import date, datetime

from schematics import types
from schematics.types.compound import ModelType, ListType


class Field:
    def __init__(self, description=None, required=None, name=None,
                 choices=None):
        self.name = name
        self.description = description
        self.required = required
        self.choices = choices

    def serialize(self):
        output = {}
        if self.name:
            output['name'] = self.name
        if self.description:
            output['description'] = self.description
        if self.required is not None:
            output['required'] = self.required
        if self.choices is not None:
            output['enum'] = self.choices
        return output


class Integer(Field):
    def serialize(self):
        return {
            "type": "integer",
            "format": "int64",
            **super().serialize()
        }


class Float(Field):
    def serialize(self):
        return {
            "type": "number",
            "format": "double",
            **super().serialize()
        }


class String(Field):
    def serialize(self):
        return {
            "type": "string",
            **super().serialize()
        }


class Boolean(Field):
    def serialize(self):
        return {
            "type": "boolean",
            **super().serialize()
        }


class Tuple(Field):
    pass


class Date(Field):
    def serialize(self):
        return {
            "type": "string",
            "format": "date",
            **super().serialize()
        }


class DateTime(Field):
    def serialize(self):
        return {
            "type": "string",
            "format": "date-time",
            **super().serialize()
        }


class Dictionary(Field):
    def __init__(self, fields=None, **kwargs):
        self.fields = fields or {}
        super().__init__(**kwargs)

    def serialize(self):
        return {
            "type": "object",
            "properties": {key: serialize_schema(schema)
                           for key, schema in self.fields.items()},
            **super().serialize()
        }


class List(Field):
    def __init__(self, items=None, *args, **kwargs):
        self.items = items or []
        if type(self.items) is not list:
            self.items = [self.items]
        super().__init__(*args, **kwargs)

    def serialize(self):
        if len(self.items) > 1:
            items = Tuple(self.items).serialize()
        elif self.items:
            items = serialize_schema(self.items[0])
        return {
            "type": "array",
            "items": items
        }


definitions = {}


class Object(Field):
    def __init__(self, cls, *args, object_name=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.cls = cls
        self.object_name = object_name or cls.__name__

        if self.cls not in definitions:
            definitions[self.cls] = (self, self.definition)

    @property
    def definition(self):
        return {
            "type": "object",
            "properties": {
                key: serialize_schema(schema)
                for key, schema in self.cls.__dict__.items()
                if not key.startswith("_")
            },
            **super().serialize()
        }

    def serialize(self):
        return {
            "type": "object",
            "$ref": "#/definitions/{}".format(self.object_name),
            **super().serialize()
        }


class JsonBody(Field):
    def __init__(self, fields=None, **kwargs):
        self.fields = fields or {}
        super().__init__(**kwargs, name="body")

    def serialize(self):
        return {
            "schema": {
                "type": "object",
                "properties": {key: serialize_schema(schema)
                               for key, schema in self.fields.items()},
            },
            **super().serialize()
        }


def serialize_schema(schema):
    schema_type = type(schema)

    # --------------------------------------------------------------- #
    # Class
    # --------------------------------------------------------------- #
    if schema_type is type:
        if issubclass(schema, Field):
            return schema().serialize()
        elif schema is dict:
            return Dictionary().serialize()
        elif schema is list:
            return List().serialize()
        elif schema is int:
            return Integer().serialize()
        elif schema is float:
            return Float().serialize()
        elif schema is str:
            return String().serialize()
        elif schema is bool:
            return Boolean().serialize()
        elif schema is date:
            return Date().serialize()
        elif schema is datetime:
            return DateTime().serialize()
        else:
            return Object(schema).serialize()

    # --------------------------------------------------------------- #
    # Object
    # --------------------------------------------------------------- #
    else:
        if issubclass(schema_type, Field):
            return schema.serialize()
        elif schema_type is dict:
            return Dictionary(schema).serialize()
        elif schema_type is list:
            return List(schema).serialize()

    return {}


# --------------------------------------------------------------- #
# Route Documenters
# --------------------------------------------------------------- #


class RouteSpec(object):
    consumes = None
    consumes_content_type = None
    produces = None
    produces_content_type = None
    summary = None
    description = None
    operation = None
    blueprint = None
    tags = None
    exclude = None
    response = None

    def __init__(self):
        self.tags = []
        self.consumes = []
        self.response = []
        super().__init__()


class RouteField(object):
    field = None
    location = None
    required = None
    description = None

    def __init__(self, field, location=None, required=False, description=None):
        self.field = field
        self.location = location
        self.required = required
        self.description = description


class CustomDefaultDict(defaultdict):

    def get_key(self, key):
        """Get method which use qualname to retrieve matching entry.

        Functions as keys are not found because each Rafter filter will alter
        the function id, so we use the qualname to found the function which
        match the same qualname.

        This will not work if 2 functions have the same name in the codebase
        but it's the best we can do for now.
        """
        ret = None
        qkey = key.__qualname__
        ret = self.get(qkey)
        if not ret:
            # check all entries if qualname match
            for k in self:
                if k.__qualname__ == qkey:
                    return self.get(k)
        return


route_specs = CustomDefaultDict(RouteSpec)


def route(summary=None, description=None, consumes=None, produces=None,
          consumes_content_type=None, produces_content_type=None,
          exclude=None, response=None):
    def inner(func):
        route_spec = route_specs[func]

        if summary is not None:
            route_spec.summary = summary
        if description is not None:
            route_spec.description = description
        if consumes is not None:
            route_spec.consumes = consumes
        if produces is not None:
            route_spec.produces = produces
        if consumes_content_type is not None:
            route_spec.consumes_content_type = consumes_content_type
        if produces_content_type is not None:
            route_spec.produces_content_type = produces_content_type
        if exclude is not None:
            route_spec.exclude = exclude
        if response is not None:
            route_spec.response = response

        return func
    return inner


def exclude(boolean):
    def inner(func):
        route_specs[func].exclude = boolean
        return func
    return inner


def summary(text):
    def inner(func):
        route_specs[func].summary = text
        return func
    return inner


def description(text):
    def inner(func):
        route_specs[func].description = text
        return func
    return inner


def consumes(*args, content_type=None, location='query', required=False,
             description=None):
    def inner(func):
        if args:
            for arg in args:
                field = RouteField(arg, location, required, description)
                route_specs[func].consumes.append(field)
                route_specs[func].consumes_content_type = [content_type]
        return func
    return inner


def produces(*args, content_type=None, description=None):
    def inner(func):
        if args:
            field = RouteField(args[0], description=description)
            route_specs[func].produces = field
            route_specs[func].produces_content_type = [content_type]
        return func
    return inner


def response(*args, description=None):
    def inner(func):
        if args:
            status_code = args[0]
            field = RouteField(args[1], description=description)
            route_specs[func].response.append((status_code, field))
        return func
    return inner


def tag(name):
    def inner(func):
        route_specs[func].tags.append(name)
        return func
    return inner


SCHEMATIC_TYPE_TO_DOC_TYPE = {
    types.NumberType: Float,
    types.IntType: Integer,
    types.LongType: Integer,
    types.FloatType: Float,
    types.DecimalType: Float,
    types.BooleanType: Boolean,
    types.StringType: String,
}


def parse_fields(model):
    properties = {}
    # Loop over each field and either evict it or convert it
    for field_name, field_instance in model._fields.items():
        # Break 3-tuple out
        # print(field_name, field_instance)
        serialized_name = getattr(field_instance, 'serialized_name', None) or field_name  # noqa

        if isinstance(field_instance, ModelType):
            properties[serialized_name] = model2json(field_instance.model_class)  # noqa

        elif isinstance(field_instance, ListType):
            if hasattr(field_instance, 'model_class'):
                properties[serialized_name] = model2json(field_instance.model_class, 'array')  # noqa
            else:
                is_req = getattr(field_instance, 'required', False)
                doctype = SCHEMATIC_TYPE_TO_DOC_TYPE.get(field_instance.__class__, String)  # noqa
                properties[serialized_name] = List(doctype, required=is_req)

        # Convert field as single model
        elif isinstance(field_instance, types.BaseType):
            doctype = SCHEMATIC_TYPE_TO_DOC_TYPE.get(field_instance.__class__, String)  # noqa
            is_req = getattr(field_instance, 'required', False)
            properties[serialized_name] = doctype(required=is_req)

    return properties


def model2json(model, _type='object'):
    return parse_fields(model)


def from_model(model):
    """Returns representation of a schematics model as a jsonBody object."""
    ret = model2json(model)
    return JsonBody(ret['body'])
