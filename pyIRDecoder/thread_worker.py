# -*- coding: utf-8 -*-
#
# *****************************************************************************
# MIT License
#
# Copyright (c) 2020 Kevin G. Schlosser
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
# THE SOFTWARE.

# ****************************************************************************

import threading
import traceback
import six


class ThreadWorkerSingleton(type):

    def __init__(cls, name, bases, dct):
        super(ThreadWorkerSingleton, cls).__init__(name, bases, dct)
        cls._instance = None

    def __call__(cls):
        if cls._instance is None:
            cls._instance = super(ThreadWorkerSingleton, cls).__call__()

        return cls._instance


@six.add_metaclass(ThreadWorkerSingleton)
class TimerThreadWorker(object):

    def __init__(self):
        self.stop_event = threading.Event()
        self.queue_event = threading.Event()
        self.queue = []
        self.thread = None

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self.run)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        if self.thread is not None:
            del self.queue[:]
            self.stop_event.set()
            self.queue_event.set()
            self.thread.join(3.0)
            if self.thread.is_alive():
                print('THREAD DID NOT EXIT: TimerThreadWorker')
            else:
                self.thread = None

    def add(self, timer):
        print(timer)
        if timer not in self.queue:
            self.queue.append(timer)
            self.queue_event.set()

    def run(self):
        del self.queue[:]

        while not self.stop_event.is_set():
            duration = 999999999999999999999
            for t in self.queue[:]:
                wait_time = t.adjusted_duration - t.timer.elapsed() - 5000
                if wait_time < 5000:
                    break
                duration = min(wait_time, duration)
            else:
                if duration == 999999999999999999999:
                    self.queue_event.wait()
                else:
                    self.queue_event.wait(duration / 1000000.0)

                self.queue_event.clear()

            for timer in self.queue[:]:
                if timer.run_func():
                    self.queue.remove(timer)

        self.queue_event.clear()
        self.stop_event.clear()


@six.add_metaclass(ThreadWorkerSingleton)
class ProcessThreadWorker(object):

    def __init__(self):
        self.stop_event = threading.Event()
        self.queue_event = threading.Event()
        self.queue = []
        self.thread = None

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self.run)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        if self.thread is not None:
            del self.queue[:]
            self.stop_event.set()
            self.queue_event.set()
            self.thread.join(3.0)
            if self.thread.is_alive():
                print('THREAD DID NOT EXIT: TimerThreadWorker')
            else:
                self.thread = None

    def add(self, func, *args):
        self.queue.append((func, args))
        self.queue_event.set()

    def run(self):
        del self.queue[:]
        while not self.stop_event.is_set():
            self.queue_event.wait()
            self.queue_event.clear()
            while self.queue:
                try:
                    func, args = self.queue.pop(0)
                except IndexError:
                    break

                try:
                    func(*args)
                except:  # NOQA
                    traceback.print_exc()

        self.queue_event.clear()
        self.stop_event.clear()
