from unittest import TestCase

from mock import Mock, patch

from wtfmongoengine.forms import (
    DocumentFormMetaClassBase, DocumentFieldConverter)


class DocumentFormMetaClassBaseTestCase(TestCase):
    """
    Test :py:class:`.DocumentFormMetaClassBase`.
    """
    def setUp(self):
        self.fields = {
            'title': Mock(return_value='title-value'),
            'body': Mock(return_value='body-value'),
            'author': Mock(return_value='author-value'),
            'timestamp': Mock(return_value='timestamp-value'),
        }

        self.document = Mock()
        self.document._fields = self.fields

        self.converter = Mock()
        self.converter.convert.side_effect = lambda x: x()

    @patch('wtfmongoengine.forms.DocumentFormMetaClassBase.model_fields')
    def test___new__(self, model_fields):
        """
        Test that ``__new__`` is creating the new class properly.
        """
        model_fields.return_value = {
            'field_a': 'a-value',
            'field_b': 'b-value'
        }

        class TestClass(object):
            __metaclass__ = DocumentFormMetaClassBase

            class Meta:
                fields = ('title', 'body',)
                exclude = ('author', 'timestamp',)
                document = 'a-document'

        model_fields.assert_called_once_with(
            'a-document',
            ('title', 'body',),
            ('author', 'timestamp',),
        )
        self.assertEqual('a-value', TestClass.field_a)
        self.assertEqual('b-value', TestClass.field_b)

    @patch('wtfmongoengine.forms.DocumentFieldConverter')
    def test_model_fields(self, DocumentFieldConverter):
        """
        Test that ``model_fields`` extracts the fields.

        Tests :py:meth:`.DocumentFormMetaClassBase.model_fields`.
        """
        DocumentFieldConverter.return_value = self.converter

        result = DocumentFormMetaClassBase.model_fields(self.document)
        self.assertEqual({
            'title': 'title-value',
            'body': 'body-value',
            'author': 'author-value',
            'timestamp': 'timestamp-value',
        }, result)

    @patch('wtfmongoengine.forms.DocumentFieldConverter')
    def test_model_fields_fields(self, DocumentFieldConverter):
        """
        Test that ``model_fields`` uses only fields in ``fields`` argument.

        Tests :py:meth:`.DocumentFormMetaClassBase.model_fields`.
        """
        DocumentFieldConverter.return_value = self.converter

        result = DocumentFormMetaClassBase.model_fields(
            self.document, fields=('title', 'author',))

        self.assertEqual({
            'title': 'title-value',
            'author': 'author-value',
        }, result)

    @patch('wtfmongoengine.forms.DocumentFieldConverter')
    def test_model_fields_exclude(self, DocumentFieldConverter):
        """
        Test that ``model_fields`` excludes fields in ``exclude`` argument.

        Tests :py:meth:`.DocumentFormMetaClassBase.model_fields`.
        """
        DocumentFieldConverter.return_value = self.converter

        result = DocumentFormMetaClassBase.model_fields(
            self.document, exclude=('title', 'author',))

        self.assertEqual({
            'body': 'body-value',
            'timestamp': 'timestamp-value',
        }, result)


class DocumentFieldConverterTestCase(TestCase):
    """
    Test :py:class:`.DocumentFieldConverter`.
    """
    @patch('wtfmongoengine.forms.validators')
    def test_convert(self, validators):
        """
        Test ``convert`` without choices.

        Tests :py:meth:`.DocumentFieldConverter.convert`.
        """
        validators.Required.return_value = 'required'

        class DocumentFieldMock(object):
            name = 'test field'
            required = True
            default = 'empty'
            choices = None

        document_field = DocumentFieldMock()

        converter = DocumentFieldConverter()
        converter.from_documentfieldmock = Mock(return_value='wtfield')

        result = converter.convert(document_field)

        converter.from_documentfieldmock.assert_called_once_with(
            document_field,
            label='test field',
            validators=['required'],
            default='empty',
        )

        self.assertEqual('wtfield', result)

    @patch('wtfmongoengine.forms.fields')
    def test_convert_choices(self, fields):
        """
        Test ``convert`` with choices.

        Tests :py:meth:`.DocumentFieldConverter.convert`.
        """
        fields.SelectField.return_value = 'select-field'

        class DocumentFieldMock(object):
            name = 'test field'
            required = False
            default = 'empty'
            choices = [('a', 'Choice A'), ('b', 'Choice B')]

        converter = DocumentFieldConverter()

        result = converter.convert(DocumentFieldMock())

        fields.SelectField.assert_called_once_with(
            label='test field',
            validators=[],
            default='empty',
            choices=[('a', 'Choice A'), ('b', 'Choice B')]
        )

        self.assertEqual('select-field', result)

    def test_convert_return_none(self):
        """
        Test the situation where ``convert`` returns ``None``.

        This happens when the field is not convertable to a WTForms field.

        Tests :py:meth:`.DocumentFieldConverter.convert`.
        """
        class DocumentFieldMock(object):
            name = 'test field'
            required = False
            default = ''
            choices = []

        converter = DocumentFieldConverter()
        result = converter.convert(DocumentFieldMock())
        self.assertEqual(None, result)

    @patch('wtfmongoengine.forms.validators')
    def test_common_string_kwargs(self, validators):
        """
        Test setting common string arguments.

        Tests :py:meth:`.DocumentFieldConverter.set_common_string_kwargs`.
        """
        validators.Length.return_value = 'length-validator'
        validators.Regexp.return_value = 'regexp-validator'

        class DocumentFieldMock(object):
            max_length = 10
            min_length = 5
            regex = 'my-regex'

        kwargs = {'foo': 'bar', 'validators': ['test']}

        converter = DocumentFieldConverter()
        converter.set_common_string_kwargs(DocumentFieldMock(), kwargs)

        self.assertEqual({
            'foo': 'bar',
            'validators': ['test', 'length-validator', 'regexp-validator'],
        }, kwargs)
        validators.Length.assert_called_once_with(max=10, min=5)
        validators.Regexp.assert_called_once_with(regex='my-regex')

    @patch('wtfmongoengine.forms.validators')
    def test_common_string_kwargs_max_length_min_one(self, validators):
        """
        Test that when there is no ``max_length``, it is set to ``-1``.

        Tests :py:meth:`.DocumentFieldConverter.set_common_string_kwargs`.
        """
        document_field = Mock()
        document_field.max_length = None
        document_field.min_length = 10

        kwargs = {'validators': []}

        converter = DocumentFieldConverter()
        converter.set_common_string_kwargs(document_field, kwargs)

        validators.Length.assert_called_once_with(max=-1, min=10)

    @patch('wtfmongoengine.forms.validators')
    def test_common_string_kwargs_min_length_min_one(self, validators):
        """
        Test that when there is no ``min_length``, it is set to ``-1``.

        Tests :py:meth:`.DocumentFieldConverter.set_common_string_kwargs`.
        """
        document_field = Mock()
        document_field.max_length = 10
        document_field.min_length = None

        kwargs = {'validators': []}

        converter = DocumentFieldConverter()
        converter.set_common_string_kwargs(document_field, kwargs)

        validators.Length.assert_called_once_with(max=10, min=-1)

    @patch('wtfmongoengine.forms.fields')
    def test_from_stringfield(self, fields):
        """
        Test :py:meth:`.DocumentFieldConverter.from_stringfield`.
        """
        fields.TextField.return_value = 'text-field'
        document_field = Mock()

        converter = DocumentFieldConverter()
        converter.set_common_string_kwargs = Mock()
        result = converter.from_stringfield(document_field, foo='bar')

        converter.set_common_string_kwargs.assert_called_once_with(
            document_field, {'foo': 'bar'})
        fields.TextField.assert_called_once_with(foo='bar')
        self.assertEqual('text-field', result)

    @patch('wtfmongoengine.forms.validators')
    @patch('wtfmongoengine.forms.fields')
    def test_from_urlfield(self, fields, validators):
        """
        Test :py:meth:`.DocumentFieldConverter.from_urlfield`.
        """
        validators.URL.return_value = 'url-validator'

        fields.TextField.return_value = 'text-field'
        document_field = Mock()

        converter = DocumentFieldConverter()
        converter.set_common_string_kwargs = Mock()
        result = converter.from_urlfield(document_field, validators=[])

        converter.set_common_string_kwargs.assert_called_once_with(
            document_field, {'validators': ['url-validator']}
        )
        self.assertEqual('text-field', result)

    @patch('wtfmongoengine.forms.validators')
    @patch('wtfmongoengine.forms.fields')
    def test_from_emailfield(self, fields, validators):
        """
        Test :py:meth:`.DocumentFieldConverter.from_emailfield`.
        """
        validators.Email.return_value = 'email-validator'

        fields.TextField.return_value = 'text-field'
        document_field = Mock()

        converter = DocumentFieldConverter()
        converter.set_common_string_kwargs = Mock()
        result = converter.from_emailfield(document_field, validators=[])

        converter.set_common_string_kwargs.assert_called_once_with(
            document_field, {'validators': ['email-validator']}
        )
        self.assertEqual('text-field', result)

    def test_from_intfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_intfield`.
        """
        pass

    def test_from_floatfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_floatfield`.
        """
        pass

    def test_from_decimalfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_decimalfield`.
        """
        pass
