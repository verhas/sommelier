import pytest
from pathlib import Path
from sommelier.config import load_config, validate_config


def test_load_valid_config(tmp_path):
    """Test loading valid YAML config."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
template_dir: templates
jobs:
  - template: test.j2
    output: output.txt
    context:
      name: John
""")

    config = load_config(str(config_file))
    assert config['template_dir'] == 'templates'
    assert len(config['jobs']) == 1
    assert config['jobs'][0]['template'] == 'test.j2'


def test_load_nonexistent_config():
    """Test loading non-existent config file."""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent.yaml")


def test_load_empty_config(tmp_path):
    """Test loading empty YAML file."""
    config_file = tmp_path / "empty.yaml"
    config_file.write_text("")

    with pytest.raises(ValueError):
        load_config(str(config_file))


def test_validate_missing_jobs():
    """Test validation fails without jobs key."""
    config = {"template_dir": "templates"}
    with pytest.raises(ValueError, match="must contain 'jobs'"):
        validate_config(config)


def test_validate_jobs_not_list():
    """Test validation fails when jobs is not a list."""
    config = {"jobs": "single_job"}
    with pytest.raises(ValueError, match="must be a list"):
        validate_config(config)


def test_validate_empty_jobs():
    """Test validation fails with empty jobs list."""
    config = {"jobs": []}
    with pytest.raises(ValueError, match="cannot be empty"):
        validate_config(config)


def test_validate_job_missing_template():
    """Test validation fails when job missing template."""
    config = {
        "jobs": [
            {
                "output": "output.txt",
                "context": {}
            }
        ]
    }
    with pytest.raises(ValueError, match="missing 'template'"):
        validate_config(config)


def test_validate_job_missing_output():
    """Test validation fails when job missing output."""
    config = {
        "jobs": [
            {
                "template": "test.j2",
                "context": {}
            }
        ]
    }
    with pytest.raises(ValueError, match="missing 'output'"):
        validate_config(config)


def test_validate_job_missing_context():
    """Test validation fails when job missing context."""
    config = {
        "jobs": [
            {
                "template": "test.j2",
                "output": "output.txt"
            }
        ]
    }
    with pytest.raises(ValueError, match="missing 'context'"):
        validate_config(config)
