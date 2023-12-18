from unittest import TestCase

from astrun import Astrun


class TestAstrunEval(TestCase):
    def test_expression(self):
        self.assertEqual(Astrun.eval("""1 + 1"""), 2)
        self.assertEqual(Astrun.eval("""'a'+'b'"""), "ab")

    def test_variable_assignment(self):
        self.assertEqual(Astrun.eval("""a = 1; a + 1"""), 2)
        self.assertEqual(Astrun.eval("""a, b = 2, 3; a * b"""), 6)

    def test_list(self):
        self.assertListEqual(
            Astrun.eval("""[0, 'a', (), [], {}, tuple(), list(), set()]"""),
            [0, 'a', (), [], {}, tuple(), list(), set()]
        )
        self.assertEqual(Astrun.eval("""[1,2,3,4,5].index(2)"""), 1)

    def test_tuple(self):
        self.assertTupleEqual(
            Astrun.eval("""(0, 'a', (), [], {}, tuple(), list(), set())"""),
            (0, 'a', (), [], {}, tuple(), list(), set())
        )

    def test_set(self):
        self.assertTrue(Astrun.eval("""3 in {1, 2, 3, 4, 5}"""))
        self.assertTrue(Astrun.eval("""l=[2, 4, 6]; 4 in {1, *l, 3}"""))

    def test_dict(self):
        self.assertEqual(Astrun.eval("""d={1:2}; d[1]"""), 2)
        self.assertEqual(Astrun.eval("""{'a':1, 'b':2}.pop('b')"""), 2)

    def test_comprehension(self):
        self.assertEqual(Astrun.eval("""tuple(x*2 for x in range(10) if x % 2 == 1 if x < 5)"""), (2, 6))
        self.assertListEqual(Astrun.eval("""[abs(i) for i in range(-3, 4)]"""), [3, 2, 1, 0, 1, 2, 3])
        self.assertDictEqual(Astrun.eval("""{i:2*i for i in range(3)}"""), {0: 0, 1: 2, 2: 4})
        self.assertListEqual(Astrun.eval("""[(i, j) for i in range(2) for j in range(4) if j<3]"""),
                             [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)])

    def test_lambda(self):
        self.assertEqual(Astrun.eval("""lambda v: v+1""")(3), 4)
        self.assertTrue(Astrun.eval("""lambda a, b: a==b""")(1, 1))
        self.assertTrue(
            Astrun.eval("""lambda path, record: record['Name'].split('-')[0].split('_')[0] in path""")
            (r"c:\path\filename.h", {'Name': 'filename_digits-343-WHATEVER'}))
        with self.assertRaises(Exception):
            Astrun.eval("""lambda: 1""")(2)
