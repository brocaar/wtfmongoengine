from wtforms import validators, fields
from wtforms.form import Form, FormMeta


class DocumentFieldConverter(object):

    def convert(self, document_field):
        """
        Convert ``document_field`` into a WTForms field.

        :param document_field:
            Instance of a Mongoengine field class.

        :return:
            Instance of a WTForms instance.

        """
        kwargs = {
            'label': document_field.name,
            'validators': [],
            'default': document_field.default,
        }

        if document_field.required:
            kwargs['validators'].append(validators.Required())

        if document_field.choices:
            kwargs['choices'] = document_field.choices
            return fields.SelectField(**kwargs)

        document_field_type = type(document_field).__name__

        convert_method_name = 'from_{0}'.format(document_field_type.lower())

        if hasattr(self, convert_method_name):
            return getattr(self, convert_method_name)(document_field, **kwargs)
        else:
            return None

    def set_common_string_kwargs(self, document_field, kwargs):
        """
        Set commong string arguments.

        :param document_field:
            Instance of Mongoengine field.

        :param kwargs:
            A ``dict`` that needs to be updated with the new arguments.

        """
        if document_field.max_length or document_field.min_length:
            kwargs['validators'].append(
                validators.Length(
                    max=document_field.max_length or -1,
                    min=document_field.min_length or -1
                )
            )

        if document_field.regex:
            kwargs['validators'].append(
                validators.Regexp(regex=document_field.regex)
            )

    def from_stringfield(self, document_field, **kwargs):
        """
        Convert ``document_field`` into a ``TextField``.

        :param document_field:
            Instance of Mongoengine field.

        :return:
            Instance of :py:class:`!wtforms.fields.TextField`.

        """
        pass


class DocumentFormMetaClassBase(type):
    """
    Meta-class for generating the actual WTForms class.
    """
    def __new__(cls, name, bases, attrs):
        if 'Meta' in attrs:
            document = attrs['Meta'].document
            fields = getattr(attrs['Meta'], 'fields', None)
            exclude = getattr(attrs['Meta'], 'exclude', None)

            attrs = DocumentFormMetaClassBase.model_fields(
                document, fields, exclude)

        return super(
            DocumentFormMetaClassBase, cls).__new__(cls, name, bases, attrs)

    @classmethod
    def model_fields(cls, document, fields=None, exclude=None):
        """
        Convert the given document into a WTForm fields.

        :param document:
            The Mongoengine document to convert.

        :param fields:
            If given, it will only parse these fields.

        :param exclude:
            If given, it will exclude these fields from parsing.

        """
        field_names = document._fields.keys()

        if fields:
            field_names = (f for f in field_names if f in fields)
        elif exclude:
            field_names = (f for f in field_names if f not in exclude)

        converter = DocumentFieldConverter()
        field_dict = {}

        for field_name in field_names:
            model_field = document._fields[field_name]
            wtf_field = converter.convert(model_field)
            if wtf_field:
                field_dict[field_name] = wtf_field

        return field_dict


class DocumentFormMetaClass(DocumentFormMetaClassBase, FormMeta):
    # This object, combining the two meta classes, is needed to avoid conflicts
    pass


class DocumentForm(Form):
    """
    Baseclass for constructing a WTF form from a Mongoengine Document class.
    """
    __metaclass__ = DocumentFormMetaClass
