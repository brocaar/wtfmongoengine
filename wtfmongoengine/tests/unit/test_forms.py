from unittest2 import TestCase

from mock import Mock, patch

from wtfmongoengine.forms import (
    DocumentFormMetaClassBase, DocumentFieldConverter)


class DocumentFormMetaClassBaseTestCase(TestCase):
    """
    Test :py:class:`.DocumentFormMetaClassBase`.
    """
    @patch('wtfmongoengine.forms.DocumentFieldConverter')
    def test___new__(self, DocumentFieldConverter):
        """
        Test that ``__new__`` is creating the new class properly.
        """
        converter = Mock()
        converter.fields = {
            'field_a': 'a-value',
            'field_b': 'b-value'
        }
        DocumentFieldConverter.return_value = converter

        class TestClass(object):
            __metaclass__ = DocumentFormMetaClassBase

            class Meta:
                fields = ('title', 'body',)
                exclude = ('author', 'timestamp',)
                document_class = 'a-document'

        DocumentFieldConverter.assert_called_once_with(
            'a-document',
            ('title', 'body',),
            ('author', 'timestamp',),
        )
        self.assertEqual('a-value', TestClass.field_a)
        self.assertEqual('b-value', TestClass.field_b)


class DocumentFieldConverterTestCase(TestCase):
    """
    Test :py:class:`.DocumentFieldConverter`.
    """
    def setUp(self):
        self.fields = {
            'title': Mock(return_value='title-value'),
            'body': Mock(return_value='body-value'),
            'author': Mock(return_value='author-value'),
            'timestamp': Mock(return_value='timestamp-value'),
        }

        self.document_class = Mock()
        self.document_class._fields = self.fields

        self.convert = Mock()
        self.convert.side_effect = lambda x: x()

    def test___init__(self):
        """
        Test ``__init__`` of :py:class:`.DocumentFieldConverter`.
        """
        converter = DocumentFieldConverter(self.document_class)

        self.assertEqual(self.document_class, converter.document_class)
        self.assertEqual(None, converter.only_fields)
        self.assertEqual(None, converter.exclude_fields)

    def test__init__with_fields_exclude(self):
        """
        Test ``__init__`` with extra ``fields`` and ``exclude`` arguments.
        """
        converter = DocumentFieldConverter(
            self.document_class, fields='fields', exclude='exclude')

        self.assertEqual(self.document_class, converter.document_class)
        self.assertEqual('fields', converter.only_fields)
        self.assertEqual('exclude', converter.exclude_fields)

    def test_fields(self):
        """
        Test :py:meth:`.DocumentFieldConverter.fields`.
        """
        converter = DocumentFieldConverter(self.document_class)
        converter.convert = self.convert

        self.assertEqual({
            'title': 'title-value',
            'body': 'body-value',
            'author': 'author-value',
            'timestamp': 'timestamp-value',
        }, converter.fields)

    def test_fields_only_fields(self):
        """
        Test :py:meth:`.DocumentFieldConverter.fields` with only fields.
        """
        converter = DocumentFieldConverter(
            self.document_class,
            fields=['title', 'author']
        )
        converter.convert = self.convert

        self.assertEqual({
            'title': 'title-value',
            'author': 'author-value',
        }, converter.fields)

    def test_fields_exclude_fields(self):
        """
        Test :py:meth:`.DocumentFieldConverter.fields` with excluded fields.
        """
        converter = DocumentFieldConverter(
            self.document_class,
            exclude=['body', 'author']
        )
        converter.convert = self.convert

        self.assertEqual({
            'title': 'title-value',
            'timestamp': 'timestamp-value',
        }, converter.fields)

    @patch('wtfmongoengine.forms.validators')
    def test_convert(self, validators):
        """
        Test ``convert`` without choices.

        Tests :py:meth:`.DocumentFieldConverter.convert`.
        """
        validators.Required.return_value = 'required'

        class DocumentFieldMock(object):
            verbose_name = 'test field'
            required = True
            default = 'empty'
            choices = None
            help_text = 'This is a field for testing purpose'

        document_field = DocumentFieldMock()

        converter = DocumentFieldConverter(Mock())
        converter.from_documentfieldmock = Mock(return_value='wtfield')

        result = converter.convert(document_field)

        converter.from_documentfieldmock.assert_called_once_with(
            document_field,
            label='test field',
            validators=['required'],
            default='empty',
            description='This is a field for testing purpose'
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
            verbose_name = 'test field'
            required = False
            default = 'empty'
            choices = [('a', 'Choice A'), ('b', 'Choice B')]
            help_text = 'Make your choice'

        converter = DocumentFieldConverter(Mock())

        result = converter.convert(DocumentFieldMock())

        fields.SelectField.assert_called_once_with(
            label='test field',
            validators=[],
            default='empty',
            choices=[('a', 'Choice A'), ('b', 'Choice B')],
            description='Make your choice'
        )

        self.assertEqual('select-field', result)

    def test_convert_return_none(self):
        """
        Test the situation where ``convert`` returns ``None``.

        This happens when the field is not convertable to a WTForms field.

        Tests :py:meth:`.DocumentFieldConverter.convert`.
        """
        class DocumentFieldMock(object):
            verbose_name = 'test field'
            required = False
            default = ''
            choices = []
            help_text = ''

        converter = DocumentFieldConverter(Mock())
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

        converter = DocumentFieldConverter(Mock())
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

        converter = DocumentFieldConverter(Mock())
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

        converter = DocumentFieldConverter(Mock())
        converter.set_common_string_kwargs(document_field, kwargs)

        validators.Length.assert_called_once_with(max=10, min=-1)

    @patch('wtfmongoengine.forms.validators')
    def test_common_number_kwargs_no_max(self, validators):
        """
        Test :py:meth:`.DocumentFieldConverter.set_common_number_kwargs`.
        """
        validators.NumberRange.return_value = 'number-range-validator'

        document_field = Mock()
        document_field.max_value = 20
        document_field.min_value = 10

        kwargs = {'validators': []}

        converter = DocumentFieldConverter(Mock(Mock()))
        converter.set_common_number_kwargs(document_field, kwargs)

        validators.NumberRange.assert_called_once_with(max=20, min=10)
        self.assertEqual({'validators': ['number-range-validator']}, kwargs)

    @patch('wtfmongoengine.forms.fields')
    def test_from_stringfield(self, fields):
        """
        Test :py:meth:`.DocumentFieldConverter.from_stringfield`.
        """
        fields.TextField.return_value = 'text-field'
        document_field = Mock()

        converter = DocumentFieldConverter(Mock())
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

        converter = DocumentFieldConverter(Mock())
        converter.set_common_string_kwargs = Mock()
        result = converter.from_urlfield(document_field, validators=[])

        converter.set_common_string_kwargs.assert_called_once_with(
            document_field, {'validators': ['url-validator']})
        fields.TextField.assert_called_once_with(validators=['url-validator'])
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

        converter = DocumentFieldConverter(Mock())
        converter.set_common_string_kwargs = Mock()
        result = converter.from_emailfield(document_field, validators=[])

        converter.set_common_string_kwargs.assert_called_once_with(
            document_field, {'validators': ['email-validator']})
        fields.TextField.assert_called_once_with(
            validators=['email-validator'])
        self.assertEqual('text-field', result)

    @patch('wtfmongoengine.forms.fields')
    def test_from_intfield(self, fields):
        """
        Test :py:meth:`.DocumentFieldConverter.from_intfield`.
        """
        fields.IntegerField.return_value = 'integer-field'
        document_field = Mock()

        converter = DocumentFieldConverter(Mock())
        converter.set_common_number_kwargs = Mock()
        result = converter.from_intfield(document_field, validators=[])

        converter.set_common_number_kwargs.assert_called_once_with(
            document_field, {'validators': []})
        fields.IntegerField.assert_called_once_with(validators=[])
        self.assertEqual('integer-field', result)

    @patch('wtfmongoengine.forms.fields')
    def test_from_floatfield(self, fields):
        """
        Test :py:meth:`.DocumentFieldConverter.from_floatfield`.
        """
        fields.FloatField.return_value = 'float-field'
        document_field = Mock()

        converter = DocumentFieldConverter(Mock())
        converter.set_common_number_kwargs = Mock()
        result = converter.from_floatfield(document_field, validators=[])

        converter.set_common_number_kwargs.assert_called_once_with(
            document_field, {'validators': []})
        fields.FloatField.assert_called_once_with(validators=[])
        self.assertEqual('float-field', result)

    @patch('wtfmongoengine.forms.fields')
    def test_from_decimalfield(self, fields):
        """
        Test :py:meth:`.DocumentFieldConverter.from_decimalfield`.
        """
        fields.DecimalField.return_value = 'decimal-field'
        document_field = Mock()

        converter = DocumentFieldConverter(Mock())
        converter.set_common_number_kwargs = Mock()
        result = converter.from_decimalfield(document_field, validators=[])

        converter.set_common_number_kwargs.assert_called_once_with(
            document_field, {'validators': []})
        fields.DecimalField.assert_called_once_with(validators=[])
        self.assertEqual('decimal-field', result)

    @patch('wtfmongoengine.forms.fields')
    def test_from_booleanfield(self, fields):
        """
        Test :py:meth:`.DocumentFieldConverter.from_booleanfield`.
        """
        fields.BooleanField.return_value = 'boolean-field'
        document_field = Mock()

        converter = DocumentFieldConverter(Mock())
        result = converter.from_booleanfield(document_field, validators=[])

        fields.BooleanField.assert_called_once_with(validators=[])
        self.assertEqual('boolean-field', result)

    @patch('wtfmongoengine.forms.fields')
    def test_from_datetimefield(self, fields):
        """
        Test :py:meth:`.DocumentFieldConverter.from_datetimefield`.
        """
        fields.DateTimeField.return_value = 'datetime-field'
        document_field = Mock()

        converter = DocumentFieldConverter(Mock())
        result = converter.from_datetimefield(document_field, validators=[])

        fields.DateTimeField.assert_called_once_with(validators=[])
        self.assertEqual('datetime-field', result)

    def test_from_complexdatetimefield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_complexdatetimefield`.
        """
        converter = DocumentFieldConverter(Mock())
        self.assertRaises(
            NotImplementedError, converter.from_complexdatetimefield, Mock())

    def test_from_listfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_listfield`.
        """
        converter = DocumentFieldConverter(Mock())
        self.assertRaises(
            NotImplementedError, converter.from_listfield, Mock())

    def test_from_sortedlistfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_sortedlistfield`.
        """
        converter = DocumentFieldConverter(Mock())
        self.assertRaises(
            NotImplementedError, converter.from_sortedlistfield, Mock())

    def test_from_dictfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_dictfield`.
        """
        converter = DocumentFieldConverter(Mock())
        self.assertRaises(
            NotImplementedError, converter.from_dictfield, Mock())

    def test_from_mapfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_mapfield`.
        """
        converter = DocumentFieldConverter(Mock())
        self.assertRaises(
            NotImplementedError, converter.from_mapfield, Mock())

    def test_from_objectidfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_objectidfield`.

        This tests that this method returns ``None``.

        """
        converter = DocumentFieldConverter(Mock())
        self.assertEqual(None, converter.from_objectidfield(Mock()))

    def test_from_referencefield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_referencefield`.
        """
        converter = DocumentFieldConverter(Mock())
        self.assertRaises(
            NotImplementedError, converter.from_referencefield, Mock())

    def test_from_genericreferencefield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_genericreferencefield`.
        """
        converter = DocumentFieldConverter(Mock())
        self.assertRaises(
            NotImplementedError, converter.from_genericreferencefield, Mock())

    def test_from_embeddeddocumentfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_embeddeddocumentfield`.
        """
        converter = DocumentFieldConverter(Mock())
        self.assertRaises(
            NotImplementedError, converter.from_embeddeddocumentfield, Mock())

    def test_from_genericembeddeddocumentfield(self):
        """
        Test :meth:`.DocumentFieldConverter.from_genericembeddeddocumentfield`.
        """
        converter = DocumentFieldConverter(Mock())
        self.assertRaises(
            NotImplementedError,
            converter.from_genericembeddeddocumentfield,
            Mock()
        )

    def test_from_filefield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_filefield`.
        """
        converter = DocumentFieldConverter(Mock())
        self.assertRaises(
            NotImplementedError, converter.from_filefield, Mock())

    def test_from_binaryfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_binaryfield`.
        """
        converter = DocumentFieldConverter(Mock())
        self.assertRaises(
            NotImplementedError, converter.from_binaryfield, Mock())

    def test_from_geopointfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_geopointfield`.
        """
        converter = DocumentFieldConverter(Mock())
        self.assertRaises(
            NotImplementedError, converter.from_geopointfield, Mock())

    def test_from_sequencefield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_sequencefield`.
        """
        converter = DocumentFieldConverter(Mock())
        self.assertRaises(
            NotImplementedError, converter.from_sequencefield, Mock())
