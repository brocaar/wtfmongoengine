from unittest import TestCase

from mock import Mock, patch

from wtfmongoengine.forms import DocumentFormMetaClassBase


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
