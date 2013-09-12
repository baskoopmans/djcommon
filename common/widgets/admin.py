# coding: utf-8

from django.contrib.admin.widgets import ManyToManyRawIdWidget
from django.utils.html import escape


class VerboseManyToManyRawIdWidget(ManyToManyRawIdWidget):
    """
    A Widget for displaying ManyToMany ids in the "raw_id" interface rather than
    in a <select multiple> box. 
    Display user-friendly value like the ForeignKeyRawId widget
    """
    def __init__(self, rel, attrs=None):
        self._rel = rel
        super(VerboseManyToManyRawIdWidget, self).__init__(rel, attrs)

    def label_for_value(self, value):
        values = []
        key = self.rel.get_related_field().name
        for v in value.split(','):
            try:
                obj = self.rel.to._default_manager.using(self.db).get(**{key: v})
                # manage unicode error, no HTML
                values.append(u"%s - %s" % (v, escape(obj)))
            except self.rel.to.DoesNotExist:
                values.append(u'???')
        return u'&nbsp;<strong>%s</strong>' % u',&nbsp;'.join(values)