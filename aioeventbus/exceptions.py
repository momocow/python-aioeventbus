class HandlerError(Exception):
    def __init__(self, handler):
        super().__init__(handler)
        self.handler = handler
