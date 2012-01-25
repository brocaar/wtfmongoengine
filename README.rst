WTForms-Mongoengine
===================

**WTForms-Mongoengine** creates WTForms ``Form`` classes from Mongoengine
``Document`` objects. Example::

    from mongoengine import Document
    from wtfmongoengine.forms import DocumentForm

    class User(Document):
        email = StringField(required=True)
        first_name = StringField(max_length=50)
        last_name = StringField(max_length=50)

    class UserForm(DocumentForm):
        class Meta:
            document = User

            # In case you want to exclude ``email`` from the form
            # exclude = ('email',)

            # In case you only want to include ``first_name`` in the form
            # fields = ('first_name',)


Changelog
---------

0.1 (in development)
~~~~~~~~~~~~~~~~~~~~

* Initial release.

Links
-----

    * http://wtforms.simplecodes.com/
    * http://mongoengine.org/
