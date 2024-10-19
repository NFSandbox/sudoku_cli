# Customize Your Game

This game provide several features that allows you to comtomize the shapes of the game generated when using `newgame` command.

## Difficulty

You could use `-d`/`--difficulty` to specify the factor of the difficulty of the newly created game. Difficulty should be a `float` number in range `[0, 1]`.

```shell
newgame -d 0.5
```

Generally, a **higher number represents more blank grids, thus a more challenging game**.

## Symmetry

When generating games by difficulty, you could also specify the symmetric behaviour! All supported symmetry pattern is listed below:

- rotate-90
- rotate-180
- mirror-x
- mirror-y
- mirror-xy

You could use this args with `newgame` command:

```shell
newgame -d 0.5 --symmetry rotate-90
```

## Templates

Game Template is a feature in this program that allow you to **completely take control of the shape of the generated games**, you could try the following pattern.

```shell
newgame --template cat
newgame --template fish
```

All template bit-mask patterns are stored in `data/templates.py`, you could add new templates into the `TEMPLATE_DICT` Python dictionary, and then it could be used as the template be specifying the key name of the dictionary when using `newgame` command.

> Notice that **not every bit-mask is a valid bit-mask of Sudoku game**, and this program will throw error if no valid games could be generated from the given template after a maximum amount of times of attempt.