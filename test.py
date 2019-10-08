from dex import converter, dex


def main():
  with open('classes.dex', 'rb') as f:
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


if __name__ == '__main__':
  main()