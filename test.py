from dex import converter, dex
from writer import dex as writer_dex
from writer.dex.writer import DexWriter
from writer.dex.stream import DexFileWriteStream
def print_dex(dex_path):
  with open(dex_path, 'rb') as f:
    x = f.read()
  manager = dex.DexManager()
  stream = dex.StreamReader(x, manager)
  header = dex.HeaderItem(manager, stream, 0)
  mdex = converter.DexConverter().get_dex(header, manager)
  for clazz in mdex.classes:
    for f in clazz.fields:
      print(f)
    for m in clazz.methods:
      print(m)

def duplicate_dex(dex_path):
  with open(dex_path, 'rb') as f:
    x = f.read()
  manager = dex.DexManager()
  stream = dex.StreamReader(x, manager)
  header = dex.HeaderItem(manager, stream, 0)
  mdex = converter.DexConverter().get_dex(header, manager)
  print(dir(writer_dex))
  stream =DexFileWriteStream()
  #mdex.write(stream)
  p = DexWriter(mdex)
  p.write(stream)


def main():
  #print_dex('test_binary/classes.dex')
  #print_dex('test_binary/more_large.dex')
  duplicate_dex('test_binary/classes.dex')

if __name__ == '__main__':
  main()