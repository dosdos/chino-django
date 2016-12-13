# A Chino.io Django integration
> ********************************************************************************
> **** This code has been made by 3rd party that developed their solution ****
> **** using chino as backend. ****
> ****  ****
> **** For this specic repository the code has been written by [mari8i](https://github.com/mari8i) ****
> **** ****
> ****  NB: This is just an example, it is NOT intended to be working code.   ****
> ********************************************************************************

Here follows a brief description of the contents of this package, file per file

This example has been created and tested using Django 1.9.11 and
Django Rest Framework 3.x

 - chino/settings.py:

   This is a narrowed example of a settings.py file in a standard
   django project. Only chino's related variables have been kept.

 - app/models.py

   A sample models.py django file that includes everything you need to
   start using django with Chino.

   The ChinoUser replaces the standard Django User class

 - app/chino_data.py

   In this file you find:

      - CHINO_DEBUG: If set to True, Chino will be completely
                     bypassed.  All users will be the same user
                     instance, so use this at you own risk.

      - CHINO_DEBUG_USER_ID: The ID of the ChinoUser that will be used
                     when CHINO_DEBUG is True.

      - USER_FIELDS: All the attributes that a User should have in
                     your web app. It is a list of tuples:
                     <name, type, indexed, default_value>

                     Note that the default_value is a function

      - RELATED_FIELDS: An example for another table in chino.

 - app/chino_model.py

   This is an interface for Chino. The User class provides some
   functionalities such as:

   - find_by_username
   - find_by_email
   - create
   - update
   - set_password
   - check_password
   - fetch
   - fetch_many

   see views.py for an example

 - app/serializers.py

   The Django Rest Framework serializer used in views.py

 - app/views.py

   A Sample view that puts all the above together to provide a sample
   get/post User API

 - app/management/commands/chino_init.py

   A Django command to initialize and/or reset the Chino repository,
   accordingly to the values in chino_data.
