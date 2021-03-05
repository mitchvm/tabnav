# TabNav Command Listing

The table below lists all of the commands provided by TabNav, and their arguments.

| Command Name                            | Required Arguments                                                          | Optional Arguments                                                    |
|:----------------------------------------|:----------------------------------------------------------------------------|:----------------------------------------------------------------------|
| `enable_tabnav`                         |                                                                             |                                                                       |
| `disable_tabnav`                        |                                                                             |                                                                       |
| `tabnav_set_csv_delimiter`              | `delimiter`: The character to use as delimiter for the CSV context.         |                                                                       |
| `tabnav_set_capture_level`              | [`capture_level`](#capture_level)                                           |                                                                       |
| `tabnav_reset_capture_level`            |                                                                             |                                                                       |
| `tabnav_move_cursor_current_cell`       | [Region&nbsp;`direction`](#region-direction)                                | [`context`](#context)                                                 |
| `tabnav_move_cursor`                    | [Movement&nbsp;`direction`](#movement-direction)                            | [`context`](#context)                                                 |
| `tabnav_add_cursor`                     | [Movement&nbsp;`direction`](#movement-direction)                            | [`context`](#context)                                                 |
| `tabnav_select_current`                 |                                                                             | [`context`](#context)<br>[Region&nbsp;`direction`](#region-direction) |
| `tabnav_select_next`                    | [Movement&nbsp;`direction`](#movement-direction)                            | [`context`](#context)                                                 |
| `tabnav_jump_end`                       | [Movement&nbsp;`direction`](#movement-direction)                            | [`context`](#context)                                                 |
| `tabnav_extend_selection`               | [Movement&nbsp;`direction`](#movement-direction)                            | [`context`](#context)                                                 |
| `tabnav_extend_end`                     | [Movement&nbsp;`direction`](#movement-direction)                            | [`context`](#context)                                                 |
| `tabnav_reduce_selection`               | [Movement&nbsp;`direction`](#movement-direction)                            | [`context`](#context)                                                 |
| `tabnav_select_row`                     |                                                                             | [`context`](#context)<br>[Region&nbsp;`direction`](#region-direction) |
| `tabnav_select_column`                  |                                                                             | [`context`](#context)<br>[Region&nbsp;`direction`](#region-direction) |
| `tabnav_select_all`                     |                                                                             | [`context`](#context)<br>[Region&nbsp;`direction`](#region-direction) |
| `tabnav_trim_whitespace_from_selection` |                                                                             |                                                                       |
| `tabnav_merge_adjacent_selections`      |                                                                             |                                                                       |
| `tabnav_copy_tab_separated`             |                                                                             |                                                                       |
| `tabnav_copy_delimited`                 | `delimiter`: The character to use as delimiter when merging copied regions. |                                                                       |

## Arguments

### `context`

Provide the name of a specific [context](README.md#contexts) to be used - the context name is the key to the context's JSON definition in the settings file. When not provided, TabNav automatically determines the applicable context.

### `capture_level`

One of `cell`, `markup`, `content`, or `trimmed`. See the [README](README.md#capture-levels) for details.

### `direction`

The `direction` arguments come in two forms: when moving/extending a selection, or when selecting a defined group of cells (current cell; row; column; table).

#### Movement `direction`

One of `up`, `down`, `left`, or `right`.

#### Region `direction`

One of `left` or `right`. When the region direction is optional, the default value is `right`.
