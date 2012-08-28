import functools

def UIModel(method):

	# 渲染之前
	@functools.wraps(method)
    def wrapper(self, *args, **kwargs):
    	return method(self, *args, **kwargs)


    # 渲染之后
    def after(self, *args, **kwargs):
    	return method(self, *args, **kwargs)