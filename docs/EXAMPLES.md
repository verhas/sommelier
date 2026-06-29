# Real-World Examples

Complete working examples showing Sommelier in action.

## Example 1: Java Spring Boot Entity

Generate a JPA entity with associated DTO and repository.

### Schema (schema.yaml)

```yaml
template_dir: templates

shared: &java
  package: com.example.app

jobs:
  - template: entity.java.j2
    output: generated/User.java
    context:
      <<: *java
      class_name: User
      table_name: users
      fields:
        - name: id
          type: Long
          annotation: "@Id @GeneratedValue"
        - name: username
          type: String
          annotation: "@Column(nullable = false, unique = true)"
        - name: email
          type: String
          annotation: "@Column(nullable = false)"

  - template: dto.java.j2
    output: generated/UserDTO.java
    context:
      <<: *java
      class_name: UserDTO
      fields:
        - name: id
          type: Long
        - name: username
          type: String
        - name: email
          type: String

  - template: repository.java.j2
    output: generated/UserRepository.java
    context:
      <<: *java
      entity_name: User
      entity_type: User
      id_type: Long
```

### Template (templates/entity.java.j2)

```jinja2
package {{ package }}.entity;

import javax.persistence.*;

@Entity
@Table(name = "{{ table_name }}")
public class {{ class_name }} {

{% for field in fields %}
    {{ field.annotation }}
    private {{ field.type }} {{ field.name }};

{% endfor %}
    public {{ class_name }}() {
    }

{% for field in fields %}
    public {{ field.type }} get{{ field.name | capitalize }}() {
        return {{ field.name }};
    }

    public void set{{ field.name | capitalize }}({{ field.type }} {{ field.name }}) {
        this.{{ field.name }} = {{ field.name }};
    }

{% endfor %}
}
```

### Generated Output (generated/User.java)

```java
package com.example.app.entity;

import javax.persistence.*;

@Entity
@Table(name = "users")
public class User {

    @Id @GeneratedValue
    private Long id;

    @Column(nullable = false, unique = true)
    private String username;

    @Column(nullable = false)
    private String email;

    public User() {
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

}
```

---

## Example 2: Rust SQLx Model

Generate a Rust struct with SQLx derive macros.

### Schema (schema.yaml)

```yaml
template_dir: templates

jobs:
  - template: model.rs.j2
    output: generated/user.rs
    context:
      struct_name: User
      derives:
        - Debug
        - Clone
        - Serialize
        - Deserialize
      fields:
        - name: id
          type: i64
        - name: username
          type: String
        - name: email
          type: String
        - name: created_at
          type: DateTime<Utc>
```

### Template (templates/model.rs.j2)

```jinja2
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;

#[derive({{ derives | join(', ') }}, FromRow)]
pub struct {{ struct_name }} {
{% for field in fields %}
    pub {{ field.name }}: {{ field.type }},
{% endfor %}
}

impl {{ struct_name }} {
    pub fn new({% for field in fields %}{{ field.name }}: {{ field.type }}{{ "," if not loop.last else "" }}{% endfor %}) -> Self {
        Self {
{% for field in fields %}
            {{ field.name }},
{% endfor %}
        }
    }
}
```

### Generated Output (generated/user.rs)

```rust
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct User {
    pub id: i64,
    pub username: String,
    pub email: String,
    pub created_at: DateTime<Utc>,
}

impl User {
    pub fn new(id: i64, username: String, email: String, created_at: DateTime<Utc>) -> Self {
        Self {
            id,
            username,
            email,
            created_at,
        }
    }
}
```

---

## Example 3: Python SQLAlchemy Model

Generate a Python SQLAlchemy ORM model.

### Schema (schema.yaml)

```yaml
template_dir: templates

jobs:
  - template: model.py.j2
    output: generated/models.py
    context:
      class_name: User
      table_name: users
      fields:
        - name: id
          type: Integer
          primary_key: true
        - name: username
          type: String(255)
          nullable: false
          unique: true
        - name: email
          type: String(255)
          nullable: false
        - name: created_at
          type: DateTime
          default: func.now()
```

### Template (templates/model.py.j2)

```jinja2
from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class {{ class_name }}(Base):
    __tablename__ = '{{ table_name }}'

{% for field in fields %}
    {{ field.name }} = Column(
        {{ field.type }}{{ "," if not loop.last else "" }}
        {% if field.primary_key %}primary_key=True{{ "," if field.default or field.unique or not field.nullable else "" }}{% endif %}
        {% if field.default %}default={{ field.default }}{{ "," if field.unique or not field.nullable else "" }}{% endif %}
        {% if field.unique %}unique=True{{ "," if not field.nullable else "" }}{% endif %}
        {% if not field.nullable %}nullable=False{% endif %}
    )

{% endfor %}
    def __repr__(self):
        return f"<{{ class_name }}(id={self.id}, username={self.username})>"
```

### Generated Output (generated/models.py)

```python
from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(
        Integer,
        primary_key=True
    )

    username = Column(
        String(255),
        unique=True,
        nullable=False
    )

    email = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=func.now()
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
```

---

## Example 4: Go GORM Model

Generate a Go struct for GORM ORM.

### Schema (schema.yaml)

```yaml
template_dir: templates

jobs:
  - template: model.go.j2
    output: generated/models.go
    context:
      package_name: models
      struct_name: User
      table_name: users
      fields:
        - name: ID
          type: uint
          gorm_tag: "primaryKey"
        - name: Username
          type: string
          gorm_tag: "uniqueIndex;not null"
        - name: Email
          type: string
          gorm_tag: "not null"
        - name: CreatedAt
          type: time.Time
          gorm_tag: "autoCreateTime"
```

### Template (templates/model.go.j2)

```jinja2
package {{ package_name }}

import "time"

type {{ struct_name }} struct {
{% for field in fields %}
    {{ field.name }} {{ field.type }} `gorm:"{{ field.gorm_tag }}"`
{% endfor %}
}

func ({{ struct_name | lower }}) TableName() string {
    return "{{ table_name }}"
}

func New{{ struct_name }}(username, email string) *{{ struct_name }} {
    return &{{ struct_name }}{
        Username: username,
        Email: email,
        CreatedAt: time.Now(),
    }
}
```

### Generated Output (generated/models.go)

```go
package models

import "time"

type User struct {
    ID        uint      `gorm:"primaryKey"`
    Username  string    `gorm:"uniqueIndex;not null"`
    Email     string    `gorm:"not null"`
    CreatedAt time.Time `gorm:"autoCreateTime"`
}

func (user) TableName() string {
    return "users"
}

func NewUser(username, email string) *User {
    return &User{
        Username: username,
        Email:    email,
        CreatedAt: time.Now(),
    }
}
```

---

## Using the Examples

Try each example:

```bash
# Initialize from a template
sommelier init --template java-spring --output my-project
cd my-project

# See what would be generated
sommelier generate schema.yaml --dry-run

# Generate the code
sommelier generate schema.yaml

# Check the generated files
ls -la generated/
cat generated/User.java
```

---

## Tips and Tricks

1. **Reuse schemas across projects**
   ```bash
   cp -r examples/java-spring my-new-java-project
   ```

2. **Extend templates**
   Add your own logic to generated templates:
   ```jinja2
   {% if add_lombok %}
   @Data
   {% endif %}
   ```

3. **Generate multiple variants**
   ```yaml
   jobs:
     - template: entity.java.j2
       output: generated/User.java
       context:
         entity_name: User
     - template: entity.java.j2
       output: generated/Product.java
       context:
         entity_name: Product
   ```

4. **Version your schemas**
   ```bash
   git add schema.yaml  # Track changes to data model
   ```

5. **Use environment-specific contexts**
   ```bash
   # Generate for development
   sommelier generate schema.dev.yaml
   
   # Generate for production
   sommelier generate schema.prod.yaml
   ```
