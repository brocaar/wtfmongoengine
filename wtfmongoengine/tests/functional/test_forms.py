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
                help_text='Fill in a string',
            )

            url_field = fields.URLField(
                verbose_name='An URL',
                help_text='Fill in an URL',
            )

            email_field = fields.EmailField(
                verbose_name='An e-mail address',
                regex=r'.*',
                max_length=101,
                min_length=11,
                help_text='Fill in an e-mail address',
            )

            int_field = fields.IntField(
                verbose_name='An int',
                min_value=1,
                max_value=102,
                help_text='Fill in an int',
            )

            float_field = fields.FloatField(
                verbose_name='A float',
                min_value=2,
                max_value=103,
                help_text='Fill in a float',
            )

        class TestForm(DocumentForm):
            class Meta:
                document = TestDocument

        self.test_form = TestForm

    def test_stringfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_stringfield`.
        """
        field = self.test_form.string_field

        self.assertEqual(field.field_class, wtfields.TextField)
        self.assertEqual('A string', field.kwargs['label'])
        self.assertEqual('Fill in a string', field.kwargs['description'])
        self.assertIsInstance(field.kwargs['validators'][0], validators.Length)
        self.assertIsInstance(field.kwargs['validators'][1], validators.Regexp)
        self.assertEqual(100, field.kwargs['validators'][0].max)
        self.assertEqual(10, field.kwargs['validators'][0].min)
        self.assertEqual(r'[\w]+', field.kwargs['validators'][1].regex.pattern)

    def test_urlfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_urlfield`.
        """
        field = self.test_form.url_field

        self.assertEqual(field.field_class, wtfields.TextField)
        self.assertEqual('An URL', field.kwargs['label'])
        self.assertEqual('Fill in an URL', field.kwargs['description'])
        self.assertIsInstance(field.kwargs['validators'][0], validators.URL)

    def test_emailfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_emailfield`.
        """
        field = self.test_form.email_field

        self.assertEqual(field.field_class, wtfields.TextField)
        self.assertEqual('An e-mail address', field.kwargs['label'])
        self.assertEqual(
            'Fill in an e-mail address', field.kwargs['description'])
        self.assertIsInstance(field.kwargs['validators'][0], validators.Email)
        self.assertIsInstance(field.kwargs['validators'][1], validators.Length)
        self.assertIsInstance(field.kwargs['validators'][2], validators.Regexp)
        self.assertEqual(101, field.kwargs['validators'][1].max)
        self.assertEqual(11, field.kwargs['validators'][1].min)
        self.assertEqual(r'.*', field.kwargs['validators'][2].regex.pattern)

    def test_intfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_intfield`.
        """
        field = self.test_form.int_field

        self.assertEqual(field.field_class, wtfields.IntegerField)
        self.assertEqual('An int', field.kwargs['label'])
        self.assertEqual('Fill in an int', field.kwargs['description'])
        self.assertIsInstance(
            field.kwargs['validators'][0], validators.NumberRange)
        self.assertEqual(1, field.kwargs['validators'][0].min)
        self.assertEqual(102, field.kwargs['validators'][0].max)

    def test_floatfield(self):
        """
        Test :py:meth:`.DocumentFieldConverter.from_floatfield`.
        """
        field = self.test_form.float_field

        self.assertEqual(field.field_class, wtfields.FloatField)
        self.assertEqual('A float', field.kwargs['label'])
        self.assertEqual('Fill in a float', field.kwargs['description'])
        self.assertIsInstance(
            field.kwargs['validators'][0], validators.NumberRange)
        self.assertEqual(2, field.kwargs['validators'][0].min)
        self.assertEqual(103, field.kwargs['validators'][0].max)
