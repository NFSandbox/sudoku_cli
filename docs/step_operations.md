# Tracing Your Steps

## Show Steps

This game program could **remember the put operations you made** from the beginning of a newgame.

To check your most recent steps*(put operations)*, run one of the following line:

```shell
step show
ss           # alias to step show
```

Or if you **want a more succinct output**, use `--short` args:

```shell
step show --short
step show -s
sss                  # alias to step show --short
```

### Steps Count To Show

By default, **only 10 most recent steps were displayed**. You could use `r`/`--recent` to override this settings:

```shell
step show --recent 100        # show 100 most recent steps
ss -r 100
```

## Reverting Your Operations

Our program allow you to revert the state of the game back to a certain previous point.

### Specify The Revert Point

There are **two ways to specify which previous point you want to go back to**:

- `--by n`/`-b n` **You want to revert your operation by `n` steps**, which will just like that the latest `n` put operations are not exists.
- `--to n`/`-t n` **You want to revert back to the `n`-th operation you made**, just like only first `n` put operations are made, all others will be ignored.

### Examples

Consider that we have the following put operations:

```
                  Steps History
    Index      Operation        Time Elapsed     
     [1]     (1, 1): - -> 1    0:00:05.453143
     [2]     (1, 1): 1 -> 2    0:00:07.274287
     [3]     (1, 1): 2 -> 3    0:00:08.663297
     [4]     (1, 1): 3 -> 4    0:00:10.188698
     [5]     (1, 1): 4 -> 5    0:00:11.431866
```

At this point, if we run `step revert --by 2`, we would get a result that just like we had performed the following put:

```
                  Steps History
    Index      Operation        Time Elapsed     
     [1]     (1, 1): - -> 1    0:00:05.453143
     [2]     (1, 1): 1 -> 2    0:00:07.274287
     [3]     (1, 1): 2 -> 3    0:00:08.663297
```

And similarly, if we run `step revert --to 2`, we would get:

```
                  Steps History
    Index      Operation        Time Elapsed     
     [1]     (1, 1): - -> 1    0:00:05.453143
     [2]     (1, 1): 1 -> 2    0:00:07.274287
```

Now let's try it out yourself! Hope you love this feature~