PyDebug
=======

Python debug logging helper

This module allows the creation of log files that indent according to
the flow of control of the program. Here is a trivial example of what
such a log file might look like:

<pre>
16:19:20 DEBUG   [MainThread] sample.&lt module&gt()@81     : hi
16:19:20 INFO    [MainThread] __main__.test_debug()@?  : -&gttest_debug(1)
16:19:20 DEBUG   [MainThread] sample.test_debug()@25   :   ii=1 (test_debug)
16:19:20 DEBUG   [MainThread] __main__.subtest()@?     :   -&gtsubtest(0)
16:19:20 DEBUG   [MainThread] sample.subtest()@17      :     p=0 (subtest)
16:19:20 DEBUG   [MainThread] __main__.subtest()@?     :   &lt -subtest()
16:19:20 DEBUG   [MainThread] sample.test_debug()@28   :   p=0 (test_debug)
16:19:20 DEBUG   [MainThread] __main__.subtest()@?     :   -&gtsubtest(1)
16:19:20 DEBUG   [MainThread] sample.subtest()@17      :     p=1 (subtest)
16:19:20 DEBUG   [MainThread] __main__.subtest()@?     :   &lt -subtest()
16:19:20 DEBUG   [MainThread] sample.test_debug()@28   :   p=1 (test_debug)
16:19:20 INFO    [MainThread] __main__.test_debug()@?  : &lt -test_debug()
16:19:20 DEBUG   [MainThread] sample.&lt module&gt()@86     : back
16:19:20 DEBUG   [MainThread] sample.__init__()@39     : self.i=0
16:19:20 DEBUG   [MainThread] __main__.happy()@?       : -&gthappy(days)
16:19:20 DEBUG   [MainThread] sample.happy()@43        :   msg=days
16:19:20 DEBUG   [MainThread] __main__.happy()@?       : &lt -happy()
16:19:20 DEBUG   [MainThread] __main__.sad()@?         : -&gtsad()
16:19:20 DEBUG   [MainThread] sample.sad()@47          :   in sad()
16:19:20 DEBUG   [MainThread] __main__.sad()@?         : &lt -sad()
16:19:20 DEBUG   [Thread-1  ] __main__.testThread()@?  : -&gttestThread(2)
16:19:20 DEBUG   [Thread-1  ] sample.testThread()@56   :   in run(2)
16:19:20 DEBUG   [Thread-2  ] __main__.testThread()@?  : -&gttestThread(1)
16:19:20 DEBUG   [Thread-2  ] sample.testThread()@56   :   in run(1)
16:19:21 DEBUG   [Thread-2  ] sample.testThread()@58   :   woke up 1
16:19:21 DEBUG   [Thread-2  ] __main__.testThread()@?  : &lt -testThread()
16:19:22 DEBUG   [Thread-1  ] sample.testThread()@58   :   woke up 2
16:19:22 DEBUG   [Thread-1  ] __main__.testThread()@?  : &lt -testThread()
16:19:22 DEBUG   [MainThread] sample.&lt module&gt()@102    : done
</pre>

The main differences are that the left hand side of the log output is
fixed width, so that the indentation of the debug output line up
correctly.
