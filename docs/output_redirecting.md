# Output Redirection Guide

Thanks to `cmd2`, we are allowed to redirect the output of nearly any command from `stdout` into other destinations, 
for example, a file.

```shell
# this will output the result on terminal
show -c
# this will output the result into a file called `output.txt`
show -c > output.txt
```

## Ensure UTF-8 Encoding

Notice that **there could be some encoding issues when writing into a non `UTF-8` encoded file** since some of the command output contain `UTF-8` characters.

To ensure the correct format, it's recommend to enable `utf8` mode with `Python` by setting the following 
environment variable to `1`

```
PYTHONUTF8=1
```

You may need to restart your terminal after editing the environment variable. To check if the operation success, you could run the following python code:

```python
import sys
print(sys.flags.utf8_mode)
```

If the output is `1`, then the UTF-8 mode has been successfully enabled.

> The [PEP 686](https://peps.python.org/pep-0686/) suggest UTF-8 be the default behaviour for `Python`, and we don't need to manually set the environment variable with Python version `>=3.15`