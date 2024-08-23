[![Supported Nuke](https://img.shields.io/badge/supported_nuke-13+-yellow)](https://www.foundry.com/products/nuke-family/nuke)
[![Python Versions](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
# NukeTesting
This project is focused on testing nuke nodes with python.
It can be used to enhance your plugin and gizmo development.
The main goal is to make pipelines and tools more stable.

The biggest benefit of tests is that you reduce the risk of regressions.
That's amazing if you constantly try to improve your tools. 
Tests allow you to be notified when you re-introduce known issues or unexpected behaviour.


## Installation
You can install the latest pre-release using this command:
```bash
pip install git+https://github.com/cglukas/NukeTesting.git@main#egg=nuketesting
```

However, for the future it is planned to add the releases to PyPI.

## How to use
The main starting point is our test runner.
This is used to run tests with nuke.

### Configure the test runner
The runner config is a simple JSON file.
It's recommended to use this if you want to test multiple nuke versions in parallel. 

If you just have one fixed version, you can simply use the `-n` option with the path to the nuke executable. 

JSON schema: 
```json
{
"runner_name": {
        "exe": "path to nuke executable",
        "args": ["(optional) list of arguments for nuke"],
        "run_in_terminal_mode": "Default: true. True to run in a native Nuke instance, false to run native python",
        "pytest_args": ["(optional) list of arguments to pass to pytest"]
    }
}
```

The minimal configuration is the runner name and the `exe` path to nuke.

Referencing the runners config can be done by the `--config` option.
Keep in mind to specify a runner name with `--runner-name`:

```bash
nuke-testrunner --config <runners.json> --runner-name nuke14 -t ./tests
```

> [!NOTE]
> For a comprehensive list of commandline options use the `--help` option.

### Using the test library 

Once you have the testrunner configured, you can start writing your tests.
This project is not teaching the concepts of testing.
Search the web for best practises on that topic.

This project provides classes and methods that help you test common nuke operations.
Planned utilities are:
- image 2 image checks
- boundingbox checks
- metadata comparisons
- node tree comparisons

## Contribute to this project
Contributions are very welcome.
Try to follow the pep guide and consider using ruff for linting.
If possible try to document your classes and function on how to use them. 
Only use inline comments for very obscure and difficult to understand concepts.

### Contribute quickstart
It is easiest to use rye to setup this project. However it is not required, as you can also setup all packages using the .lock files.

Once done, sync the dependancies:
```bash
rye sync
```

From now on, you can test the nuke-testrunner in your shell with:

```bash
rye run nuke-testrunner --help
```

#### Unit tests

We recommend to run the unit tests locally before pushing.
A convenient way is by using `rye`:

```bash
rye test
```

Besides the plain python unit tests, we also have unit tests that require nuke.
In that case, you can use the package `nuke-testrunner`

```bash
rye run nuke-testrunner -n <path_to_nuke> -t ./tests
```

> [!IMPORTANT]
> This package is developed in the spare time, so replies might not come as quickly as you might wish.
