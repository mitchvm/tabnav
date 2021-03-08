# Todo

## Cell Edit mode

* (Shift+)Tab or (Shift+)Enter should jump to the neighbouring cell without selecting the current cell
* Up/down should do nothing
* Left/right movements should be restricted to the cell's edges
* All cell movement/selection commands should set `tabnav.cell_edit` to false.

## Cell Nav mode

* Left/Right/Up/Down should move out of the table when at the edge
* Left/Right/Up/Down should select the cell when moving from outside the table to inside the table 
* Add global, per-context settings to enable cell nav mode by default

## Refactor

* Consider a significant refactor of the commands to more closely resemble the built-in movement commands. See the default key bindings for the command list and arguments:
    - Commands:
        + `move`: move one unit defined with `by` argument
        + `move_to`: jump to target defined by `to` argument
    - Common Arguments:
        + `forward`: true to move right/down, false to move left/up
        + `extend`: true to extend the region, false to move the cursor
    
