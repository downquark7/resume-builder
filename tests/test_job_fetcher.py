from resume_builder.io.job_fetcher import clean_text

def test_clean_text():
    s = "This   has\n\tmultiple    spaces\n  and newlines\t\t"
    out = clean_text(s)
    assert out == "This has multiple spaces and newlines"
