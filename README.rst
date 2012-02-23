WTFMongoengine
==============

**WTFMongoengine** creates WTForms ``Form`` classes from Mongoengine
``Document`` objects. Example::

    from mongoengine import document, fields
    from wtfmongoengine.forms import DocumentForm

    class User(document.Document):
        first_name = fields.StringField(
            verbose_name='First name',
            max_length=50,
            required=True,
        )
        last_name = fields.StringField(
            verbose_name='Last name',
            max_length=50,
            required=False,
        )
        email = fields.EmailField(
            verbose_name='E-mail address',
            required=True,
        )

    class UserForm(DocumentForm):
        class Meta:
            document_class = User

            # In case you only want to include ``first_name`` in the form
            # fields = ('first_name',)

            # In case you want to exclude ``email`` from the form
            # exclude = ('email',)


Changelog
---------

0.1.1
~~~~~

* Example updates.
* Fix: README.rst and LICENSE included in package.

0.1
~~~

* Initial release.


Links
-----

    * http://wtforms.simplecodes.com/
    * http://mongoengine.org/
