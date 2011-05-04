import os
import Tkinter  as tk
import Image, ImageTk
from util import renderMachine


class PreviewWindow(object):
  TEMP_FOLDER = 'temp'
  TEMP_FILENAME = 'fsm.png'
  ERROR_LOG_FILENAME = 'graphviz_error.log'
  ERROR_FILEPATH = 'data/preview_error.png'
  INVALID_FILEPATH = 'data/preview_invalid.png'

  def __init__(self, master, fsm, showrefresh=True):
    self._window = tk.Toplevel(master)
    self._window.title('Preview')
    self._window.transient(master)
    self._window.resizable(0,0)

    self._fsm = fsm

    self._panel = tk.Label(self._window)
    self._panel.pack(side='top', fill='both', expand='yes')

    self._button = tk.Button(self._window, text='Refresh', command=self.refresh)
    self._button.lift()

    if showrefresh:
      self._button.place(y=0)
    else:
      self._button.place(y=-50)

    self.refresh()

  def refresh(self, fsm=None):
    if fsm: self._fsm = fsm

    if not self._fsm.isValid():
      filename = self.INVALID_FILEPATH
    else:
      if not os.path.exists(self.TEMP_FOLDER):
        os.mkdir(self.TEMP_FOLDER)
      temp_path = os.path.join(self.TEMP_FOLDER, self.TEMP_FILENAME)
      if os.path.exists(temp_path):
        os.unlink(temp_path)
      try:
        res = self._window.winfo_fpixels('1i')
        y_margin = 60 #Shell GUI (e.g. taskbar)
        size = (self._window.winfo_screenwidth() / res,
            (self._window.winfo_screenheight()-y_margin) / res)

        renderMachine(self._fsm, outfile=temp_path, size=size)

        if os.path.exists(temp_path):
          filename = temp_path
        else:
          raise SystemError, 'No output rendered.'
      except:
        open(ERROR_LOG_FILENAME, 'w').write(self._fsm.toGraphViz(size))
        filename = self.ERROR_FILEPATH

    self._image = ImageTk.PhotoImage(Image.open(filename))

    self._panel.configure(image=self._image)

    self.reposition()

  def reposition(self, y=None):
    w = self._image.width()
    h = self._image.height()

    x = (self._window.winfo_screenwidth() - w) / 2

    if y:
      self._window.geometry("%dx%d+%d+%d" % (w, h, x, y))
    else:
      self._window.geometry("%dx%d+%d+%d" % (w, h, x, self._window.winfo_y()))

    x_offset = w-self._button.winfo_reqwidth()
    self._button.place(x=x_offset)
