from zlib import adler32
import struct
import inspect
"""
parse dex

"""

BYTE = 1
UBYTE = 2
SHORT = 3
USHORT = 4
INT = 5
UINT = 6
LONG = 7
ULONG = 8
SLEB = 9
ULEB = 10
ULEBP1 = 11
STRING = 12

MAGIC = 13
SIGNATURE = 14


## def item, do not use instanceof() for speed
DEX_BASE = 0x100000
ITEM_HEADER = DEX_BASE | 1
STRING_ID_ITEM = DEX_BASE | 2
TYPE_ID_ITEM = DEX_BASE | 3
PROTO_ID_ITEM = DEX_BASE | 4
FIELD_ID_ITEM = DEX_BASE | 5
METHOD_ID_ITEM = DEX_BASE | 6
CLASS_DEF_ITEM = DEX_BASE | 7
CALL_SITE_ID_ITEM = DEX_BASE | 8
METHOD_HANDLE_ITEM = DEX_BASE | 9

ENCODED_VALUE = DEX_BASE | 10
ENCODED_ARRAY = DEX_BASE | 11
ENCODED_ANNOTATION = DEX_BASE | 12
ANNOTATION_ELEMENT = DEX_BASE | 13
ENCODED_FIELD = DEX_BASE | 14
ENCODED_METHOD = DEX_BASE | 15

#type codes
TYPE_HEADER_ITEM = 0x0000
TYPE_STRING_ID_ITEM = 0x0001
TYPE_TYPE_ID_ITEM = 0x0002
TYPE_PROTO_ID_ITEM = 0x0003
TYPE_FIELD_ID_ITEM = 0x0004
TYPE_METHOD_ID_ITEM = 0x0005
TYPE_CLASS_DEF_ITEM = 0x0006
TYPE_CALL_SITE_ID_ITEM = 0x0007
TYPE_METHOD_HANDLE_ITEM = 0x0008
TYPE_MAP_LIST = 0x1000
TYPE_TYPE_LIST = 0x1001
TYPE_ANNOTATION_SET_REF_LIST = 0x1002
TYPE_ANNOTATION_SET_ITEM = 0x1003
TYPE_CLASS_DATA_ITEM = 0x2000
TYPE_CODE_ITEM = 0x2001
TYPE_STRING_DATA_ITEM = 0x2002
TYPE_DEBUG_INFO_ITEM = 0x2003
TYPE_ANNOTATION_ITEM = 0x2004
TYPE_ENCODED_ARRAY_ITEM = 0x2005
TYPE_ANNOTATIONS_DIRECTORY_ITEM = 0x2006
TYPE_HIDDENAPI_CLASS_DATA_ITEM = 0xf000


#method handle type codes
METHOD_HANDLE_TYPE_STATIC_PUT = 0x00
METHOD_HANDLE_TYPE_STATIC_GET = 0x01
METHOD_HANDLE_TYPE_INSTANCE_PUT = 0x02
METHOD_HANDLE_TYPE_INSTANCE_GET = 0x03
METHOD_HANDLE_TYPE_INVOKE_STATIC = 0x04
METHOD_HANDLE_TYPE_INVOKE_INSTANCE = 0x05
METHOD_HANDLE_TYPE_INVOKE_CONSTRUCTOR = 0x06
METHOD_HANDLE_TYPE_INVOKE_DIRECT = 0x07
METHOD_HANDLE_TYPE_INVOKE_INTERFACE = 0x08

# encoded value item
ENCODED_VALUE_BYTE = 0x00
ENCODED_VALUE_SHORT = 0x02
ENCODED_VALUE_CHAR = 0x03
ENCODED_VALUE_INT = 0x04
ENCODED_VALUE_LONG = 0x06
ENCODED_VALUE_FLOAT = 0x10
ENCODED_VALUE_DOUBLE = 0x11
ENCODED_VALUE_METHOD_TYPE = 0x15
ENCODED_VALUE_METHOD_HANDLE = 0x16
ENCODED_VALUE_STRING = 0x17
ENCODED_VALUE_TYPE = 0x18
ENCODED_VALUE_FIELD = 0x19
ENCODED_VALUE_METHOD = 0x1a
ENCODED_VALUE_ENUM = 0x1b
ENCODED_VALUE_ARRAY = 0x1c
ENCODED_VALUE_ANNOTATION = 0x1d
ENCODED_VALUE_NULL = 0x1e
ENCODED_VALUE_BOOLEAN = 0x1f


## ACCESS_FLAG
ACC_PUBLIC = 0x1
ACC_PRIVATE = 0x2
ACC_PROTECTED = 0x4
ACC_STATIC = 0x8
ACC_FINAL = 0x10
ACC_SYNCHRONIZED = 0x20
ACC_VOLATILE = 0x40
ACC_BRIDGE = 0x40
ACC_TRANSIENT = 0x80
ACC_VARARGS = 0x80
ACC_NATIVE = 0x100
ACC_INTERFACE = 0x200
ACC_ABSTRACT = 0x400
ACC_STRICT = 0x800
ACC_SYNTHETIC = 0x1000
ACC_ANNOTATION = 0x2000
ACC_ENUM = 0x4000
ACC_UNUSED = 0x8000
ACC_CONSTRUCTOR = 0x10000
ACC_DECLARED_SYNCHRONIZED = 0x20000

# VISIBILITY
VISIBILITY_BUILD = 0x00
VISIBILITY_RUNTIME = 0x01
VISIBILITY_SYSTEM = 0x02

# DEBUG_INFO_ITEM
DBG_END_SEQUENCE = 0x00
DBG_ADVANCE_PC = 0x01
DBG_ADVANCE_LINE = 0x02
DBG_START_LOCAL = 0x03
DBG_START_LOCAL_EXTENDED = 0x04
DBG_END_LOCAL = 0x05
DBG_RESTART_LOCAL = 0x06
DBG_SET_PROLOGUE_END = 0x07
DBG_SET_EPILOGUE_BEGIN = 0x08
DBG_SET_FILE = 0x09
NO_INDEX = 0xffffffff

MOD_ADLER = 65521

def calc_adler32(data, length):
  a = 1
  b = 0
  for i in range(length):
    a = (a + ord(data[i])) % MOD_ADLER
    b = (b + a) % MOD_ADLER
  return (b << 16) | a



class StreamReader(object):
  UINT_FMT = '<I'
  USHORT_FMT = '<H'
  INT_FMT = '<i'
  SHORT_FMT = '<h'
  LONG_FMT = '<l'
  ULONG_FMT = '<L'
  LONGLONG_FMT = '<q'
  ULONGLONG_FMT = '<Q'
  UBYTE_FMT = '<B'
  BYTE_FMT = '<b'

  def __init__(self, buf, manager):
    self.buf = buf
    self.manager = manager
    self.read_map = {
      BYTE: self.read_ubyte,
      UBYTE: self.read_ubyte,

      SHORT: self.read_short,
      USHORT: self.read_ushort,

      INT: self.read_int,
      UINT: self.read_uint,

      LONG: self.read_ulong,
      ULONG: self.read_ulong,

      SLEB: self.read_sleb,
      ULEB: self.read_uleb,
      ULEBP1: self.read_ulebp1,
      STRING: self.read_string,

      MAGIC: self.read_magic,
      SIGNATURE: self.read_signature
    }
  def read_ubyte(self, index, *args):
    ret = self.__read(index, 1, *args)
    ret.value = struct.unpack(self.UBYTE_FMT, ret.value)[0]
    return ret
  
  def read_uint(self, index, *args):
    ret = self.__read(index, 4, *args)
    ret.value = struct.unpack(self.UINT_FMT, ret.value)[0]
    return ret

  def read_int(self, index, *args):
    ret = self.__read(index, 4, *args)
    ret.value = struct.unpack(self.INT_FMT, ret.value)[0]
    return ret

  def read_ushort(self, index, *args):
    ret = self.__read(index, 2, *args)
    ret.value = struct.unpack(self.USHORT_FMT, ret.value)[0]
    return ret

  def read_short(self, index, *args):
    ret = self.__read(index, 2, *args)
    ret.value = struct.unpack(self.SHORT_FMT, ret.value)[0]
    return ret

  def read_ulong(self, index, *args):
    ret = self.__read(index, 8, *args)
    ret.value = struct.unpack(self.ULONGLONG_FMT, ret.value)[0]
    return ret

  def read_magic(self, index, *args):
    ret = self.__read(index, 8, *args)
    return ret

  def read_signature(self, index, *args):
    ret = self.__read(index, 20, *args)
    return ret
  def decode_string(self, arr):
    ret = [None] * len(arr)
    chr_index = 0
    size = len(arr)
    while chr_index < size:
      c = arr[chr_index]
      if c is None:
        break
      if (c >> 10) == 0b110110:
        n = None
        try:
          n = arr[chr_index + 1]
        except:
          pass
        if n and (n >> 10) == 0b110111:
          ret[chr_index] = chr(((c & 0x3ff) << 10 | (n & 0x3ff)) + 0x10000)
        else:
          ret[chr_index] = chr(c)
      else:
        ret[chr_index] = chr(c)
      chr_index += 1
    return ''.join(ret).encode('utf-8')

  def read_string(self, index):
    s = 0
    size = 0
    ret = bytearray()
    while True:
      a = self.read_ubyte(index + size).value
      size += 1
      if a == 0:
        x = self.decode_string(ret)
        #print('return string : {}'.format(x))
        return DexPrimitive(x, size)
      if a >> 7 == 0:
        ret.append(a & 0x7f)
      elif a >> 5 == 0b110:
        b = self.read_ubyte(index + size).value
        size += 1
        if (b & 0xc0) != 0x80:
          raise Exception('BAD SECOND BYTE')
        data = (((a & 0x1f) << 6) & 0xff) | b & 0x3f
        ret.append(data)
      elif a >> 4 == 0b1110:
        b = self.read_ubyte(index + size).value
        size += 1
        c = self.read_ubyte(index + size).value
        size += 1
        if ((b & 0xc0) != 0x80) or ((c & 0xc0) != 0x80):
          raise Exception('BAD THIRD BYTE')
        data = (((a & 0xf) << 12) & 0xff) | ((( b & 0x3f) << 6) & 0xff) | c & 0x3f
        ret.append(data)
      else:
        raise Exception('read string error')

  def read_sleb(self, index):
    result = 0
    shift = 0
    size = 0
    while True:
      b = self.read_ubyte(index + size).value
      size += 1
      result |= ((b & 0x7f) << shift)
      shift += 7
      if b & 0x80 == 0: break
    
    if (b & 0x40):
      result |= -(1 << shift)
    return DexPrimitive(result, size)


  
  def read_uleb(self, index, *args):
    result = 0
    shift = 0
    size = 0
    while True:
      b = self.buf[index + size]
      size += 1
      result |= ((b & 0x7f) << shift)
      if b & 0x80 == 0: break
      shift += 7
    
    return DexPrimitive(result, size)

  def read_ulebp1(self, index):
    ret = self.read_uleb(index)
    ret.val += 1
    return ret


  def __read(self, index, size, *args):
    return DexPrimitive(self.buf[index : index + size], size)

  def read_function(self, size):
    def __read(_self, index, *args):
      return DexPrimitive(self.buf[index : index + size], size)
    return __read


  def read(self, index, read_type, *args):
    fcn = self.read_map[read_type]
    return fcn(index, *args)
    
  def read_encoded_field(self, index):
    pass
  def read_encoded_method(self, index):
    pass
  def read_try_item(self, index):
    pass
  def read_encoded_catch_handler_list(self, index):
    pass
  def read_encoded_catch_handler(self, index):
    pass
  def read_encoded_type_addr_pair(self, index):
    pass
  def read_field_annotation(self, index):
    pass
  def read_method_annotation(self, index):
    pass
  def read_parameter_annotation(self, index):
    pass
  def read_annotation_set_item(self, index):
    pass
  def read_encoded_annotation(self, index):
    pass
  def read_encoded_array(self, index):
    pass
  def read_map_item(self, index):
    return MapItem(self.manager, self, index)


class DexPrimitive(object):
  def __init__(self, val, size):
    self.value = val
    self.read_size = size


class DexItem(object):
  descriptor = None

  def __init__(self, manager, root_stream, index):
    self.manager = manager
    self.root_stream = root_stream
    self.base_index = index
    self.read_size = 0
    self.value_list = {}

    for name in self.descriptor:
      self.value_list[name] = None
    self.read_property()
    self.parse_remain()

  def parse_remain(self):
    pass

  def read_property(self):
    for x in self.value_list:
      #print('read descriptor : {}'.format(x))
      #print('index : {} read_size : {}'.format(self.base_index, self.read_size))
      readobj = self.root_stream.read(self.base_index + self.read_size, self.descriptor[x])
      self.read_size += readobj.read_size
      self.value_list[x] = readobj.value

  def __getattr__(self, name):
    if name not in self.value_list:
      raise Exception('{} is not exist in {}'.format(name, self.__class__.__name__))

    return self.value_list[name]
  def __get_members(self):
    except_members = [
      'manager', 'root_stream', 'descriptor', 'value_list'
    ]
    return [i for i in dir(self) if i[:1] != '_' and i not in except_members and not inspect.ismethod(getattr(self, i))]
  def __str__(self):
    ret = ''
    for x in self.value_list:
      ret += '{} : {}\n'.format(x, self.value_list[x])
    for x in self.__get_members():
      ret += ' {} : {}\n'.format(x, getattr(self, x))

    return ret
class EncodedValue(DexItem):
  descriptor = {
    'value_type': UBYTE
  }
  def parse_remain(self):
    self.type = self.value_type & 0x1f
    self.value_size = ((self.value_type >> 5) & 0x7) + 1
    if self.type == ENCODED_VALUE_ARRAY:
      self.value = EncodedArray(self.manager, self.root_stream, self.base_index + self.read_size)
      self.read_size += self.value.read_size
      return
    elif self.type == ENCODED_VALUE_ANNOTATION:
      self.value = EncodedAnnotation(self.manager, self.root_stream, self.base_index + self.read_size)
      self.read_size += self.value.read_size
      return
    elif self.type == ENCODED_VALUE_BOOLEAN:
      self.value = ((self.value_type >> 5) == 1)
      return
    elif self.type == ENCODED_VALUE_NULL:
      self.value = None
      return
    elif self.type == ENCODED_VALUE_BYTE:
      self.value = self.root_stream.read_ubyte(self.base_index + self.read_size).value
      self.read_size += 1
      return
    value = bytearray(8)
    for i in range(self.value_size):
      value[i] = self.root_stream.read_ubyte(self.base_index + self.read_size).value
      self.read_size += 1

    if self.type in [ENCODED_VALUE_FLOAT, ENCODED_VALUE_DOUBLE]:
      self.value = self.as_float(value)
    else:
      self.value = self.as_int(value)

    if self.type == ENCODED_VALUE_METHOD_TYPE:
      self.value = self.manager.proto_list[self.value]
    elif self.type == ENCODED_VALUE_METHOD_HANDLE:
      raise Exception('METHOD HANDLE IS NOT IMPLEMENTED')
    elif self.type == ENCODED_VALUE_STRING:
      self.value = self.manager.string_list[self.value]
    elif self.type == ENCODED_VALUE_TYPE:
      self.value = self.manager.type_list[self.value]
    elif self.type == ENCODED_VALUE_FIELD:
      self.value = self.manager.field_list[self.value]
    elif self.type == ENCODED_VALUE_METHOD:
      self.value = self.manager.method_list[self.value]
    elif self.type == ENCODED_VALUE_ENUM:
      self.value = self.manager.field_list[self.value]

  def as_float(self, value):
    if self.type == ENCODED_VALUE_DOUBLE:
      return struct.unpack('d', value)[0]
    return struct.unpack('f', value[:4])[0]

  def as_int(self, value):
    if self.type == ENCODED_VALUE_LONG:
      return struct.unpack('Q', value)[0]
    return struct.unpack('I', value[:4])[0]


  def __str__(self):
    return str(self.value)
    #return 'type : 0x{:08x} value : {}'.format(self.type, self.value)



class EncodedArray(DexItem):
  descriptor = {
    'size': ULEB
  }


  def parse_remain(self):
    self.values = []
    for x in range(self.size):
      item = EncodedValue(self.manager, self.root_stream, self.base_index + self.read_size)
      self.values.append(item)
      self.read_size += item.read_size

  def __str__(self):
    return '[' + '], ['.join([str(x.value) for x in self.values]) + ']'


class EncodedAnnotation(DexItem):
  descriptor = {
    'type_idx': ULEB,
    'size': ULEB
  }

  def parse_remain(self):
    self.elements = []
    for x in range(self.size):
      item = AnnotationElement(self.manager, self.root_stream, self.base_index + self.read_size)
      self.elements.append(item)
      self.read_size += item.read_size


class AnnotationElement(DexItem):
  descriptor = {
    'name_idx': ULEB,
    #'value': ENCODED_VALUE
  }
  def parse_remain(self):
    self.value = EncodedValue(self.manager, self.root_stream, self.base_index + self.read_size)
    self.read_size += self.value.read_size

class ProtoIdItem(DexItem):
  descriptor = {
    'shorty_idx': UINT,
    'return_type_idx': UINT,
    'parameters_off': UINT
  }
  def parse_remain(self):
    self.type_list = None
    if self.parameters_off:
      self.type_list = TypeList(self.manager, self.root_stream, self.parameters_off)


class FieldIdItem(DexItem):
  descriptor = {
    'class_idx': USHORT,
    'type_idx': USHORT,
    'name_idx': UINT
  }
  def get_name(self):
    return self.manager.string_list[self.name_idx]

class MethodIdItem(DexItem):
  descriptor = {
    'class_idx': USHORT,
    'proto_idx': USHORT,
    'name_idx': UINT
  }
  def repr(self):
    return self.manager.type_list[self.class_idx] + '->' + self.manager.string_list[self.name_idx]

  def get_name(self):
    return self.manager.string_list[self.name_idx]
class ClassDefItem(DexItem):
  descriptor = {
    'class_idx': UINT,
    'access_flags': UINT,
    'superclass_idx': UINT,
    'interfaces_off': UINT,
    'source_file_idx': UINT,
    'annotations_off': UINT,
    'class_data_off': UINT,
    'static_values_off': UINT
  }
  def parse_remain(self):
    #print('** parse class_idx {}'.format(self.manager.type_list[self.class_idx]))
    self.data = None
    if self.class_data_off:
      self.data = ClassDataItem(self.manager, self.root_stream, self.class_data_off)
    self.annotations = None
    if self.annotations_off:
      self.annotations = AnnotationsDirectoryItem(self.manager, self.root_stream, self.annotations_off)
    self.static_values = None
    if self.static_values_off:
      self.static_values = EncodedArrayItem(self.manager, self.root_stream, self.static_values_off)
    self.interfaces = []
    if self.interfaces_off:
      tl = TypeList(self.manager, self.root_stream, self.interfaces_off)
      self.interfaces = [x.type_idx for x in tl.list]
  def __str__(self):
    return 'Class@' + self.manager.type_list[self.class_idx]

class ClassDataItem(DexItem):
  descriptor = {
    'static_fields_size': ULEB,
    'instance_fields_size': ULEB,
    'direct_methods_size': ULEB,
    'virtual_methods_size': ULEB
  }
  def parse_remain(self):
    self.static_fields = []
    self.instance_fields = []
    self.direct_methods = []
    self.virtual_methods = []
    for x in range(self.static_fields_size):
      item = EncodedField(self.manager, self.root_stream, self.base_index + self.read_size)
      self.static_fields.append(item)
      self.read_size += item.read_size

    for x in range(self.instance_fields_size):
      item = EncodedField(self.manager, self.root_stream, self.base_index + self.read_size)
      self.instance_fields.append(item)
      self.read_size += item.read_size

    for x in range(self.direct_methods_size):
      item = EncodedMethod(self.manager, self.root_stream, self.base_index + self.read_size)
      self.direct_methods.append(item)
      self.read_size += item.read_size

    for x in range(self.virtual_methods_size):
      item = EncodedMethod(self.manager, self.root_stream, self.base_index + self.read_size)
      self.virtual_methods.append(item)
      self.read_size += item.read_size

class EncodedField(DexItem):
  descriptor = {
    'field_idx_diff': ULEB,
    'access_flags': ULEB
  }

class EncodedMethod(DexItem):
  descriptor = {
    'method_idx_diff': ULEB,
    'access_flags': ULEB,
    'code_off': ULEB
  }
  def parse_remain(self):
    self.code = None
    if self.code_off:
      self.code = CodeItem(self.manager, self.root_stream, self.code_off)

class TypeList(DexItem):
  descriptor = {
    'size': UINT
  }
  def parse_remain(self):
    self.list = []
    for x in range(self.size):
      item = TypeItem(self.manager, self.root_stream, self.base_index + self.read_size)
      self.list.append(item)
      self.read_size += item.read_size


class TypeItem(DexItem):
  descriptor = {
    'type_idx': USHORT
  }

class CodeItem(DexItem):
  descriptor = {
    'registers_size': USHORT,
    'ins_size': USHORT,
    'outs_size': USHORT,
    'tries_size': USHORT,
    'debug_info_off': UINT,
    'insns_size': UINT
  }

  def parse_remain(self):
    #print('codesize {}'.format(self.insns_size))
    self.insns = []
    self.padding = 0
    self.tries = []
    self.handlers = None
    
    for x in range(self.insns_size):
      item = self.root_stream.read_ushort(self.base_index + self.read_size)
      self.insns.append(item.value)
      self.read_size += item.read_size
    #print('read instruction finished')
    if self.tries_size != 0 and self.insns_size % 2 == 1:
      self.padding = 0
      self.read_size += 2
    for x in range(self.tries_size):
      item = TryItem(self.manager, self.root_stream, self.base_index + self.read_size)
      self.tries.append(item)
      self.read_size += item.read_size
    #print('tries finished, parse size was {}'.format(self.tries_size))
    if self.tries_size:
      self.handlers = EncodedCatchHandlerList(self.manager, self.root_stream, self.base_index + self.read_size)
      self.read_size += self.handlers.read_size
      
    for x in self.tries:
      x.handlers = EncodedCatchHandler(self.manager, self.root_stream, x.handler_off + self.handlers.base_index)
    #print('parse finished')
    
class TryItem(DexItem):
  descriptor = {
    'start_addr': UINT,
    'insn_count': USHORT,
    'handler_off': USHORT
  }
  pass


class EncodedCatchHandlerList(DexItem):
  descriptor = {
    'size': ULEB
  }


class EncodedCatchHandler(DexItem):
  descriptor = {
    'size': SLEB
  }

  def parse_remain(self):
    self.handlers = []
    self.catch_all_addr = -1
    #print('encoded catch handler size : {}'.format(self.size))
    for x in range(abs(self.size)):
      item = EncodedTypeAddrpair(self.manager, self.root_stream, self.base_index + self.read_size)
      self.handlers.append(item)
      self.read_size += item.read_size
    if self.size < 0:
      item = self.root_stream.read_uleb(self.base_index + self.read_size)
      self.catch_all_addr = item.value
      self.read_size += item.read_size

class EncodedTypeAddrpair(DexItem):
  descriptor = {
    'type_idx': ULEB,
    'addr': ULEB
  }


class DebugInfoItem(DexItem):
  descriptor = {
    'line_start': ULEB,
    'parameters_size': ULEB
  }

  def parse_remain(self):
    self.parameter_names = []
    for x in self.parameters_size:
      item = self.root_stream.read_ulebp1(self.base_index + self.read_size)
      self.parameter_names.append(item.value)
      self.read_size += item.read_size


class AnnotationsDirectoryItem(DexItem):
  descriptor = {
    'class_annotations_off': UINT,
    'fields_size': UINT,
    'annotated_methods_size': UINT,
    'annotated_parameters_size': UINT
  }

  def parse_remain(self):
    self.field_annotations = []
    self.method_annotations = []
    self.parameter_annotations = []
    self.class_item = None
    if self.class_annotations_off:
      self.class_item = AnnotationSetItem(self.manager, self.root_stream, self.class_annotations_off)

    for x in range(self.fields_size):
      item = FieldAnnotation(self.manager, self.root_stream, self.base_index + self.read_size)
      self.field_annotations.append(item)
      self.read_size += item.read_size
    for x in range(self.annotated_methods_size):
      item = MethodAnnotation(self.manager, self.root_stream, self.base_index + self.read_size)
      self.method_annotations.append(item)
      self.read_size += item.read_size
    for x in range(self.annotated_parameters_size):
      item = ParameterAnnotation(self.manager, self.root_stream, self.base_index + self.read_size)
      self.parameter_annotations.append(item)
      self.read_size += item.read_size

class FieldAnnotation(DexItem):
  descriptor = {
    'field_idx': UINT,
    'annotations_off': UINT
  }
  def parse_remain(self):
    self.annotation = AnnotationSetItem(self.manager, self.root_stream, self.annotations_off)

class MethodAnnotation(DexItem):
  descriptor = {
    'method_idx': UINT,
    'annotations_off': UINT
  }
  def parse_remain(self):
    self.annotation = AnnotationSetItem(self.manager, self.root_stream, self.annotations_off)


class ParameterAnnotation(DexItem):
  descriptor = {
    'method_idx': UINT,
    'annotations_off': UINT
  }
  def parse_remain(self):
    self.annotation_ref = AnnotationSetRefList(self.manager, self.root_stream, self.annotations_off)

class AnnotationSetRefList(DexItem):
  descriptor = {
    'size': UINT
  }
  def parse_remain(self):
    self.list = []
    for x in range(self.size):
      item = AnnotationSetRefItem(self.manager, self.root_stream, self.base_index + self.read_size)
      self.list.append(item)
      self.read_size += item.read_size


class AnnotationSetRefItem(DexItem):
  descriptor = {
    'annotations_off': UINT
  }
  def parse_remain(self):
    self.annotation = None
    if self.annotations_off:
      self.annotation = AnnotationSetItem(self.manager, self.root_stream, self.annotations_off)

class AnnotationSetItem(DexItem):
  descriptor = {
    'size': UINT
  }
  def parse_remain(self):
    self.entries = []
    for x in range(self.size):
      item = AnnotationOffItem(self.manager, self.root_stream, self.base_index + self.read_size)
      self.entries.append(item)
      self.read_size += item.read_size



class AnnotationOffItem(DexItem):
  descriptor = {
    'annotation_off': UINT
  }

  def parse_remain(self):
    self.annotation = AnnotationItem(self.manager, self.root_stream, self.annotation_off)

class AnnotationItem(DexItem):
  descriptor = {
    'visibility': UBYTE
  }
  def parse_remain(self):
    self.annotation = EncodedAnnotation(self.manager, self.root_stream, self.base_index + self.read_size)
    self.read_size += self.annotation.read_size


class EncodedArrayItem(DexItem):
  descriptor = {

  }
  def parse_remain(self):
    self.value = EncodedArray(self.manager, self.root_stream, self.base_index + self.read_size)

class HiddenapiClassDataItem(DexItem):
  descriptor = {
    'size': UINT
  }
  def parse_remain(self):
    self.offsets = []
    self.flags = []

class DexManager(object):
  def __init__(self):
    self.string_list = []
    self.type_list = []
    self.proto_list = []
    self.field_list = []
    self.method_list = []
    self.class_def_list = []
    self.method_item_list = {}
    self.field_item_list = {}
    self.proto_item_list = {}
    self.externel_class_list = []
    
  def get_string(self, index):
    return self.string_list[index]
  def get_type(self, index):
    return self.type_list[index]
  def get_string_by_index(self, index):
    return self.get_string(index)
  def get_type_by_index(self, index):
    return self.get_type(index)
  def get_proto_by_index(self, index):
    return self.proto_list[index]
  def get_field_by_index(self, index):
    return self.field_list[index]
  def get_method_by_index(self, index):
    return self.method_list[index]
  def get_class_def_by_index(self, index):
    return self.class_def_list[index]
  def get_proto_dex_item_by_index(self, index):
    return self.proto_item_list[self.string_list[self.proto_list[index].shorty_idx]]
  def get_method_dex_item_by_index(self, index):
    return self.method_item_list[self.type_list[self.method_list[index].class_idx] + \
      self.string_list[self.method_list[index].name_idx] + \
      self.string_list[self.proto_list[self.method_list[index].proto_idx].shorty_idx]]
  def get_field_dex_item_by_index(self, index):
    return self.field_item_list[self.string_list[self.field_list[index].name_idx] + self.type_list[self.field_list[index].class_idx]]


class HeaderItem(DexItem):
  descriptor = {
    'magic': MAGIC,
    'checksum': UINT,
    'signature': SIGNATURE,
    'file_size': UINT,
    'header_size': UINT,
    'endian_tag': UINT,
    'link_size': UINT,
    'link_off': UINT,
    'map_off': UINT,
    'string_ids_size': UINT,
    'string_ids_off': UINT,
    'type_ids_size': UINT,
    'type_ids_off': UINT,
    'proto_ids_size': UINT,
    'proto_ids_off': UINT,
    'field_ids_size': UINT,
    'field_ids_off': UINT,
    'method_ids_size': UINT,
    'method_ids_off': UINT,
    'class_defs_size': UINT,
    'class_defs_off': UINT,
    'data_size': UINT,
    'data_off': UINT
  }

  def __init__(self, manager, root_stream, index):
    super(HeaderItem, self).__init__(manager, root_stream, index)

    index = self.string_ids_off
    self.manager.string_list = []
    for x in range(self.string_ids_size):
      item = StringIdItem(self.manager, self.root_stream, index)
      self.manager.string_list.append(item.get_value().value.decode('utf-8'))
      index += item.read_size

    index = self.type_ids_off
    self.type_list = []
    for x in range(self.type_ids_size):
      item = TypeIdItem(self.manager, self.root_stream, index)
      self.manager.type_list.append(self.manager.get_string(item.descriptor_idx))
      index += item.read_size

    index = self.proto_ids_off
    for x in range(self.proto_ids_size):
      item = ProtoIdItem(self.manager, self.root_stream, index)
      self.manager.proto_list.append(item)
      index += item.read_size
    index = self.field_ids_off
    for x in range(self.field_ids_size):
      item = FieldIdItem(self.manager, self.root_stream, index)
      self.manager.field_list.append(item)
      index += item.read_size

    index = self.method_ids_off
    for x in range(self.method_ids_size):
      item = MethodIdItem(self.manager, self.root_stream, index)
      self.manager.method_list.append(item)
      index += item.read_size

    index = self.class_defs_off
    for x in range(self.class_defs_size):
      item = ClassDefItem(self.manager, self.root_stream, index)
      self.manager.class_def_list.append(item)
      index += item.read_size

    self.manager.data_off = self.data_off

    if self.map_off != 0:
      self.map_list = MapList(self.manager, root_stream, self.map_off)




class MapList(DexItem):
  descriptor = {
    'size': UINT
  }

  def __init__(self, manager, root_stream, index):
    super(MapList, self).__init__(manager, root_stream, index)
    self.list = {}
    self.manager = manager

    for x in range(self.size):
      item = root_stream.read_map_item(index + self.read_size)
      item.set_manager(self.manager)
      item.parse_remain()
      self.list[item.type] = item
      self.read_size += item.read_size

  def __str__(self):
    base = super(MapList, self).__str__()
    for x in self.list:
      base += '{} : {}\n'.format(x, self.list[x])
    return base

  def get_string(self, index):
    string_id_items = self.list[TYPE_STRING_ID_ITEM]

class TypeIdItem(DexItem):
  descriptor = {
    'descriptor_idx': UINT
  }

class MapItem(DexItem):
  descriptor = {
    'type': USHORT,
    'unused': USHORT,
    'size': UINT,
    'offset': UINT
  }
  def __init__(self, manager, root_stream, index):
    super(MapItem, self).__init__(manager, root_stream, index)
    self.manager = None

  def set_manager(self, manager):
    self.manager = manager
  def parse_remain(self):
    if self.type == TYPE_HEADER_ITEM:
      pass
    if self.type == TYPE_STRING_ID_ITEM:
      pass
    elif self.type == TYPE_TYPE_ID_ITEM:
      index = self.offset
      self.type_list = []
      for x in range(self.size):
        item = TypeIdItem(self.manager, self.root_stream, index)
        #print("get type index {}".format(item.descriptor_idx))
        self.type_list.append(self.manager.get_string(item.descriptor_idx))
        index += item.read_size

    elif self.type == TYPE_PROTO_ID_ITEM:
      pass
    elif self.type == TYPE_FIELD_ID_ITEM:
      pass
    elif self.type == TYPE_METHOD_ID_ITEM:
      pass
    elif self.type == TYPE_CLASS_DEF_ITEM:
      pass
    elif self.type == TYPE_CALL_SITE_ID_ITEM:
      pass
    elif self.type == TYPE_METHOD_HANDLE_ITEM:
      pass
    elif self.type == TYPE_MAP_LIST:
      pass
    elif self.type == TYPE_TYPE_LIST:
      pass
    elif self.type == TYPE_ANNOTATION_SET_REF_LIST:
      pass
    elif self.type == TYPE_ANNOTATION_SET_ITEM:
      pass
    elif self.type == TYPE_CLASS_DATA_ITEM:
      pass
    elif self.type == TYPE_CODE_ITEM:
      pass
    elif self.type == TYPE_STRING_DATA_ITEM:
      pass
    elif self.type == TYPE_DEBUG_INFO_ITEM:
      pass
    elif self.type == TYPE_ENCODED_ARRAY_ITEM:
      pass
    elif self.type == TYPE_ANNOTATIONS_DIRECTORY_ITEM:
      pass
    elif self.type == TYPE_HIDDENAPI_CLASS_DATA_ITEM:
      pass


class StringIdItem(DexItem):
  descriptor = {
    'string_data_off': UINT
  }
  def __init__(self, manager, root_stream, index):
    super(StringIdItem, self).__init__(manager, root_stream, index)
    self.string_value = None

  def get_value(self):
    if self.string_value is None:
      v = StringDataItem(self.manager, self.root_stream, self.string_data_off)
      self.string_value = v.value
    return self.string_value

class StringDataItem(DexItem):
  descriptor = {
    'utf16_size': ULEB
  }
  def __init__(self, manager, root_stream, index):
    super(StringDataItem, self).__init__(manager, root_stream, index)
    self.value = root_stream.read_string(index + self.read_size)


