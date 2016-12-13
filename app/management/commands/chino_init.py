from chino.api import ChinoAPIClient

from django.conf import settings
from django.core.management.base import BaseCommand

from backend import chino_data

class Command(BaseCommand):

    def _process_fields(self, fields):
        return [dict(name=a, type=t, indexed=i)
                for a, t, i, d in fields]

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', dest='reset', default=False,
                            help="Resets everything...")
        parser.add_argument('--softreset', action='store_true', dest='softreset', default=False,
                            help="Resets users and relateds, keeps schemas...")

    def handle(self, **options):
        _chino = ChinoAPIClient(customer_id=settings.CHINO_ID,
                            customer_key=settings.CHINO_KEY,
                            url=settings.CHINO_URL)

        if options['softreset']:
            repos = _chino.repositories.list()
            for r in repos.repositories:
                schemas = _chino.schemas.list(r._id)
                for schema in schemas.schemas:
                    for d in _chino.documents.list(schema._id).documents:
                        _chino.documents.delete(d.document_id, force=True)

            uschemas = _chino.user_schemas.list()
            for schema in uschemas.user_schemas:
                for u in _chino.users.list(schema._id).users:
                    _chino.users.delete(u._id, force=True)

        elif options['reset']:

            repos = _chino.repositories.list()
            for r in repos.repositories:
                print r, r._id
                schemas = _chino.schemas.list(r._id)
                for schema in schemas.schemas:
                    _chino.schemas.delete(schema._id, force=True)
                _chino.repositories.delete(r._id, force=True)

            uschemas = _chino.user_schemas.list()
            for schema in uschemas.user_schemas:
                for u in _chino.users.list(schema._id).users:
                    _chino.users.delete(u._id, force=True)
                _chino.user_schemas.delete(schema._id, force=True)
            print "Chino users, user_schema and schemas have been wiped out"
        else:
            schema = _chino.user_schemas.create('blue2_users',
                                                self._process_fields(chino_data.USER_FIELDS))


            repo = _chino.repositories.create('blue2')
            pschema = _chino.schemas.create(repo._id,
                                            'relateds',
                                            self._process_fields(chino_data.RELATED_FIELDS))

            print "#" * 80
            print "## PLEASE COPY THE FOLLOWING IN YOUR SETTINGS:"
            print "CHINO_USERS_SCHEMA = '" + schema._id + "'"
            print "CHINO_REPOSITORY = '" + repo._id + "'"
            print "CHINO_RELATEDS_SCHEMA = '" + pschema._id + "'"
            print "#" * 80
    pass
