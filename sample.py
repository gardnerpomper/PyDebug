#!/usr/bin/env python
import logging
import time
from threading import Thread, local
from Debug import DebugFilter, debug, debug_class

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

#@debug_class(__name__,logging.DEBUG,'happy')
@debug_class(__name__,logging.DEBUG)
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
                        format='%(asctime)s %(levelname)-7s [%(threadName)-10s] %(modfuncline)-25s: %(debug_message)s',
                        datefmt='%H:%M:%S')
    #
    # ----- apply the debug filter to all the handlers, so they don't
    # ----- complain when they see the "modfuncline" and "debug_message" attributes
    #
    f = DebugFilter('%(module)s.%(funcName)s()@%(lineno)s',maxlen=25)
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

    
