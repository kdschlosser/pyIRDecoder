# -*- coding: utf-8 -*-
#
# ***********************************************************************************
# MIT License
#
# Copyright (c) 2020 Kevin G. Schlosser
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# ***********************************************************************************

import threading
import traceback
import six
from collections import deque


class ThreadWorkerSingleton(type):

    def __init__(cls, name, bases, dct):
        super(ThreadWorkerSingleton, cls).__init__(name, bases, dct)
        cls._instance = None

    def __call__(cls):
        if cls._instance is None:
            cls._instance = super(ThreadWorkerSingleton, cls).__call__()
            cls._instance.start()

        return cls._instance


@six.add_metaclass(ThreadWorkerSingleton)
class TimerThreadWorker(threading.Thread):

    def __init__(self):
        self.stop_event = threading.Event()
        self.queue_event = threading.Event()
        self.queue = []
        threading.Thread.__init__(self)
        self.daemon = True

    def add(self, timer):
        if timer not in self.queue:
            self.queue.append(timer)
            self.queue_event.set()

    def run(self):
        def _wait():
            duration = 999999999999999999999
            for t in self.queue[:]:
                wait_time = t.adjusted_duration - t.timer.elapsed() - 5000
                if wait_time < 5000:
                    return

                duration = min(wait_time, duration)

            if duration == 999999999999999999999:
                self.queue_event.wait()
            else:
                self.queue_event.wait(duration / 1000000.0)

        while not self.stop_event.is_set():
            _wait()

            for timer in self.queue[:]:
                if timer.run_func():
                    self.queue.remove(timer)

            self.queue_event.clear()


@six.add_metaclass(ThreadWorkerSingleton)
class ProcessThreadWorker(threading.Thread):

    def __init__(self):
        self.stop_event = threading.Event()
        self.queue_event = threading.Event()
        self.queue = deque()
        threading.Thread.__init__(self)
        self.daemon = True

    def add(self, func):
        self.queue.append(func)
        self.queue_event.set()

    def run(self):
        while not self.stop_event.is_set():
            self.queue_event.wait()
            while len(self.queue):
                func = self.queue.popleft()
                try:
                    func()
                except:
                    traceback.print_exc()

            self.queue_event.clear()
