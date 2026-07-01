import pytest
from pathlib import Path
from pati.config import load_config, validate_config


def test_load_valid_config(tmp_path):
    """Test loading valid YAML config."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
template_dir: templates
jobs:
  test_job:
    template: test.j2
    output: output.txt
    context:
      name: John
""")

    config = load_config(str(config_file))
    assert config['template_dir'] == 'templates'
    assert len(config['jobs']) == 1
    assert config['jobs']['test_job']['template'] == 'test.j2'


def test_load_nonexistent_config():
    """Test loading non-existent config file."""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent.yaml")


def test_load_empty_config(tmp_path):
    """Test loading empty YAML file."""
    config_file = tmp_path / "empty.yaml"
    config_file.write_text("")

    config = load_config(str(config_file))
    assert config == {}


def test_load_default_config(tmp_path):
    """Test loading default schema."""
    pati_dir = tmp_path / ".pati"
    pati_dir.mkdir()
    schema_file = pati_dir / "schema.yaml"
    schema_file.write_text("""
jobs:
  test_job:
    template: test.j2
    output: output.txt
    context: {}
""")

    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        config = load_config()
        assert 'jobs' in config
        assert len(config['jobs']) == 1
    finally:
        os.chdir(original_cwd)


def test_validate_missing_jobs():
    """Test validation passes without jobs key."""
    config = {"template_dir": "templates"}
    validate_config(config)


def test_validate_jobs_not_dict():
    """Test validation fails when jobs is not a dict."""
    config = {"jobs": ["single_job"]}
    with pytest.raises(ValueError, match="must be a dict"):
        validate_config(config)


def test_validate_empty_jobs():
    """Test validation passes with empty jobs dict."""
    config = {"jobs": {}}
    validate_config(config)


def test_validate_job_missing_template():
    """Test validation fails when job missing template."""
    config = {
        "jobs": {
            "job1": {
                "output": "output.txt",
                "context": {}
            }
        }
    }
    with pytest.raises(ValueError, match="missing 'template'"):
        validate_config(config)


def test_validate_job_missing_output():
    """Test validation fails when job missing output."""
    config = {
        "jobs": {
            "job1": {
                "template": "test.j2",
                "context": {}
            }
        }
    }
    with pytest.raises(ValueError, match="missing 'output'"):
        validate_config(config)


def test_validate_job_missing_context():
    """Test validation fails when job missing context."""
    config = {
        "jobs": {
            "job1": {
                "template": "test.j2",
                "output": "output.txt"
            }
        }
    }
    with pytest.raises(ValueError, match="missing 'context'"):
        validate_config(config)
