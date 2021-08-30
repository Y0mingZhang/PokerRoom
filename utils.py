class print_and_emit:
    def __init__(self, emit_func):
        self.emit_func = emit_func

    def __call__(self, content):
        print(content)
        self.emit_func(content)
