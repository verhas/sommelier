# YAML Schema Documentation

![Pâtisserie](../logo.svg)

Complete reference for pati's YAML configuration format.

**License**: MIT OR Apache 2.0 at your option — See [LICENSE-MIT](../LICENSE-MIT) or [LICENSE-APACHE](../LICENSE-APACHE).

## Project Structure

The default pati project uses this structure:

```
my-project/
└── .pati/
    ├── schema.yaml       # Your configuration file
    └── tmplts/           # Template files directory
```

The default schema location is `.pati/schema.yaml` and default template directory is `.pati/tmplts/`.

## Top-level Keys

### `template_dir` (optional)
Path to the directory containing your Jinja2 templates.

**Default:** `./tmplts/` (relative to schema.yaml)

**Example:**
```yaml
template_dir: templates    # Relative to schema.yaml location
```

**Note:** Usually not needed, as `.pati/tmplts/` is the default.

### `shared` (optional)
Shared data that can be reused across jobs using YAML anchors and aliases.

**Example:**
```yaml
shared:
  base_package: &pkg com.example
  database: &db
    host: localhost
    port: 5432
```

### `defaults` (optional)
Default values applied to every job's context when a key is absent. These are the **lowest-priority** values — a job's own `context` or `defaults` always wins.

Two kinds of values belong here:

**Scalar defaults** — values that are shared across many jobs and would be tedious to repeat in every `context:` block:
```yaml
defaults:
  package: com.example   # all jobs get this unless they set package themselves
  author: Team
```

**List-element defaults** — when a context key holds a list of dicts (such as `fields`), a dict under that same key in `defaults` is merged into every element of the list. Use this to supply fallback attributes for list items without repeating them on every element. Multiple list keys can have their own defaults independently:
```yaml
defaults:
  fields:
    nullable: true    # every field that does not set nullable gets true
    type: String      # every field that does not set type gets String
  annotations:
    required: false   # every annotation that does not set required gets false
```

With the above schema-level defaults, a job only needs to list the values that differ from the fallback:
```yaml
jobs:
  user_entity:
    context:
      fields:
        - name: id
          type: Long     # overrides the String default
        - name: email    # gets type: String and nullable: true from defaults
        - name: active
          nullable: false  # overrides the true default; gets type: String
```

See [Multi-level Defaults](#multi-level-defaults) for the full priority rules.

### `jobs` (required)
Dictionary/map of generation jobs. Each key is a job name.

**Format:**
```yaml
jobs:
  job_name:
    template: ...
    output: ...
    context: ...
```

---

## Job Configuration

Each job in the `jobs` dictionary must have:

### `template` (required)
Either:
1. **Template filename** — Name of file in `tmplts/` directory
2. **Inline template** — Multiline Jinja2 template string

**Type:** string

**Examples:**

Template file reference:
```yaml
template: entity.java.j2
```

Inline template:
```yaml
template: |
  class {{ name }} {
    // Auto-generated
  }
```

### `output` (required)
Path where the generated file will be written.

**Type:** string

**Example:**
```yaml
output: src/main/java/com/example/User.java
```

### `context` (required)

Dictionary of variables passed to the template. In addition to the values you define here, pati automatically injects a set of predefined variables (job name, output path, date/time, etc.) — see [Predefined Variables](TEMPLATE_SYNTAX.md#predefined-variables).

Any context value may itself contain a `{{ }}` Jinja2 expression that references other context values or predefined variables. pati resolves these automatically — see [Template Expressions in Context Values](#template-expressions-in-context-values).

**Type:** object

**Example:**
```yaml
context:
  package: com.example
  class_name: User
  fields:
    - name: id
      type: Long
    - name: name
      type: String
```

### `defaults` (optional, per-job)
Default values applied to this job's context only. Higher priority than schema-level `defaults`, lower priority than the job's own `context`.

The primary use for per-job defaults is **list-element defaults**: supplying fallback attributes for every item in a list without repeating them on each element. If a context value can simply be set directly in `context:`, putting it in `defaults:` adds indirection without benefit.

When a `defaults` key maps to a dict and the matching `context` key holds a list, that dict is merged into every element of the list. Multiple list keys can each have their own defaults and are all applied independently:

```yaml
jobs:
  user_entity:
    template: entity.java.j2
    output: generated/User.java
    defaults:
      fields:
        type: String      # applied to each field that does not set type
      annotations:
        required: false   # applied to each annotation that does not set required
    context:
      class_name: User
      fields:
        - name: id
          type: Long      # explicit — not overwritten by defaults
        - name: email     # type absent — gets String from defaults
      annotations:
        - target: class
        - target: field
          required: true  # explicit — not overwritten by defaults
```

Scalar fallbacks that apply to all jobs belong in the schema-level `defaults:` block instead.

---

## Template Expressions in Context Values

Any value in `context:` or `defaults:` may contain a Jinja2 `{{ }}` expression that references other values. pati resolves all expressions automatically using **fixed-point iteration**: it makes repeated passes over the unresolved values, resolving each one as soon as all the values it references are available.

### How resolution works

1. All plain (non-templated) values and predefined variables are made available immediately.
2. In each pass every still-unresolved value is attempted. If all variables it references are already resolved, it resolves successfully and becomes available for the next pass. Otherwise it waits.
3. Passes repeat until all values are resolved or no progress is made.
4. If any values remain unresolved after a pass that resolved nothing, pati raises an error — see [Circular Dependencies](#circular-dependencies) below.

**Order does not matter.** A value may reference another that is defined later in the file; pati figures out the dependency order automatically.

### Chains and derived values

```yaml
context:
  first_name: John
  last_name:  Doe
  full_name:  "{{ first_name }} {{ last_name }}"
  greeting:   "Hello, {{ full_name }}!"
```

`greeting` depends on `full_name`, which in turn depends on `first_name` and `last_name`. pati resolves the whole chain in two passes.

### Referencing predefined variables

Predefined variables such as `__DATE__`, `__OUTPUT_STEM__`, and `__JOB__` behave like the lowest-priority defaults: pati injects them only when the `context:` block does not already define a key with the same name. They are available from the start of resolution and can be referenced like any other value:

```yaml
context:
  class_name: "{{ __OUTPUT_STEM__ }}"
  header: "// Generated on {{ __DATE__ }} by pâtisserie {{ __PATISSERIE_VERSION__ }}"
```

> **Do not define keys named `__...__` in your context.** Predefined variable names are reserved. Defining one in `context:` will silently suppress the real value and produce confusing output.

See [Predefined Variables](TEMPLATE_SYNTAX.md#predefined-variables) for the full list.

### Referencing defaults

Context values may reference values that are supplied by `defaults:` (either job-level or schema-level), and defaults may reference context values. Both participate in the same resolution pass:

```yaml
defaults:
  base_package: com.example
  repo_class: "{{ class_name }}Repository"

jobs:
  user_entity:
    context:
      class_name: User
      package: "{{ base_package }}.entity"   # references a default → "com.example.entity"
      # repo_class absent → filled from defaults → "UserRepository"
```

### Circular dependencies

A value that directly or indirectly references itself can never be resolved. pati detects this as a dead end: when a full pass completes without resolving any new value, it stops immediately and raises:

```
ValueError: Context resolution did not converge.
Possible circular dependency or unresolvable values: {'a': '{{ b }}', 'b': '{{ a }}'}
```

**Example of a circular dependency:**
```yaml
context:
  a: "{{ b }}"   # a needs b
  b: "{{ a }}"   # b needs a — neither can ever resolve
```

**How to avoid it:** every chain must ultimately bottom out in a plain value. Break the cycle by giving at least one variable a literal value:

```yaml
context:
  a: hello        # plain value — resolves immediately
  b: "{{ a }}"   # fine — a is already resolved
```

The most common accidental circular dependency is a **typo** in a variable name — the misspelled name is never defined, so the value that references it can never resolve. When you see the error, check the listed keys carefully for spelling mistakes.

---

## Multi-level Defaults

pati supports a three-level defaults cascade. Values are resolved in this priority order — highest to lowest:

```
context  >  job defaults  >  config defaults
```

### Priority rules

| Source | Key in YAML | Scope | Priority |
|--------|-------------|-------|----------|
| Job `context:` | `jobs.my_job.context` | This job only | **Highest** — never overwritten |
| Job `defaults:` | `jobs.my_job.defaults` | This job only | Fills in what context did not set |
| Schema `defaults:` | top-level `defaults:` | All jobs | **Lowest** — fills in what neither context nor job defaults set |

A key is only filled in from a lower-priority source when it is **absent** (not present at all or `null`). A value of `false`, `0`, or `""` is considered present and is never overwritten.

### Scalar defaults

```yaml
defaults:                 # schema-level: applies to all jobs
  package: com.example
  author: Team

jobs:
  user_entity:
    defaults:             # job-level: overrides schema defaults for this job only
      package: com.users
    context:
      class_name: User
      # package not set → gets com.users (job default wins over schema default)
      # author not set  → gets Team    (schema default fills in)

  product_entity:
    context:
      class_name: Product
      # package not set → gets com.example (schema default, no job default here)
      # author not set  → gets Team
```

### Defaults for lists of dicts

When a defaults value is a **dict** and the matching context value is a **list**, the dict defaults are merged into every item in the list. Multiple list keys can each carry their own defaults and are all applied independently in a single pass:

```yaml
defaults:
  fields:
    nullable: true    # every field that doesn't set nullable gets true
    type: String      # every field that doesn't set type gets String
  annotations:
    required: false   # every annotation that doesn't set required gets false

jobs:
  user_entity:
    context:
      class_name: User
      fields:
        - name: id
          type: Long        # explicit → preserved; nullable absent → gets true
        - name: email
          nullable: false   # explicit → preserved; type absent → gets String
        - name: bio
                            # both absent → gets type: String, nullable: true
      annotations:
        - target: class
                            # required absent → gets false
        - target: field
          required: true    # explicit → preserved
```

After defaults are applied, the effective lists are:

```yaml
fields:
  - {name: id,    type: Long,   nullable: true}
  - {name: email, type: String, nullable: false}
  - {name: bio,   type: String, nullable: true}
annotations:
  - {target: class, required: false}
  - {target: field, required: true}
```

### Defaults for nested dicts

When a defaults value is a **dict** and the matching context value is also a **dict**, the defaults are merged recursively:

```yaml
defaults:
  database:
    host: localhost
    port: 5432

jobs:
  my_job:
    context:
      database:
        host: prod-db.example.com   # explicit → preserved
        # port absent → gets 5432 from defaults
```

### Defaults as template expressions

Default values follow exactly the same resolution rules as context values and participate in the same fixed-point pass. See [Template Expressions in Context Values](#template-expressions-in-context-values) for the full explanation, including how to avoid circular dependencies.

---

## Template Detection

pati automatically detects whether a template is a filename or inline content:

- **Inline template** — If contains `{{`, `{%`, or newlines
- **Template filename** — Simple string without template syntax

Examples:
```yaml
jobs:
  # Treated as inline template (contains {{)
  greeting:
    template: "echo {{ message }}"
    output: output.txt

  # Treated as template filename
  entity:
    template: entity.java.j2
    output: output.java

  # Clearly inline (multiline)
  config:
    template: |
      [app]
      name={{ app_name }}
    output: config.ini
```

---

## YAML Anchors and Aliases

Use YAML anchors (`&name`) and aliases (`*name`) to define reusable blocks:

### Basic Usage

```yaml
shared:
  java_config: &java
    package: com.example.app
    author: John Doe

jobs:
  user_entity:
    template: entity.java.j2
    output: generated/User.java
    context:
      <<: *java              # Merge java_config into context
      class_name: User
```

The `<<` merge key (`<<: *java`) includes all keys from `java_config` into `context`.

### Complex Example

```yaml
shared:
  base_package: &pkg com.example
  common_fields: &fields
    - name: id
      type: Long
      primary_key: true
    - name: created_at
      type: DateTime

jobs:
  user_entity:
    template: entity.java.j2
    output: generated/User.java
    context:
      package: *pkg
      class_name: User
      fields:
        - name: username
          type: String
        - <<: *fields         # Merge common fields
```

---

## Context Variables

The `context` passed to a template can contain:

### Scalars
```yaml
context:
  app_name: MyApp
  version: 1.0
  debug: true
```

### Lists
```yaml
context:
  fields:
    - name: id
      type: Long
    - name: name
      type: String
```

### Nested Objects
```yaml
context:
  database:
    host: localhost
    port: 5432
    credentials:
      user: admin
      password: secret
```

---

## Complete Example

```yaml
# pati YAML Schema - .pati/schema.yaml

# Shared configuration for reuse
shared:
  java_config: &java
    package: com.example.app
    java_version: 11
    
  common_fields: &base_fields
    - name: id
      type: Long
      annotation: "@Id @GeneratedValue"
    - name: created_at
      type: LocalDateTime
      annotation: "@CreationTimestamp"

# Generation jobs (as dictionary with job names)
jobs:
  # Generate User entity from file template
  user_entity:
    template: entity.java.j2
    output: src/main/java/com/example/app/entity/User.java
    context:
      <<: *java
      class_name: User
      table_name: users
      fields:
        <<: *base_fields
        - name: username
          type: String
          annotation: "@Column(unique=true, nullable=false)"

  # Generate Product entity
  product_entity:
    template: entity.java.j2
    output: src/main/java/com/example/app/entity/Product.java
    context:
      <<: *java
      class_name: Product
      table_name: products
      fields:
        <<: *base_fields
        - name: sku
          type: String

  # Generate config with inline template
  app_config:
    template: |
      # Configuration for {{ app_name }}
      spring.application.name={{ app_name }}
      spring.jpa.hibernate.ddl-auto=update
      server.port={{ port }}
    output: src/main/resources/application.properties
    context:
      app_name: MyApp
      port: 8080

  # Generate repository
  user_repository:
    template: repository.java.j2
    output: src/main/java/com/example/app/repository/UserRepository.java
    context:
      <<: *java
      entity_name: User
      id_type: Long
```

---

## Best Practices

1. **Use job names that describe the purpose**
   ```yaml
   jobs:
     user_entity:       # Good: clear purpose
     config_file:       # Good: clear purpose
     my_job_1:          # Bad: not descriptive
   ```

2. **Use anchors for DRY configuration**
   ```yaml
   shared:
     base_package: &pkg com.example
   
   jobs:
     my_job:
       context:
         package: *pkg  # Reuse instead of repeating
   ```

3. **Organize jobs by type**
   ```yaml
   jobs:
     # Entities
     user_entity:
       ...
     product_entity:
       ...
     
     # Repositories
     user_repository:
       ...
     
     # Configuration
     app_config:
       ...
   ```

4. **Use inline templates for small content**
   ```yaml
   # Good: small inline template
   greeting:
     template: "echo {{ message }}"
     
   # Better: large template in file
   entity:
     template: entity.java.j2
   ```

5. **Use consistent context structure**
   ```yaml
   # Good: parallel structure for multiple entities
   jobs:
     user:
       context:
         class_name: User
         table_name: users
     
     product:
       context:
         class_name: Product
         table_name: products
   ```

---

## Common Errors

### Missing required key
```
Error: Job 'my_job' missing 'template' key
```
Ensure each job has `template`, `output`, and `context`.

### Invalid YAML syntax
```
YAML Error: mapping values are not allowed
```
Check for:
- Tabs (use spaces only)
- Proper indentation
- Quotes around strings with special characters

### Template not found
```
ERROR: Template not found: entity.java.j2
```
Verify:
1. File exists in `.pati/tmplts/`
2. Filename matches exactly (case-sensitive)
3. No custom `template_dir` is hiding the file

### Jobs must be dict, not list
```
Error: 'jobs' must be a dict/map
```
Use dict format:
```yaml
jobs:
  job_name:
    template: ...
    output: ...
    context: ...
```

Not array format:
```yaml
jobs:
  - template: ...
    output: ...
    context: ...
```
