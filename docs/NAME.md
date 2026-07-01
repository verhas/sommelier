# Why Pâtisserie?

![Pâtisserie](../logo.svg)

## The culinary tradition in software naming

Developers have long borrowed from the kitchen. There is something honest about it: software that transforms raw ingredients into finished products, following recipes, wielding tools, serving hungry consumers. The metaphor fits. But different kitchen metaphors carry different philosophies, and the choice of name reveals something about the tool's soul.

---

## A brief tour of the kitchen

**Cookie Cutter** (`cookiecutter`) is perhaps the most direct analogy in the scaffolding space. A cookie cutter is a metal stamp: press it into dough and you get a shape — always the same shape, quickly, reliably, identically. This is exactly what the tool does: it stamps out project structures from a single template. The metaphor is honest and the tool is excellent. But a cookie cutter has one job: one template, one output, repeat.

**Chef** manages server infrastructure the way a head chef manages a kitchen: with authority, with recipes (cookbooks), with a brigade of workers (nodes). Its sub-tools carry the metaphor through — **Knife** is the chef's primary instrument, **Kitchen** is where you test your recipes before serving them, **Berkshelf** is where you store your cookbook collection. The whole ecosystem is a kitchen. The philosophy is orchestration and convergence.

**Homebrew** brews software packages the way a brewer crafts beer — formulae, kegs, taps, cellars. The language implies patience, craft, and a certain locality: you brew for your own machine.

**Chocolatey** (Windows) and **Cake** (.NET build tool) lean into sweets: packages and builds as confections, delivered reliably and enjoyed without fuss.

**Celery** (Python task queue) and **Cucumber** (BDD testing) take vegetables rather than pastry, grounding themselves in the everyday rather than the refined.

**Flask** and **Bottle** are vessels for liquid — lightweight containers that hold what you pour into them, shaped by the user rather than the framework.

---

## What makes a pâtisserie different

A pâtisserie is not a diner. It is not a fast-food counter. It is not a factory stamping out identical biscuits.

A **pâtisserie** is a workshop of precision and artistry. The patissier works from a small set of core ingredients — flour, butter, eggs, sugar — and from those same ingredients produces croissants, éclairs, macarons, mille-feuilles, tarts, and brioches. Each output is different in form, texture, and purpose. Each follows its own template. The unity lies in the ingredients, not in the shape of the product.

This is exactly what Pâtisserie the software does.

You define your data model once — your ingredients. A single `schema.yaml` describes your entities, their fields, their relationships. From that one source of truth, Pâtisserie produces a Java entity class, a Python SQLAlchemy model, a Rust struct, a SQL migration, a Liquibase changeset, a TypeScript interface, an API specification. Each output follows its own Jinja2 template. Each is a different pastry. The ingredients are shared.

---

## The philosophy in three principles

**Same ingredients, many pastries.**
Define your data model once. Generate boilerplate in every language your project touches. When the model changes, regenerate. The source of truth never splits.

**The patissier follows a template, not an instinct.**
A great patissier does not improvise the croissant lamination process. They follow a precise, repeatable template — and so do yours. Jinja2 templates are explicit, version-controlled, reviewable, and yours to own. Pâtisserie does not generate code by magic; it renders templates with data, transparently.

**Craft, not stamping.**
Cookie cutters make identical shapes. A pâtisserie makes refined artifacts, each appropriate to its context. Your Java entity has annotations. Your Rust struct has derives. Your SQL migration has rollback logic. The same field definition in `schema.yaml` becomes the right thing in each language, because you wrote the templates that know the difference.

---

## Why `pati`?

The CLI is `pati` — the affectionate French shorthand for pâtisserie, the way a regular customer might ask for "the usual from the pati on the corner." It is short to type, easy to remember, and carries a lightness that the longer name earns but does not need to announce on every invocation.

```bash
pati cuire
```

That is all. The workshop does the rest.

---

## The name you did not choose

The project directory is still called `sommelier` — a wine steward, another culinary professional, another tradition of taking something complex and making it approachable for someone who just wants the right thing paired with their meal. The sommelier knows the cellar so you do not have to. The name that did not make it to the package still describes the spirit: deep knowledge, quietly in service, making the right match.
