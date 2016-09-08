# -*- coding: utf-8 -*-

import pytest


def pytest_addoption(parser):
    group = parser.getgroup('dolphin')
    group.addoption(
        '--foo',
        action='store',
        dest='dest_foo',
        default='2016',
        help='Set the value for the fixture "bar".'
    )

    parser.addini('HELLO', 'Dummy pytest.ini setting')


@pytest.fixture
def bar(request):
    return request.config.option.dest_foo


@pytest.yield_fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Fixture that will clean up remaining connections, that might be hanging
    from threads or external processes. Extending pytest_django.django_db_setup
    """

    yield

    with django_db_blocker.unblock():
        from django.db import connections

        conn = connections['default']
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM pg_stat_activity;""")
        print('current connections')
        for r in cursor.fetchall():
            print(r)

        terminate_sql = """
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '%s'
                AND pid <> pg_backend_pid();
        """ % conn.settings_dict['NAME']
        print 'Terminate SQL: ', terminate_sql
        cursor.execute(terminate_sql)
