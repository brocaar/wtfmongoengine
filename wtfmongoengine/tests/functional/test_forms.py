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
                verbose_name='A string',
                regex=r'[\w]+',
                max_length=100,
                min_length=10,
            )

            url_field = fields.URLField(verbose_name='An URL')

            email_field = fields.EmailField(
                verbose_name='An e-mail address',
                regex=r'.*',
                max_length=101,
                min_length=11,
            )

            int_field = fields.IntField(
                verbose_name='An int', min_value=1, max_value=102)

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

        self.assertEqual(
            'A string', self.test_form.string_field.kwargs['label'])

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

        self.assertEqual(
            'An URL', self.test_form.url_field.kwargs['label'])

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

        self.assertEqual(
            'An e-mail address', self.test_form.email_field.kwargs['label'])

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

    def test_intfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_intfield`.
        """
        self.assertEqual(
            self.test_form.int_field.field_class,
            wtfields.IntegerField
        )

        self.assertEqual(
            'An int', self.test_form.int_field.kwargs['label'])

        self.assertIsInstance(
            self.test_form.int_field.kwargs['validators'][0],
            validators.NumberRange
        )

        self.assertEqual(
            1, self.test_form.int_field.kwargs['validators'][0].min)

        self.assertEqual(
            102, self.test_form.int_field.kwargs['validators'][0].max)
