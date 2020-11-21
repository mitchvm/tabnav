# TabNav - Keyboard Navigation of Tabular Data

TabNav is a Sublime Text 3 plugin for keyboard navigation of tabular text data. Quickly move and select "cells" of text in the following formats, without taking your hands off the keyboard:

* CSV
* Markdown tables

TabNav also provides the ability to copy only the contents of the table, excluding markup, in a format that can be readily-pasted into other programs, such as Excel.

## Commands

TabNav adds the following commands to Sublime Text. They are all accessible via the Command Palette, as well as the the TabNav submenu under the Selection menu.

### Table Navigation Commands

The table navigation commands below only operate within the context of a table. All of the table commands are compatible with multiple cursors, and even multiple cursors in multiple, disjoint tables.

On initial invocation, all commands except the select row/column/table cells commands operate only cells that intersect the current selection(s). For example, if a line of text in a table is currently selected, all of the "Select" and "Extend selection" commands simply split the region into the table cells found on the line. Subsequent invocations will move/extend the selections.

The default keybindings are intended for use on a US-English QWERTY keyboard. They make heavy use of the cluster of four keys immediately to the left of the <kbd>Enter</kbd> key. If you are using a different keyboard layout, or simply want to customize your keybindings, all of the default keybindings can be individually disabled. See [Customization](#customization).

<table>
<tbody>
<tr>
<td align="center">Up<br><kbd>[</kbd>
</td>
</tr>
<tr>
<td align="center">Left <kbd>;</kbd> | <kbd>'</kbd> Right</td>
</tr>
<tr>
<td align="center"><kbd>/</kbd><br>Down</td>
</tr>
</tbody>
</table>

| Name                                 |                                   Windows/Linux Keybinding |                                  macOS Keybinding |
|:-------------------------------------|-----------------------------------------------------------:|--------------------------------------------------:|
| Move cursor to start of current cell |                                                            |                                                   |
| Move cursor to end of current cell   |                                                            |                                                   |
| Move cursor to cell on left          |                                <kbd>Alt</kbd>+<kbd>;</kbd> |                         <kbd>^</kbd>+<kbd>;</kbd> |
| Move cursor to cell on right         |                                <kbd>Alt</kbd>+<kbd>'</kbd> |                         <kbd>^</kbd>+<kbd>'</kbd> |
| Move cursor to cell above            |                                <kbd>Alt</kbd>+<kbd>[</kbd> |                         <kbd>^</kbd>+<kbd>[</kbd> |
| Move cursor to cell below            |                                <kbd>Alt</kbd>+<kbd>/</kbd> |                         <kbd>^</kbd>+<kbd>/</kbd> |
| Add cursor to cell on left           |                <kbd>Alt</kbd><kbd>Shift</kbd>+<kbd>;</kbd> |             <kbd>^</kbd><kbd>⇧</kbd>+<kbd>;</kbd> |
| Add cursor to cell on right          |                <kbd>Alt</kbd><kbd>Shift</kbd>+<kbd>'</kbd> |             <kbd>^</kbd><kbd>⇧</kbd>+<kbd>'</kbd> |
| Add cursor to cell above             |                <kbd>Alt</kbd><kbd>Shift</kbd>+<kbd>[</kbd> |             <kbd>^</kbd><kbd>⇧</kbd>+<kbd>[</kbd> |
| Add cursor to cell below             |                <kbd>Alt</kbd><kbd>Shift</kbd>+<kbd>/</kbd> |             <kbd>^</kbd><kbd>⇧</kbd>+<kbd>/</kbd> |
| Select current cell                  |                                                            |                                                   |
| Select cell on left                  |                               <kbd>Ctrl</kbd>+<kbd>;</kbd> |                         <kbd>⌘</kbd>+<kbd>;</kbd> |
| Select cell on right                 |                               <kbd>Ctrl</kbd>+<kbd>'</kbd> |                         <kbd>⌘</kbd>+<kbd>'</kbd> |
| Select cell above                    |                               <kbd>Ctrl</kbd>+<kbd>[</kbd> |                         <kbd>⌘</kbd>+<kbd>[</kbd> |
| Select cell below                    |                               <kbd>Ctrl</kbd>+<kbd>/</kbd> |                         <kbd>⌘</kbd>+<kbd>/</kbd> |
| Extend selection to cell on left     |               <kbd>Ctrl</kbd><kbd>Shift</kbd>+<kbd>;</kbd> |             <kbd>⌘</kbd><kbd>⇧</kbd>+<kbd>;</kbd> |
| Extend selection to cell on right    |               <kbd>Ctrl</kbd><kbd>Shift</kbd>+<kbd>'</kbd> |             <kbd>⌘</kbd><kbd>⇧</kbd>+<kbd>'</kbd> |
| Extend selection to cell above       |               <kbd>Ctrl</kbd><kbd>Shift</kbd>+<kbd>[</kbd> |             <kbd>⌘</kbd><kbd>⇧</kbd>+<kbd>[</kbd> |
| Extend selection to cell below       |               <kbd>Ctrl</kbd><kbd>Shift</kbd>+<kbd>/</kbd> |             <kbd>⌘</kbd><kbd>⇧</kbd>+<kbd>/</kbd> |
| Select row cells                     |               <kbd>Ctrl</kbd><kbd>Shift</kbd>+<kbd>L</kbd> |             <kbd>⌘</kbd><kbd>⇧</kbd>+<kbd>L</kbd> |
| Select column cells                  |               <kbd>Ctrl</kbd><kbd>Shift</kbd>+<kbd>C</kbd> |             <kbd>⌘</kbd><kbd>⇧</kbd>+<kbd>C</kbd> |
| Select all table cells               | <kbd>Ctrl</kbd><kbd>Alt</kbd><kbd>Shift</kbd>+<kbd>C</kbd> | <kbd>⌘</kbd><kbd>^</kbd><kbd>⇧</kbd>+<kbd>C</kbd> |

### Other Commands

In addition to the table navigation commands, the following commands are provided for configuration or convenience. These commands will operate even outside the context of a table.

| Name                                    |                                   Windows/Linux Keybinding |                                  macOS Keybinding | Description                                                                                                                                                                                                                 |
|:----------------------------------------|-----------------------------------------------------------:|--------------------------------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Enable on current view                  |                               <kbd>Ctrl</kbd>+<kbd>'</kbd> |                         <kbd>⌘</kbd>+<kbd>'</kbd> | Enables TabNav on the current view. Note, once enabled, the keybinding is clobbered by the "Move cursor to cell on right" command.                                                                                          |
| Disable on current view                 | <kbd>Ctrl</kbd><kbd>Alt</kbd><kbd>Shift</kbd>+<kbd>'</kbd> | <kbd>⌘</kbd><kbd>^</kbd><kbd>⇧</kbd>+<kbd>'</kbd> | Disables TabNav on the current view.                                                                                                                                                                                        |
| Include separator lines in selections   |                                                            |                                                   | Configures TabNav to include row separator lines in selections and movements. By default, they are excluded.                                                                                                                |
| Exclude separator lines from selections |                                                            |                                                   | Configures TabNav to exclude row separator lines from selections and movements.                                                                                                                                             |
| Set CSV delimiter                       |                                                            |                                                   | Sets the delimiter to use for CSV files. See [CSV Compatibility](#csv-compatibility) for more information.                                                                                                                  |
| Trim whitespace from selections         |                                <kbd>Alt</kbd>+<kbd>W</kbd> |                         <kbd>^</kbd>+<kbd>W</kbd> | Removes all whitespace characters from either end of all current selections.                                                                                                                                                |
| Copy selections as TSV                  |                                                            |                                                   | Copies all current selections as tab-delimited data, with all selections on the same row of text tab-separated and a newline between selection row. This is useful, for example, to copy data from a text table into Excel. |
| Copy selections with delimiter          |                                                            |                                                   | Same as the "Copy selections as TSV" command, but prompts the user to input the delimiter to use.                                                                                                                           |

