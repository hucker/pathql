
import pathlib
from pathql.filters.fileext import FileExt
from pathql.filters.size import Size
from pathql.filters.age import AgeMinutes
from pathql.query import Query

# Example usage
if __name__ == "__main__":
    query = Query(
        (FileExt in ("png", "bmp")) & (Size < 1_000_000) & (AgeMinutes < 10)
    )
    for f in query.files(path=pathlib.Path("."), recursive=True, files=True):
        print(f)
