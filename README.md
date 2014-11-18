PyDebug
=======

Python debug logging helper

This module allows the creation of log files that indent according to
the flow of control of the program. The main features of Debug.py are
definition of a fixed width multivariable field in the logging output,
and automatic indentation (and de-dent) of the debug output each time
a new function is entered or exitted.

The Debug.py module allows one to format the module name, function
name and line number (for example) into a single fixed length field, and also
indents the output of logging statements by 'n' spaces in each
subroutine. All that needs to be done for this to work is to define a
DebugFilter object with content of the module/function/line number,
and then to add a <code lang="python">@debug(__name__)</code>
decorator before each function that is to use the indenting. Example:

<pre>
<code lang="python">
#!/usr/bin/env python
# file t.py
import logging
from Debug import debug, DebugFilter

@debug(__name__)
def subtest(jj):
    logging.getLogger(__name__).info('hi!')
    return

@debug(__name__)
def test_debug(ii):
    '''
    test that indent is increased corectly
    '''
    logger = logging.getLogger(__name__)
    logger.debug( 'ii=%d (test_debug)'%ii )
    for jj in range(2):
        subtest(jj)
        logger.debug( 'p=%d (test_debug)'%jj )

logging.basicConfig(filename='test.log',
                    filemode='w',
					level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-7s [%(threadName)-10s] %(modfuncline)-25s: %(debug_message)s',
                    datefmt='%H:%M:%S')
f = DebugFilter('%(module)s.%(funcName)s()@%(lineno)s',maxlen=25)
test_debug(7)
</code>
</pre>
produces a file, test.log, containing this:
<pre>
12:23:52 DEBUG   [MainThread] __main__.test_debug()@?  : -&gt;test_debug(7)
12:23:52 DEBUG   [MainThread] t.test_debug()@16        :   ii=7 (test_debug)
12:23:52 DEBUG   [MainThread] __main__.subtest()@?     :   -&gt;subtest(0)
12:23:52 INFO    [MainThread] t.subtest()@7            :     hi!
12:23:52 DEBUG   [MainThread] __main__.subtest()@?     :   &lt;-subtest()
12:23:52 DEBUG   [MainThread] t.test_debug()@19        :   p=0 (test_debug)
12:23:52 DEBUG   [MainThread] __main__.subtest()@?     :   -&gt;subtest(1)
12:23:52 INFO    [MainThread] t.subtest()@7            :     hi!
12:23:52 DEBUG   [MainThread] __main__.subtest()@?     :   &lt;-subtest()
12:23:52 DEBUG   [MainThread] t.test_debug()@19        :   p=1 (test_debug)
12:23:52 DEBUG   [MainThread] __main__.test_debug()@?  : &lt;-test_debug()
</pre>

