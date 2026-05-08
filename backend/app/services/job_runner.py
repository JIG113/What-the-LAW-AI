from concurrent.futures import Future, ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)
futures: dict[int, Future] = {}
