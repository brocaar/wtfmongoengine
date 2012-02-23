WTForms-Mongoengine
===================

**WTForms-Mongoengine** creates WTForms ``Form`` classes from Mongoengine
``Document`` objects. Example::

    from mongoengine import document, fields
    from wtfmongoengine.forms import DocumentForm

    class User(document.Document):
        email = fields.StringField(required=True)
        first_name = fields.StringField(max_length=50)
        last_name = fields.StringField(max_length=50)

    class UserForm(DocumentForm):
        class Meta:
            document_class = User

            # In case you only want to include ``first_name`` in the form
            # fields = ('first_name',)

            # In case you want to exclude ``email`` from the form
            # exclude = ('email',)


Changelog
---------

0.1 (in development)
~~~~~~~~~~~~~~~~~~~~

* Initial release.


Links
-----

    * http://wtforms.simplecodes.com/
    * http://mongoengine.org/
