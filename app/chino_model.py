import json
from django.conf import settings
import random
import string
import datetime

from backend import models, chino_data
from chino.exceptions import CallError

def get_all_chino_users(chino):
    all_users = []

    obj = chino.users.list(settings.CHINO_USERS_SCHEMA)

    all_users.extend(obj.users)

    total_users = obj.paging.total_count
    current = obj.paging.count

    while current < total_users:
        obj = chino.users.list(settings.CHINO_USERS_SCHEMA,
                               offset=current)
        all_users.extend(obj.users)
        current += obj.paging.count

    return all_users


class User(object):

    def __init__(self, id=-1, type=models.PATIENT, username="", first_name="", last_name="",
                 email="", sex=0, fiscal_code="", birth_date=chino_data.DATE_NULL,
                 date_joined=chino_data.DATETIME_NULL,
                 image="", img_square="", img_large="", img_thumbnail_square="", img_thumbnail="",
                 address_type_1=0, address_1="", address_type_2=1, address_2="",
                 phone_type_1=0, phone_1="", phone_type_2=1, phone_2="",
                 has_powers=True, therapist=None, language=models.LANGUAGE_IT,
                 scholarity=0):

        self.id = id
        self.type = type
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.sex = sex
        self.fiscal_code = fiscal_code
        self.birth_date = birth_date
        self.date_joined = date_joined
        self.image = image
        self.img_square = img_square
        self.img_large = img_large
        self.img_thumbnail_square = img_thumbnail_square
        self.img_thumbnail = img_thumbnail
        self.address_type_1 = address_type_1
        self.address_1 = address_1
        self.address_type_2 = address_type_2
        self.address_2 = address_2
        self.phone_type_1 = phone_type_1
        self.phone_1 = phone_1
        self.phone_type_2 = phone_type_2
        self.phone_2 = phone_2
        self.language = language
        self.has_powers = has_powers
        self.therapist = therapist
        self.scholarity = scholarity
        return


    def create(self, password):
        """
        Creates the given user in the chino backend. Returns the created
        ChinoUser instance
        """


        if chino_data.CHINO_DEBUG:
            user = models.ChinoUser(chino_id=chino_data.get_random_chino_id())
            user.save()
            return user


        _chino = models.get_chino_client()

        attrs = self._get_attrs()

        chino_user = _chino.users.create(settings.CHINO_USERS_SCHEMA,
                                         username=self.username,
                                         password=password,
                                         attributes=attrs)

        user = models.ChinoUser(chino_id=chino_user.user_id)
        user.save()

        return user

    def update(self, django_user):
        """
        Syncs the given instance of User, associated with the given
        django_user, to chino
        """

        if chino_data.CHINO_DEBUG:
            # Just don't do anything
            return

        _chino = models.get_chino_client()


        data = {
            'username' : self.username,
            'attributes' : self._get_attrs(),
            }

        chino_user = _chino.users.update(django_user.chino_id, **data)

        return

    def set_password(self, django_user, password):

        if chino_data.CHINO_DEBUG:
            # Just don't do anything
            return

        _chino = models.get_chino_client()

        # TODO: There will soon be a patch feature

        data = {
            'password' : password,
            }

        _chino.users.partial_update(django_user.chino_id, **data)

        return

    def _get_attrs(self):
        attrs = dict((a, chino_data.field_to_json(t, getattr(self, a)))
                     for a, t, i, d in chino_data.USER_FIELDS)
        #print "ATTRS", attrs
        return attrs

    @staticmethod
    def check_password(username, password):

        if chino_data.CHINO_DEBUG:
            # Just don't do anything
            return True

        # TODO: There will soon be a search/filter feature

        _chino = models.get_chino_client()

        try:
            _chino.users.login(username, password)
        except CallError:
            # Unable to authenticate..
            return False

        return True

    @staticmethod
    def _copy_remote(local, remote, indepth=True):
        user = User(id=local.id, username=remote.username)

        for attr, attrtype, _, _ in chino_data.USER_FIELDS:
            setattr(user, attr,
                    chino_data.field_from_json(attrtype,
                                               getattr(remote.attributes, attr)))

        user.type = -1

        try:
            patient = models.Patient.objects.get(user=local)
            user.type = models.PATIENT

            user.has_powers = patient.has_powers

            if indepth:
                if patient.therapist:
                    user.therapist = User.fetch(patient.therapist,
                                                indepth=False)
                    pass
                pass

        except models.Patient.DoesNotExist:
            # For the moment, we don't have attributes to be copied..
            models.Therapist.objects.get(user=local)
            user.type = models.THERAPIST
            pass

        return user

    @staticmethod
    def _create_debug_user():
        # Just don't do anything
        return User(id=chino_data.CHINO_DEBUG_USER_ID,
                    first_name="Chino",
                    last_name="Debug",
                    birth_date=datetime.date(1986, 1, 1),
                    date_joined=datetime.datetime(1986, 1, 1, 15, 0, 0),
                    username="dummy",
                    email="mariotti.devel@gmail.com",
                    type=chino_data.CHINO_DEBUG_USER_TYPE)


    @staticmethod
    def fetch(django_user, indepth=True):
        """
        Makes a chino call and returns a ChinoUser filled with all

        """

        if chino_data.CHINO_DEBUG:
            return User._create_debug_user()

        _chino = models.get_chino_client()

        chino_user = _chino.users.detail(django_user.chino_id)

        user = User._copy_remote(django_user, chino_user, indepth=indepth)

        return user

    @staticmethod
    def fetch_many(django_users, indepth=False):
        _chino = models.get_chino_client()

        chino_ids2user = dict((dj.chino_id, dj) for dj in django_users)
        chino_ids = [_id for _id in chino_ids2user.iterkeys()]

        chino_users = _chino.searches.users(settings.CHINO_USERS_SCHEMA,
                                            result_type="FULL_CONTENT",
                                            filters=[{"field" : "_id",
                                                      "type": "in",
                                                      "value": chino_ids}])

        return [User._copy_remote(chino_ids2user[cu.user_id], cu, indepth=indepth)
                for cu in chino_users.users]

    @staticmethod
    def username_available(username):
        """
        Checks whether the given username is taken or is available
        """

        if chino_data.CHINO_DEBUG:
            return User._create_debug_user()

        _chino = models.get_chino_client()
        exists = _chino.searches.users(settings.CHINO_USERS_SCHEMA,
                                       result_type="USERNAME_EXISTS",
                                       filters=[{"field": "username",
                                                 "type": "eq",
                                                 "value": username}])
        return not exists
        #return not any(cu.username == username
        #               for cu in get_all_chino_users(_chino))

    @staticmethod
    def email_available(email):
        """
        Checks whether the given email is taken or is available
        NB: the mail attribute requires indexing!
        """

        if chino_data.CHINO_DEBUG:
            # Just don't do anything
            return True

        _chino = models.get_chino_client()

        exists = _chino.searches.users(settings.CHINO_USERS_SCHEMA,
                                       result_type="EXISTS",
                                       filters=[{"field": "email",
                                                 "type": "eq",
                                                 "value": email}])
        return not exists

        # return not any(cu.attributes.email == email
        #                for cu in get_all_chino_users(_chino))


    @staticmethod
    def get_by_email(email):
        """
        Get chino user object by email, null if it not exist
        NB: the mail attribute requires indexing!
        """

        if chino_data.CHINO_DEBUG:
            return User._create_debug_user()

        _chino = models.get_chino_client()

        res = _chino.searches.users(settings.CHINO_USERS_SCHEMA,
                                    result_type="FULL_CONTENT",
                                    filters=[{"field": "email",
                                              "type": "eq",
                                              "value": email}])

        if res.paging.count == 1:
            return res.users[0]

        # for cu in get_all_chino_users(_chino):
        #     if cu.attributes.email == email:
        #         return cu

        return None

    @staticmethod
    def get_by_username(username):
        """
        Get chino user object by email, null if it not exist
        """

        if chino_data.CHINO_DEBUG:
            return User._create_debug_user()

        _chino = models.get_chino_client()

        res = _chino.searches.users(settings.CHINO_USERS_SCHEMA,
                                    result_type="FULL_CONTENT",
                                    filters=[{"field": "username",
                                              "type": "eq",
                                              "value": username}])

        if res.paging.count == 1:
            return res.users[0]

        # for cu in get_all_chino_users(_chino):
        #     if cu.username == username:
        #         return cu

        return None

    def __str__(self):
        return str(self._get_attrs())

    pass



class Related(object):

    def __init__(self, id=-1, patient=-1, first_name="", last_name="", email="", notes="",
                 image="", img_square="", img_large="", img_thumbnail_square="", img_thumbnail="",
                 address_type_1=0, address_1="", address_type_2=1, address_2="",
                 phone_type_1=0, phone_1="", phone_type_2=1, phone_2=""):

        self.id = id

        self.patient = patient
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.notes = notes

        self.image = image
        self.img_square = img_square
        self.img_large = img_large
        self.img_thumbnail_square = img_thumbnail_square
        self.img_thumbnail = img_thumbnail

        self.address_type_1 = address_type_1
        self.address_1 = address_1
        self.address_type_2 = address_type_2
        self.address_2 = address_2

        self.phone_type_1 = phone_type_1
        self.phone_1 = phone_1
        self.phone_type_2 = phone_type_2
        self.phone_2 = phone_2

        return

    def create(self, django_related_to):
        """
        Creates the given related in the chino backend. Returns the created
        Related instance
        """

        _chino = models.get_chino_client()

        attrs = self._get_attrs()

        chino_related = _chino.documents.create(settings.CHINO_RELATEDS_SCHEMA, attrs)

        rel = models.Related(patient=django_related_to,
                             chino_id=chino_related.document_id)
        rel.save()

        return rel


    @staticmethod
    def fetch(django_related):
        """
        Makes a chino call and returns a ChinoUser filled with all

        """
        _chino = models.get_chino_client()

        chino_related = _chino.documents.detail(django_related.chino_id)

        user = Related._copy_remote(django_related, chino_related)

        return user

    @staticmethod
    def fetch_many(django_relateds, each=None):
        # TODO: Fix me: I need improvements: A search query over chino
        # DB instead of filtering afterwards would be probably the
        # best solution

        _chino = models.get_chino_client()

        chino_ids = dict((dj.chino_id, dj)
                         for dj in django_relateds)

        res = []
        for cr in _chino.documents.list(settings.CHINO_RELATEDS_SCHEMA, full_document=True).documents:
            if cr.document_id in chino_ids:
                dj_rel = chino_ids[cr.document_id]

                related = Related._copy_remote(dj_rel, cr)


                if each: each(dj_rel, related)

                res.append(related)
                pass
            pass

        return res


    def _get_attrs(self):
        attrs = dict((a, chino_data.field_to_json(t, getattr(self, a)))
                     for a, t, i, d in chino_data.RELATED_FIELDS)
        return attrs

    @staticmethod
    def _copy_remote(local, remote):
        related = Related(id=local.id, patient=local.patient_id)

        # TODO: THIS IS REALLY BAD!!
        #_chino = models.get_chino_client()
        #remote.content = content #_chino.documents.detail(remote.document_id).content
        # END OF BAD CODE

        for attr, attrtype, _, _ in chino_data.RELATED_FIELDS:
            setattr(related, attr,
                    chino_data.field_from_json(attrtype,
                                               getattr(remote.content, attr)))

        return related

    def update(self, django_related):
        """
        Syncs the given instance of Related, associated with the given
        django_related, to chino
        """

        _chino = models.get_chino_client()

        data = {
            'content' : self._get_attrs(),
            }

        # TODO
        _chino.documents.update(django_related.chino_id, **data)

        return

    @staticmethod
    def delete(django_related):
        _chino = models.get_chino_client()

        _chino.documents.delete(django_related.chino_id, force=True)

        return


################################################################################
## SOME DEBUG METHODS.. USE THESE FROM python manage.py shell
################################################################################

def change_user_password(chino_id, password):
    m = models.ChinoUser.objects.get(chino_id=chino_id)
    c = User.fetch(m)
    c.set_password(m, password)


def list_users():
    _chino = models.get_chino_client()

    for u in get_all_chino_users(_chino):
        print u.username, u.user_id, u.attributes.first_name, u.attributes.last_name
