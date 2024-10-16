# Introduction To Sudoku Game

**[Sudoku](https://en.wikipedia.org/wiki/Sudoku)** _(/suːˈdoʊkuː, -ˈdɒk-, sə-/; Japanese: 数独, romanized: sūdoku, lit. 'digit-single'_, is a **logic-based, combinatorial number-placement puzzle**. 

In classic Sudoku, the objective is to **fill a 9 × 9 grid with digits so that each column, each row**, and **each of the nine 3 × 3 subgrids** that compose the grid (also called "boxes", "blocks", or "regions") **contains all of the digits from 1 to 9**.

<br>

> This introductions comes from Wikipedia.

# Used Packages

- `cmd2` Create modern REPL applications in Python.
- `sudokutools` Simple yet powerful tools for sudoku games.
- `rich` Print everything in a prettier way.

# Sudoku CLI Game Tutorial

## Create New Game

To start a new game, run `newgame` and program will show you a Sudoku grid, then you can use `put` command to put number into the grids.

```shell
newgame      # create a new game
put 1 2 5    # set value=5 for block that column=1, row=2
```

## Show Current Game Process

To show the grid of currently-going Sudoku game, run `show` (or alias `sh`). To check the candidates of unfilled grids, run one of following command:

```shell
show --candidates   # show candidates
show -c             # using abbr
sh -c               # using alias
```

## Commands Help

All commands in this program are well-documented. Run `help [command_name]` or `[command_name] help` to check deteild help message for a certain command.

For example, for help text or put command, you could run one of the following command:

```shell
help put
put --help
put -h
p -h
```

There are lots of other useful commands that we could not fully covered in this simple guide, please using the `help` command to check out those wonderful commands yourself.

That's all for this introductions, have a good time, you may want to use `newgame` to start a new game now!