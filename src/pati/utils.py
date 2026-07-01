import datetime
import os
from pathlib import Path
from shutil import copy2
import logging
from typing import Dict, Any
from jinja2 import Environment, Undefined

import pati

logger = logging.getLogger(__name__)


def is_templated(value: Any) -> bool:
    return isinstance(value, str) and ('{{' in value or '{%' in value)


def purge(resolved, unresolved):
    for key in resolved.keys():
        unresolved.pop(key, None)


class TemplateFieldResolver:
    """Resolve template syntax in context field values using fixed-point iteration."""

    def __init__(self, env: Environment, job: Dict[str, Any], job_name: str, config: Dict[str, Any]):
        """Initialize the resolver with Jinja2 environment and context.

        Args:
            env: Jinja2 Environment
            context: Dictionary of context values
        """
        self.env = env
        self.job = job
        self.job_name = job_name
        self.context = job.get('context', {})
        self.config = config

    def merge(self, source: Dict[str, Any], target: Dict[str, Any], warn: bool = False):
        for key in source.keys():
            if isinstance(source[key], dict):
                if not key in target:
                    target[key] = {}
                if isinstance(target[key], list):
                    for item in target[key]:
                        self.merge(source[key], item, False)
                else:
                    if isinstance(target[key], dict):
                        self.merge(source[key], target[key], warn)
            else:
                if target.get(key) is None:
                    target[key] = source[key]
                    if warn:
                        logger.warning(f"Defining the key '{key}' in '{self.job_name}.defaults' is bad. Just move it to '{self.job_name}.context'.")

    def add_defaults(self):
        defaults = self.job.get('defaults')
        if not defaults is None:
            self.merge(defaults, self.context, True)
        defaults = self.config.get('defaults', {})
        if not defaults is None:
            self.merge(defaults, self.context)
        if not '__JOB__' in self.context:
            self.context['__JOB__'] = self.job_name
        if not '__TEMPLATE__' in self.context:
            self.context['__TEMPLATE__'] = self.job.get('template')
        if not '__DATE__' in self.context:
            self.context['__DATE__'] = datetime.date.today().isoformat()
        if not '__TIME__' in self.context:
            self.context['__TIME__'] = datetime.datetime.now().strftime('%H:%M:%S')
        if not '__YEAR__' in self.context:
            self.context['__YEAR__'] = str(datetime.date.today().year)
        if not '__PATISSERIE_VERSION__' in self.context:
            self.context['__PATISSERIE_VERSION__'] = pati.__version__
        output = self.job.get('output')
        if not '__OUTPUT__' in self.context:
            self.context['__OUTPUT__'] = output
        if not is_templated(output):
            if not '__OUTPUT_STEM__' in self.context:
                self.context['__OUTPUT_STEM__'] = str(Path(output).stem)
            if not '__OUTPUT_DIR__' in self.context:
                self.context['__OUTPUT_DIR__'] = str(Path(output).parent)
            if not '__OUTPUT_EXT__' in self.context:
                self.context['__OUTPUT_EXT__'] = str(Path(output).suffix)

    def resolve_all(self) -> Dict[str, Any]:
        """Resolve all context fields using fixed-point iteration.

        Iteratively renders all template strings until they stop changing.
        This handles nested dependencies correctly.

        Returns:
            Dictionary with all resolved values
        """
        self.add_defaults()
        unresolved = dict(self.context)  # Start with original values
        resolved = {}
        for key, value in unresolved.items():
            if is_templated(value):
                continue
            resolved[key] = value

        purge(resolved, unresolved)

        changed = True  # becomes False after executing the inner loop if no key was resolved: dead end
        while changed and len(unresolved) > 0:
            changed = False
            for key, value in unresolved.items():
                try:
                    new_value = self._resolve_value(value, resolved)
                    resolved[key] = new_value
                    changed = True
                except Exception as e:
                    continue

            purge(resolved, unresolved)

        if len(unresolved) > 0:
            raise ValueError(
                f"Context resolution did not converge .\nPossible circular dependency or unresolvable values: {unresolved}.")
        output = resolved.get('__OUTPUT__', self.job.get('output'))
        if not '__OUTPUT_STEM__' in resolved:
            resolved['__OUTPUT_STEM__'] = str(Path(output).stem)
        if not '__OUTPUT_DIR__' in resolved:
            resolved['__OUTPUT_DIR__'] = str(Path(output).parent)
        if not '__OUTPUT_EXT__' in resolved:
            resolved['__OUTPUT_EXT__'] = str(Path(output).suffix)

        return resolved

    def _resolve_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """Resolve a single value using the provided context.

        Args:
            value: Value to resolve
            context: Current resolved context

        Returns:
            Resolved value, or the original value if there is nothing to be resolved or
            the referenced {{ value }} to be used is not available yet
        """
        if is_templated(value):
            template = self.env.from_string(value)
            return template.render(context)
        elif isinstance(value, list):
            return [self._resolve_value(item, context) for item in value]
        elif isinstance(value, dict):
            return {k: self._resolve_value(v, context) for k, v in value.items()}
        else:
            return value


def ensure_directories(path: str) -> Path:
    """Create directories recursively if they don't exist.

    Args:
        path: Directory path to create

    Returns:
        Path object for the created directory
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured directory exists: {p}")
    return p


def safe_write_file(path: str, content: str) -> None:
    """Write content to file with backup of an existing file if content changed.

    If the file already exists with identical content, skip writing and backup.

    Args:
        path: File path to write to
        content: Content to write
    """
    p = Path(path)
    ensure_directories(str(p.parent))

    # If the file exists, check if the content is identical
    if p.exists():
        try:
            existing_content = p.read_text()
            if existing_content == content:
                logger.debug(f"File unchanged, skipping write: {p}")
                return
        except Exception as e:
            logger.debug(f"Could not read existing file {p}: {e}")

        # Content differs, create backup
        backup_path = Path(str(p) + '.bak')
        copy2(p, backup_path)
        logger.info(f"Backed up existing file to {backup_path}")

    with open(p, 'w') as f:
        f.write(content)
    logger.debug(f"Wrote file: {p}")


def get_example_templates_path() -> Path:
    """Get path to bundled example templates.

    Returns:
        Path to examples directory
    """
    return Path(__file__).parent.parent.parent / "examples"


def get_package_root() -> Path:
    """Get the root directory of the pati package.

    Returns:
        Path to package root
    """
    return Path(__file__).parent.parent.parent
