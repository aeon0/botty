"""
Thread-safe version of Tkinter
Copyright (c) 2009, Allen B. Taylor
Copyright (c) 2017, baldk
Copyright (c) 2018, RedFantom
This module is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser Public License for more details.
You should have received a copy of the GNU Lesser Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
Usage:
    import mtTkinter as Tkinter
    # Use "Tkinter." as usual.
or
    from mtTkinter import *
    # Use Tkinter module definitions as usual.
This module modifies the original Tkinter module in memory, making all
functionality thread-safe. It does this by wrapping the Tk class' tk
instance with an object that diverts calls through an event queue when
the call is issued from a thread other than the thread in which the Tk
instance was created. The events are processed in the creation thread
via an 'after' event.
Note that, because it modifies the original Tkinter module (in memory),
other modules that use Tkinter (e.g., Pmw) reap the benefits automagically
as long as mtTkinter is imported at some point before extra threads are
created.
Authors:
Allen B. Taylor, a.b.taylor@gmail.com
RedFantom, redfantom@outlook.com
baldk, baldk@users.noreply.github.com
Docstrings and line-comments wrapped to 80 characters, code wrapped to
100 characters.
"""
import sys
import threading
# Python 3
from tkinter import *
import queue


class _Tk(object):
    """Wrapper for underlying attribute tk of class Tk"""

    def __init__(self, tk, mt_debug=0, mt_check_period=10):
        """
        :param tk: Tkinter.Tk.tk Tk interpreter object
        :param mt_debug: Determines amount of debug output.
            0 = No debug output (default)
            1 = Minimal debug output
            ...
            9 = Full debug output
        :param mt_check_period: Amount of time in milliseconds (default
            10) between checks for out-of-thread events when things are
            otherwise idle. Decreasing this value can improve GUI
            responsiveness, but at the expense of consuming more CPU
            cycles.
        # TODO: Replace custom logging functionality with standard
        # TODO: logging.Logger for easier access and standardization
        """
        self._tk = tk

        # Create the incoming event queue
        self._event_queue = queue.Queue(1)

        # Identify the thread from which this object is being created
        # so we can tell later whether an event is coming from another
        # thread.
        self._creation_thread = threading.current_thread()

        # Create attributes for kwargs
        self._debug = mt_debug
        self._check_period = mt_check_period
        # Destroying flag to be set by the .destroy() hook
        self._destroying = False

    def __getattr__(self, name):
        """
        Diverts attribute accesses to a wrapper around the underlying tk
        object.
        """
        return _TkAttr(self, getattr(self._tk, name))


class _TkAttr(object):
    """Thread-safe callable attribute wrapper"""

    def __init__(self, tk, attr):
        self._tk = tk
        self._attr = attr

    def __call__(self, *args, **kwargs):
        """
        Thread-safe method invocation. Diverts out-of-thread calls
        through the event queue. Forwards all other method calls to the
        underlying tk object directly.
        """

        # Check if we're in the creation thread
        if threading.current_thread() == self._tk._creation_thread:
            # We're in the creation thread; just call the event directly
            if self._tk._debug >= 8 or \
                    self._tk._debug >= 3 and self._attr.__name__ == 'call' and \
                    len(args) >= 1 and args[0] == 'after':
                print('Calling event directly:', self._attr.__name__, args, kwargs)
            return self._attr(*args, **kwargs)
        else:
            if not self._tk._destroying:
                # We're in a different thread than the creation thread;
                # enqueue the event, and then wait for the response.
                response_queue = queue.Queue(1)
                if self._tk._debug >= 1:
                    print('Marshalling event:', self._attr.__name__, args, kwargs)
                self._tk._event_queue.put((self._attr, args, kwargs, response_queue), True, 1)
                is_exception, response = response_queue.get(True, None)

                # Handle the response, whether it's a normal return value or
                # an exception.
                if is_exception:
                    ex_type, ex_value, ex_tb = response
                    raise ex_type(ex_value, ex_tb)
                return response


def _Tk__init__(self, *args, **kwargs):
    """
    Hook for Tkinter.Tk.__init__ method
    :param self: Tk instance
    :param args, kwargs: Arguments for Tk initializer
    """
    # We support some new keyword arguments that the original __init__ method
    # doesn't expect, so separate those out before doing anything else.
    new_kwnames = ('mt_check_period', 'mt_debug')
    new_kwargs = {
        kw_name: kwargs.pop(kw_name) for kw_name in new_kwnames
        if kwargs.get(kw_name, None) is not None
    }

    # Call the original __init__ method, creating the internal tk member.
    self.__original__init__mtTkinter(*args, **kwargs)

    # Replace the internal tk member with a wrapper that handles calls from
    # other threads.
    self.tk = _Tk(self.tk, **new_kwargs)

    # Set up the first event to check for out-of-thread events.
    self.after_idle(_check_events, self)


# Define a hook for class Tk's destroy method.
def _Tk_destroy(self):
    self.tk._destroying = True
    self.__original__destroy()


def _check_events(tk):
    """Checks events in the queue on a given Tk instance"""

    used = False
    try:
        # Process all enqueued events, then exit.
        while True:
            try:
                # Get an event request from the queue.
                method, args, kwargs, response_queue = tk.tk._event_queue.get_nowait()
            except queue.Empty:
                # No more events to process.
                break
            else:
                # Call the event with the given arguments, and then return
                # the result back to the caller via the response queue.
                used = True
                if tk.tk._debug >= 2:
                    print('Calling event from main thread:', method.__name__, args, kwargs)
                try:
                    response_queue.put((False, method(*args, **kwargs)))
                except SystemExit:
                    raise  # Raises original SystemExit
                except Exception:
                    # Calling the event caused an exception; return the
                    # exception back to the caller so that it can be raised
                    # in the caller's thread.
                    from sys import exc_info  # Python 2 requirement
                    ex_type, ex_value, ex_tb = exc_info()
                    response_queue.put((True, (ex_type, ex_value, ex_tb)))
    finally:
        # Schedule to check again. If we just processed an event, check
        # immediately; if we didn't, check later.
        if used:
            tk.after_idle(_check_events, tk)
        else:
            tk.after(tk.tk._check_period, _check_events, tk)


"""Perform in-memory modification of Tkinter module"""
# Replace Tk's original __init__ with the hook.
Tk.__original__init__mtTkinter = Tk.__init__
Tk.__init__ = _Tk__init__

# Replace Tk's original destroy with the hook.
Tk.__original__destroy = Tk.destroy
Tk.destroy = _Tk_destroy