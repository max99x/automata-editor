# Windows build script.

from distutils.dir_util import copy_tree, remove_tree
from distutils.file_util import copy_file
from distutils.core import setup
import py2exe, sys, os

#Includes
includes = ('data', 'samples')

#Create backup
if os.path.exists('RELEASE'):
  if os.path.exists('RELEASE.old'):
    remove_tree('RELEASE.old')
  os.rename('RELEASE', 'RELEASE.old')

#Use py2exe
sys.argv.append('py2exe')

#Run setup
setup(options = {'py2exe': {'optimize': 2}},
      windows = [{'script': 'gui.pyw', 
                  'icon_resources': [(1, 'data/icon.ico')]}])

#Remove build/
remove_tree('build')

#Rename to RELEASE, Automata Editor.exe
os.rename('dist', 'RELEASE')
os.rename(os.path.join('RELEASE', 'gui.exe'),
          os.path.join('RELEASE', 'Automata Editor.exe'))

#Copy data dirs
for i in includes:
  if os.path.isdir(i):
    copy_tree(i, os.path.join('RELEASE', i))
  else:
    copy_file(i, os.path.join('RELEASE', i))
os.mkdir(os.path.join('RELEASE', 'temp'))

#Copy src
os.mkdir(os.path.join('RELEASE', 'src'))
for i in os.listdir('.'):
  if os.path.isfile(i) and i.endswith(('py', 'pyw')):
    copy_file(i, os.path.join('RELEASE', 'src', i))
