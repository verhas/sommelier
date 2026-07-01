import pytest
from pathlib import Path
from pati.generator import Generator


def test_generator_initialization(tmp_path):
    """Test Generator initialization with valid template directory."""
    gen = Generator(str(tmp_path))
    assert gen.template_dir == tmp_path


def test_generator_initialization_nonexistent():
    """Test Generator initialization fails with non-existent directory."""
    with pytest.raises(FileNotFoundError):
        Generator("/nonexistent/path")


def test_generate_simple_template(tmp_path):
    """Test generating output from simple template file."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    template_file = templates_dir / "hello.txt.j2"
    template_file.write_text("Hello {{ name }}!")

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    gen = Generator(str(templates_dir))
    job = {
        "template": "hello.txt.j2",
        "output": str(output_dir / "hello.txt"),
        "context": {"name": "World"}
    }

    result = gen.generate("test_job", job)
    assert result is True

    output_file = output_dir / "hello.txt"
    assert output_file.exists()
    assert output_file.read_text() == "Hello World!"


def test_generate_inline_template(tmp_path):
    """Test generating with inline template."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    gen = Generator(str(templates_dir))
    job = {
        "template": "Hello {{ name }}!",
        "output": str(output_dir / "hello.txt"),
        "context": {"name": "World"}
    }

    result = gen.generate("test_job", job)
    assert result is True

    output_file = output_dir / "hello.txt"
    assert output_file.exists()
    assert output_file.read_text() == "Hello World!"


def test_generate_missing_template(tmp_path):
    """Test generate fails with missing template file."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    gen = Generator(str(templates_dir))
    job = {
        "template": "missing.j2",
        "output": str(tmp_path / "output.txt"),
        "context": {}
    }

    result = gen.generate("test_job", job)
    assert result is False


def test_generate_template_with_loops(tmp_path):
    """Test generating with loop constructs."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    template_file = templates_dir / "list.txt.j2"
    template_file.write_text("""Items:
{% for item in items %}
- {{ item }}
{% endfor %}""")

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    gen = Generator(str(templates_dir))
    job = {
        "template": "list.txt.j2",
        "output": str(output_dir / "list.txt"),
        "context": {"items": ["apple", "banana", "cherry"]}
    }

    result = gen.generate("test_job", job)
    assert result is True

    output_file = output_dir / "list.txt"
    content = output_file.read_text()
    assert "apple" in content
    assert "banana" in content
    assert "cherry" in content


def test_generate_dry_run(tmp_path):
    """Test dry-run mode doesn't create files."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    template_file = templates_dir / "test.txt.j2"
    template_file.write_text("Test {{ value }}")

    output_file = tmp_path / "output.txt"

    gen = Generator(str(templates_dir))
    job = {
        "template": "test.txt.j2",
        "output": str(output_file),
        "context": {"value": "123"}
    }

    result = gen.generate("test_job", job, dry_run=True)
    assert result is True
    assert not output_file.exists()


def test_generate_all_multiple_jobs(tmp_path):
    """Test generating all jobs from config."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    for name in ["one.txt.j2", "two.txt.j2"]:
        template_file = templates_dir / name
        template_file.write_text(f"Content from {name}")

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    config = {
        "jobs": {
            "job1": {
                "template": "one.txt.j2",
                "output": str(output_dir / "one.txt"),
                "context": {}
            },
            "job2": {
                "template": "two.txt.j2",
                "output": str(output_dir / "two.txt"),
                "context": {}
            }
        }
    }

    gen = Generator(str(templates_dir))
    successful = gen.generate_all(config)

    assert successful == 2
    assert (output_dir / "one.txt").exists()
    assert (output_dir / "two.txt").exists()


def test_generate_all_partial_failure(tmp_path):
    """Test generate_all with partial failures."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    good_template = templates_dir / "good.txt.j2"
    good_template.write_text("Good")

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    config = {
        "jobs": {
            "good_job": {
                "template": "good.txt.j2",
                "output": str(output_dir / "good.txt"),
                "context": {}
            },
            "bad_job": {
                "template": "missing.txt.j2",
                "output": str(output_dir / "missing.txt"),
                "context": {}
            }
        }
    }

    gen = Generator(str(templates_dir))
    successful = gen.generate_all(config)

    assert successful == 1
    assert (output_dir / "good.txt").exists()
    assert not (output_dir / "missing.txt").exists()


def test_multiline_inline_template(tmp_path):
    """Test multiline inline template."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    gen = Generator(str(templates_dir))
    job = {
        "template": """class {{ name }} {
    // Generated class
}""",
        "output": str(output_dir / "test.java"),
        "context": {"name": "TestClass"}
    }

    result = gen.generate("test_job", job)
    assert result is True

    output_file = output_dir / "test.java"
    assert output_file.exists()
    content = output_file.read_text()
    assert "class TestClass" in content
