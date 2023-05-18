import sys
import pyqtgraph.debug as pgdebug
from pyqtgraph.exceptionHandling import original_excepthook
from .LogWindow import LogWindow


def printExc(msg="", indent=4, prefix="|", msgType="error"):
    """Print an error message followed by an indented exception backtrace
    (This function is intended to be called within except: blocks)"""
    pgdebug.printExc(msg, indent, prefix)
    logExc(msg=msg, msgType=msgType)


def logMsg(msg, **kwargs):
    """msg: the text of the log message
       msgTypes: user, status, error, warning (status is default)
       importance: 0-9 (0 is low importance, 9 is high, 5 is default)
       other supported keywords:
          exception: a tuple (type, exception, traceback) as returned by sys.exc_info()
          docs: a list of strings where documentation related to the message can be found
          reasons: a list of reasons (as strings) for the message
          traceback: a list of formatted callstack/traceback objects (formatting a traceback/callstack returns a list of strings), usually looks like [['line 1', 'line 2', 'line3'], ['line1', 'line2']]
       Feel free to add your own keyword arguments. These will be saved in the log.txt file, but will not affect the content or way that messages are displayed.
    """
    logger = LogWindow.instance
    if logger is None:
        print("Can't log message; no log window created yet.")
        print(kwargs)
        return
        
    try:
        logger.logMsg(msg, **kwargs)
    except:
        print("Error logging message:")
        print("    " + "\n    ".join(msg.split("\n")))
        print("    " + str(kwargs))
        sys.excepthook(*sys.exc_info())


def logExc(msg, *args, **kwargs):
    """
    Calls logMsg, but adds in the current exception and callstack. 
    
    Must be called within an except block, and should only be called if the exception is not re-raised. 
    Unhandled exceptions are automatically logged, so logging an exception that will be re-raised can 
    cause the exception to be logged twice.
    """
    logger = LogWindow.instance
    if logger is None:
        print("Can't log exception; no log window created yet.")
        print(args)
        print(kwargs)
        return

    try:
        logger.logExc(msg, *args, **kwargs)
    except:
        print("Error logging exception:")
        print("    " + "\n    ".join(msg.split("\n")))
        print("    " + str(kwargs))
        sys.excepthook(*sys.exc_info())


def installExceptionHandler():
    # install global exception handler for others to hook into.
    import pyqtgraph.exceptionHandling as exceptionHandling

    exceptionHandling.setTracebackClearing(True)
    exceptionHandling.register(exceptionCallback)

blockLogging = False


def exceptionCallback(*args):
    # Called whenever there is an unhandled exception.

    # unhandled exceptions generate an error message by default, but this
    # can be overridden by raising HelpfulException(msgType='...')
    global blockLogging
    if not blockLogging:
        # if an error occurs *while* trying to log another exception, disable any further logging to prevent recursion.
        try:
            blockLogging = True
            logMsg("Unexpected error: ", exception=args, msgType="error")
        except:
            print("Error: Exception could no be logged.")
            original_excepthook(*sys.exc_info())
        finally:
            blockLogging = False
