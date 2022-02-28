import time

function_execution_times: dict[str, float] = {}
function_usage_counts: dict[str, int] = {}


def timeit(method):
	def timed(*args, **kw):
		time_start = time.time()
		result = method(*args, **kw)
		time_end = time.time()

		if method.__name__ not in function_execution_times:
			function_execution_times[method.__name__] = 0
		function_execution_times[method.__name__] += time_end - time_start

		if method.__name__ not in function_usage_counts:
			function_usage_counts[method.__name__] = 0
		function_usage_counts[method.__name__] += 1

		return result
	return timed


def get_function_execution_times():
	return function_execution_times
def get_function_usage_counts():
	return function_usage_counts
def reset_stats():
	global function_execution_times, function_usage_counts
	function_execution_times = {}
	function_usage_counts = {}

# @timeit
# def test():
# 	e = 0
# 	for i in range(999):
# 		e += 1 / math.factorial(i)
# 	return e

# for i in range(100):
# 	test()
# print(get_function_execution_times())
