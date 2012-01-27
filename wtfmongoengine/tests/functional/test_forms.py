import unittest

from mongoengine.document import Document
from mongoengine import fields
from wtforms import validators, fields as wtfields

from wtfmongoengine.forms import DocumentForm, DocumentFieldConverter


class DocumentFormTestCase(unittest.TestCase):
    """
    Non nested tests :py:class:`wtfmongoengine.forms.DocumentForm`.
    """
    def setUp(self):
        class TestDocument(Document):
            string_field = fields.StringField(
                regex=r'[\w]+',
                max_length=100,
                min_length=10,
            )

            url_field = fields.URLField()

            email_field = fields.EmailField(
                regex=r'.*',
                max_length=101,
                min_length=11,
            )

        class TestForm(DocumentForm):
            class Meta:
                document = TestDocument

        self.test_form = TestForm

    def test_stringfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_stringfield`.
        """
        self.assertEqual(
            self.test_form.string_field.field_class,
            wtfields.TextField
        )

        self.assertIsInstance(
            self.test_form.string_field.kwargs['validators'][0],
            validators.Length
        )

        self.assertIsInstance(
            self.test_form.string_field.kwargs['validators'][1],
            validators.Regexp
        )

        self.assertEqual(
            100, self.test_form.string_field.kwargs['validators'][0].max)

        self.assertEqual(
            10, self.test_form.string_field.kwargs['validators'][0].min)

        self.assertEqual(
            r'[\w]+',
            self.test_form.string_field.kwargs['validators'][1].regex.pattern
        )

    def test_urlfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_urlfield`.
        """
        self.assertEqual(
            self.test_form.url_field.field_class,
            wtfields.TextField
        )

        self.assertIsInstance(
            self.test_form.url_field.kwargs['validators'][0],
            validators.URL
        )

    def test_emailfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_emailfield`.
        """
        self.assertEqual(
            self.test_form.email_field.field_class,
            wtfields.TextField
        )

        self.assertIsInstance(
            self.test_form.email_field.kwargs['validators'][0],
            validators.Email
        )

        self.assertIsInstance(
            self.test_form.email_field.kwargs['validators'][1],
            validators.Length
        )

        self.assertIsInstance(
            self.test_form.email_field.kwargs['validators'][2],
            validators.Regexp
        )

        self.assertEqual(
            101, self.test_form.email_field.kwargs['validators'][1].max)

        self.assertEqual(
            11, self.test_form.email_field.kwargs['validators'][1].min)

        self.assertEqual(
            r'.*',
            self.test_form.email_field.kwargs['validators'][2].regex.pattern
        )
