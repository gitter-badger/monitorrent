from mock import Mock
from sqlalchemy import MetaData, Table, Column, String, Integer, DateTime
from monitorrent.db import upgrade, DBSession, MigrationContext, MonitorrentOperations
from monitorrent.tests import DbTestCase


class DbTest(DbTestCase):
    def test_upgrade_dict(self):
        upgrade_func = Mock(side_effect=Exception)
        upgrade([upgrade_func])

        self.assertEqual(1, upgrade_func.call_count)

    def test_monitorrent_operations_create_table(self):
        with DBSession() as db:
            migration_context = MigrationContext.configure(db)
            monitorrent_operations = MonitorrentOperations(db, migration_context)

            monitorrent_operations.create_table(
                'account',
                Column('id', Integer, primary_key=True),
                Column('name', String, nullable=False),
                Column('description', String),
                Column('timestamp', DateTime)
            )

            db.rollback()

    def test_monitorrent_operations_create_table_2(self):
        with DBSession() as db:
            migration_context = MigrationContext.configure(db)
            monitorrent_operations = MonitorrentOperations(db, migration_context)

            m = MetaData(self.engine)
            table = Table('account', m,
                          Column('id', Integer, primary_key=True),
                          Column('name', String, nullable=False),
                          Column('description', String),
                          Column('timestamp', DateTime))

            monitorrent_operations.create_table(table,
                                                Column('new_column', Integer))

            db.rollback()
