import IPython
import os

ipython_shell = IPython.core.interactiveshell.InteractiveShell()
print(os.getcwd())
ipython_shell.run_line_magic('cd', '..')
print(os.getcwd())