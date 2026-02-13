---
layout: home

hero:
  name: "Nestipy"
  text: "The Modular Python Framework"
  tagline: "Unleash the power of NestJS patterns in Python. Build scalable, testable, and maintainable APIs with FastAPI or Blacksheep."
  image:
    src: /images/nestipy.png
    alt: Nestipy Logo
  actions:
    - theme: brand
      text: Get Started
      link: /overview/first-step
    - theme: alt
      text: View on GitHub
      link: https://github.com/nestipy/nestipy

features:
  - title: "Modular Architecture"
    details: "Nestipy follows a strict modular structure, allowing you to encapsulate logic into reusable modules. This architectural pattern, popularized by NestJS, ensures that your codebase remains organized as it grows."
    icon: 📦
  - title: "Powered by FastAPI & Blacksheep"
    details: "Choose your underlying engine. Nestipy works seamlessly with FastAPI for industry-standard performance or Blacksheep for extreme speed. You get the best of both worlds: robust structure and high-performance execution."
    icon: 🚀
  - title: "True Dependency Injection"
    details: "Stop worrying about manual instantiation. Nestipy features a sophisticated built-in Inversion of Control (IoC) container that handles dependency resolution, scoping, and lifecycle management automatically."
    icon: 💉
  - title: "GraphQL support with Strawberry"
    details: "Build modern, flexible APIs. Nestipy integrates natively with Strawberry GraphQL, providing a type-safe and developer-friendly experience for building GraphQL schemas and resolvers within your modules."
    icon: 🕸️
  - title: "Type Safety & Validation"
    details: "Utilize Python's type hints to their fullest extent. Nestipy uses Pydantic or standard Dataclasses to ensure your data is validated and your API is self-documenting from the ground up."
    icon: ✅
  - title: "Decorator-Driven DX"
    details: "Experience a clean and intuitive API. Use decorators like @Controller, @Injectable, and @Module to define your application structure, reducing boilerplate and making your intentions clear."
    icon: 🎨

---

## Why Nestipy?

Python's web ecosystem is vast, with frameworks like FastAPI offering incredible speed and flexibility. However, as applications grow, maintaining a clear structure can become challenging. **Nestipy** solves this by bringing the architectural excellence of **NestJS** to the Python world.

### The Modular Spirit
In a Nestipy application, everything is a module. Whether it's a feature, a library, or a utility, encapsulating it within a module makes it easy to share, test, and maintain. This structure isn't just about organization; it's about creating a mental model that scales.

### Intuitive and Scalable
By combining Dependency Injection with Python's modern type system, Nestipy allows you to write code that is decoupled and easy to reason about. You don't just build APIs; you build systems.

### Enjoyable Development
We believe development should be fun. Nestipy's CLI, decorator-based syntax, and seamless integrations are all designed to minimize friction, so you can focus on what matters: building great software.

---

## Installation

Getting started is easy with the **Nestipy CLI**. It handles project scaffolding and service generation for you, ensuring you follow best practices from day one.

```bash
# Install the CLI globally
pip install nestipy-cli

# Create a new project
nestipy new my-awesome-project
```

Or install Nestipy directly:

```bash
pip install nestipy
```