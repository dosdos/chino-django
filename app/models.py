from chino.api import ChinoAPIClient
from chino.exceptions import CallError

from django.conf import settings
from django.contrib.auth.models import User, AbstractBaseUser, BaseUserManager
from django.contrib.auth.backends import RemoteUserBackend
from django.db import models

from backend import utils, chino_data

def get_chino_client():
    chino = ChinoAPIClient(customer_id=settings.CHINO_ID,
                           customer_key=settings.CHINO_KEY,
                           url=settings.CHINO_URL,
                           client_id=settings.CHINO_APPLICATION_ID,
                           client_secret=settings.CHINO_APPLICATION_SECRET)
    return chino


class ChinoUserManager(BaseUserManager):

    def create_user(self, chino_id, password):
        """

        we expect a chino_id here, but the fact is that we pass a
        username. The chino_id will be assigned by chino itself.
        This is only because django expects kwargs.

        """

        return self._create(chino_id, password, False)


    def create_superuser(self, chino_id, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """

        return self._create(chino_id, password, True)

    def _create(self, username, password, is_super=False):

        if chino_data.CHINO_DEBUG:
            user = self.model(chino_id=chino_data.get_random_chino_id(),
                                is_superuser=is_super,
                                is_staff=is_super)

            user.save()
            return user


        _chino = get_chino_client()

        attrs = dict((a, chino_data.field_to_json(t, d()))
                     for a, t, i, d in chino_data.USER_FIELDS)

        chino_user = _chino.users.create(settings.CHINO_USERS_SCHEMA,
                                         username=username,
                                         password=password,
                                         attributes=attrs)

        user = self.model(chino_id=chino_user.user_id,
                          is_superuser=is_super,
                          is_staff=is_super)

        user.save()

        return user

    pass


class ChinoUser(AbstractBaseUser):

    chino_id = models.CharField('username', max_length=128, unique=True)
    is_superuser = models.BooleanField('is_superuser', default=False)
    is_staff = models.BooleanField('is_superuser', default=False)
    is_active = models.BooleanField('is_active', default=True)

    objects = ChinoUserManager()

    USERNAME_FIELD = 'chino_id'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.chino_id

    def get_short_name(self):
        return self.chino_id

    def __unicode__(self):
        return self.chino_id

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    pass


class ChinoRemoteUserBackend(RemoteUserBackend):
    # Create a User object if not already in the database? Absolutely not.
    create_unknown_user = False

    def authenticate(self, **credentials):
        """Authenticates using chino"""

        if chino_data.CHINO_DEBUG:
            return ChinoUser.objects.get(pk=chino_data.CHINO_DEBUG_USER_ID)

        _chino = get_chino_client()

        try:
            _chino.users.login(credentials['username'],
                               credentials['password'])
        except CallError as e:
            # Unable to authenticate..
            print "Unable to authenticate", e
            print e
            return None

        remote_user = _chino.users.current()

        return ChinoUser.objects.get(chino_id=remote_user.user_id)

    pass
