#!/bin/env python
'''
Debugging support functions

Typical usage:

from Debug import debug, debug_class, DebugFilter
import logging

@debug(__name__)
def myfunc():
    logger = logging.getLogger(__name__)
    logger.debug('inside')

@debug_class(__name__,level=logging.DEBUG, 'start', 'run')
class MyClass(object):
    def __init__(self,arg):
        self.arg = arg
    def start(self,msg):
        logger = logging.getLogger(__name__)
        logger.debug('in start')

if __name__ == '__main__':
    logging.basicConfig(filename='debug.log',
                        filemode='w',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-7s %(modfuncline)-30s: %(debug_message)s',
                        datefmt='%H:%M:%S')
    f = DebugFilter('[%(threadName)s] %(module)s.%(funcName)s()@%(lineno)d',maxlen=30)
    myfunc()
    o = MyClass('fred')
    o.start()

'''
import logging
try:
    from functools import partial, wraps
except ImportError, e:
    from _functools import partial
    from functools32 import wraps
from threading import Thread, local
import time
#from Borg import Borg

class Borg(object):
    '''
    standard pattern for a "singleton" type object, except that it is
    just shared state, instead of exactly the same object. Google it
    for more info
    '''
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state


class DebugLog(Borg):
    '''
    "singleton" object to keep track of the debug level indentation
    although the indentation is specific to the actual thread
    this is the class that allows the log to look like this:
    -->myfunc( (1,2),{"type":"script"})
        internal debug message
        -->subfunc()
           debug from inside subfunc
        <--subfunc()
        post subfunc message from myfunc
    <--myfunc()
    '''
    tls = local() # create thread local storage for the class
    def __init__(self):
        Borg.__init__(self) # make this a "singleton"
        #
        # ----- create the dbg_indent for this thread the first time
        # ----- a DebugLog object is created in the thread
        #
        if not hasattr(DebugLog.tls,'dbg_indent'):
            DebugLog.tls.dbg_indent = 0
            DebugLog.tls.stack = []
        #
        # ----- create a global indent increment, for all messages
        #
        if not hasattr(self,'indent'):
            self.indent = 2

    def _pushLocation(self,module_name,func_name,lineno):
        DebugLog.tls.stack.append( (module_name, func_name, lineno) )

    def _enter(self):
        '''
        entering a function increases the dbg_indent by the indent
        '''
        DebugLog.tls.dbg_indent += self.indent

    def _loc(self):
        return DebugLog.tls.stack[-1]

    def _exit(self):
        '''
        exiting a function decreases the dbg_indent by the indent
        '''
        DebugLog.tls.dbg_indent -= self.indent

    def _popLocation(self):
        DebugLog.tls.stack.pop()

    def _dashes(self):
        '''
        entering/exiting functions puts ----> or <---- before the func name
        the number of dashes is based on the global indent increment
        '''
        return '-'*(self.indent-1)
    def _prefix(self):
        '''
        return the string of leading spaces to indent the message
        '''
        return ' '*DebugLog.tls.dbg_indent
    def _msg(self,msg):
        '''
        prefix the message to be logged with the proper indentation
        '''
        return self._prefix() + msg

def dbgIndent(indent=2):
    '''
    all the app to decide how much to indent. Don't change this partway through!!!
    because it is also used for dedenting
    '''
    DebugLog().indent = indent

# ======================================================================

class DebugFilter( logging.Filter):
    '''
    a logging filter is applied to each message sent to a logger before
    the log formatting is done. This custom filter enables makeing the
    location of where the log statement appeared (module, function, line number)
    get formatted as a fixed width string, so that the indentation used by
    the @debug and @debug_class decorators don't get messed up

    To use this, put this (or something similar) immediately after the logging
    system is set up in  your app:

        from pygcp import DebugFilter
        dbgFilter = DebugFilter('%(module)s.%(funcName)s()@%(lineno)s',40)
        for handler in logging.root.handlers:
            handler.addFilter(dbgFilter)

    '''
    def __init__(self,fmt='%(module)s:%(funcName)s.%(lineno)s',maxlen=None,handlers=None):
        '''
        specify the logging attributes that will be combined into a single
        string and truncated to a maxlen (if given). Any of the standard
        logger format specifiers are allowed
        '''
        logging.Filter.__init__(self)
        self.fmt = fmt
        self.maxlen = maxlen
        #
        # ----- add this filter to either the specified logging handlers
        # ----- or to all of them (default)
        #
        if handlers is None:
            handlers = logging.root.handlers
        for handler in handlers:
            handler.addFilter(self)

    def filter(self, record):
        '''
        this is the function that is called per record. It applies the
        formatting for this filter and returns True to indicate success.
        The new "modfuncline" logger attribute is created. Also, the
        "debug_message" attribute is created with the indented message
        (see the @debug and @debug_class decorators)
        '''
        recD = record.__dict__.copy()
        if recD['module'] == 'Debug':
            recD['module'], recD['funcName'], recD['lineno'] = DebugLog()._loc()

        #cpath = self.fmt % record.__dict__
        cpath = self.fmt % recD
        #print 'DebugFilter.filter: module.funcName = %s.%s@%s' % (recD['module'],recD['funcName'],recD['lineno'])
        if not self.maxlen is None:
            cpath = cpath[-self.maxlen:].ljust(self.maxlen)
        record.modfuncline = cpath
        record.debug_message = DebugLog()._msg( record.getMessage() )
        return True

# ======================================================================

def debug(modname,level=logging.DEBUG):
    '''
    @debug function decorator. This will enable the logging messages to
    be printed in a nested format, based on the call tree (see DebugLog
    for more details)

    Usage:
    @debug(__name__,level=logging.INFO)

    NOTE: it is necessary to include __name__ as the first param, so that
    the logger which is used is based on the originating module
    the level parameter specifies the logging level for the entry and exit
    messages only
    '''
    def decorating_function(user_function):
        #print('in decorating_function for user_function %s.%s' % (modname,user_function.__name__))
        @wraps(user_function)
        def wrapper(*args,**kwds):
            dlogger = DebugLog()
            logger = logging.getLogger(modname)
            #
            # ----- format the args into a csv of positional args, followed by keyword args
            #
            argL = []
            pos_args = ','.join( [str(a)[:100] for a in args] )
            if len(pos_args) > 0: argL.append(pos_args)
            kw_args = ','.join( ['%s=%s'%(k,str(v)[:100]) for k,v in kwds.items()])
            if len(kw_args) > 0: argL.append(kw_args)
            enter_msg = '%s>%s(%s)' % (DebugLog()._dashes(),user_function.__name__,','.join(argL))
            #
            # ----- save the module and function name for the undecorated function
            # ----- print the enter message
            # ----- and increase the debug indent level
            #
            dlogger._pushLocation(modname,user_function.__name__,'?')
            logger.log(level,enter_msg)
            dlogger._enter()
            #
            # ----- call the undecorated function
            #
            result = user_function(*args,**kwds)
            #
            # ----- decrease the indent level
            # ----- print the exit message
            # ----- pop the undecorated module/function name
            #
            dlogger._exit()
            exit_msg = '<%s%s()' % (DebugLog()._dashes(),user_function.__name__)
            logger.log(level,exit_msg)
            dlogger._popLocation()
            return result
        return wrapper
    return decorating_function

def debug_class(modname,level=logging.DEBUG,*method_names):
    '''
    @debug_class class decorator. This will apply the @debug
    function decorator to all the methods in the class, or to
    those methods listed as optional arguments, if supplied

    Usage:
    @debug_class(__name__,level=logging.INFO,'start','run')
    class MyClass(object):

    NOTE: the class must be a "new-style" class, derived from object
    '''
    def class_rebuilder(cls):
        class NewClass(cls):
            def __getattribute__(self,attr_name):
                obj = super(NewClass,self).__getattribute__(attr_name)
                if hasattr(obj,'__call__') and (len(method_names) == 0 or attr_name in method_names):
                    return debug(modname,level)(obj)
                return obj
        return NewClass
    return class_rebuilder

# ======================================================================
# test methods
# ======================================================================

@debug(__name__)
def subtest(p):
    '''
    test that indent is increased corectly when called from inside another @debug func
    '''
    logger = logging.getLogger(__name__)
    logger.debug( 'p=%d (subtest)' % p )

@debug(__name__,logging.INFO)
def test_debug(ii):
    '''
    test that indent is increased corectly
    '''
    logger = logging.getLogger(__name__)
    logger.debug( 'ii=%d (test_debug)'%ii )
    for jj in range(2):
        subtest(jj)
        logger.debug( 'p=%d (test_debug)'%jj )

@debug_class(__name__,logging.DEBUG,'happy')
class test_debug_class(object):
    '''
    test that debug is applied to all the specified functions
    '''
    def __init__(self):
        logger = logging.getLogger(__name__)
        self.i = 0
        logger.debug('self.i=%s'% self.i)

    def happy(self,msg):
        logger = logging.getLogger(__name__)
        logger.debug('msg=%s'% msg)

    def sad(self):
        logger = logging.getLogger(__name__)
        logger.debug('in sad()')

@debug(__name__)
def testThread(idx):
    '''
    test that the debug decorators work across threads
    NOTE: indent level must be thread specific
    '''
    logger = logging.getLogger(__name__)
    logger.debug('in run(%d)'% idx)
    time.sleep(idx)
    logger.debug('woke up %d'% idx)

if __name__ == '__main__':
    '''
    test cases and usage examples
    '''
    #
    # ----- set up logging
    #
    logging.basicConfig(filename='debug.log',
                        filemode='w',
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-7s %(modfuncline)-30s: %(debug_message)s',
                        datefmt='%H:%M:%S')
    #
    # ----- apply the debug filter to all the handlers, so they don't
    # ----- complain when they see the "modfuncline" and "debug_message" attributes
    #
    f = DebugFilter('[%(threadName)s] %(module)s.%(funcName)s()@%(lineno)d',maxlen=30)
    for handler in logging.root.handlers:
        handler.addFilter(f)
    #
    # ----- just use logging as usual
    #
    logger = logging.getLogger()
    logger.debug('hi')
    #
    # ----- test the @debug decorator
    #
    test_debug(1)
    logger.debug('back')
    #
    # ----- test the @debug_class decorator
    #
    o = test_debug_class()
    o.happy('days')
    o.sad()
    #
    # ----- test thread safety
    #
    t1 = Thread(target=testThread,args=(2,))
    t2 = Thread(target=testThread,args=(1,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    logger.debug('done')

    
