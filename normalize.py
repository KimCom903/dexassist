
class Dex(object):
  def __init__(self):
    self.classes = []

  def add_class(self, clazz):
    self.classes.append(clazz)

class DexClassItem(object):
  def __init__(self):
    self.annotations = []
    self.methods = []
    # direct_methods = any of static, private, or constructor
    # virtual_methods = none of static, private, or constructor
    self.fields = []
    self.type = None
    self.name = None
    self.access_flag = 0
    self.superclass = None
    self.source_file_name = None
    self.interfaces = []
  def set_name(self):
    return self.name
  def add_annotation(self, annotation):
    self.annotations.append(annotation)
  def __str__(self):
    return self.name

  def get_related_strings(self):
    ret = set()
    OP_CONST_STRING = 0x1a
    ret.add(self.name)
    ret.add(self.type)
    for x in self.methods:
      editor = x.get_editor()
      for opcode in editor.opcodes:
        if opcode.op == OP_CONST_STRING:
          ret.add(opcode.get_string())
      return ret
    for x in self.fields:
      ret.add(x.type)


class DexField(object):
  def __init__(self, parent, field_name, type_name, access_flags):
    self.annotations = []
    self.name = field_name
    self.type = type_name
    self.clazz = parent
    self.access_flags = access_flags

  def __str__(self):
    ret = '{}::{} [{}]'.format(self.clazz, self.name, self.type)
    if self.annotations:
      a = []
      for ann in self.annotations:
        a.append('@' + str(ann))
      ret += ''.join(a)
    print(ret)
    return ret



class DexMethod(object):
  def __init__(self, parent, method_name, access_flags, signature, editor):
    self.annotations = []
    self.name = method_name
    self.clazz = parent
    self.return_type, self.params = self.parse_signature(signature)
    self.signature = signature
    print('signature : {}'.format(signature))
    self.editor = editor

  def create_proto(self):
    pass

  def create_shorty_descriptor(self):
    return self.signature

  def parse_type(self, value):
    pass

  def parse_signature(self, signature):
    x = signature.split(')')
    return_type = x[1]
    params = x[0][1:]
    return return_type, params

  def __str__(self):
    ret = '{}::{} [{}]'.format(self.clazz, self.name, self.signature)
    if self.annotations:
      a = []
      for ann in self.annotations:
        a.append('@' + str(ann))
      ret += ''.join(a)
    opcodes = '\n'
    if self.editor:
      for x in self.editor.opcodes:
        opcodes += str(x) + '\n'
      for x in self.editor.tries:
        opcodes += str(x) + '\n'
    ret += opcodes

    return ret

class DexAnnotation(object):
  def __init__(self, target, visibility, type_name, key_name_tuples):
    self.target = target
    self.visibility = visibility
    self.type_name = type_name
    self.key_name_tuples = key_name_tuples

  def __str__(self):
    return '{}({})'.format(self.type_name, self.key_name_tuples)
VALUE_TYPE_BYTE = 0x00
VALUE_TYPE_SHORT = 0x02
VALUE_TYPE_CHAR = 0x03
VALUE_TYPE_INT = 0x04
VALUE_TYPE_LONG = 0x06
VALUE_TYPE_FLOAT = 0x10
VALUE_TYPE_DOUBLE = 0x11
VALUE_TYPE_METHOD_TYPE = 0x15
VALUE_TYPE_METHOD_HANDLE = 0x16
VALUE_TYPE_STRING = 0x17
VALUE_TYPE_TYPE = 0x18
VALUE_TYPE_FIELD = 0x19
VALUE_TYPE_METHOD = 0x1a
VALUE_TYPE_ENUM = 0x1b
VALUE_TYPE_ARRAY = 0x1c
VALUE_TYPE_ANNOTATION = 0x1d
VALUE_TYPE_NULL = 0x1e
VALUE_TYPE_BOOLEAN = 0x1f
VALUE_TYPE_AUTO = 0xff
class DexValue(object):
  def __init__(self, value, value_type = VALUE_TYPE_AUTO):
    self.value = value
    self.value_type = value_type
  
  def encode(self, stream):
    encoded_type = self.get_type()
    encoded_value = self.value_as_byte(encoded_type)
    value_arg = len(encoded_value) - 1
    if encoded_type in [VALUE_TYPE_BYTE, VALUE_TYPE_ARRAY, VALUE_TYPE_ANNOTATION, VALUE_TYPE_NULL, VALUE_TYPE_BOOLEAN]:
      value_arg = 0
    stream.write_ubyte((((value_arg & 0xffffffff) << 5) | encoded_type))
    stream.wrte_byte_array(encoded_value)

  def value_as_byte(self, type_value):
    if type_value == VALUE_TYPE_BYTE:
      return write_1(self.value)
    if type_value in [VALUE_TYPE_SHORT, VALUE_TYPE_CHAR]:
      return write_2(self.value)
    # need struct.pack()
    
    return bytes()

  def write_1(self, value):
    return bytes([value & 0xff])
  def write_2(self, value):
    return bytes([value << 8 & 0xff, value & 0xff])
  def write_4(self, value):
    return bytes([value << 24 & 0xff, value << 16 & 0xff, value << 8 & 0xff, value & 0xff])
  def get_type(self):
    if self.value_type == VALUE_TYPE_AUTO:
      return self.get_inferenced_type()
    return self.value_type
  
  def get_inferenced_type(self):
    if self.value is None:
      return VALUE_TYPE_NULL
    if isinstance(self.value, bool):
      return VALUE_TYPE_BOOLEAN
    if isinstance(self.value, list):
      return VALUE_TYPE_ARRAY
    if isinstance(self.value, int):
      if self.value <= 0xff:
        return VALUE_TYPE_BYTE
      if self.value <= 0xffff:
        return VALUE_TYPE_SHORT
      if self.value <= 0xffffffff:
        return VALUE_TYPE_INT
      if self.value <= 0xffffffffffffffff:
        return VALUE_TYPE_LONG
    if isinstance(self.value, str):
      if len(self.value) == 1:
        return VALUE_TYPE_CHAR
      return VALUE_TYPE_STRING
    if isinstance(self.value, float):
      return VALUE_TYPE_DOUBLE
    if isinstance(self.value, DexMethod):
      return VALUE_TYPE_METHOD
    if isinstance(self.value, DexField):
      return VALUE_TYPE_FIELD
    if isinstance(self.value, DexAnnotation):
      return VALUE_TYPE_ANNOTATION