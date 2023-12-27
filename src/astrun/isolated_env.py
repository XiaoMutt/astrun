import resource
from multiprocessing import Process, Queue
from queue import Empty


def _run_virtual_environment_(run, input_queue: Queue, output_queue: Queue, MAX_MEMORY, MAX_CPU_TIME):
    """
    Run in a different Process and memory is not shared.
    """
    # see resource limit
    # resource.setrlimit(resource.RLIMIT_AS, (MAX_MEMORY, MAX_MEMORY))
    resource.setrlimit(resource.RLIMIT_CPU, (MAX_CPU_TIME, MAX_CPU_TIME))
    # no file can be opened, so read/write on files, directories, devices, sockets are prevented.
    # if os get imported. many os methods will not run, such as os.getcwd(), os.listdir(), etc.
    # however, os.remove and os.removedirs still works because no files get opened.
    resource.setrlimit(resource.RLIMIT_NOFILE, (0, 0))
    resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))

    while True:
        try:
            args = input_queue.get()
            output_queue.put(run(args))
        except Exception as err:
            output_queue.put(err)


class IsolatedEnv:
    def __init__(self,
                 MAX_MEMORY=64 * 1024 * 1024,  # in bytes
                 MAX_CPU_TIME=60,
                 RESULT_WAITING_TIME=3):
        """
        This only works on Linux.

        :param MAX_MEMORY:
        :param MAX_CPU_TIME:
        :param RESULT_WAITING_TIME:
        """

        self.input_queue = Queue()
        self.output_queue = Queue()
        self.process = Process(target=_run_virtual_environment_,
                               args=(self._run, self.input_queue, self.output_queue, MAX_MEMORY, MAX_CPU_TIME))
        self.process.start()
        self.RESULT_WAITING_TIME = RESULT_WAITING_TIME

    @staticmethod
    def _run(args):
        raise NotImplemented

    def __call__(self, args):
        if not self.process.is_alive():
            raise RuntimeError(f"The worker process has been terminated.")

        try:
            self.input_queue.put(args)  # blocking
            result = self.output_queue.get(timeout=self.RESULT_WAITING_TIME)  # blocking
            if isinstance(result, Exception):
                raise result

            return result

        except Empty:
            # when the process exceed resource limit, the exception cannot be sent back through the queue
            # so the queue will be timeout
            if self.process.is_alive():
                self.process.terminate()
            raise TimeoutError("The worker did not return results on time and is terminated.")

    def close(self):
        self.process.terminate()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
