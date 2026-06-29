import pytest
from pathlib import Path
from sommelier.config import load_config
from sommelier.generator import Generator


def test_java_spring_example():
    """Test Java Spring example generates correctly."""
    example_dir = Path(__file__).parent.parent / "examples" / "java-spring"
    schema_file = example_dir / "schema.yaml"

    if not schema_file.exists():
        pytest.skip("Java Spring example not found")

    config = load_config(str(schema_file))
    template_dir = example_dir / "templates"

    gen = Generator(str(template_dir))
    successful = gen.generate_all(config, dry_run=True)

    assert successful > 0


def test_rust_sqlx_example():
    """Test Rust SQLx example generates correctly."""
    example_dir = Path(__file__).parent.parent / "examples" / "rust-sqlx"
    schema_file = example_dir / "schema.yaml"

    if not schema_file.exists():
        pytest.skip("Rust SQLx example not found")

    config = load_config(str(schema_file))
    template_dir = example_dir / "templates"

    gen = Generator(str(template_dir))
    successful = gen.generate_all(config, dry_run=True)

    assert successful > 0


def test_python_example():
    """Test Python SQLAlchemy example generates correctly."""
    example_dir = Path(__file__).parent.parent / "examples" / "python-sqlalchemy"
    schema_file = example_dir / "schema.yaml"

    if not schema_file.exists():
        pytest.skip("Python SQLAlchemy example not found")

    config = load_config(str(schema_file))
    template_dir = example_dir / "templates"

    gen = Generator(str(template_dir))
    successful = gen.generate_all(config, dry_run=True)

    assert successful > 0


def test_go_example():
    """Test Go GORM example generates correctly."""
    example_dir = Path(__file__).parent.parent / "examples" / "go-gorm"
    schema_file = example_dir / "schema.yaml"

    if not schema_file.exists():
        pytest.skip("Go GORM example not found")

    config = load_config(str(schema_file))
    template_dir = example_dir / "templates"

    gen = Generator(str(template_dir))
    successful = gen.generate_all(config, dry_run=True)

    assert successful > 0


def test_generate_with_custom_output_dir(tmp_path):
    """Test override output directory functionality."""
    example_dir = Path(__file__).parent.parent / "examples" / "java-spring"
    schema_file = example_dir / "schema.yaml"

    if not schema_file.exists():
        pytest.skip("Java Spring example not found")

    config = load_config(str(schema_file))
    template_dir = example_dir / "templates"

    output_dir = tmp_path / "custom_output"
    output_dir.mkdir()

    for job_name, job in config['jobs'].items():
        job['output'] = str(output_dir / Path(job['output']).name)

    gen = Generator(str(template_dir))
    successful = gen.generate_all(config, dry_run=False)

    assert successful > 0
    assert list(output_dir.glob("*"))
