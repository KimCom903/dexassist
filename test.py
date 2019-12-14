import zipfile, os

from dexassist.dex import converter, dex
from dexassist.writer import dex as writer_dex
from dexassist.writer.dex.writer import DexWriter
from dexassist.writer.dex.stream import OutputStream
def print_dex(dex_path):
  with open(dex_path, 'rb') as f:
    x = f.read()
  manager = dex.DexManager()
  stream = dex.StreamReader(x, manager)
  header = dex.HeaderItem(manager, stream, 0)
  mdex = converter.DexConverter().get_dex(header, manager)
  for clazz in mdex.classes:
    for m in clazz.methods:
      print(m.clazz.name + m.name)
      if m.editor:
        print(len(m.editor.tries))
        for tryitem in m.editor.tries:
          print("count except_type: {}".format(len(tryitem.catch_handlers)))

def duplicate_dex(dex_path):
  with open(dex_path, 'rb') as f:
    x = f.read()
  manager = dex.DexManager()
  stream = dex.StreamReader(x, manager)
  header = dex.HeaderItem(manager, stream, 0)
  mdex = converter.DexConverter().get_dex(header, manager)
  buf = bytearray()
  stream = OutputStream(buf,0)
  #mdex.write(stream)
  p = DexWriter(mdex)
  p.write(stream)

def remake(src, dst):
  with zipfile.ZipFile(src, 'r') as s:
    with zipfile.ZipFile(dst, 'w') as d:
      for x in s.infolist():
        if x.filename == 'classes.dex': continue
        if 'META-INF' in x.filename: continue
        buf = s.read(x.filename)
        d.writestr(x, buf)

def remake_apk(apk_path, out_apk_path):
  with zipfile.ZipFile(apk_path, 'r') as f:
    x = f.read('classes.dex')
  
  manager = dex.DexManager()
  stream = dex.StreamReader(x, manager)
  header = dex.HeaderItem(manager, stream, 0)
  mdex = converter.DexConverter().get_dex(header, manager)
  buf = bytearray()
  stream = OutputStream(buf,0)
  #mdex.write(stream)
  p = DexWriter(mdex)
  p.write(stream)
  with open('test.dex', 'rb') as f:
    buf = f.read()
  remake(apk_path, out_apk_path)
  

  with zipfile.ZipFile(out_apk_path, 'a') as f:
    
    f.writestr('classes.dex', buf)
  

def main():
  #print_dex('test_binary/classes_mid.dex')
  #print_dex('test_binary/more_large.dex')
  #duplicate_dex('test_binary/classes_mid.dex')
  #duplicate_dex('test_binary/classes.dex')
  #duplicate_dex('test_binary/classes.dex')
  #duplicate_dex('test_binary/large.dex')
  remake_apk('sample_apk/sample1.apk', 'out.apk')
if __name__ == '__main__':
  main()
