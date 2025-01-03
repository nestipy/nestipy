REPL(Read-Eval-Print-Loop) is a simple interactive environment that takes single user inputs, executes them, and returns
the result to the user. The REPL feature lets you inspect your dependency graph and call methods on your providers (and
controllers) directly from your terminal.

## Usage
To run your Nestipy application in REPL mode, run the following command in root of your project:
```bash

$ nestipy repl

```

Once it's up and running, you should see the following message in your console:

```bash
Nestipy REPL

>>> 
```

And now you can start interacting with your dependencies graph. For instance, you can retrieve an `AppService` (we are using the starter project and call the `get()` method for example:

```python
>>> await get(AppService).get()
'test'
```

To display all public methods available on a given provider or controller, use the `methods()` function, as follows:
```python
>>> methods(AppService)
AppService:
 ◻ delete
 ◻ get
 ◻ post
 ◻ put
```
To print all registered modules as a list together with their controllers and providers, use `debug()`.

```python
>>> debug(AppModule)
AppModule:
  - Controllers:
    ◻ AppController
  - Providers:
    ◻ AppService
```
