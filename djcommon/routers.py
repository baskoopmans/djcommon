# coding: utf-8

class ModelDatabaseRouter(object):
    """
    A router to control all database operations on models for different databases.

    In case an model object's Meta is provided with db_name, the router
    will take that database for all its transactions.

    Settings example:

    class Meta:
        db_name = 'foo'
        db_table = 'bar' #django native

    """

    def _get_database_name(self, model):
        return getattr(model._meta, 'db_name', 'default')

    def db_for_read(self, model, **hints):
        "Point all read operations to the specific database."
        return self._get_database_name(model)

    def db_for_write(self, model, **hints):
        "Point all write operations to the specific database."
        return self._get_database_name(model)

    def allow_relation(self, model_a, model_b, **hints):
        "Allow any relation between apps that use the same database."
        db_model_a = self._get_database_name(model_a)
        db_model_b = self._get_database_name(model_b)
        if db_model_a and db_model_b:
            if db_model_a == db_model_b:
                return True
            else:
                return False
        return None

    def allow_syncdb(self, db, model):
        "Make sure that apps only appear in the related database."
        if self._get_database_name(model) == db:
            return True
        return None
