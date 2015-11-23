from distutils.core import setup
import py2exe

py2exe_options = {
        "includes":["sip",],
        }

setup(console=[{'script': 'jobExecuter.py'}])
setup(windows=["execUnit.py"], options={'py2exe': py2exe_options})

