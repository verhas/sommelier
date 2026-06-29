#!/usr/bin/env python3
import argparse
import logging
import sys
from pathlib import Path

from . import __version__
from .config import load_config
from .generator import Generator
from .utils import get_example_templates_path, ensure_directories

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_generate(args):
    """Handle 'generate' command."""
    try:
        config = load_config(args.config)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return 1

    config_dir = Path(args.config).parent
    template_dir_str = config.get('template_dir', 'templates')
    template_dir = config_dir / template_dir_str if not Path(template_dir_str).is_absolute() else template_dir_str

    try:
        gen = Generator(str(template_dir))
    except Exception as e:
        logger.error(f"Failed to initialize generator: {e}")
        return 1

    if args.output_dir:
        for job in config.get('jobs', []):
            job['output'] = str(Path(args.output_dir) / Path(job['output']).name)

    successful = gen.generate_all(config, dry_run=args.dry_run)

    if args.dry_run:
        logger.info(f"Dry run complete: {successful} job(s) ready")
    else:
        logger.info(f"Generation complete: {successful} file(s) created")

    return 0 if successful == len(config.get('jobs', [])) else 1


def cmd_init(args):
    """Handle 'init' command."""
    template_name = args.template or 'java-spring'
    output_dir = args.output or '.'

    examples_dir = get_example_templates_path()
    template_source = examples_dir / template_name

    if not template_source.exists():
        logger.error(f"Template not found: {template_name}")
        logger.info(f"Available templates: java-spring, rust-sqlx, python-sqlalchemy, go-gorm")
        return 1

    try:
        output_path = Path(output_dir)
        ensure_directories(output_path)

        schema_src = template_source / 'schema.yaml'
        schema_dst = output_path / 'schema.yaml'
        if schema_src.exists():
            with open(schema_src) as src, open(schema_dst, 'w') as dst:
                dst.write(src.read())
            logger.info(f"Created: {schema_dst}")

        templates_src = template_source / 'templates'
        templates_dst = output_path / 'templates'
        if templates_src.exists():
            ensure_directories(templates_dst)
            for template_file in templates_src.glob('*'):
                dst = templates_dst / template_file.name
                with open(template_file) as src, open(dst, 'w') as dstf:
                    dstf.write(src.read())
                logger.info(f"Created: {dst}")

        logger.info(f"Initialized project from template: {template_name}")
        logger.info(f"Next: edit schema.yaml and templates/, then run 'sommelier generate schema.yaml'")
        return 0

    except Exception as e:
        logger.error(f"Failed to initialize project: {e}")
        return 1


def cmd_list_templates(args):
    """Handle 'list-templates' command."""
    examples_dir = get_example_templates_path()

    if not examples_dir.exists():
        logger.error(f"Examples directory not found: {examples_dir}")
        return 1

    templates = [d.name for d in examples_dir.iterdir() if d.is_dir()]
    templates.sort()

    print("Available templates:")
    for template in templates:
        print(f"  - {template}")

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Language-agnostic boilerplate generator from YAML data models and Jinja2 templates',
        prog='sommelier'
    )

    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # generate command
    gen_parser = subparsers.add_parser('generate', help='Generate boilerplate from YAML config')
    gen_parser.add_argument('config', help='Path to YAML configuration file')
    gen_parser.add_argument('--dry-run', action='store_true', help='Show what would be generated without writing')
    gen_parser.add_argument('--output-dir', help='Override output directory for all jobs')
    gen_parser.set_defaults(func=cmd_generate)

    # init command
    init_parser = subparsers.add_parser('init', help='Initialize new project from template')
    init_parser.add_argument('--template', help='Template name (default: java-spring)')
    init_parser.add_argument('--output', '-o', help='Output directory (default: current)')
    init_parser.set_defaults(func=cmd_init)

    # list-templates command
    list_parser = subparsers.add_parser('list-templates', help='List available templates')
    list_parser.set_defaults(func=cmd_list_templates)

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not hasattr(args, 'func'):
        parser.print_help()
        return 0

    try:
        return args.func(args)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
