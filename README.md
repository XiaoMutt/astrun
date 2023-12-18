# Introduction

The astrun package is to provide a "relative" secure way to evaluate Python expressions similar to Python's `eval`,
as the builtin `eval` and `exec` are insecure and can be exploited in many ways.

This package is very small and need no dependencies. You can just copy, modify and use. Happy Programming.

# Use Cases

- you want to build a web calculator do simple math calculations or string operations.
- you want to give certain users high flexibility to configure some conditions. E.g.
    - to determine if a file path is good for further process.
    - to customize string transformations.

# Examples

```
Astrun.eval("1 in {i for i in range(10) if i % 2 == 1}") # return True

Astrun.eval("__import__('os')") # will through PermissionError
Astrun.eval("open('file', 'w')") # will through PermissionError
```

For more examples, see the test code in `test` and the source code in `src`.

NOTICE: this library can only be used in Python >= 3.11 because it used * unpacking in subscription which is a
feature introduced in Python 3.11. If you would like to use it in earlier Python versions, change the code in
Astrun.visit_Subscript to other ways of unpacking.

# How It Works

`Astrun` evaluates the given code text as instructions only, and the execution is done by `Astrun`'s own code:

- `Astrun` uses the ast library to parse the code text to an Abstract Syntax Tree (AST).
- The tree is then executed by translating each node back to `Astrun`'s own Python code.
    - The execution is within a namespace that excludes the dangerous builtins functions such as
      `eval`, `exec`,`globals`, `__import__`, etc.
    - Advanced AST nodes, such as function and class definition, are blocked.
    - Private or dunder attributes' access of any object is prohibited.

However, using `Astrun` alone is still not secure for a server to execute arbitrary code texts, because a user
can still provide code that

- overloads the CPU. e.g. `1024**1024**1024**1024`
- causes memory overflow. e.g. `[0] * (1024*1024*1024*1024)`
- exploits other ways to access system IO or network

Therefore, `IsolatedEnv` is provided (**ATTENTION: Linux Only, not even Mac OS**) to isolate any code execution in a
separated constraint Python Process:

- the total memory is limited.
- the total CPU time is limited.
- file descriptor creation is blocked.
- subprocess creation is blocked.
- the response time of a single execution is timed.
- if any restriction violated the Process is terminated.

E.g.

```
class AstrunIsolatedEnv(IsolatedEnv)
    @staticmethod
    def _run(args):
        return Astrun.eval(args)

with AstrunIsolatedEnv() as env:
    assert env("1+1")==2
```

# Safety Warnings

It is NOT guaranteed that arbitrary code can be executed harmlessly by using `Astrun` inside a `IsolatedEnv` . Since
users provided the code text, they may find loopholes to bypass the restrictions and Python is nothing short of
convenient loopholes.

Therefore, if you use `astrun` to run arbitrary users code text, make sure the OS account to run the process is
restricted (no sudo, no access to important files, etc.).

It is better to only expose `astrun` to the responsible users, such as the admins of your webapp, and log the users and
the code text they provide.

# Last But Not Least

I searched the web for a long time for a package like `astrun` but cannot find one, so I made my own. If you find a
loophole of `astrun`, please open an issue and submit it, so that it can be blocked.

Or maybe it cannot be blocked. Then, it explains why no such package exists. An alternative way is to run JavaScript in
Python, since JavaScript has no IO access, so it is IO safe. However, import a JavaScript engine into a Python
program is likely an overkill.

# LICENSE

Can you believe it is "MIT"!
