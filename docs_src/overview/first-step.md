# First Steps

Welcome to the Nestipy documentation! These articles are designed to guide you through the fundamental principles of building modern, modular APIs with Nestipy. Whether you're coming from NestJS, FastAPI, or you're new to modular architectures, you'll find that Nestipy provides a structured and enjoyable way to develop scalable Python applications.

In this guide, we'll walk through the initial setup and the core components of a Nestipy application.

## Prerequisites

Before we begin, ensure that you have **Python (version >= 3.10)** installed on your machine. Nestipy leverages modern Python features like `contextvars`, `generics`, and `annotated types`, so an up-to-date Python environment is essential.

## Setup

The most efficient way to start a new project is using the **Nestipy CLI**. It scaffolds a boilerplate project with a recommended structure, saving you time and ensuring you follow best practices from the start.

### 1. Install the CLI
```bash
pip install nestipy-cli
```

### 2. Create a New Project
```bash
nestipy new my-nestipy-app
```

The CLI will prompt you for some information and then generate a directory named `my-nestipy-app`.

## Project Structure

A typical Nestipy project follows a layout optimized for modularity. Here's a breakdown of the core files generated in the root and `src/` directory:

| File | Description |
| :--- | :--- |
| `main.py` | The entry point of the application. Handles bootstrapping and starting the server. |
| `app_module.py` | The root module of your application, which ties everything together. |
| `app_controller.py` | A basic controller providing an initial endpoint. |
| `app_service.py` | A simple service to demonstrate dependency injection. |
| `cli.py` | Configuration for CLI-related tasks. |
| `uv.lock` / `pyproject.toml` | Dependency management files (compatible with `uv`, `pip`, or `poetry`). |

## Bootstrapping the Application

The `main.py` file is where the magic starts. It uses the `NestipyFactory` to create an application instance based on your root `AppModule`.

```python
from granian.constants import Interfaces
from nestipy.core import NestipyFactory
from app_module import AppModule

# Create the application instance
app = NestipyFactory.create(AppModule)

if __name__ == '__main__':
    # Start the server using Granian (high-speed ASGI server)
    app.listen(
        "main:app",
        address="0.0.0.0",
        port=8000,
        interface=Interfaces.ASGI,
        reload=True,
    )
```

### NestipyFactory
The `NestipyFactory` is a static class that allows you to create an application instance. It's the core of the bootstrapping process, resolving the entire dependency tree starting from the `AppModule`.

### Server Deployment
By default, Nestipy uses **Granian** for its high performance. The `app.listen()` method handles the server startup. You can pass various options like `address`, `port`, and `reload` (useful during development).

::: tip
For simple use cases or embedding Nestipy into other scripts, you can use the compact mode:
```python
if __name__ == '__main__':
    app.listen(address="0.0.0.0", port=8000)
```
:::

## Platform Independence

One of Nestipy's strengths is its platform-agnostic design. While it provides a structured modular layer, the underlying ASGI execution is handled by a platform adapter.

Nestipy supports two primary platforms out of the box:

### 1. FastAPI (Default)
FastAPI is the industry standard for Python APIs, known for its robustness and great developer experience.
```python
from nestipy.core import FastApiApplication
app = NestipyFactory[FastApiApplication].create(AppModule)
```

### 2. BlackSheep
BlackSheep is focus on extreme performance and asynchronous execution.
```python
from nestipy.core import BlackSheepApplication
app = NestipyFactory[BlackSheepApplication].create(AppModule)
```

## Running the Application

To start your application in development mode with auto-reload enabled, use the CLI:

```bash
nestipy start --dev
```

Your API should now be running at `http://localhost:8000`. You can visit this URL to see your first Nestipy response!

---

**Next Up:** Learn how to organize your routes and handle requests in the [Controllers](/overview/controller) section.
