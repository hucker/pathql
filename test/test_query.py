import unittest
import pathlib
from src.pathql.filters.fileext import FileExt
from src.pathql.filters.size import Size
from src.pathql.filters.age import AgeMinutes
from src.pathql.query import Query

class TestQuery(unittest.TestCase):
    def test_fileext(self):
        f = FileExt.in_({"*.py"})
    self.assertTrue(f.match(pathlib.Path(__file__)))
    self.assertFalse(f.match(pathlib.Path("test.txt")))
    def test_size(self):
        s = Size(lambda x, y: x < y, 1000000)
    self.assertTrue(s.match(pathlib.Path(__file__)))
    def test_age(self):
        a = AgeMinutes(lambda x, y: x > y, 0)
    self.assertTrue(a.match(pathlib.Path(__file__)))
    def test_query(self):
        q = Query(FileExt.in_({"*.py"}))
    files = list(q.files(path=pathlib.Path("."), recursive=False, files=True))
        self.assertTrue(any(str(f).endswith(".py") for f in files))

if __name__ == "__main__":
    unittest.main()
