import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, Gdk
import os
import struct

class RichTextEditor(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Rich Text Editor")
        self.set_default_size(800, 600)
        
        # Setup accelerators (only once)
        self.accel_group = Gtk.AccelGroup()
        self.add_accel_group(self.accel_group)
        
        # Main container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.add(vbox)
        
        # Menu Bar
        self.create_menu_bar(vbox)
        
        # Toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        vbox.pack_start(toolbar, False, False, 2)
        
        # Text view with scrolling
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        vbox.pack_start(scrolled_window, True, True, 0)
        
        self.textview = Gtk.TextView()
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.textview.set_hexpand(True)
        self.textview.set_vexpand(True)
        self.textview.set_left_margin(10)
        self.textview.set_right_margin(10)
        self.textbuffer = self.textview.get_buffer()
        scrolled_window.add(self.textview)
        
        # Create format buttons
        self.bold_button = Gtk.ToggleButton(label="Bold")
        self.italic_button = Gtk.ToggleButton(label="Italic")
        self.underline_button = Gtk.ToggleButton(label="Underline")
        
        # Add keyboard shortcuts for formatting
        key, mod = Gtk.accelerator_parse("<Control>B")
        self.bold_button.add_accelerator("clicked", self.accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        
        key, mod = Gtk.accelerator_parse("<Control>I")
        self.italic_button.add_accelerator("clicked", self.accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        
        key, mod = Gtk.accelerator_parse("<Control>U")
        self.underline_button.add_accelerator("clicked", self.accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        
        # Font size buttons and combo
        self.font_size_combo = Gtk.ComboBoxText()
        font_sizes = ['8', '9', '10', '11', '12', '14', '16', '18', '20', '22', '24', '28', '32', '36', '48', '72']
        for size in font_sizes:
            self.font_size_combo.append_text(size)
        self.font_size_combo.set_active(4)  # Default to 12pt
        self.font_size_combo.connect('changed', self.on_font_size_changed)
        
        # Font size buttons
        self.increase_font_button = Gtk.Button(label="A+")
        self.decrease_font_button = Gtk.Button(label="A-")
        
        # Add keyboard shortcuts for font size
        key, mod = Gtk.accelerator_parse("<Control>equal")  # Ctrl+=
        self.increase_font_button.add_accelerator("clicked", self.accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        
        key, mod = Gtk.accelerator_parse("<Control>minus")  # Ctrl+-
        self.decrease_font_button.add_accelerator("clicked", self.accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        
        # Font family combo box
        self.font_combo = Gtk.ComboBoxText()
        font_families = ['Sans', 'Serif', 'Monospace', 'Arial', 'Times New Roman', 'Courier New']
        for font in font_families:
            self.font_combo.append_text(font)
        self.font_combo.set_active(0)
        self.font_combo.connect('changed', self.on_font_family_changed)
        
        # Add buttons to toolbar
        toolbar.pack_start(self.bold_button, False, False, 0)
        toolbar.pack_start(self.italic_button, False, False, 0)
        toolbar.pack_start(self.underline_button, False, False, 0)
        toolbar.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 5)
        toolbar.pack_start(Gtk.Label(label="Size:"), False, False, 2)
        toolbar.pack_start(self.font_size_combo, False, False, 0)
        toolbar.pack_start(self.increase_font_button, False, False, 0)
        toolbar.pack_start(self.decrease_font_button, False, False, 0)
        toolbar.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 5)
        toolbar.pack_start(Gtk.Label(label="Font:"), False, False, 2)
        toolbar.pack_start(self.font_combo, False, False, 0)
        
        # Connect signals
        self.bold_button.connect("toggled", self.on_format_button_toggled, "bold")
        self.italic_button.connect("toggled", self.on_format_button_toggled, "italic")
        self.underline_button.connect("toggled", self.on_format_button_toggled, "underline")
        self.increase_font_button.connect("clicked", self.change_font_size, 1)
        self.decrease_font_button.connect("clicked", self.change_font_size, -1)
        
        # Initialize default font
        self.current_font_family = 'Sans'
        self.update_default_font()
        
        # Current file path
        self.current_file = None

    def create_menu_bar(self, vbox):
        menubar = Gtk.MenuBar()
        vbox.pack_start(menubar, False, False, 0)
        
        # File Menu
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="File")
        file_item.set_submenu(file_menu)
        
        new_item = Gtk.MenuItem(label="New")
        new_item.connect("activate", self.on_new)
        new_item.add_accelerator("activate", self.accel_group, ord('N'),
                               Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        
        open_item = Gtk.MenuItem(label="Open")
        open_item.connect("activate", self.on_open)
        open_item.add_accelerator("activate", self.accel_group, ord('O'),
                                Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        
        save_item = Gtk.MenuItem(label="Save")
        save_item.connect("activate", self.on_save)
        save_item.add_accelerator("activate", self.accel_group, ord('S'),
                                Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        
        save_as_item = Gtk.MenuItem(label="Save As")
        save_as_item.connect("activate", self.on_save_as)
        save_as_item.add_accelerator("activate", self.accel_group, ord('S'),
                                   Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK,
                                   Gtk.AccelFlags.VISIBLE)
        
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", Gtk.main_quit)
        quit_item.add_accelerator("activate", self.accel_group, ord('Q'),
                                Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        
        file_menu.append(new_item)
        file_menu.append(open_item)
        file_menu.append(save_item)
        file_menu.append(save_as_item)
        file_menu.append(Gtk.SeparatorMenuItem())
        file_menu.append(quit_item)
        
        # Edit Menu
        edit_menu = Gtk.Menu()
        edit_item = Gtk.MenuItem(label="Edit")
        edit_item.set_submenu(edit_menu)
        
        cut_item = Gtk.MenuItem(label="Cut")
        cut_item.connect("activate", self.on_cut)
        cut_item.add_accelerator("activate", self.accel_group, ord('X'),
                               Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        
        copy_item = Gtk.MenuItem(label="Copy")
        copy_item.connect("activate", self.on_copy)
        copy_item.add_accelerator("activate", self.accel_group, ord('C'),
                                Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        
        paste_item = Gtk.MenuItem(label="Paste")
        paste_item.connect("activate", self.on_paste)
        paste_item.add_accelerator("activate", self.accel_group, ord('V'),
                                 Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        
        edit_menu.append(cut_item)
        edit_menu.append(copy_item)
        edit_menu.append(paste_item)
        
        menubar.append(file_item)
        menubar.append(edit_item)

    def on_new(self, widget):
        if self.confirm_save():
            # Clear the buffer properly
            self.textbuffer.set_text("")
            # Reset the buffer's modified flag
            self.textbuffer.set_modified(False)
            # Reset the current file path
            self.current_file = None
            # Reset the window title
            self.set_title("Rich Text Editor")
            # Reset to default font
            self.font_combo.set_active(0)  # Set to Sans
            self.font_size_combo.set_active(4)  # Set to 12pt
            self.update_default_font()
            # Unset any toggle buttons
            self.bold_button.set_active(False)
            self.italic_button.set_active(False)
            self.underline_button.set_active(False)

    def on_open(self, widget):
        if not self.confirm_save():
            return
            
        dialog = Gtk.FileChooserDialog(
            title="Open File",
            parent=self,
            action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
                    
        # Add file filters
        rtf_filter = Gtk.FileFilter()
        rtf_filter.set_name("Rich Text Files")
        rtf_filter.add_pattern("*.rtf")
        dialog.add_filter(rtf_filter)
        
        txt_filter = Gtk.FileFilter()
        txt_filter.set_name("Text Files")
        txt_filter.add_pattern("*.txt")
        dialog.add_filter(txt_filter)
        
        all_filter = Gtk.FileFilter()
        all_filter.set_name("All Files")
        all_filter.add_pattern("*")
        dialog.add_filter(all_filter)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.current_file = dialog.get_filename()
            try:
                if self.current_file.lower().endswith('.rtf'):
                    self.load_rtf_file(self.current_file)
                else:
                    # Plain text file
                    with open(self.current_file, 'r') as file:
                        self.textbuffer.set_text(file.read())
                self.set_title(f"Rich Text Editor - {os.path.basename(self.current_file)}")
            except Exception as e:
                self.show_error_dialog(f"Error opening file: {str(e)}")
        
        dialog.destroy()

    def on_save(self, widget):
        if self.current_file:
            self.save_file(self.current_file)
        else:
            self.on_save_as(widget)

    def on_save_as(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Save As",
            parent=self,
            action=Gtk.FileChooserAction.SAVE)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK
        )
        
        # Add file filters
        rtf_filter = Gtk.FileFilter()
        rtf_filter.set_name("Rich Text Files")
        rtf_filter.add_pattern("*.rtf")
        dialog.add_filter(rtf_filter)
        
        txt_filter = Gtk.FileFilter()
        txt_filter.set_name("Text Files")
        txt_filter.add_pattern("*.txt")
        dialog.add_filter(txt_filter)
        
        dialog.set_do_overwrite_confirmation(True)
        
        # Default to RTF
        if not self.current_file:
            dialog.set_current_name("Untitled.rtf")
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.current_file = dialog.get_filename()
            # Ensure RTF extension if using RTF filter
            if dialog.get_filter() == rtf_filter and not self.current_file.lower().endswith('.rtf'):
                self.current_file += '.rtf'
            self.save_file(self.current_file)
        
        dialog.destroy()

    def save_file(self, filename):
        try:
            if filename.lower().endswith('.rtf'):
                self.save_rtf_file(filename)
            else:
                # Plain text file
                start, end = self.textbuffer.get_bounds()
                text = self.textbuffer.get_text(start, end, False)
                with open(filename, 'w') as file:
                    file.write(text)
            self.set_title(f"Rich Text Editor - {os.path.basename(filename)}")
        except Exception as e:
            self.show_error_dialog(f"Error saving file: {str(e)}")

    def save_rtf_file(self, filename):
        rtf = "{\\rtf1\\ansi\\deff0"
        rtf += "{\\fonttbl{\\f0\\fswiss\\fcharset0 Sans;}}"  # Changed font table format
        rtf += "{\\colortbl;}"
        rtf += "\\viewkind4\\uc1\\pard\\f0"  # Added default paragraph formatting
        
        start, end = self.textbuffer.get_bounds()
        iter = start.copy()
        
        while iter.compare(end) < 0:
            char = iter.get_char()
            tags = iter.get_tags()
            
            # Start formatting
            format_string = ""
            for tag in tags:
                if tag.get_property('weight') == Pango.Weight.BOLD:
                    format_string += "\\b"
                if tag.get_property('style') == Pango.Style.ITALIC:
                    format_string += "\\i"
                if tag.get_property('underline') == Pango.Underline.SINGLE:
                    format_string += "\\ul"
                if tag.get_property('size-points'):
                    size = int(tag.get_property('size-points') * 2)  # RTF uses half-points
                    format_string += f"\\fs{size}"
                if tag.get_property('family'):
                    format_string += f"\\f0"  # We're only using one font for now
            
            if format_string:
                rtf += "{" + format_string + " "
            
            # Add the character, escaping special characters
            if char in '\\{}':
                rtf += f"\\{char}"
            elif ord(char) > 127:
                rtf += f"\\u{ord(char)}?"
            else:
                rtf += char
            
            if format_string:
                rtf += "}"
            
            iter.forward_char()
        
        rtf += "}"
        
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(rtf)

    def load_rtf_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                rtf = file.read()
            
            # Clear the buffer
            self.textbuffer.set_text("")
            
            # Simple RTF parsing
            in_control = False
            control_word = ""
            current_format = {}
            text = ""
            in_header = True
            
            i = 0
            while i < len(rtf):
                char = rtf[i]
                
                # Handle control words
                if char == '\\':
                    if i + 1 < len(rtf) and rtf[i + 1] in '\\{}':
                        text += rtf[i + 1]
                        i += 2
                        continue
                    
                    # Process any pending text before handling new control word
                    if text and not in_header:
                        self.insert_text_with_format(text, current_format)
                        text = ""
                    
                    in_control = True
                    control_word = ""
                    i += 1
                    continue
                
                if in_control:
                    if char.isalpha():
                        control_word += char
                    elif char.isdigit() or char == '-':
                        control_word += char
                    else:
                        # Process control word
                        if control_word in ['rtf', 'ansi', 'deff0', 'fonttbl', 'colortbl']:
                            in_header = True
                        elif control_word == 'pard':
                            in_header = False
                        elif not in_header:
                            if control_word == 'b':
                                current_format['bold'] = True
                            elif control_word == 'i':
                                current_format['italic'] = True
                            elif control_word == 'ul':
                                current_format['underline'] = True
                            elif control_word.startswith('fs'):
                                try:
                                    size = int(control_word[2:]) / 2
                                    current_format['size'] = size
                                except ValueError:
                                    pass
                            elif control_word == 'par':
                                # Insert any pending text before the newline
                                if text:
                                    self.insert_text_with_format(text, current_format)
                                    text = ""
                                self.textbuffer.insert(self.textbuffer.get_end_iter(), "\n")
                        
                        in_control = False
                        if char != ' ':
                            i -= 1
                
                elif char == '{':
                    # Process any pending text before new group
                    if text and not in_header:
                        self.insert_text_with_format(text, current_format)
                        text = ""
                
                elif char == '}':
                    # Process any pending text before ending group
                    if text and not in_header:
                        self.insert_text_with_format(text, current_format)
                        text = ""
                    current_format = {}
                    
                elif not in_header and char not in '\\':
                    text += char
                
                i += 1
            
            # Insert any remaining text
            if text and not in_header:
                self.insert_text_with_format(text, current_format)
        
        except Exception as e:
            self.show_error_dialog(f"Error loading RTF file: {str(e)}")
            # Fallback to plain text
            with open(filename, 'r') as file:
                self.textbuffer.set_text(file.read())

    def insert_text_with_format(self, text, format_dict):
        if not text:
            return
            
        end_iter = self.textbuffer.get_end_iter()
        self.textbuffer.insert(end_iter, text)
        
        if format_dict:
            start_iter = self.textbuffer.get_end_iter()
            start_iter.backward_chars(len(text))
            end_iter = self.textbuffer.get_end_iter()
            
            if format_dict.get('bold'):
                tag = self.textbuffer.create_tag(None, weight=Pango.Weight.BOLD)
                self.textbuffer.apply_tag(tag, start_iter, end_iter)
            if format_dict.get('italic'):
                tag = self.textbuffer.create_tag(None, style=Pango.Style.ITALIC)
                self.textbuffer.apply_tag(tag, start_iter, end_iter)
            if format_dict.get('underline'):
                tag = self.textbuffer.create_tag(None, underline=Pango.Underline.SINGLE)
                self.textbuffer.apply_tag(tag, start_iter, end_iter)
            if format_dict.get('size'):
                tag = self.textbuffer.create_tag(None, size_points=format_dict['size'])
                self.textbuffer.apply_tag(tag, start_iter, end_iter)

    def confirm_save(self):
        if self.textbuffer.get_modified():
            dialog = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text="Save changes?")
            dialog.format_secondary_text(
                "Your changes will be lost if you don't save them.")
            response = dialog.run()
            dialog.destroy()
            
            if response == Gtk.ResponseType.YES:
                self.on_save(None)
            elif response == Gtk.ResponseType.NO:
                return True
            else:
                return False
        return True

    def show_error_dialog(self, message):
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error")
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def on_cut(self, widget):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.textbuffer.cut_clipboard(clipboard, True)

    def on_copy(self, widget):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.textbuffer.copy_clipboard(clipboard)

    def on_paste(self, widget):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.textbuffer.paste_clipboard(clipboard, None, True)

    def on_font_size_changed(self, combo):
        bounds = self.textbuffer.get_selection_bounds()
        if not bounds:
            return
            
        size = int(combo.get_active_text())
        self.apply_font_size(size)

    def apply_font_size(self, size):
        bounds = self.textbuffer.get_selection_bounds()
        if not bounds:
            return
            
        start, end = bounds
        
        # Remove any existing font size tags in the selection
        tags = start.get_tags()
        for tag in tags:
            if tag.get_property('size-points'):
                self.textbuffer.remove_tag(tag, start, end)
        
        # Create or get the font size tag
        tag_name = f"font-size-{size}"
        tag_table = self.textbuffer.get_tag_table()
        tag = tag_table.lookup(tag_name)
        
        if not tag:
            tag = self.textbuffer.create_tag(tag_name, size_points=size)
        
        self.textbuffer.apply_tag(tag, start, end)

    def change_font_size(self, button, change):
        bounds = self.textbuffer.get_selection_bounds()
        if not bounds:
            return
            
        start, end = bounds
        
        # Get current size of first character in selection
        tags = start.get_tags()
        current_size = 12  # Default size
        
        for tag in tags:
            if tag.get_property('size-points'):
                current_size = tag.get_property('size-points')
                break
        
        new_size = max(8, min(72, current_size + (2 * change)))
        self.apply_font_size(new_size)
        
        # Update the combo box to reflect the new size
        size_str = str(int(new_size))
        model = self.font_size_combo.get_model()
        for i in range(len(model)):
            if model[i][0] == size_str:
                self.font_size_combo.set_active(i)
                break

    def on_font_family_changed(self, combo):
        bounds = self.textbuffer.get_selection_bounds()
        if not bounds:
            return
            
        font_family = combo.get_active_text()
        start, end = bounds
        
        # Remove any existing font family tags
        tags = start.get_tags()
        for tag in tags:
            if tag.get_property('family'):
                self.textbuffer.remove_tag(tag, start, end)
        
        # Create or get the font family tag
        tag_name = f"font-family-{font_family}"
        tag_table = self.textbuffer.get_tag_table()
        tag = tag_table.lookup(tag_name)
        
        if not tag:
            tag = self.textbuffer.create_tag(tag_name, family=font_family)
        
        self.textbuffer.apply_tag(tag, start, end)

    def update_default_font(self):
        # Modern way to set font
        css_provider = Gtk.CssProvider()
        css = f"""
            textview {{
                font-family: {self.current_font_family};
                font-size: 12pt;
            }}
        """
        css_provider.load_from_data(css.encode())
        context = self.textview.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def on_format_button_toggled(self, button, format_type):
        bounds = self.textbuffer.get_selection_bounds()
        if not bounds:
            # If no selection, create a mark at cursor position for formatting
            cursor = self.textbuffer.get_insert()
            cursor_iter = self.textbuffer.get_iter_at_mark(cursor)
            self.textbuffer.move_mark(cursor, cursor_iter)
            start = end = cursor_iter
        else:
            start, end = bounds
            
        tag_table = self.textbuffer.get_tag_table()
        tag = tag_table.lookup(format_type)
        
        if not tag:
            if format_type == "bold":
                tag = self.textbuffer.create_tag(format_type, weight=Pango.Weight.BOLD)
            elif format_type == "italic":
                tag = self.textbuffer.create_tag(format_type, style=Pango.Style.ITALIC)
            elif format_type == "underline":
                tag = self.textbuffer.create_tag(format_type, underline=Pango.Underline.SINGLE)
        
        # Toggle the button state
        if isinstance(button, Gtk.ToggleButton):
            active = button.get_active()
        else:  # If triggered by keyboard shortcut
            if format_type == "bold":
                self.bold_button.set_active(not self.bold_button.get_active())
                active = self.bold_button.get_active()
            elif format_type == "italic":
                self.italic_button.set_active(not self.italic_button.get_active())
                active = self.italic_button.get_active()
            elif format_type == "underline":
                self.underline_button.set_active(not self.underline_button.get_active())
                active = self.underline_button.get_active()
        
        if active:
            self.textbuffer.apply_tag(tag, start, end)
        else:
            self.textbuffer.remove_tag(tag, start, end)

def main():
    win = RichTextEditor()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main() 