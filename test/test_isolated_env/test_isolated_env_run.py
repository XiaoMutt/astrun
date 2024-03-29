from unittest import TestCase

from astrun import Astrun
from astrun import IsolatedEnv


class ExecIsolatedEnv(IsolatedEnv):
    @staticmethod
    def _run(*args):
        exec(*args)


class AstrunIsolatedEnv(IsolatedEnv):
    @staticmethod
    def _run(*args):
        return Astrun.eval(*args)


class TestIsolatedEnv(TestCase):
    def test_fun_as_param(self):
        with IsolatedEnv(Astrun.eval) as env:
            self.assertEqual(env("max(0,1)"), 1)

    def test_memory(self):
        with ExecIsolatedEnv() as env:
            with self.assertRaises(TimeoutError):
                env("""'0'*(64 * 1024 * 1024)""")

    def test_cpu_time(self):
        with ExecIsolatedEnv() as env:
            with self.assertRaises(TimeoutError):
                env("""while True: 2**2""")

    def test_file_open(self):
        with ExecIsolatedEnv() as env:
            with self.assertRaises(OSError):
                env("""open("test", "w")""")

    def test_file_read(self):
        with ExecIsolatedEnv() as env:
            with self.assertRaises(OSError):
                env("""import os;os.getcwd()""")

    def test_web_access(self):
        with ExecIsolatedEnv() as env:
            with self.assertRaises(OSError):
                env("""from urllib import request;request.urlopen("http://www.google.com")""")

    def test_shell_command(self):
        with ExecIsolatedEnv() as env:
            with self.assertRaises(AssertionError):
                env("""import os;assert os.system("ls")==0""")

    def test_command(self):
        with ExecIsolatedEnv() as env:
            with self.assertRaises(OSError):
                env("""import os;os.getcwd()""")

    def test_astrun(self):
        with AstrunIsolatedEnv() as env:
            self.assertEqual(env("""1+1"""), 2)
            self.assertEqual(env("""tuple(i for i in range(5))"""), (0, 1, 2, 3, 4))
