# Sudoku CLI Advanced Tutorial

Our system is developed based on standard REPL conventions, thus there's bunch of useful shortcuts available out of the box.

## Command History

You could use `history` command to list or manage your command history. Also, **you could use `🠙` and `🠛` on keyboard to quickly navigated to previous executed commands**.

## Tab Auto-complete

Theoretically, all places that is allowed to input command will be able to use `Tab` auto-complete feature. Program will **check and show all possible following part of the command** based on the part that has already be input. Also if **there is only one possible input left, `Tab` will auto-complete that command** for you.

Here is an example:

```shell
(Cmd) s    # press tab will print:
# sh       show     so       solve
(Cmd) sol  # press tab will trigger auto-complete
(Cmd) solve
```



## Command Alias

Our program support user-defined command alias (We've added some common alias by using startup scripts, like `p` for `put`, `n` for `newgames` etc. You could run `alias list` to check all alias currently available in the program)

Also, you could prefer to add your own alias using `alias` command. Check out more info using `help alias`.

Alias will also works with paramters, for example, if we have `n` as the alias for `newgame`, then both of following command is a legal command:

```
newgame -d 0.5
n -d 0.5
```

## Startup Scripts

You could edit `./sodukurc` files to add your own startup script, which will be executed upon CLI startup.