import sys
sys.path.append('../')
import json
from dexassist.dex import converter, dex
from dexassist.writer import dex as writer_dex
from dexassist.writer.dex.writer import DexWriter
from dexassist.writer.dex.stream import OutputStream
def name_generator():
  index = 0
  while True:
    index += 1
    yield 'a' + bin(index)[2:].replace('0', 'I')
def read_obfuscate(path):
  with open(path, 'r') as f:
    return json.load(f)

def obfuscate(dex_path, out_path, obfuscate_table):
  name_gen = name_generator()
  with open(dex_path, 'rb') as f:
    x = f.read()
  manager = dex.DexManager()
  stream = dex.StreamReader(x, manager)
  header = dex.HeaderItem(manager, stream, 0)
  mdex = converter.DexConverter().get_dex(header, manager)
  all = True
  for clazz in mdex.classes:
    print(clazz.type)
    if clazz.type not in obfuscate_table: continue
    detail_rule = obfuscate_table[clazz.type]
    all = False
    if detail_rule == "*":
      all = True
    for method in clazz.methods:
      if not all and method.name not in detail_rule: continue
      method.name = next(name_gen)
    for field in clazz.fields:
      if not all and field.name not in detail_rule: continue
      field.name = next(name_gen)

  buf = bytearray()
  stream = OutputStream(buf,0)
  #mdex.write(stream)
  p = DexWriter(mdex)
  p.write(stream)


def main():
  dex_path = sys.argv[1]
  out_path = sys.argv[2]
  obfuscate_table = read_obfuscate(sys.argv[3])
  obfuscate(dex_path, out_path, obfuscate_table)


main()