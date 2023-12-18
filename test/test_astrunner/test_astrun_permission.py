from unittest import TestCase

from astrun import Astrun


class TestAstrunPermission(TestCase):

    def test_import_permission(self):
        with self.assertRaises(PermissionError):
            Astrun.eval("""import os; os.getcwd()""")

        with self.assertRaises(PermissionError):
            Astrun.eval("""__import__(os)""")

    def test_file_access(self):
        with self.assertRaises(PermissionError):
            Astrun.eval("""open("file", "w")""")

    def test_string_format(self):
        with self.assertRaises(PermissionError):
            Astrun.eval("""'{}'.format(__import__("os"))""")

    def test_error_catch(self):
        with self.assertRaises(PermissionError):
            Astrun.eval("try: a=__import__('os')\nfinally: b=__import__('os');")

    def test_builtins_exploitation(self):
        with self.assertRaises(PermissionError):
            Astrun.eval("""__builtins__""")

        with self.assertRaises(PermissionError):
            Astrun.eval("""globals()""")

        with self.assertRaises(PermissionError):
            Astrun.eval("[t for t in ().__class__.__bases__[0].__subclasses__() "
                        "if 'warning' in t.__name__][0]()._module.__builtins__")

    def test_astrun_exploitation(self):
        with self.assertRaises(PermissionError):
            Astrun.eval("""a=self""")

        with self.assertRaises(PermissionError):
            Astrun.eval("""lambda: self.namespace""")()
