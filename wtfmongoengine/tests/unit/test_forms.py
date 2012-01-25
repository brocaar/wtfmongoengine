from unittest import TestCase

from mock import Mock, patch

from wtfmongoengine.forms import DocumentFormMetaClassBase


class DocumentFormMetaClassBaseTestCase(TestCase):
    """
    Tests :py:class:`.DocumentFormMetaClassBase`.
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

        Test :py:meth:`.DocumentFormMetaClassBase.model_fields`.

        """
        converter = Mock()
        converter.convert.side_effect = lambda x: x()
        DocumentFieldConverter.return_value = converter

        result = DocumentFormMetaClassBase.model_fields(self.document)
        self.assertEqual({
            'title': 'title-value',
            'body': 'body-value',
            'author': 'author-value',
            'timestamp': 'timestamp-value',
        }, result)
