# coding: utf-8

def fast_iter(context, func, args=[], kwargs={}):
    # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    # Author: Liza Daly
    for event, elem in context:
        func(elem, *args, **kwargs)
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context