import tkinter as tk
import tkinter.simpledialog
import tkinter.filedialog
import tkinter.messagebox


class ChoiceWindow(object):
    def __init__(self, master, choices, title='Selection', text='Select item:', selected=0):
        if len(choices) == 0:
            raise RuntimeError('No choices supplied.')

        self._window = tk.Toplevel(master)
        self._window.transient(master)
        self._window.resizable(0, 0)
        self._window.title(title)

        # Widgets
        self._prompt = tk.Label(self._window, text=text)
        self._prompt.pack(side='top', anchor=tk.W)

        self._list = tk.Listbox(self._window)
        self._list.pack(side='top', fill='both',
                        expand=True, after=self._prompt)

        self._scroll = tk.Scrollbar(self._list, command=self._list.yview)
        self._scroll.pack(side='right', fill='y')

        self._list.configure(yscrollcommand=self._scroll.set)
        self._window.bind('<MouseWheel>', lambda e: self._list.yview(
            tk.SCROLL, -1*(1 if e.delta > 0 else -1), tk.UNITS))

        self._ok = tk.Button(self._window, text='Ok', command=self.accept)
        self._ok.pack(side=tk.LEFT, padx=20, ipadx=20, pady=10)

        self._cancel = tk.Button(
            self._window, text='Cancel', command=self.close)
        self._cancel.pack(side=tk.RIGHT, padx=20, ipadx=20, pady=10)

        # Take care of choices
        self._items = choices
        for item in choices:
            self._list.insert(tk.END, unicode(item))
        self._list.selection_set(selected)

        self._val = None

        #Resize and reposition
        self._window.geometry("200x150")

        self.centre()

        # Make Modal
        self._window.transient()
        self._window.grab_set()
        self._window.focus_set()

    def accept(self):
        self._val = self._items[self._list.index(tk.ACTIVE)]
        self.close()

    def close(self):
        self._window.destroy()

    def get(self):
        self._window.wait_window()
        return self._val

    def centre(self):
        h = self._window.winfo_reqheight()
        w = self._window.winfo_reqwidth()

        master_h = self._window.master.winfo_height()
        master_w = self._window.master.winfo_width()

        x = self._window.master.winfo_x() + ((master_w - w) / 2)
        y = self._window.master.winfo_y() + ((master_h - h) / 2)

        g = '+%d+%d' % (x, y)

        self._window.geometry(g)


class MultiChoiceWindow(ChoiceWindow):
    def __init__(self, master, choices, title='Selection', text='Select items:', selected=None):
        ChoiceWindow.__init__(self, master, choices, title, text)

        self._list.configure(selectmode=tk.MULTIPLE)
        self._list.selection_clear(0)

        if selected:
            for i in selected:
                self._list.selection_set(i)

    def accept(self):
        self._val = [self._items[int(i)] for i in self._list.curselection()]
        self.close()


def askForString(master, title, text):
    return tkinter.simpledialog.askstring(parent=master, title=title, prompt='')


def askForChoice(master, title, text, choices, selected=0):
    return ChoiceWindow(master, choices, title, text, selected).get()


def askForSelect(master, title, text, choices, selected):
    return MultiChoiceWindow(master, choices, title, text, selected).get()


def askForOpen(master, title, type=('Finite State Machine', '*.fsm')):
    return tkinter.filedialog.askopenfilename(parent=master, title=title, filetypes=[type, ('All Files', '*.*')])


def askForSave(master, title, type=('Finite State Machine', '*.fsm')):
    return tkinter.filedialog.asksaveasfilename(parent=master, title=title, filetypes=[type, ('All Files', '*.*')], defaultextension=type[1])


def askYesNo(master, title, text):
    return tkinter.messagebox.askyesno(title=title, message=text, parent=master)


def messageBox(master, title, text, icon='warning'):
    if icon == 'warning':
        tkinter.messagebox.showwarning(
            title=title, message=text, parent=master)
    elif icon == 'info':
        tkinter.messagebox.showinfo(title=title, message=text, parent=master)
    else:
        raise RuntimeError('Invalid message icon.')
