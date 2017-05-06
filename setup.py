#setup.py
#from distutils.core import setup
#import py2exe
#setup(windows=[{"script":"copy.py"}], options={"py2exe":{"includes":["sip"]}})


import py2exe
from distutils.core import setup
setup( console=[{"script": "Copy.py"}] )
