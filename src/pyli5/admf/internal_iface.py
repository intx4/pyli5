from queue import Queue

class InternalInterface():
    def __init__(self):
        self.upL = Queue()
        self.downL = Queue()

    def send_request(self, obj):
        self.upL.put(obj, block=True)

    def get_request(self):
        return self.upL.get(block=True)

    def get_response(self):
        return self.downL.get(block=True)

    def send_response(self, obj):
        self.downL.put(obj, block=True)