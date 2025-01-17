import zipfile, os

from dexassist.dex import converter, dex
from dexassist.bytecodes import base
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
    print(clazz.name)

def remove_ads(dex_path):
  mdex = dex.from_file(dex_path, converter.DexConverter())
  for clazz in mdex.classes:
    for m in clazz.methods:
      if m.editor:
        for opcode in m.editor.opcode_list:
          if opcode.op == 0x70 or opcode.op == 0x76:
            if 'setupAds' in opcode.ref.name: m.editor.remove(opcode)
  stream = OutputStream(bytearray(), 0)
  mdex.save_as(DexWriter, stream)

  with open('classes.dex', 'wb') as f:
    f.write(stream.buf)



def remake(src, dst):
  with zipfile.ZipFile(src, 'r') as s:
    with zipfile.ZipFile(dst, 'w') as d:
      for x in s.infolist():
        if x.filename == 'classes.dex': continue
        if 'META-INF' in x.filename: continue
        buf = s.read(x.filename)
        d.writestr(x, buf)

def baksmali(dex_path):
  os.system('java -jar baksmali-2.3.4.jar d {}'.format(dex_path))

def smali(out_path):
  os.system('java -jar smali-2.3.4.jar a {} --out test.dex'.format(out_path))

def remake_apk(apk_path, out_apk_path):
  with zipfile.ZipFile(apk_path, 'r') as f:
    x = f.read('classes.dex')
  with open('test.dex', 'rb') as f:
    buf = f.read()
  remake(apk_path, out_apk_path)
  

  with zipfile.ZipFile(out_apk_path, 'a') as f:
    
    f.writestr('classes.dex', buf)
  

def main():
  #print_dex('test_binary/classes_mid.dex')
  #print_dex('test_binary/more_large.dex')
  remove_ads('test_binary/classes_mid.dex')
  #duplicate_dex('test_binary/classes.dex')
  #duplicate_dex('test_binary/large.dex')
  #remake_apk('sample_apk/sample1.apk', 'out.apk')
if __name__ == '__main__':
  main()
