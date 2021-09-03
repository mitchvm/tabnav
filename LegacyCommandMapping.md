# Legacy Command Mapping

Beginning with v3.5, the TabNav commands were significantly refactored to be more inline with the built-in Sublime Text movement commands, and reduce the number of command objects that need to be created for each view. The legacy commands are officially deprecated, but will continue to be supported until a forthcoming v4.0 release.

The table below details the mapping from the legacy commands to the new commands.

<table>
<thead>
<tr>
<th align="left">Action</th>
<th align="left">Legacy Command (&lt;v3.5)</th>
<th align="left">New Command (&ge;v3.5)</th></tr>
</thead>
<tbody>
<tr>
<td>Move cursor to cell above</td>
<td><pre>
<code>"command": "tabnav_move_cursor",
"args": { "direction": "up" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": {
    "scope": "column",
    "forward": false,
    "select": false
}</code>
</pre></td>
</tr><tr>
<td>Move cursor to cell below</td>
<td><pre>
<code>"command": "tabnav_move_cursor",
"args": { "direction": "down" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": {
    "scope": "column",
    "select": false
}</code>
</pre></td>
</tr><tr>
<td>Move cursor to cell on left</td>
<td><pre>
<code>"command": "tabnav_move_cursor",
"args": { "direction": "left" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": {
    "scope": "row",
    "forward": false,
    "select": false
}</code>
</pre></td>
</tr><tr>
<td>Move cursor to cell on right</td>
<td><pre>
<code>"command": "tabnav_move_cursor",
"args": { "direction": "right" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": {
    "scope": "row",
    "select": false
}</code>
</pre></td>
</tr><tr>
<td>Add cursor to cell above</td>
<td><pre>
<code>"command": "tabnav_add_cursor",
"args": { "direction": "up" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": {
    "scope": "column",
    "forward": false,
    "select": false,
    "extend": 1
}</code>
</pre></td>
</tr><tr>
<td>Add cursor to cell below</td>
<td><pre>
<code>"command": "tabnav_add_cursor",
"args": { "direction": "down" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": {
    "scope": "column",
    "select": false,
    "extend": 1
}</code>
</pre></td>
</tr><tr>
<td>Add cursor to cell on left</td>
<td><pre>
<code>"command": "tabnav_add_cursor",
"args": { "direction": "left" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": {
    "scope": "row",
    "forward": false,
    "select": false,
    "extend": 1
}</code>
</pre></td>
</tr><tr>
<td>Add cursor to cell on right</td>
<td><pre>
<code>"command": "tabnav_add_cursor",
"args": { "direction": "right" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": {
    "scope": "row",
    "select": false,
    "extend": 1
}</code>
</pre></td>
</tr><tr>
<td>Select cell above</td>
<td><pre>
<code>"command": "tabnav_select_next",
"args": { "direction": "up" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": {
    "scope": "column",
    "forward": false
}</code>
</pre></td>
</tr><tr>
<td>Select cell below</td>
<td><pre>
<code>"command": "tabnav_select_next",
"args": { "direction": "down" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": { "scope": "column" }</code>
</pre></td>
</tr><tr>
<td>Select cell on left</td>
<td><pre>
<code>"command": "tabnav_select_next",
"args": { "direction": "left" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": {
    "scope": "row",
    "forward": false
}</code>
</pre></td>
</tr><tr>
<td>Select cell on right</td>
<td><pre>
<code>"command": "tabnav_select_next",
"args": { "direction": "right" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": { "scope": "row" }</code>
</pre></td>
</tr><tr>
<td>Extend selection to cell above</td>
<td><pre>
<code>"command": "tabnav_extend_selection",
"args": { "direction": "up" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": {
    "scope": "column",
    "forward": false,
    "extend": 1
}</code>
</pre></td>
</tr><tr>
<td>Extend selection to cell below</td>
<td><pre>
<code>"command": "tabnav_extend_selection",
"args": { "direction": "down" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": {
    "scope": "column",
    "extend": 1
}</code>
</pre></td>
</tr><tr>
<td>Extend selection to cell on left</td>
<td><pre>
<code>"command": "tabnav_extend_selection",
"args": { "direction": "left" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": {
    "scope": "row",
    "forward": false,
    "extend": 1
}</code>
</pre></td>
</tr><tr>
<td>Extend selection to cell on right</td>
<td><pre>
<code>"command": "tabnav_extend_selection",
"args": { "direction": "right" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": {
    "scope": "row",
    "extend": 1
}</code>
</pre></td>
</tr><tr>
<td>Reduce selection upwards</td>
<td><pre>
<code>"command": "tabnav_reduce_selection",
"args": { "direction": "up" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": {
    "scope": "column",
    "forward": false,
    "extend": -1
}</code>
</pre></td>
</tr><tr>
<td>Reduce selection downwards</td>
<td><pre>
<code>"command": "tabnav_reduce_selection",
"args": { "direction": "down" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": {
    "scope": "column",
    "extend": -1
}</code>
</pre></td>
</tr><tr>
<td>Reduce selection to the left</td>
<td><pre>
<code>"command": "tabnav_reduce_selection",
"args": { "direction": "left" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": {
    "scope": "row",
    "forward": false,
    "extend": -1
}</code>
</pre></td>
</tr><tr>
<td>Reduce selection to the right</td>
<td><pre>
<code>"command": "tabnav_reduce_selection",
"args": { "direction": "right" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move",
"args": {
    "scope": "row",
    "extend": -1
}</code>
</pre></td>
</tr><tr>
<td>Select cell at top of column</td>
<td><pre>
<code>"command": "tabnav_jump_end",
"args": { "direction": "up" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move_end",
"args": {
    "scope": "column",
    "forward": false
}</code>
</pre></td>
</tr><tr>
<td>Select cell at bottom of column</td>
<td><pre>
<code>"command": "tabnav_jump_end",
"args": { "direction": "down" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move_end",
"args": { "scope": "column" }</code>
</pre></td>
</tr><tr>
<td>Select cell at beginning of row</td>
<td><pre>
<code>"command": "tabnav_jump_end",
"args": { "direction": "left" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move_end",
"args": {
    "scope": "row",
    "forward": false
}</code>
</pre></td>
</tr><tr>
<td>Select cell at end of row</td>
<td><pre>
<code>"command": "tabnav_jump_end",
"args": { "direction": "right" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move_end",
"args": { "scope": "row" }</code>
</pre></td>
</tr><tr>
<td>Extend selection to top of column</td>
<td><pre>
<code>"command": "tabnav_extend_end",
"args": { "direction": "up" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move_end",
"args": {
    "scope": "column",
    "forward": false,
    "extend": true
}</code>
</pre></td>
</tr><tr>
<td>Extend selection to bottom of column</td>
<td><pre>
<code>"command": "tabnav_extend_end",
"args": { "direction": "down" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move_end",
"args": {
    "scope": "column",
    "extend": true
}</code>
</pre></td>
</tr><tr>
<td>Extend selection to beginning of row</td>
<td><pre>
<code>"command": "tabnav_extend_end",
"args": { "direction": "left" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move_end",
"args": {
    "scope": "row",
    "forward": false,
    "extend": true
}</code>
</pre></td>
</tr><tr>
<td>Extend selection to end of row</td>
<td><pre>
<code>"command": "tabnav_extend_end",
"args": { "direction": "right" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move_end",
"args": {
    "scope": "row",
    "extend": true
}</code>
</pre></td>
</tr><tr>
<td>Move cursor to beginning of current cell</td>
<td><pre>
<code>"command": "tabnav_move_cursor_current_cell",
"args": { "direction": "left" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move_end",
"args": {
    "by": "cell",
    "forward": false
}</code>
</pre></td>
</tr><tr>
<td>Move cursor to end of current cell</td>
<td><pre>
<code>"command": "tabnav_move_cursor_current_cell",
"args": { "direction": "right" }</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move_end",
"args": { "by": "cell" }</code>
</pre></td>
</tr><tr>
<td>Extend selection to beginning of current cell</td>
<td><pre>
<code>N/A (new with v3.5)</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move_end",
"args": {
    "by": "cell",
    "forward": false,
    "extend": true
}</code>
</pre></td>
</tr><tr>
<td>Extend selection to end of current cell</td>
<td><pre>
<code>N/A (new with v3.5)</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_move_end",
"args": {
    "by": "cell",
    "extend": true
}</code>
</pre></td>
</tr><tr>
<td>Select current cell<sup>1</sup></td>
<td><pre>
<code>"command": "tabnav_select_current"</code></pre></pre>
<td><pre>
<code>"command": "tabnav_select",
"args": { "scope": "cell" }</code>
</pre></td>
</tr><tr>
<td>Select all cells in current row<sup>1</sup></td>
<td><pre>
<code>"command": "tabnav_select_row"</code></pre></pre>
<td><pre>
<code>"command": "tabnav_select",
"args": { "scope": "row" }</code>
</pre></td>
</tr><tr>
<td>Select all cells in current column<sup>1</sup></td>
<td><pre>
<code>"command": "tabnav_select_column"</code></pre></pre>
<td><pre>
<code>"command": "tabnav_select",
"args": { "scope": "row" }</code>
</pre></td>
</tr><tr>
<td>Select all cells in table<sup>1</sup></td>
<td><pre>
<code>"command": "tabnav_select_all"</code></pre></pre>
<td><pre>
<code>"command": "tabnav_select",
"args": { "scope": "table" }</code>
</pre></td>
</tr><tr>
<td>Copy selections as tab-separated values</td>
<td><pre>
<code>"command": "tabnav_copy_tab_separated"</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_copy_delimited",
"args": { "delimiter": "\\t" }</code>
</pre></td>
</tr><tr>
<td>Disable TabNav on view</td>
<td><pre>
<code>"command": "disable_tabnav"</code>
</pre></td>
<td><pre>
<code>"command": "enable_tabnav",
"args": { "enable": false }</code>
</pre></td>
</tr><tr>
<td>Reset capture level</td>
<td><pre>
<code>"command": "tabnav_reset_capture_level"</code>
</pre></td>
<td><pre>
<code>"command": "tabnav_set_capture_level",
"args": { "capture_level": null }</code>
</pre></td>
</tr></tbody></table>

<sup>1</sup> These legacy `select` commands accepted an optional `direction` argument with a value of `"left"` or `"right"` that determined the direction of the Sublime Text selections (i.e., at which end the cursor was placed), default `right`. The new commands accept a `"forward"` boolean argument, where `true` is equivalent to the legacy `"right"`, and `false` the legacy `"left"`.