from pathlib import Path
from resume_builder.io.data_loader import load_data_dir

def test_load_data_dir(tmp_path: Path):
    d = tmp_path / "data"
    d.mkdir()
    (d / "a.txt").write_text(" hello \n", encoding="utf-8")
    (d / "b.txt").write_text("world", encoding="utf-8")
    res = load_data_dir(d)
    assert res == {"a": "hello", "b": "world"}
