# Quickstart
## Install the package
```{note}
You need the Foundry Nuke installed and a valid licence to use this package.
Download nuke [here](https://www.foundry.com/product-downloads).
```

To use this package you need to install it first from pypi:
```shell
pip install git+https://github.com/cglukas/NukeTesting.git@main#egg=nuketesting
```
Afterwards check the installation by running the nuke-testrunner one:
```shell
nuke-testrunner --help
```
The output should look like this:
```text
Usage: nuke-testrunner [OPTIONS]

  Nuke Test Runner CLI Interface.

  This bootstraps Nuke within the test runner to be able to run pytest like
  usual, with all Nuke dependencies.

  `nuke-executable` is the filepath to the nuke executable. If you provided a
  "runner.json" configuration, you can also reference the runner by its
  configured name.

  `test-path` is the folder of file of the tests you want to execute. Use the
  pytest folder/file.py::class::method notation to run single tests. For
  further options consult the pytest documentation.

  If you don't specify the test-path it will use the current directory like
  pytest does.

Options:
  -n, --nuke-executable PATH      Path to the executable of Nuke.
  -t, --test-path PATH            Directory to test. This defaults to the
                                  current directory and will search for tests
                                  in that folder recursively like pytest does.
  -c, --config PATH               Specify a json to read as config to use for
                                  the tests.
  -r, --runner-name TEXT          Only run the runners in the config specified
                                  with this name
  --run-in-terminal-mode, --terminal BOOLEAN
                                  Launch a Nuke interpreter to run the tests
                                  in. This defaults to True.
  -p, --pytest-arg TEXT           Specify an arg to forward to pytest. You can
                                  add as many of these as you want.
  --help                          Show this message and exit.
```

## Run your first test

Next step is to run your first test. 
Let's create a simple unit test that checks if a nuke node can be created.
Create a `tutorial.py` file and add the following content:
```python
import nuke

def test_nuke_creation() -> None:
    """Test that nuke nodes can be created."""
    assert nuke.createNode("Blur")
```
The last step is to check if this test works.
Open up a shell in the directory of `tutorial.py` and run the following command:
```shell
nuke-testrunner --nuke-executable <your_path_to_nuke> --test-path tutorial.py
```
Nuke will start up and execute the test with pytest. 
You should see something like this output:

```text
Nuke 15.1v1, 64 bit, built Jun  6 2024.
...
Inserted packages for the NukeTestRunner successfully. Starting tests...
================================ test session starts =================================
platform win32 -- Python 3.10.10, pytest-8.3.3, pluggy-1.5.0
rootdir: C:\Users\Lukas
plugins: anyio-4.4.0, cov-5.0.0, html-4.1.1, metadata-3.1.1
collected 1 item

.\tutorial.py .                                                                 [100%] 

================================= 1 passed in 0.13s ==================================
```
If everything worked, congratulations! 
You can now start testing your nuke gizmos, plugins and python packages.

If something did not work, please open an issue in [github](https://github.com/cglukas/NukeTesting/issues).