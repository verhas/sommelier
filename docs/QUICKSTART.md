# Quick Start Guide

Get up and running with Sommelier in 5 minutes!

## 1. Install Sommelier

```bash
pip install sommelier
```

## 2. Initialize a Project

Choose a template and initialize a new project:

```bash
sommelier init --template java-spring --output my-project
cd my-project
```

This creates:
- `schema.yaml` — Your data model configuration
- `templates/` — Jinja2 templates for code generation

## 3. Explore the Schema

Open `schema.yaml` and see the structure:

```yaml
template_dir: templates

shared: &base_package
  package: com.example.demo

jobs:
  - template: entity.java.j2
    output: generated/Entity.java
    context:
      <<: *base_package
      entity_name: User
      table_name: users
      fields:
        - name: id
          type: Long
          annotation: "@Id @GeneratedValue"
        # ... more fields
```

**Key concepts:**
- `template_dir` — Location of your Jinja2 templates
- `shared` — Reusable data with YAML anchors (`&name`) and aliases (`<<: *name`)
- `jobs` — Array of generation tasks
  - `template` — Template file to render
  - `output` — Where to write the generated file
  - `context` — Data passed to the template

## 4. Look at a Template

Open `templates/entity.java.j2`:

```jinja2
package {{ package }}.entity;

@Entity
@Table(name = "{{ table_name }}")
public class {{ entity_name }} {

{% for field in fields %}
    {{ field.annotation }}
    private {{ field.type }} {{ field.name }};

{% endfor %}
    // getters and setters...
}
```

**Template syntax:**
- `{{ variable }}` — Insert variable
- `{% for item in items %}` — Loop over items
- `{% if condition %}` — Conditional

[Full Jinja2 reference →](TEMPLATE_SYNTAX.md)

## 5. Generate Code

Dry run (preview without writing):

```bash
sommelier generate schema.yaml --dry-run
```

Real generation (creates files):

```bash
sommelier generate schema.yaml
```

Check the `generated/` folder — you'll see `Entity.java`, `UserDTO.java`, etc.

## 6. Customize

Edit `schema.yaml` to change your data model:

```yaml
context:
  entity_name: Product  # was: User
  table_name: products  # was: users
  fields:
    - name: sku
      type: String
```

Then regenerate:

```bash
sommelier generate schema.yaml
```

The templates will adapt to your new data!

## Next Steps

- [Full YAML schema documentation](YAML_SCHEMA.md)
- [Advanced template syntax](TEMPLATE_SYNTAX.md)
- [Real-world examples](EXAMPLES.md)
- [Template best practices](https://jinja.palletsprojects.com/)

## Common Patterns

### Multiple tables/entities

Add more jobs to `schema.yaml`:

```yaml
jobs:
  - template: entity.java.j2
    output: generated/User.java
    context:
      entity_name: User
      # ...

  - template: entity.java.j2
    output: generated/Product.java
    context:
      entity_name: Product
      # ...
```

### Reusable config with anchors

```yaml
shared:
  common_fields: &common
    - name: id
      type: Long
    - name: created_at
      type: DateTime

jobs:
  - template: entity.java.j2
    output: generated/User.java
    context:
      entity_name: User
      fields:
        <<: *common
        - name: username
          type: String
```

### Override output directory

```bash
sommelier generate schema.yaml --output-dir /path/to/output
```

## Getting Help

- List available templates: `sommelier list-templates`
- Show help: `sommelier --help`
- Show command help: `sommelier generate --help`

Happy generating!
