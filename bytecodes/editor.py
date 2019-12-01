


"""
this class can modify dex opcodes.

```
editor = method.get_editor()

for opcode in editor.opcodes:
  if opcode.op == CONST_STRING:
    opcode.string = opcode.string + ' update'
  if opcode.op == INVOKE_DYNAMIC:
    opcode.method = new_method
```

"""
class Editor(object):
  def find_label(self, name):
    for x in self.labels:
      if x.name == name: return x
    return None

  @property
  def unique_key(self):
    self.__unique_key += 1
    return self.__unique_key
  def __init__(self):
    """
      Parameters
        virtualized opcode list
      initialize editor instance
    """

    self.tries = []
    self.opcode_list = []
    self.labels = []
    self.__unique_key = 0
    for x in self.opcodes:
      x.unique_key = self.unique_key


  def commit(self):
    """
      commit all changed.

      changes will not affected after commit() calls.

      call in dexwriter
    """
    pass

  def save(self):
    """
      alternative commit()

      ```
        def save(self):
          self.commit()
      ```
    """
    self.commit()


  @property
  def opcodes(self):
    """
      opcode iterator
    """
    return self.opcode_list

  def is_in_try(self, opcode):
    offset = self.get_opcode_offset(opcode)
    for t in self.tries:
      if t.is_in(offset):
        return t
    return None
  def get_opcode_offset(self, opcode):
    """
      return current opcode offset
      return -1 if opcode does not exist in opcodes
    """
    i = 0
    for x in self.opcodes:
      if x.unique_key == opcode.unique_key:
        return i
      i += 1
    return -1


"""
try-catch class.


"""
class TryCatch(object):
  def __init__(self, editor, start, end, catch_handlers, catch_all_handlers):
    self.editor = editor
    self.start = start
    self.end = end
    self.catch_handlers = catch_handlers
    self.catch_all_handlers = catch_all_handlers
  def __str__(self):
    return 'start : {} end : {}'.format(self.start, self.end)
  def is_in(self, opcode):
    if isinstance(opcode, int):
      offset = opcode
    else:
      offset = self.editor.get_opcode_offset(opcode)

    start_offset = self.editor.get_opcode_offset(self.start)
    end_offset = self.editor.get_opcode_offset(self.end)
    return offset >= start_offset and offset <= end_offset

"""
virtual opcode class.

make compatable with dex opcode <-> editor opcode.

compat layer class of smali/dex opcode.

this class will be assume same interface between dex/smali
"""
class VopCode(object):
  def __init__(self, op):
    self.op = op


"""
target offset class

if opcode has target branch offset, target branch offset will be replaced with label class.


"""
class Label(object):
  def __init__(self, editor, op, name=None):
    self.op = op
    op.labeled = True
    self.editor = editor
    self.name = name
    self.editor.register_label(self)
  
  def get_offset(self):
    return self.editor.get_opcode_offset(self.op)


"""
```
label = editor.get_label_by_name("test_label")
opcode = editor.get_opcode_by_offset(68)
if opcode 

```
"""