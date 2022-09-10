![License](https://img.shields.io/github/license/mitchvm/tabnav?style=flat-square)
![Release](https://img.shields.io/github/v/release/mitchvm/tabnav?sort=semver&style=flat-square)
![Downloads](https://img.shields.io/packagecontrol/dt/TabNav?style=flat-square)

# TabNav - Keyboard Navigation of Tabular Data

TabNav is a Sublime Text plugin for keyboard navigation of tabular text data. Quickly move and select "cells" of text in the following formats, without taking your hands off the keyboard:

* Markdown pipe tables
* Org Mode tables
* Textile tables
* CSV files

TabNav also provides the ability to copy only the contents of the table, excluding markup, in a format that can be readily-pasted into other programs, such as Excel.

![Demo](teaser.gif)

## Table of Contents

<!-- MarkdownTOC -->

- [Installation Instructions](#installation-instructions)
	- [Package Control](#package-control)
	- [Git Clone](#git-clone)
	- [Manual](#manual)
- [Recommended Key Bindings](#recommended-key-bindings)
	- [Key binding setup](#key-binding-setup)
- [Commands](#commands)
	- [Table Navigation Commands](#table-navigation-commands)
	- [Other Commands](#other-commands)
- [Contexts](#contexts)
	- [Markdown](#markdown)
	- [Org Mode](#org-mode)
	- [Textile](#textile)
	- [CSV](#csv)
- [Capture Levels](#capture-levels)
- [Key Bindings](#key-bindings)
	- [Custom Key Bindings](#custom-key-bindings)
- [Customization](#customization)
	- [Configuration Options](#configuration-options)
	- [Context Configuration](#context-configuration)
		- [CSV Context Configuration](#csv-context-configuration)
	- [Custom Contexts](#custom-contexts)
		- [Pattern Definitions](#pattern-definitions)
			- [`line` capture group](#line-capture-group)
			- [`cell` capture groups](#cell-capture-groups)

<!-- /MarkdownTOC -->

## Installation Instructions

### Package Control

1. If you haven't already, install [Package Control](https://packagecontrol.io/installation).
2. In the Sublime Text command palette, run the command: `Package Control: Install Package`.
3. Select `TabNav` from the list of available packages.

### Git Clone

1. Clone this repository to your local machine: `git clone https://github.com/mitchvm/tabnav.git`
2. If you didn't clone directly to the Sublime Text packages directory, create a symbolic link to the repository in your local Sublime Text packages directory.

### Manual

1. Download the latest [TabNav release](https://github.com/mitchvm/tabnav/releases) and unzip it to your local packages directory. 
	1. To find the local packages directory, open the Sublime Text Preferences and select "Browse packages..."
	2. Note: All of the TabNav files should be directly under a `tabnav` directory in the `Packages` directory. If the files are nested further, Sublime Text will **not** find them.

## Recommended Key Bindings

> :warning: TabNav has **no** keybindings enabled on initial install.

A package like TabNav will obviously require many key bindings. In an effort to not clobber either the default Sublime Text key bindings, or the key bindings of other packages you may have installed, while also allowing maximum flexibility for configuring key bindings based on your own personal preferences and keyboard layout, no key bindings are configured by default.

A set of recommended key bindings is provided in the package's key bindings files, however they are all commented out. The recommended key bindings are based on a US-English QWERTY keyboard. They make heavy use of the cluster of four keys immediately to the left of the <kbd>Enter</kbd> key.

### Key binding setup

1. From the Sublime Text Main menu, select _Preferences_ ❯ _Package Settings_ ❯ _TabNav_ ❯ _Key Bindings_ 
	1. This will open the the TabNav key bindings package key bindings file (on the left) along with your user key bindings file (on the right) in a new window. Notice that all of the default key bindings have been commented out with `//` at the start of each line.
2. Copy commented-out key TabNav bindings to into your user key bindings array.
	1. You must paste the key bindings **inside** of the outer-most array brackets in your user key bindings file.
3. With the copied key bindings still selected (and still commented out), un-comment the entire selection. (Main menu: _Edit_ ❯ _Comment_ ❯ _Toggle Comment_)
	1. If you have no other custom key bindings, your user key bindings file should look like this. Notice the brackets - `[` and `]` - on the first and last lines, respectively, and no `//` at the start of each line other than comment lines.

	```
	[
	    // =================== TabNav Key Bindings =========================

	    // #### TabNav: Non-navigation keybindings ####

	    {
	        // Enable TabNav on current view
	        // Note: this keybinding gets clobbered by the "select cell on right" keybindings
	        // once TabNav is enabled. In a CSV file, what this means is that the first press
	        // of this keybinding enables TabNav, and the next press selects the current cell.
	        "keys": ["ctrl+'"],
	        "command": "enable_tabnav"
	    },
	... (a lot more key bindings here)
	    // =================== End: TabNav Key Bindings =====================
	]
	```

See the [Key Bindings](#key-bindings) section for more details on the recommended key bindings, as well as how to use custom key bindings.

## Commands

TabNav adds the following commands to Sublime Text. They are all accessible via the Command Palette, as well as the _TabNav_ submenu under the _Selection_ menu.

> Note: If you're reading this on packagecontrol.io, the tables render more clearly when read on [GitHub](https://github.com/mitchvm/tabnav/blob/main/README.md).

### Table Navigation Commands

The table navigation commands below only operate within the context of a table. All of the table commands are compatible with multiple cursors, and even multiple cursors in multiple, disjoint tables.

As noted [above](#recommended_key_bindings), TabNav has no key bindings enabled by default. The key bindings shown below are the _recommended_ bindings. The core movement and selection key bindings combine one of four basic modifier key combinations together with with one of the four direction keys:

| Name                                     | Windows/Linux                                 | macOS                                | Description                                                                                                                                                                |
|:-----------------------------------------|:----------------------------------------------|:-------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Move cursor to cell...                   | <kbd>Alt</kbd>                                | <kbd>^</kbd>                         | Moves all cursors to the next cell in the desired direction.                                                                                                               |
| Select next cell...                      | <kbd>Ctrl</kbd>                               | <kbd>⌘</kbd>                         | Moves all selections to the adjacent cell in the desired direction.                                                                                                        |
| Select last cell...                      | <kbd>Ctrl</kbd><kbd>Alt</kbd>                 | <kbd>⌘</kbd><kbd>^</kbd>             | Moves all selections to the furthest cell in the row/column in the desired direction.                                                                                      |
| Extend selection...                      | <kbd>Ctrl</kbd><kbd>Shift</kbd>               | <kbd>⌘</kbd><kbd>⇧</kbd>             | Adds the next cell in the desired direction to the current selections.                                                                                                     |
| Extend selection to end of row/column... | <kbd>Ctrl</kbd><kbd>Alt</kbd><kbd>Shift</kbd> | <kbd>⌘</kbd><kbd>^</kbd><kbd>⇧</kbd> | Selects all cells in the row/column between the currently selected cell and the end of the row/column in the desired direction.                                            |
| Reduce selection...                      | <kbd>Alt</kbd><kbd>Shift</kbd>                | <kbd>^</kbd><kbd>⇧</kbd>             | When two or more cells in sequence are selected, removes the selection from a cell in the desired direction.                                                               |
| Add cursor to cell...                    |                                               |                                      | For each active cursor, add an additional cursor to the cell in the desired direction. The recommended key bindings do not include these commands.                         |
| Remove cursor from cell...               |                                               |                                      | When two or more cells in sequences contain cursors, removes the cursors from a cell in the desired direction. The recommended key bindings do not include these commands. |

<table>
<thead>
<tr>
<th align="center">Direction Key</th>
</tr>    
</thead>
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

Beyond the core navigation commands, these additional movement and selection commands are provided. Unlike most of the core commands, all of these commands are idempotent - that is, they generate the same Sublime Text selections/cursors regardless of how many times they are invoked, even if the current selections/cursors are already aligned with table cells. This might prove useful, for example, if recording a macro.

| Name                                             |                                  Windows/Linux Key binding |                                 macOS Key binding |
|:-------------------------------------------------|-----------------------------------------------------------:|--------------------------------------------------:|
| Move cursor to start of current cell<sup>1</sup> |                                                            |                                                   |
| Move cursor to end of current cell<sup>1</sup>   |                                                            |                                                   |
| Select text to start of current cell             |                                                            |                                                   |
| Select text to end of current cell               |                                                            |                                                   |
| Select current cell<sup>2</sup>                  |                                                            |                                                   |
| Select row cells                                 |               <kbd>Ctrl</kbd><kbd>Shift</kbd>+<kbd>L</kbd> |             <kbd>⌘</kbd><kbd>⇧</kbd>+<kbd>L</kbd> |
| Select column cells                              |               <kbd>Ctrl</kbd><kbd>Shift</kbd>+<kbd>C</kbd> |             <kbd>⌘</kbd><kbd>⇧</kbd>+<kbd>C</kbd> |
| Select all table cells                           | <kbd>Ctrl</kbd><kbd>Alt</kbd><kbd>Shift</kbd>+<kbd>C</kbd> | <kbd>⌘</kbd><kbd>^</kbd><kbd>⇧</kbd>+<kbd>C</kbd> |

<sup>1</sup> On initial invocation, the core move cursor left/right commands will also move the cursor to the start/end of the current cell, respectively, if not all selections are already at that position.

<sup>2</sup> On initial invocation, the core select next and extend selection commands will also select the current cell, if not all existing selections line up with table cells.

### Other Commands

These commands will operate even outside the context of a table.

| Name                            |    Windows/Linux Key Binding |         macOS Key Binding | Description                                                                                                                                                                                                                 |
|:--------------------------------|-----------------------------:|--------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Enable on current view          | <kbd>Ctrl</kbd>+<kbd>'</kbd> | <kbd>⌘</kbd>+<kbd>'</kbd> | Enables TabNav on the current view. Note, once enabled, the key binding is clobbered by the "Move cursor to cell on right" command (if using the recommended key bindings).                                                 |
| Disable on current view         |                              |                           | Disables TabNav on the current view.                                                                                                                                                                                        |
| Set capture level               |                              |                           | Configures the selection [capture level](#capture-levels) in use on the current view.                                                                                                                                       |
| Reset capture level to previous |                              |                           | Resets to the previously configured capture level. Useful for recording macros (i.e., change capture level, perform action, reset capture level).                                                                           |
| Set CSV delimiter               |                              |                           | Sets the delimiter to use for CSV files. See the [CSV](#csv) context section for more information.                                                                                                                          |
| Trim whitespace from selections |                              |                           | Removes all whitespace characters from either end of all current selections.                                                                                                                                                |
| Merge adjacent selections       |                              |                           | Merges selected regions that share a common start/end point. Useful if wanting to cut/paste multiple adjacent columns. Use with the `cell` [capture level](#capture-levels).                                                |
| Copy selections as TSV          |                              |                           | Copies all current selections as tab-delimited data, with all selections on the same row of text tab-separated and a newline between selection row. This is useful, for example, to copy data from a text table into Excel. |
| Copy selections with delimiter  |                              |                           | Same as the "Copy selections as TSV" command, but prompts the user to input the delimiter to use.                                                                                                                           |

## Contexts

TabNav operates on the concept of "contexts", which define how it identifies tabular data in a document. By default, it includes context definitions for Markdown, Org Mode, Textile, and CSV documents.

### Markdown

TabNav is enabled by default in Markdown documents. Only "pipe" style tables are supported. Other styles of Markdown tables are not currently supported.

Some flavours of Markdown support "borderless" tables, where pipes are not required on the outer edges of the table. For example, this is a valid table:

```
| Heading 1 | Heading 2 | Heading 3 |
|:----------|:----------|----------:|
| 1.1       | 1.2       |       1.3 |
| 2.1       | 2.2       |       2.3 |
```

Alternatively, the same table as a "bordered" table would look like this:

```
| Heading 1 | Heading 2 | Heading 3 |
|:----------|:----------|----------:|
| 1.1       | 1.2       |       1.3 |
| 2.1       | 2.2       |       2.3 |
```

By default, TabNav supports both borderless and bordered tables. To be able to support borderless tables, however, any line of (non-raw) text containing a pipe character is considered to be part of a table. 

Since this is a Markdown file, if I put a pipe right here | then this line of text is considered to be a table with two cells.

If you only use bordered Markdown tables, you can configure TabNav to be more restrictive in what it considers to be a table. See [Context Configuration](#context-configuration).

### Org Mode

TabNav is enabled by default in [Org Mode](https://orgmode.org/) documents, using the scopes defined by either the [orgmode](https://github.com/danielmagnussons/orgmode) or [orgextended](https://github.com/ihdavids/orgextended) packages. Tables in "raw" scopes are ignored.

TabNav recognizes three kinds of markup rows in Org Mode tables:

1. [Horizontal rules](https://orgmode.org/manual/Built_002din-Table-Editor.html)
2. [Column width rows](https://orgmode.org/manual/Column-Width-and-Alignment.html)
3. [Column group rows](https://orgmode.org/manual/Column-Groups.html)

### Textile

TabNav is enabled by default in [Textile](https://textile-lang.com/) documents. Textile tables differ from most of the other supported markup languages in two ways:

1. Cells and rows may contain inline table markup in addition to content.
2. Markup rows might not contain "cells" of markup that are aligned with the table cells.

Inline markup directly in the cell respects the current [capture level](#capture-levels) - when set to `trimmed` or `content`, the markup is omitted from selections; when set to `markup` or `cell`, the markup is included in selections. However, row markup - that is, styles and classes assigned to the row, before the first pipe - and stand-alone markup rows without a pipe at the end of the row are always ignored, regardless of capture level. Header and footer rows are treated as normal content rows.

Textile also supports cells spanning multiple rows and/or columns, though TabNav makes no special effort to support row and column spanning. When moving a single cursor/selection, the behaviour is _mostly_ how you would expect, or at least predictable, but when it comes to selecting regions of the table, cells spanning multiple rows or columns tend to give pretty funky results.

At this time, there is no intention of adding "proper" support for cells spanning multiple rows or columns in Textile tables.

### CSV

CSV requires special handling, specifically because there are so many permutations of "separated value" documents. There is no specific Sublime Text scope for CSV documents. Rather, TabNav treats CSV as the fall-back context if no other context was positively identified, though TabNav is disabled by default in CSV contexts - use the ["Enable on current view"](#other-commands) command to enable it.

TabNav integrates with both the [Advanced CSV](https://github.com/wadetb/Sublime-Text-Advanced-CSV) and [Rainbow CSV](https://github.com/mechatroner/sublime_rainbow_csv/)<sup>3</sup> packages. If the syntax on the current view comes from either of those packages, the delimiter being used by them is also automatically used by TabNav.

If the syntaxes provided by those two packages are not in use on the current view, then TabNav attempts to infer the delimiter to use by inspecting the first line of the file. If the first line of the file contains only one of the following characters, then that character is assumed to be the delimiter:

1. Comma: `,`
2. Semi-colon: `;`
3. Pipe: `|`
3. Tab

You can also specify a particular delimiter to use (when not in an Advanced CSV or Rainbow CSV syntax) with the ["Set CSV delimiter"](#other-commands) command. Note that a space cannot be used as the delimiter for the built-in CSV context.

Finally, if all other methods of determining the delimiter fail, TabNav uses a comma as the default delimiter.

<sup><b>3</b></sup> TabNav only partially supports Rainbow CSV syntaxes. The two restrictions are: only single-character delimiters are supported, and all CSV files are treated as quoted files, regardless if using a Rainbow CSV "simple" syntax.

## Capture Levels

TabNav contexts provide multiple "capture levels" that define how much text to select within a table cell. The available capture levels are listed below. Each level captures all of the text as the level above, and potentially more.

1. **Trimmed**: Only the text contained within the cell, excluding any whitespace on either side. Cells containing only markup are omitted from selections.
2. **Content**: The text in the cell as well as any whitespace around the text. Cells containing only markup are omitted from selections.
3. **Markup**: The content of the cell, plus any markup in the cell, but excluding the delimiter. All table cells, including those without any markup, are included in selections.
4. **Cell**: The entirety of all table cells are included in selections, including the delimiter preceding each cell, if applicable.

Note that not all capture levels are relevant to all contexts - CSV, for example, does not contain any markup beyond the cell delimiter. What's more, most contexts do not mix markup and content within the same cell.

The default capture level is `content`. The capture level in use on a particular view can be changed with the ["Set capture level"](#other-commands) command. The default capture level can be configured [globally](#configuration-options) or [per-context](#context-configuration).

## Key Bindings

Simply due to the nature of the package, TabNav requires many key bindings. The [recommended key bindings](#recommended_key_bindings) include several that override built-in Sublime Text key bindings. Effort has been made to minimize the impact on the default Sublime Text key bindings by having the TabNav key bindings take effect only under very specific circumstances. Only if _all_ of the following conditions are met will the TabNave key bindings override the built-in key bindings. 

1. There is a TabNav [context](#contexts) configured that matches the current view.
2. TabNav is enabled on the current view - in most contexts it is enabled by default.
4. The start point of the first selection is within a table.

The following built-in Sublime Text key bindings get overridden by the recommended TabNav key bindings:

| Operating System | Key Binding                                  | Sublime Text Command          | TabNav Command               |
|:-----------------|:---------------------------------------------|:------------------------------|:-----------------------------|
| Windows, Linux   | <kbd>Ctrl</kbd>+<kbd>;</kbd>                 | Open "go to word" overlay     | Select cell(s) left          |
| Windows, Linux   | <kbd>Ctrl</kbd>+<kbd>[</kbd>                 | Un-indent line(s)             | Select cell(s) up            |
| Windows, Linux   | <kbd>Ctrl</kbd>+<kbd>/</kbd>                 | Comment line(s)               | Select cell(s) down          |
| Windows, Linux   | <kbd>Ctrl</kbd><kbd>Shift</kbd>+<kbd>[</kbd> | Fold selection(s)             | Extend selection(s) up       |
| Windows, Linux   | <kbd>Ctrl</kbd><kbd>Shift</kbd>+<kbd>/</kbd> | Insert comment                | Extend selection(s) down     |
| Windows, Linux   | <kbd>Ctrl</kbd><kbd>Shift</kbd>+<kbd>L</kbd> | Split selection(s) into lines | Select cells in table row(s) |
| macOS            | <kbd>⌘</kbd>+<kbd>[</kbd>                    | Un-indent line(s)             | Select cell(s) up            |
| macOS            | <kbd>⌘</kbd><kbd>⇧</kbd>+<kbd>[</kbd>        | Fold selection(s)             | Extend selection(s) up       |
| macOS            | <kbd>⌘</kbd><kbd>⇧</kbd>+<kbd>L</kbd>        | Split selection(s) into lines | Select cells in table row(s) |

To temporarily disable most of the recommended TabNav keybindings, it is enough to [disable TabNav](#other-commands) on the current view. The only (recommended) key binding that is not disabled by doing this is the binding to enable TabNav on the view.

### Custom Key Bindings

Of course, it is entirely valid to ignore the recommended key bindings and use your own custom key bindings, or add more key bindings for commands not covered by the recommended bindings.

All of the available commands are and arguments enumerated in the [`CommandListing`](CommandListing.md) file.

For each navigation key binding, it is recommended to add the `is_tabnav_context` key binding context to limit the scopes within which the key binding will take effect, as described above.

## Customization

TabNav offers considerable configuration, or even customizability to modify the default contexts' behaviour or add new contexts.

### Configuration Options

Selecting the _Preferences_ ❯ _Package Settings_ ❯ _TabNav_ ❯ _Settings - TabNav_ menu item opens the TabNav default settings file, as well as your local TabNav settings file. Override the default configurations by placing the parameter into your local settings file. The following global configuration parameters are available:

* `capture_level`: The initial [capture level](#capture-levels) to use. The capture level can also be configured per-context, or changed on the active view using the ["Set capture level" command](#other-commands). Options: `trimmed`, `content`, `markup`, `cell`. Default: `content`.
* `trim_on_copy`: When true, the ["Copy selections" commands](#other-commands) trim whitespace from the selected regions' text prior to putting it on the clipboard. The selections in the view themselves are not altered. Default: `true`.
* `enable_explicitly`: When false, TabNav is assumed to be enabled if a [context](#contexts) is successfully matched to the file. When true, TabNav must be explicitly enabled on each view. This setting can also be configured per-context. Default: `false`.
* `log_level`: Set to `INFO` or `DEBUG` to see TabNav log messages in the Sublime Text console. Default `WARNING`.

### Context Configuration

To modify the behaviour of the default contexts, or to add new contexts, use the `user_contexts`<sup>4</sup> element in your local TabNav settings file

To override a default context's setting, you only need to provide the path to that setting in the `user_contexts` element; you don't need to copy the full context definition. For example, to configure the [Markdown](#markdown) context to only support bordered tables, add this to your user configuration:

```json
{
  "user_contexts":
  {
	"markdown":
	{
	  "patterns": [
		{
		  "line": "^(?P<table>(\\|\\s*[:-]+\\s*(?=\\|))+\\|)$",
		  "cell": "(?P<cell>\\|(?P<markup>\\s*[:-]+\\s*))(?=\\|)"
		},
		{ 
		  "line": "^(?P<table>\\|.*\\|)$",
		  "cell": "(?P<cell>\\|(?P<content>\\s*(?P<trimmed>.*?)\\s*))(?=\\|)"
		}
	  ]
	}
  }
}
```

See the [Custom Contexts](#custom-contexts) section below for descriptions of the standard context parameters.

<sup><b>4</b></sup> The default settings file has a `contexts` element. TabNav merges settings from the `user_contexts` and `contexts` settings. If you want to completely overwrite the default contexts, you can use the `contexts` element in your local settings file, however this is not recommended.

#### CSV Context Configuration

The `auto_csv` context is a special case with several custom parameters in addition to the standard context parameters.

1. `auto_delimiters`: The list of delimiters that TabNav will check when attempting to infer the CSV delimiter from the first line of the file.
2. `default_delimiter`: The ultimate fallback delimiter used for the CSV context if all other methods of determining the delimiter fail.

### Custom Contexts

Additional contexts can also be defined in the `user_contexts` element. For examples, see the `tabnav.sublime-settings` file (_Preferences_ ❯ _Package Settings_ ❯ _TabNav_ ❯ _Settings - TabNav_) to see the default contexts, which are generously commented.

The following parameters are used to define a TabNav context:

1. `selector`: **Required**. A [Sublime Text selector](https://www.sublimetext.com/docs/3/selectors.html) that identifies the scope within which the context operates. If multiple selections are currently active, only the first selection's scope is checked. If multiple TabNav contexts' selectors match the current scope, then the context with the highest selector "score" (as returned by the Sublime Text API) is used.
2. `except_selector`: _Optional_. A [Sublime Text selector](https://www.sublimetext.com/docs/3/selectors.html) that overrides the base `selector`. If the first selection matches this selector, then the context is _not_ matched.
3. `patterns`: **Required**. One or more [pattern definitions](#pattern-definitions) used to identify and parse rows of table content. If only one pattern is provided, it need-not be placed in a JSON array. If multiple patterns are provided, they are applied in sequence until the first match. In general, patterns for markup rows should be placed above patterns for content rows.
5. `enable_explicitly`: _Optional_. A boolean to indicate if the TabNav must be explicitly enabled when this context is matched. Overrides the global `enable_explicitly` setting. Default `false`.
6. `capture_level`: _Optional_. The default [capture level](#capture-levels) to use with this context. Overrides the global `capture_level` setting. Possible values: `trimmed`, `content`, `markup`, `cell`.

#### Pattern Definitions

The each element of the `patterns` [context parameter](#custom-contexts) defines how to:

1. identify that a line of text is part of a table, and
2. parse the contents of the table cells of that line of text.

Each pattern contains two elements, explained in more detail below.

1. `line`: _Optional_. A single [regular expression](https://docs.python.org/3.3/library/re.html) that is used to determine if the line of text is part of a table.
2. `cell`: **Required**. One or more [regular expressions](https://docs.python.org/3.3/library/re.html) that are used to identify cell contents from a line of text.

##### `line` capture group

The optional `line` expression is used to determine if the pattern applies to the line of text and, if so, the portion of the line of text that constitutes the table. If used, the `line` expression must return a named `table` group that captures the part of the line to use for matching table content with the `cell` expressions. If a `line` expression is not provided with the pattern, the entire line of text is parsed using the `cell` expressions.

There is one scenario where the `line` element is required, and the `cell` element can be omitted: to capture a line of a table, but not parse any cells from the line, include a `line` element _without_ a `table` capture group.

##### `cell` capture groups

Each element of the `cell` expressions should contain up to four **nested** named capture groups:

```
(cell (markup (content (trimmed))))
```

These correspond to the four TabNav [capture levels](#capture-levels). All outer capture groups must be defined if an inner group is to be used, regardless if the outer group captures anything additional to the inner group or not. For example, most table formats do not contain markup within content cells, however, the `markup` group must be included to be able to capture the `content` group.

To define markup-only cells that should not be included in selections at the `content` or `trimmed` levels, omit the `content` and `trimmed` capture groups.

The `cell` capture group should capture the delimiter that **precedes** the content of the cell, if applicable. In "borderless" contexts, such as CSV and borderless Markdown tables, the first cell of the line does not capture a delimiter.

Each match of each expression in the array should return a single cell's contents. Each expression can also, optionally, return a zero-width match immediately prior to the last matching delimiter. This match will be ignored.

If multiple expressions are provided in a JSON array, they are each processed in sequence until their matches are exhausted. Use this to have, for example, one expression to capture the first cell of the row, a different expression to capture cells in the middle of the row, and a third expression to capture the final cell. If only one expression is provided, it need-not be placed in a JSON array.

###### Example

One table format that mixes markup and content in a table cell is [Textile](https://textile-lang.com/doc/tables). Here is a sample row of a Textile table that defines headers. Cells are pipe-delimited, and the `_.` at the start of the cell is markup indicating that the cell is a header cell.

```
|_. First Header  |_. Second Header |
```

Here is a visual representation of what the four TabNav capture groups should capture from this row:

```
|_. First Header  |_. Second Header |
↑↑ ↑↑          ↑ ↑↑↑ ↑↑           ↑↑
|| |└ trimmed ─┘ ||| |└ trimmed ──┘|
|| └─ content ───┤|| └─ content ───┤
|└─── markup ────┤|└─── markup ────┤
└──── cell ──────┘└──── cell ──────┘
```

Alternatively, presented as a table (how meta):

| Capture Group | First Cell Selection                 | Second Cell Selection                |
|:--------------|:-------------------------------------|:-------------------------------------|
| `cell`        | <code>&vert;_. First Header  </code> | <code>&vert;_. Second Header </code> |
| `markup`      | `_. First Header  `                  | `_. Second Header `                  |
| `content`     | ` First Header  `                    | ` Second Header `                    |
| `trimmed`     | `First Header`                       | `Second Header`                      |

Notice that the final `|` is not captured as part of any cell - each cell only captures the _preceding_ delimiter.