## TabNav

**Thank you for trying out TabNav!**

TabNav has **no** keybindings enabled on initial install, but it will obviously
require many key bindings to function.

In an effort to not clobber either the default Sublime Text key bindings, or
the key bindings of other packages you may have installed, while also allowing
maximum flexibility for configuring key bindings based on your own personal
preferences and keyboard layout, no key bindings are configured by default.

A set of recommended key bindings is provided in the package's key bindings
files, however they are all commented out. The recommended key bindings are
based on a US-English QWERTY keyboard. They make heavy use of the cluster of
four keys immediately to the left of the Enter key.

To use the recommended key bindings:

  1. From the Sublime Text Main menu, select
     Main menu: Preferences ❯ Package Settings ❯ TabNav ❯ Key Bindings
	   * This will open the the TabNav key bindings package key bindings file
	     (on the left) along with your user key bindings file (on the right)
	     in a new window. Notice that all of the default key bindings have been
	     commented out with `//` at the start of each line.
  2. Copy commented-out key TabNav bindings to into your user key bindings array.
	   * You must paste the key bindings **inside** of the outer-most array
	     brackets in your user key bindings file.
  3. With the copied key bindings still selected (and still commented out),
     un-comment the entire selection.
     Main menu: Edit ❯ Comment ❯ Toggle Comment

### Quick start with the recommended key bindings

The four keys to the left of the Enter key are used as directional control:

* [ : up
* ; : left
* ' : right
* / : down

Combine those for directions with a modifier to navigate the cells of your table.

Windows/Linux:

* Alt        : Move cursors
* Ctrl       : Select cell
* Ctrl+Alt   : Jump to end
* Ctrl+Shift : Extend selection
* Alt+Shift  : Reduce selection

macOS:

* Control         : Move cursors
* Command         : Select cell
* Command+Control : Jump to end
* Command+Shift   : Extend selection
* Control+Shift   : Reduce selection

Additional commands for selecting rows, columns, or tables of cells; copying
cell contents; trimming whitespace from selections. See the README for those
details, and much more.

https://github.com/mitchvm/tabnav/blob/main/README.md