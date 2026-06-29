# YAML Schema Documentation

Complete reference for Sommelier's YAML configuration format.

## Top-level Keys

### `template_dir` (optional)
Path to the directory containing your Jinja2 templates.

**Default:** Directory of the config file

**Example:**
```yaml
template_dir: ./templates
```

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

### `jobs` (required)
List of generation jobs to execute.

**Example:**
```yaml
jobs:
  - template: user_entity.j2
    output: generated/User.java
    context:
      name: User
```

---

## Job Configuration

Each job in the `jobs` array must have:

### `template` (required)
Name of the Jinja2 template file (relative to `template_dir`).

**Type:** string

**Example:**
```yaml
template: entity.java.j2
```

### `output` (required)
Path where the generated file will be written.

**Type:** string

**Example:**
```yaml
output: src/main/java/com/example/User.java
```

### `context` (required)
Dictionary of variables passed to the template.

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
  - template: entity.java.j2
    output: generated/User.java
    context:
      <<: *java  # Merge java_config into context
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
  - template: entity.java.j2
    output: generated/User.java
    context:
      package: *pkg
      class_name: User
      fields:
        <<: *fields
        - name: username
          type: String
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
# Sommelier YAML Schema

template_dir: templates

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

# Generation jobs
jobs:
  # Generate User entity
  - template: entity.java.j2
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
        - name: email
          type: String
          annotation: "@Column(nullable=false)"

  # Generate Product entity
  - template: entity.java.j2
    output: src/main/java/com/example/app/entity/Product.java
    context:
      <<: *java
      class_name: Product
      table_name: products
      fields:
        <<: *base_fields
        - name: sku
          type: String
          annotation: "@Column(unique=true, nullable=false)"
        - name: price
          type: BigDecimal
          annotation: "@Column(nullable=false)"

  # Generate repository
  - template: repository.java.j2
    output: src/main/java/com/example/app/repository/UserRepository.java
    context:
      <<: *java
      entity_name: User
      entity_type: User
      id_type: Long

  # Generate Liquibase migration
  - template: liquibase.xml.j2
    output: src/main/resources/db/changelog/001-create-tables.xml
    context:
      changelog_id: "001-create-users-table"
      table_name: users
      columns:
        - name: id
          type: BIGINT
          constraints: "primaryKey=true autoIncrement=true"
        - name: username
          type: VARCHAR(255)
          constraints: "nullable=false unique=true"
```

---

## Best Practices

1. **Use anchors for DRY configuration**
   ```yaml
   shared:
     base_package: &pkg com.example
   
   jobs:
     - context:
         package: *pkg  # Reuse instead of repeating
   ```

2. **Organize jobs by type**
   ```yaml
   jobs:
     # Entities
     - template: entity.java.j2
       ...
     # DTOs
     - template: dto.java.j2
       ...
     # Repositories
     - template: repository.java.j2
       ...
   ```

3. **Keep template names descriptive**
   ```yaml
   template: entity.java.j2      # Good
   template: e.j2                # Bad
   ```

4. **Use consistent context structure**
   ```yaml
   # Good: parallel structure for multiple entities
   jobs:
     - context:
         class_name: User
         table_name: users
     - context:
         class_name: Product
         table_name: products
   ```

---

## Common Errors

### Missing required key
```
Error: Job 0 missing 'template' key
```
Add the missing key to your job configuration.

### Invalid YAML syntax
```
YAML Error: mapping values are not allowed
```
Check for tabs (use spaces), proper indentation, and quote strings with special characters.

### Template not found
```
Template not found: entity.java.j2
```
Verify:
1. File exists in `template_dir`
2. Filename matches exactly (case-sensitive)
3. `template_dir` points to the correct directory
