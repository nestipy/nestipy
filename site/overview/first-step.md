These articles will teach you the basic principles of Nestipy. You'll get to know its key components by building a simple CRUD application, which will introduce you to various beginner-level features.
## Prerequisites
Please make sure that <strong>Python</strong> (version >= 3.10) is installed on your operating system.

## Setup
Starting a fresh project using the <strong>Nestipy CLI</strong> is simple. Just configure Python's environment and run these commands in your OS terminal to create a new Nestipy project.
```bash

pip install nestipy-cli
nestipy new project-name
```
Upon execution, a directory named `project-name` will be generated, containing a src/ directory filled with essential core files.

```
├── app_module.py
├── app_controller.py
├── app_service.py
├── main.py
|── cli.py
|── uv.lock
|── pyproject.yaml
|── README.md
├── src
│    ├── __init__.py
```

The main.py file contains an instance of application and bootstrapping it with uvicorn.

```python
import uvicorn
from nestipy.core import NestipyFactory

from app_module import AppModule

app = NestipyFactory.create(AppModule)

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
```

## Platform
In essence, Nestipy can function with any ASGI framework once an adapter is developed. It inherently supports two ASGI platforms: <strong>FastAPI</strong> and <strong>BlackSheep</strong>. You have the freedom to select the one that aligns most closely with your requirements.
By default, Nestipy use FastAPI adapter.  We can specify platform from NestipyFactory.

```python
from nestipy.core import FastApiApplication

app = NestipyFactory[FastApiApplication].create(AppModule)

```
Or with blacksheep

```python
from nestipy.core import BlackSheepApplication

app = NestipyFactory[BlackSheepApplication].create(AppModule)
```

## Running the application#

After installation, simply run this command in your OS terminal to start the application and listen for incoming HTTP requests:

```bash
nestipy start --dev
```
Take a look **[here](https://github.com/nestipy/sample/tree/main/sample-app)** for an  example.

<br/>

























