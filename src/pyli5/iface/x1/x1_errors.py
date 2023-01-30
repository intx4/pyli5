class X1RequestError(Exception):
    """ request not understood"""
    def __init__(self, info:str):
        self.message = "X1 request not understood: "+info
        super().__init__(self.message)

class X1TaskNotSupported(Exception):
    """ type of task not supported"""
    def __init__(self, info:str, type_for_error:str):
        self.message = "X1 task not supported - task should be compliant to TS 103 221 clause 5.2.7: "+info
        self.type_for_error = type_for_error
        super().__init__(self.message)
class X1ResponseError(Exception):
    """ resp not understood"""
    def __init__(self, info:str):
        self.message = "X1 response not understood: "+info
        super().__init__(self.message)

class X1IdentityAssociationNotSupported(Exception):
    def __init__(self, info:str):
        self.message = "XQR Identity association not supported: "+info
        super().__init__(self.message)

class X1MessageError(Exception):
    """ message not understood"""
    def __init__(self, info:str, type_for_error, admf_id, ne_id, x1_tid, code):
        self.message = "X1 message not understood: " + info
        self.type_for_error = type_for_error
        self.admf_id = admf_id
        self.ne_id = ne_id
        self.x1_tid = x1_tid
        self.code = code
        super().__init__(self.message)