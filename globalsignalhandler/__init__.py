from threading import Thread

from django.dispatch import Signal
from django.db.models import signals

from tcms.core.models import SIG_BULK_UPDATE
from tcms.apps.testplans.models import TestPlan
from tcms.apps.testcases.models import TestCase, TestCasePlan
from tcms.apps.testruns.models import TestRun, TestCaseRun

class SignalConfig(object):
    SIG_SAVE = signals.post_save
    SIG_DELETE = signals.pre_delete
    SIG_BULK_UPDATE = SIG_BULK_UPDATE
    MODEL_ALL = 'ALL'

class SignalHandlerType(type):
    def __init__(cls, name, bases, attr):
        """
        connect signals to handlers
        """
        handling = getattr(cls, 'handling', None)
        if handling:
            cls.connect(handling)

    def connect(cls, handling):
        for model_kls, signals in handling.iteritems():
            for signal in signals:
                if model_kls == SignalConfig.MODEL_ALL:
                    signal.connect(cls.map_handler(signal))
                else:
                    signal.connect(cls.map_handler(signal), sender=model_kls)

class SignalHandlerTask(Thread):
    pass

class BaseHandler(object):
    __metaclass__ = SignalHandlerType
    async = True

    @classmethod
    def map_handler(cls, signal):
        handlers = {
                SignalConfig.SIG_SAVE: cls._save_handler,
                SignalConfig.SIG_BULK_UPDATE: cls._bulk_update_handler,
                SignalConfig.SIG_DELETE: cls._delete_handler,
                }
        return handlers.get(signal, None)

    @classmethod
    def _save_handler(cls, **kwargs):
        if kwargs['created']:
            handler = cls.create_handler
        else:
            handler = cls.update_handler
        if cls.async:
            task = SignalHandlerTask(target=handler, kwargs=kwargs)
            task.start()
        else:
            handler(kwargs=kwargs)
        pass

    @classmethod
    def _delete_handler(cls, **kwargs):
        if cls.async:
            task = SignalHandlerTask(target=cls.delete_handler, kwargs=kwargs)
            task.start()
        else:
            cls.delete_handler(kwargs=kwargs)
        pass

    @classmethod
    def _bulk_update_handler(cls, **kwargs):
        if cls.async:
            task = SignalHandlerTask(target=cls.update_handler, kwargs=kwargs)
            task.start()
        else:
            cls.update_handler(kwargs=kwargs)
        pass

    @classmethod
    def generic_handler(cls, **kwargs):
        if cls.async:
            task = SignalHandlerTask(target=cls.action, kwargs=kwargs)
            task.start()
        else:
            cls.action()

    @classmethod
    def action(self, **kwargs):
        raise NotImplementedError

class EmailHandler(BaseHandler):
    handling = {
        TestPlan: (SignalConfig.SIG_SAVE, SignalConfig.SIG_BULK_UPDATE, SignalConfig.SIG_DELETE),
        TestCase: (SignalConfig.SIG_SAVE, SignalConfig.SIG_BULK_UPDATE, SignalConfig.SIG_DELETE),
        TestCasePlan: (SignalConfig.SIG_SAVE,SignalConfig.SIG_BULK_UPDATE, SignalConfig.SIG_DELETE),
        TestRun: (SignalConfig.SIG_SAVE, SignalConfig.SIG_BULK_UPDATE, SignalConfig.SIG_DELETE),
        TestCaseRun: (SignalConfig.SIG_SAVE, SignalConfig.SIG_BULK_UPDATE, SignalConfig.SIG_DELETE),
    }

    @classmethod
    def create_handler(cls, **kwargs):
        """
        Implement notification for create operation.
        """
        print 'email notification triggered by create signal.%s:%s' %(cls, kwargs)
        pass

    @classmethod
    def update_handler(cls, **kwargs):
        """
        Implement notification for update operation.
        """
        print 'email notification triggered by update signal. %s:%s' %(cls, kwargs)
        pass

    @classmethod
    def delete_handler(cls, **kwargs):
        """
        Implement notification for delete operation.
        """
        print 'email notification triggered by delete signal. %s:%s' %(cls, kwargs)
        pass

class ChangeLogHandler(BaseHandler):
    handling = {
        SignalConfig.MODEL_ALL: (SignalConfig.SIG_SAVE, SignalConfig.SIG_BULK_UPDATE, SignalConfig.SIG_DELETE)
    }

    @classmethod
    def create_handler(cls, **kwargs):
        """
        changelog for create operation.
        """
        print 'change log triggered by create signal.%s:%s' %(cls, kwargs)
        pass

    @classmethod
    def update_handler(cls, **kwargs):
        """
        changelog for update operation.
        """
        print 'changelog triggered by update signal. %s:%s' %(cls, kwargs)
        pass

    @classmethod
    def delete_handler(cls, **kwargs):
        """
        changelog for delete operation.
        """
        print 'changelog triggered by delete signal. %s:%s' %(cls, kwargs)
        pass


