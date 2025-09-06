from resume_builder.prompts.loader import load_prompt

def test_load_prompt_tailoring_system():
    txt = load_prompt("tailoring_system")
    assert "professional resume writer" in txt
