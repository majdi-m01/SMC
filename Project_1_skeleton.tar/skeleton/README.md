# Secure Multi-party Computation System

In this project, you will develop a secure multi-party computation system in
Python 3. We provide this code skeleton to help with the development.

### Skeleton
You will have to implement the SMC client, the trusted parameter generator,
secret sharing mechanisms, and tools for specifying expressions to compute. We
already implemented network communications and the trusted server, along with a
test suite that your implementation will have to pass.

#### Files in the skeleton

The skeleton contains the following files.

Components for building an SMC protocol. You should modify these:
* `expression.py`—Tools for defining arithmetic expressions.
* `secret_sharing.py`—Secret sharing scheme
* `ttp.py`—Trusted parameter generator for the Beaver multiplication scheme.
* `smc_party.py`—SMC party implementation

We also provide tests. Feel free to add your own:
* `test_integration.py`—Integration test suite (do not modify this file, they
  should run as is)
* `test_expression.py`—Template of a test suite for expression handling.
* `test_ttp.py`—Template of a test suite for the trusted parameter generator.
* `test_secret_sharing.py`—Template of a test suite for secret sharing.

Code that handles the communication. You should not need to modify these files unless
you bump into some serialization issues. But you'll need to use the classes defined
in `protocol.py` and `communication.py` to enable your SMC clients:
* `protocol.py` — Specification of SMC protocol
* `communication.py` — SMC party-side of communication
* `server.py` — Trusted server to exchange information between SMC parties (you
  shouldn't need to modify this file)

Read the comments in each of the files for more details and pointers.

#### Requirements and what files should you change
As you can see above, you can change most of the files in this skeleton.
However, the **requirement** is that all existing tests in `test_integration.py`
should pass **without any modification** (you can, however, add new tests.) We
will test your solution using our own version of ``test_integration.py`` and all
failing tests will negatively contribute to the grade.

### Testing

An integral part of a system development is testing.
For this first project, we provide you with an integration test suite to ensure
the functionalities you will have to implement works correctly.

They are implemented using *pytest*, and you can run them using the command
```
python3 -m pytest
```
in the directory of the skeleton.

If you want to run only one specific test suite, you can specify the file in
the command line. For example, if we only want to test our implementation for
handling the expression, we will run the following command:
```
python3 -m pytest test_expression.py
```

In some versions, pytest captures the program output, and only displays the
result of the test. When debugging, you can disable this capture by passing the
option `-s` to Pytest.
```
python3 -m pytest -s
```
(This is particularly helpful when running integration tests as the nature of
the solution with multiple processes might causes tests to hang without output
otherwise.)

When running the integration test suite, you will notice that it will run SMC
parties and trusted server as independent processes and that these processes
will communicate via a network.

You are free to write additional test suites to ensure your code is working as
you expect. Consult the description of the files in the project for some
skeleton test files.

## Setting up the development environment

This code was implemented and tested with Python 3.9, you may want to install a
higher version, in which case, ensure that you only use features supported by
Python 3.9 in your code. (All code also works flawlessly with Python 3.6, in
case your system only supports an older version.)

We recommend using a virtual environment to ease installing of dependencies. To
set it up, you run inside the skeleton directory:
```
python3 -m venv venv
```
You only need to setup the virtual environment once. You can then subsequently
activate it using

```
source venv/bin/activate       # On Mac/Linux
venv\Scripts\activate.bat      # On Windows
```
(You will need to call this every time you (re)open a terminal.)

You can then install the dependant python libraries by running the command
```
python3 -m pip install -r requirements.txt
```
in the directory of the skeleton.

The name given to the Python binary might differ depending on your system,
sometimes you specifically have to use `python3` in others, the command might
simply be called `python`. So when running the commands we provide, ensure you
are using the correct interpreter.

**Note:** For your curiosity, the network communications rely on the library
*Requests*, and on the *Flask* framework, while the tests are implemented with
the *pytest* framework. Feel free to consult their documentation, if you would
like to understand in details how they work, and feel free to have a look at the
files `communication.py`, `server.py`, and at the test suites to see how we use
these library and frameworks in practice. Understanding these internals,
however, is not needed to complete the project.

### Collaboration

You can use git repositories to sync your work with your teammates. However,
keep in mind that you are not allowed to use public repositories, so make sure
that your repository is **private**.

## Example of a test run

Once a part of your project is finished, you can test if it works correctly with
*pytest*.  Here is an example of output that the tests might produce if your
project is well implemented.

```
python3 -m pytest -s
============================= test session starts =============================
platform linux -- Python 3.6.9, pytest-6.2.2, py-1.10.0, pluggy-0.13.1
rootdir: /home/student/Desktop/solution
plugins: cov-2.11.1
collected 25 items

test_expression.py .
test_integration.py [ PUBLISH  ] SENDER Alice / LABEL final
Alice has finished!
Server stopped.
.[ PUBLISH  ] SENDER Alice / LABEL final
Alice has finished!
Server stopped.
.[ SEND     ] SENDER Alice / LABEL 4f3963326a673d3d / RECEIVER Bob
[ SEND     ] SENDER Bob / LABEL 434e38516c413d3d / RECEIVER Alice
[ SEND     ] SENDER Alice / LABEL 3067437662413d3d / RECEIVER Bob
[ RETRIEVE ] RECEIVER Bob / LABEL 4f3963326a673d3d
[ RETRIEVE ] RECEIVER Alice / LABEL 434e38516c413d3d
[ RETRIEVE ] RECEIVER Bob / LABEL 3067437662413d3d
[ PUBLISH  ] SENDER Alice / LABEL final
[ PUBLISH  ] SENDER Bob / LABEL final
[ RETRIEVE ] RECEIVER Alice. LABEL final / SENDER Bob
[ RETRIEVE ] RECEIVER Bob. LABEL final / SENDER Alice
Alice has finished!
Bob has finished!
Server stopped.
.[ SEND     ] SENDER Alice / LABEL 3562684370413d3d / RECEIVER Bob
[ SEND     ] SENDER Bob / LABEL 4d6d706f35673d3d / RECEIVER Alice
[ RETRIEVE ] RECEIVER Alice / LABEL 4d6d706f35673d3d
[ RETRIEVE ] RECEIVER Bob / LABEL 3562684370413d3d
[ PUBLISH  ] SENDER Alice / LABEL final
[ PUBLISH  ] SENDER Bob / LABEL final
[ RETRIEVE ] RECEIVER Alice. LABEL final / SENDER Bob
[ RETRIEVE ] RECEIVER Bob. LABEL final / SENDER Alice
Alice has finished!
Bob has finished!
Server stopped.
.[ SEND     ] SENDER Alice / LABEL 783156716e773d3d / RECEIVER Bob

...

[ RETRIEVE ] RECEIVER Bob. LABEL final / SENDER Alice
Bob has finished!
Server stopped.
.
test_secret_sharing.py ..

======================= 25 passed in 116.59s (0:01:56) ========================
```

**Note:** You might encounter some warnings when running the tests.
In this case, all of them were related to the libraries used in the project, so
they were not related to the project code by itself.
If you encounter some warning, you might pay attention to them if some relate
to your code, they might reveal some code soon to be obsolete, or some part of
your code that you might want to change.
