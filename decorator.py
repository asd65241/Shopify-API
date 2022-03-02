def Error_Handler(func):
    def Inner_Function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as msg:
            raise Exception(f"[{func.__name__}] error, {repr(msg)}")
    return Inner_Function