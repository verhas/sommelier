import pytest
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from pati.utils import TemplateFieldResolver

OUTPUT = 'generated/Test.txt'


def make_resolver(tmp_path, job, config):
    job.setdefault('output', OUTPUT)
    env = Environment(loader=FileSystemLoader(str(tmp_path)))
    return TemplateFieldResolver(env, job, "hibanka", config)


# ---------------------------------------------------------------------------
# Config-level defaults
# ---------------------------------------------------------------------------

def test_config_defaults_fill_missing(tmp_path):
    """Config-level defaults add values absent from context."""
    job = {'context': {'name': 'User'}}
    config = {'defaults': {'package': 'com.example'}}

    result = make_resolver(tmp_path, job, config).resolve_all()

    assert result['name'] == 'User'
    assert result['package'] == 'com.example'


def test_config_defaults_do_not_overwrite_context(tmp_path):
    """Context values take priority over config-level defaults."""
    job = {'context': {'name': 'User', 'package': 'com.custom'}}
    config = {'defaults': {'package': 'com.default'}}

    result = make_resolver(tmp_path, job, config).resolve_all()

    assert result['package'] == 'com.custom'


# ---------------------------------------------------------------------------
# Job-level defaults
# ---------------------------------------------------------------------------

def test_job_defaults_fill_missing(tmp_path):
    """Job-level defaults add values absent from context."""
    job = {'context': {'name': 'User'}, 'defaults': {'package': 'com.example'}}
    config = {}

    result = make_resolver(tmp_path, job, config).resolve_all()

    assert result['name'] == 'User'
    assert result['package'] == 'com.example'


def test_job_defaults_do_not_overwrite_context(tmp_path):
    """Context values take priority over job-level defaults."""
    job = {'context': {'name': 'User', 'package': 'com.custom'},
           'defaults': {'package': 'com.job_default'}}
    config = {}

    result = make_resolver(tmp_path, job, config).resolve_all()

    assert result['package'] == 'com.custom'


# ---------------------------------------------------------------------------
# Three-level priority: context > job defaults > config defaults
# ---------------------------------------------------------------------------

def test_job_defaults_override_config_defaults(tmp_path):
    """Job-level defaults take priority over config-level defaults."""
    job = {'context': {'name': 'User'}, 'defaults': {'package': 'com.job'}}
    config = {'defaults': {'package': 'com.config'}}

    result = make_resolver(tmp_path, job, config).resolve_all()

    assert result['package'] == 'com.job'


def test_all_three_levels(tmp_path):
    """Full priority chain: context wins over job default wins over config default."""
    job = {
        'context': {
            'name': 'User',
            'package': 'com.explicit',   # wins — set explicitly in context
        },
        'defaults': {
            'package': 'com.job',        # would lose to context
            'author': 'job-author',      # wins over config default
        },
    }
    config = {
        'defaults': {
            'package': 'com.config',     # lowest priority
            'author': 'config-author',   # lost to job default
            'version': '1.0',            # only provided here
        }
    }

    result = make_resolver(tmp_path, job, config).resolve_all()

    assert result['package'] == 'com.explicit'   # context wins
    assert result['author'] == 'job-author'      # job default wins
    assert result['version'] == '1.0'            # config default fills in


def test_no_defaults_key(tmp_path):
    """Resolver works normally when neither job nor config has a defaults key."""
    job = {'context': {'name': 'User', 'package': 'com.example'}}
    config = {}

    result = make_resolver(tmp_path, job, config).resolve_all()

    assert result['name'] == 'User'
    assert result['package'] == 'com.example'


# ---------------------------------------------------------------------------
# Dict defaults applied to each item in a list  (the primary "fields" use case)
# ---------------------------------------------------------------------------

def test_defaults_applied_to_each_list_item(tmp_path):
    """Dict default under a list key is merged into every item in the list."""
    job = {
        'context': {
            'fields': [
                {'name': 'id',    'type': 'Long'},    # type present — not overwritten
                {'name': 'email'},                     # type absent  — gets default
                {'name': 'active', 'nullable': False}, # nullable present — not overwritten
            ]
        },
        'defaults': {
            'fields': {'type': 'String', 'nullable': True}
        }
    }
    config = {}

    result = make_resolver(tmp_path, job, config).resolve_all()
    fields = result['fields']

    assert fields[0]['type'] == 'Long'     # explicit value preserved
    assert fields[0]['nullable'] is True   # default filled in

    assert fields[1]['type'] == 'String'   # default filled in
    assert fields[1]['nullable'] is True   # default filled in

    assert fields[2]['type'] == 'String'   # default filled in
    assert fields[2]['nullable'] is False  # explicit value preserved


def test_config_defaults_applied_to_each_list_item(tmp_path):
    """Config-level dict defaults cascade into list items the same way."""
    job = {
        'context': {
            'fields': [
                {'name': 'id'},
                {'name': 'name', 'nullable': False},
            ]
        }
    }
    config = {
        'defaults': {
            'fields': {'type': 'String', 'nullable': True}
        }
    }

    result = make_resolver(tmp_path, job, config).resolve_all()
    fields = result['fields']

    assert fields[0]['type'] == 'String'
    assert fields[0]['nullable'] is True
    assert fields[1]['type'] == 'String'
    assert fields[1]['nullable'] is False   # explicit value preserved


def test_job_list_defaults_override_config_list_defaults(tmp_path):
    """Job-level list defaults take priority over config-level list defaults."""
    job = {
        'context': {'fields': [{'name': 'id'}]},
        'defaults': {'fields': {'type': 'Long'}},
    }
    config = {
        'defaults': {'fields': {'type': 'String', 'nullable': True}}
    }

    result = make_resolver(tmp_path, job, config).resolve_all()
    fields = result['fields']

    assert fields[0]['type'] == 'Long'     # job default wins over config default
    assert fields[0]['nullable'] is True   # config default fills in what job default didn't supply


# ---------------------------------------------------------------------------
# Multiple dict-type keys in a single defaults block (regression: was a bug
# where only the first dict key was processed)
# ---------------------------------------------------------------------------

def test_multiple_dict_keys_in_defaults(tmp_path):
    """All dict-type keys in a defaults block are applied, not just the first one."""
    job = {
        'context': {
            'fields': [{'name': 'id'}],
            'annotations': [{'target': 'class'}],
        },
        'defaults': {
            'fields':      {'type': 'String'},
            'annotations': {'required': False},
        },
    }
    config = {}

    result = make_resolver(tmp_path, job, config).resolve_all()

    assert result['fields'][0]['type'] == 'String'
    assert result['annotations'][0]['required'] is False


# ---------------------------------------------------------------------------
# Nested dict defaults
# ---------------------------------------------------------------------------

def test_nested_dict_defaults_merged(tmp_path):
    """Dict defaults are recursively merged into a matching dict in context."""
    job = {
        'context': {
            'database': {'host': 'prod-server'}
        }
    }
    config = {
        'defaults': {
            'database': {'host': 'localhost', 'port': 5432, 'name': 'mydb'}
        }
    }

    result = make_resolver(tmp_path, job, config).resolve_all()
    db = result['database']

    assert db['host'] == 'prod-server'  # explicit value preserved
    assert db['port'] == 5432           # default filled in
    assert db['name'] == 'mydb'         # default filled in


# ---------------------------------------------------------------------------
# Defaults and template resolution interact
# ---------------------------------------------------------------------------

def test_defaults_values_available_in_templates(tmp_path):
    """Values injected by defaults can be referenced by template expressions."""
    job = {
        'context': {
            'entity_name': 'User',
            'repository_class': '{{ entity_name }}Repository',
            'package': '{{ base }}.entity',
        }
    }
    config = {'defaults': {'base': 'com.example'}}

    result = make_resolver(tmp_path, job, config).resolve_all()

    assert result['base'] == 'com.example'
    assert result['package'] == 'com.example.entity'
    assert result['repository_class'] == 'UserRepository'


def test_config_defaults_can_contain_templates(tmp_path):
    """Config defaults may themselves be template strings resolved against context."""
    job = {
        'context': {'entity_name': 'Product'},
        'defaults': {'table_name': '{{ entity_name | lower }}s'},
    }
    config = {}

    result = make_resolver(tmp_path, job, config).resolve_all()

    assert result['table_name'] == 'products'


# ---------------------------------------------------------------------------
# Predefined macros
# ---------------------------------------------------------------------------

def test_predefined_job_macro(tmp_path):
    """__JOB__ is set to the job name passed to the resolver."""
    job = {'context': {}}
    result = make_resolver(tmp_path, job, {}).resolve_all()
    assert result['__JOB__'] == 'hibanka'


def test_predefined_output_macros(tmp_path):
    """__OUTPUT__, __OUTPUT_STEM__, __OUTPUT_DIR__, __OUTPUT_EXT__ are derived from output path."""
    job = {'output': 'generated/User.java', 'context': {}}
    result = make_resolver(tmp_path, job, {}).resolve_all()

    assert result['__OUTPUT__'] == 'generated/User.java'
    assert result['__OUTPUT_STEM__'] == 'User'
    assert result['__OUTPUT_DIR__'] == 'generated'
    assert result['__OUTPUT_EXT__'] == '.java'


def test_predefined_output_macros_when_output_is_templated(tmp_path):
    """Path macros are still present after resolution when output contains {{ }}."""
    job = {'output': 'generated/{{ name }}.java', 'context': {'name': 'Product'}}
    result = make_resolver(tmp_path, job, {}).resolve_all()

    assert result['__OUTPUT_STEM__'] == 'Product'
    assert result['__OUTPUT_DIR__'] == 'generated'
    assert result['__OUTPUT_EXT__'] == '.java'


def test_predefined_date_year_macros(tmp_path):
    """__DATE__ and __YEAR__ are non-empty strings in the expected format."""
    import re
    job = {'context': {}}
    result = make_resolver(tmp_path, job, {}).resolve_all()

    assert re.match(r'\d{4}-\d{2}-\d{2}', result['__DATE__'])
    assert re.match(r'\d{4}', result['__YEAR__'])


def test_predefined_time_macro(tmp_path):
    """__TIME__ is a non-empty string."""
    job = {'context': {}}
    result = make_resolver(tmp_path, job, {}).resolve_all()
    assert result['__TIME__']


def test_predefined_version_macro(tmp_path):
    """__PATISSERIE_VERSION__ matches the installed package version."""
    import pati
    job = {'context': {}}
    result = make_resolver(tmp_path, job, {}).resolve_all()
    assert result['__PATISSERIE_VERSION__'] == pati.__version__
