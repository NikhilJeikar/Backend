import sys
import threading


class Thread(threading.Thread):
    def __init__(self, *args, **keywords):
        super(Thread, self).__init__(*args, **keywords)
        self.__killed = False
        self.__Parent = None

    def run(self):
        sys.settrace(self.__trace)
        super().run()

    def __trace(self, frame, event, arg):
        # print(f"Function: {frame.f_code.co_name}() Event: {event} Line: {frame.f_lineno}")
        if self.__killed:
            raise SystemExit()
        if self.__Parent is not None:
            if not self.__Parent.isAlive():
                raise SystemExit()
        return self.__trace

    def Bind(self, Parent):
        self.__Parent = Parent

    def kill(self):
        self.__killed = True
