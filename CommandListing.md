# TabNav Command Listing

## Contents

<!-- MarkdownTOC levels="1,2,3" markdown_preview="github" -->

- [Navigation Commands](#navigation-commands)
    - [Command: `tabnav_move`](#command-tabnav_move)
    - [Command: `tabnav_move_end`](#command-tabnav_move_end)
    - [Command: `tabnav_select`](#command-tabnav_select)
- [Non-navigation Commands](#non-navigation-commands)
    - [Command: `enable_tabnav`](#command-enable_tabnav)
    - [Command: `tabnav_set_capture_level`](#command-tabnav_set_capture_level)
    - [Command: `tabnav_set_csv_delimiter`](#command-tabnav_set_csv_delimiter)
    - [Command: `tabnav_copy_delimited`](#command-tabnav_copy_delimited)
    - [Command: `tabnav_trim_whitespace_from_selection`](#command-tabnav_trim_whitespace_from_selection)
    - [Command: `tabnav_merge_adjacent_selections`](#command-tabnav_merge_adjacent_selections)

<!-- /MarkdownTOC -->

## Navigation Commands

### Command: `tabnav_move`

Moves the current selections by one cell relative to current cells within the table in any direction. A cursor can be placed in the cell, or the entire cell selected as a Sublime Text region. Existing selections can be moved, extended &ndash; that is, place an additional cursor in, or extend the selection to the next cell &ndash; or reduced &ndash; that is, remove the cursors/selections from the most extreme cell in each contiguous selection of more than one cell.

When invoked, if the current Sublime Text selections aren't a set of individual cursors (if `select:false`) or regions with full table cells selected (if `select:true`), then the initial invocation splits the current selections to achieve that state &ndash; similar to [`tabnav_select`](#tabnav_select). Subsequent invocations perform the movements.

If the neighbouring cell in the given direction is at a higher capture level than the current configuration, it will be skipped. For example, if the current capture level is `content`, then a cell containing only markup is skipped and the subsequent cell is selected. An exception is made if all initial selections are at a higher capture level _and_ all neighbouring cells of the current selections in the given direction are also at the higher capture level. This allows movement within a markup row, even when the capture level is `content`.

Similarly, when reducing the selection, gaps in contiguous regions due to cells at higher capture level are spanned. For example, if the entire column of a Markdown table is selected but only at capture level `content` (i.e., the cell in the markup row is _not_ selected, but the cells both above it and below it are selected), then it is considered to be one contiguous region. Reducing the selection by one cell downwards would remove the header cell from the selection, despite it being separated from the rest of the selections.

When moving/extending the selection, if the current cell is the last cell (at the current capture level) in the direction of movement, then selection of the cell is not changed. However, each cell's movement is determined individually, so some cells may move while others may not.

#### Parameters

<dl>
    <dt><strong>scope</strong> : { "row", "column" }</dt>
    <dd>
        <p><strong>Required</strong>. Indicates if movement should be within the same row (horizontally) or column (vertically).</p>
    </dd>
    <dt><strong>forward</strong> : bool, default true</dt>
    <dd>
        <p>If <code>true</code>, moves to the right or down. If <code>false</code>, moves to the left or up.</p>
    </dd>
    <dt><strong>select</strong> : bool, default true</dt>
    <dd>
        <p>If <code>true</code>, a Sublime Text region is created spanning the entirety of each selected cell. If <code>false</code>, a cursor is placed in each selected cell. When moving <code>"scope":"column"</code> with <code>"select":false</code>, TabNav attempts to maintain the relative position of the cursor within the cell.</p>
    </dd>
    <dt><strong>extend</strong> : { -1, 0, 1 }, default 0</dt>
    <dd>
        <p>Determines if the cursors/selections are moved, extended, or reduced.</p>
        <ul>
            <li><code>1</code> : Add neighbouring cell to existing selections</li>
            <li><code>0</code> : Move selection to neighbouring cell</li>
            <li><code>-1</code> : Remove outer-most cell from each contiguous group of selected cells with >1 cell selected</li>
        </ul>
    </dd>
    <dt><strong>context</strong> : string, optional</dt>
    <dd>
        <p>Specify the name of the TabNav context to use. If not provided, TabNav infers the context based on the current scope.</p>
    </dd>
</dl>

[Back to top](#)

### Command: `tabnav_move_end`

Moves the current selections to the outer-most cell within the table in any direction. A cursor can be placed in each cell, or the entire cell selected as a Sublime Text region. Existing selections can be moved, extended &ndash; that is, place an additional cursor in, or extend the selection to all cells between the current cell and the outer-most cell &ndash; or reduced &ndash; that is, remove the cursors/selections from the all but one cell in the given direction.

When invoked, if the current Sublime Text selections aren't a set of individual cursors (if `select:false`) or regions with full table cells selected (if `select:true`), then the initial invocation splits the current selections to achieve that state &ndash; similar to [`tabnav_select`](#tabnav_select). Subsequent invocations perform the movements.

When moving selections, if the outer-most cell in the given direction is at a higher capture level than the current configuration, then the outer-most cell at the current capture level will be selected. For example, if the current capture level is `content` and the outer-most cell is a markup cell, then the second-to-last cell is selected (provided it is a content cell). Similarly, when extending selections, cells of a higher capture level are omitted from selections, and when reducing selections, gaps in regions due to cells of higher capture levels are spanned.

If the current cell is the last cell (at the current capture level) in the direction of movement, then selection of the cell is not changed. However, each cell's movement is determined individually, so some cells may move while others may not. This command is idempotent. That is, regardless of how many consecutive invocations with the same parameters are made, the resulting Sublime Text regions/cursors will not change.s

#### Parameters

<dl>
    <dt><strong>scope</strong> : { "row", "column" }</dt>
    <dd>
        <p><strong>Required</strong>. Indicates if movement should be within the same rows (horizontally) or column (vertically).</p>
    </dd>
    <dt><strong>forward</strong> : bool, default true</dt>
    <dd>
        <p>If <code>true</code>, moves to the right or down. If <code>false</code>, moves to the left or up.</p>
    </dd>
    <dt><strong>select</strong> : bool, default true</dt>
    <dd>
        <p>If <code>true</code>, a Sublime Text region is created spanning the entirety of each selected cell. If <code>false</code>, a cursor is placed in each selected cell. When moving <code>"scope":"column"</code> with <code>"select":false</code>, TabNav attempts to maintain the relative position of the cursor within the cell.</p>
    </dd>
    <dt><strong>extend</strong> : { -1, 0, 1 }, default 0</dt>
    <dd>
        <p>Determines if the cursors/selections are moved, extended, or reduced.</p>
        <ul>
            <li><code>1</code> : Add neighbouring cell to existing selections</li>
            <li><code>0</code> : Move selection to neighbouring cell</li>
            <li><code>-1</code> : Remove outer-most cell from each contiguous group of selected cells with >1 cell selected</li>
        </ul>
    </dd>
    <dt><strong>context</strong> : string, optional</dt>
    <dd>
        <p>Specify the name of the TabNav context to use. If not provided, TabNav infers the context based on the current scope.</p>
    </dd>
</dl>

[Back to top](#)

### Command: `tabnav_select`

Selects the current cell, or all cells in the current row, column, or table. A cursor can be placed in each cell, or the entire cell selected as a Sublime Text region, based on the value of the `select` parameter. This command is idempotent. That is, regardless of how many consecutive invocations with the same parameters are made, the resulting Sublime Text regions/cursors will not change.

#### Parameters

<dl>
    <dt><strong>scope</strong> : { "cell", "row", "column", "table" }</dt>
    <dd>
        <p><strong>Required</strong>. Indicates the scope of selection.</p>
    </dd>
    <dt><strong>forward</strong> : bool, default true</dt>
    <dd>
        <p>Determines at which end of the cell the cursor is placed. If <code>true</code>, the cursor is placed on the right. If <code>false</code>, it is on the left.</p>
    </dd>
    <dt><strong>select</strong> : bool, default true</dt>
    <dd>
        <p>If <code>true</code>, a Sublime Text region is created spanning the entirety of each selected cell. If <code>false</code>, a cursor is placed in each selected cell.</p>
    </dd>
    <dt><strong>context</strong> : string, optional</dt>
    <dd>
        <p>Specify the name of the TabNav context to use. If not provided, TabNav infers the context based on the current scope.</p>
    </dd>
    <dt><strong>capture_level</strong> : { "cell", "markup", "content", "trimmed" }, optional</dt>
    <dd>
        <p>Sets the capture level to use for the selection. If not provided, the normal rules to determine the capture level apply.</p>
    </dd>
</dl>

[Back to top](#)

## Non-navigation Commands

### Command: `enable_tabnav`

Explicitly enables or disables TabNav on the current view. Note that by default, in most supported contexts, TabNav is _implicitly_ enabled and does not need to be explicitly enabled.

#### Parameters

<dl>
    <dt><strong>enabled</strong> : bool, default true</dt>
    <dd>
        <p>Provide <code>"enabled":false</code> to disable TabNav on the view.</p>
    </dd>
</dl>

[Back to top](#)

### Command: `tabnav_set_capture_level`

Overrides the default capture level used for the current context with the provided level, or resets the capture level to the previously used capture level on the view.

#### Parameters

<dl>
    <dt><strong>capture_level</strong> : { "cell", "markup", "content", "trimmed" }, optional</dt>
    <dd>
        <p>The capture level to use for on the view. If not provided, the capture level is reset to the previously used capture level on the view.</p>
    </dd>
</dl>

[Back to top](#)

### Command: `tabnav_set_csv_delimiter`

Sets the delimiter to use for the "auto_csv" context on the current view. The delimiter is only used if the view isn't using a syntax provided by either the [Advanced CSV](https://github.com/wadetb/Sublime-Text-Advanced-CSV) or [Rainbow CSV](https://github.com/mechatroner/sublime_rainbow_csv/) packages.

Note: space characters are not supported in the CSV delimiter.

<dl>
    <dt><strong>delimiter</strong> : string, optional</dt>
    <dd>
        <p>The delimiter to use on the view. If not provided, any explicitly set delimiter set previously is cleared and the fall-back auto-detection logic is used.</p>
    </dd>
</dl>

[Back to top](#)

### Command: `tabnav_copy_delimited`

Copies all current Sublime Text regions as delimited strings to the clipboard. Useful to copy table contents without markup to other programs, such as Excel.

#### Parameters

<dl>
    <dt><strong>delimiter</strong> : string, default "\\\\t" (tab)</dt>
    <dd>
        <p>The delimiter to insert between selections on the same line of text.</p>
    </dd>
    <dt><strong>trim</strong> : bool, default true</dt>
    <dd>
        <p>If <code>true></code>, all whitespace characters are trimmed from either end of each selection prior to placing it onto the cliboard. The selected Sublime Text regions themselves are not modified.</p>
    </dd>
</dl>

[Back to top](#)

### Command: `tabnav_trim_whitespace_from_selection`

Utility command to reduce all currently selected Sublime Text regions by removing whitespace characters from either end.

[Back to top](#)

### Command: `tabnav_merge_adjacent_selections`

Utility command to merge regions that have a coincident end point.

[Back to top](#)