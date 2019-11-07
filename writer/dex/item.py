from zlib import adler32
import struct
import inspect


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

OFFSET = 15

MOD_ADLER = 65521

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

def calc_adler32(data, length):
  a = 1
  b = 0
  for i in range(length):
    a = (a + ord(data[i])) % MOD_ADLER
    b = (b + a) % MOD_ADLER
  return (b << 16) | a

class BaseStream(object):
  def __init__(self):
    self.buf = bytearray()
  def write(self, arr):
    self.buf += arr

class DexWriteStream(object):

  def count_bytes(self, value, is_short_length):
    result = 0
    length = len(value)
    i = 0
    while(i < length):
      ch = value[i]
      if ch != 0 and ch <= 127: 
        result += 1
      elif ch <= 2047:
        result += 2
      else:
        result += 3
      
      if not is_short_length or result <= 65535:
        i += 1
    
    return result
  
  def encode(self, value):
    ret = bytearray(self.count_bytes(True))
    length = len(value)
    i = 0
    offset = 0
    offset2 = 0
    while i < length:
      ch = value[i]
      if ch != 0 and ch <= 127:
        offset = offset2 + 1
        ret[offset2] = ch
      elif ch <= 2047:
        offset = offset2 + 1
        ret[offset2] = ((ch >> 6) & 31) | 192
        offset2 = offset + 1
        ret[offset] = ((ch & 63) | 128)
        offset = offset2
      else:
        offset = offset2 + 1
        ret[offset2] = ((ch >> 12) & 15) | 224
        offset2 = offset + 1
        ret[offset] = ((ch >> 6) & 63 | 128)
        offset = offset2 + 1
        ret[offset2] = ((ch & 63) | 128)
      i += 1
      offset2 = offset
    return ret

  def as_byte(self, fmt, value):
    return struct.pack(fmt, value)
  def write_ubyte(self, value):
    self.write_byte_array( as_byte(UBYTE_FMT, value))
    return 1
  def write_short(self, value):
    self.write_byte_array( as_byte(SHORT_FMT, value))
    return 2
  def write_ushort(self, value):
    self.write_byte_array( as_byte(USHORT_FMT, value))
    return 2
  def write_int(self, value):
    self.write_byte_array( as_byte(INT_FMT, value))
    return 4
  def write_uint(self, value):
    self.write_byte_array( as_byte(UINT_FMT, value))
    return 4
  def write_ulong(self, value):
    self.write_byte_array( as_byte(ULONGLONG_FMT, value))
    return 8
  def write_long(self, value):
    self.write_byte_array( as_byte(LONGLONG_FMT, value))
    return 8
  def write_string(self, value):
    val = self.encode(value)
    self.write_byte_array( val)
    return len(val)

  def write_uleb(self, value):
    ret = bytearray()
    remaining = value >> 7
    size = 0
    while remaining:
      ret.append((value & 127) | 128)
      value = remaining
    ret.append(value & 127)
    size += 1
    self.write_byte_array(ret)
    return size

  def write_sleb(self, value):
    ret = bytearray()
    remaining = value >> 7
    has_more = 128
    end = 0 if 0x7fffffff & value == 0 else 1
    size = 0
    while has_more:
      has_more = 0 if remaining == end and (remaining & 1) == ((value >> 6) & 1) else 128
      ret.append(has_more | (value & 127))
      value = remaining
      remaining >>= 7
      size += 1
    self.write_byte_array(ret)
    return size
  def write_ulebp1(self, value):
    return self.write_uleb(value + 1)

  def __init__(self):

    self.write_map = {
      BYTE: self.write_ubyte,
      UBYTE: self.write_ubyte,

      SHORT: self.write_short,
      USHORT: self.write_ushort,

      INT: self.write_int,
      UINT: self.write_uint,

      LONG: self.write_long,
      ULONG: self.write_ulong,

      SLEB: self.write_sleb,

      ULEB: self.write_uleb,
      ULEBP1: self.write_ulebp1,
      STRING: self.write_string,

      MAGIC: self.write_magic,
      SIGNATURE: self.write_signature

    }
  def write_object(self, offset, item):
    """
    return item.size
    """
    self.base_stream.tell(offset)
    return item.write(self.base_stream, offset)
  def write_object(self, item):
    return item.write(self.base_stream, offset)
  def write_byte_array(self, byte_arr):
    self.base_stream.write(byte_arr)

  def get_current_offset(self):
    return self.offset
  def __init__(self, base_stream):
    self.offset = 0
    self.base_stream = base_stream
  
  def set_offset(self, offset):
    self.offset = offset

def onOffsetUpdate(offset_object):
  def _offset_update(stream, caller):
    if offset_object.offset == -1:
      raise Exception('offset update failed, offset is not set!')
    stream.at(offset_object.offset).write_uint(caller.base_index)
  return _offset_update

class Offset(object):
  def __init__(self, item):
    item.on_update.append(onOffsetUpdate(self))
    self.offset = -1

  def get_type(self):
    return UINT

class DexWriteItem(object):
  descriptor = {}
  def __init__(self):
    self.on_update = []
    self.base_index = 0

  def as_byte(self, stream):
    self.base_index = stream.get_offset()
    ret = self.write_byte_descriptor(stream)
    ret += self.write_byte_remain(stream)
    for x in self.on_update:
      x(stream, self)
    return ret

  def write_byte_remain(self, stream):
    return 0

  def write_byte_descriptor(self, stream):
    ret = 0
    for x in self.descriptor:
      if x == OFFSET:
        getattr(self, x).offset = stream.get_offset()
        ret += stream.write_map[getattr(self, x).get_type()](0)

      else:
        ret += stream.write_map[self.descriptor[x]](getattr(self, x))
    return ret

  def write(self, stream):
    ret = self.write_byte_descriptor(stream)
    ret += self.write_byte_remain(stream)
    return ret



class StringIdItem(DexWriteItem):
  descriptor = {
    'string_data_off': UINT
  }
  def __init__(self,value,manager):
    self.string_data_off = Offset(StringDataItem(value))
    pass

class StringDataItem(DexWriteItem):
  descriptor = {
    'utf16_size': ULEB
  }

  def __init__(self, value,manager):
    self.string_value = value
    self.utf16_size = len(value)

  def write_byte_remain(self, stream):
    ret = stream.write_string(self.string_value)
    return ret
    
class MaplistItem(DexWriteItem):
  descriptor = {
    'size': UINT
  }
  
  def __init__(self, value, manager):
    self.manager = manager
    self.map_list = value
    self.uint_size = len(value)

  def write_byte_remain(self, stream):
    ret = 0
    for it in self.map_list:
      ret = MapItem(it,self.manager).write(stream)
    return ret
  
class MapItem(DexWriteItem):
  descriptor = {
    'type': USHORT,
    'unused': USHORT,
    'size': UINT,
    'offset': UINT
  }
  
  def __init__(self,value,manager):
    self.manager = manager
    self.type - value.type
    self.unused = 0
    self.size = value.size
    type_desc = [
      0x0000:	HeaderItem,
      0x0001:	StringIdItem,
      0x0002:	TypeIdItem,
      0x0003:	ProtoIdItem,
      0x0004:	FieldIdItem,
      0x0005:	MethodIdItem,
      0x0006:	ClassDefItem,
      0x0007:	CallSiteIdItem,
      0x0008:	MethodHandleItem,
      0x1000:	MapList,
      0x1001:	TypeList,
      0x1002:	AnnotationSetRefList,
      0x1003:	AnnotationSetItem,
      0x2000:	ClassDataItem,
      0x2001:	CodeItem,
      0x2002:	StringDataItem,
      0x2003:	DebugInfoItem,
      0x2004:	AnnotationItem,
      0x2005:	EncodedArrayItem,
      0x2006:	AnnotationsDirectoryItem,
      0xF000:	HiddenapiClassDataItem
    ]
    self.offset = Offset(type_desc[value.type]())

## 이거 item 마다 param가 다름 일일히 하나하나 설정해야하는지 생각



class TypeIdItem(DexWriteItem):
  descriptor = {
    'descriptor_idx': UINT
  }
  def __init__(self,type_value,manager):
    self.descriptor_idx = manager.StringSection.get_id(type_value)
    
class ProtoIdItem(DexWriteItem):
  descriptor = {
    'shorty_idx': UINT,
    'return_type_idx': UINT,
    'parameters_off': UINT
  }
  def __init__(self, proto_value, manager):
    self.shorty_idx = manager.StringSection.get_id(proto_value)
    self.return_type_idx = manager.TypeSection.get_id(proto_value)
    self.parameters_off = Offset(TypeItem(proto_value))

class FieldIdItem(DexWriteItem):
  descriptor = {
    'class_idx': USHORT,
    'type_idx': USHORT,
    'name_idx': UINT
  }
  def __init__(self, DexField, manager):
    self.class_idx = manager.ClassSection.get_id(DexField.clazz) 
    self.type_idx = manager.TypeSection.get_id(DexField.type)
    self.name_idx = manager.StringSection.get_id(DexField.name)

class MethodIdItem(DexWriteItem):
  descriptor = {
    'class_idx': USHORT,
    'proto_idx': USHORT,
    'name_idx': UINT
  }
  def __init__(self, DexMethod, manager):
    self.class_idx = manager.ClassSection.get_id(DexMethod.clazz)
    self.proto_idx = manager.ProtoSection.get_id(DexMethod.params) ## proto로 따로 저장된게 없어서 param으로 두긴 했는데 가능 할까요??
    self.name_idx = manager.StringSection.get_id(DexMethod.name)

class ClassDefItem(DexWriteItem):
  descriptor = {
    'class_idx': UINT,
    'access_flags': USHORT,
    'superclass_idx': UINT,
    'interfaces_off': UINT,
    'source_file_idx': UINT,
    'annotations_off': UINT,
    'class_data_off': UINT,
    'static_values_off': UINT
  }
  def __init__(self,DexClass, manager):
    self.class_idx = manager.TypeSection.get_id(DexClass)
    self.access_flags = value.access_flag
    self.superclass_idx = manager.TypeSection.get_id(DexClass.superclass)
    self.interfaces_off = Offset(TypeList(DexClass.interfaces,self.manager))
    self.source_file_idx = manager.StringSection.get_id(DexClass.source_file_name)
    self.annotations_off = Offset(AnnotationsDirectoryItem(DexClass,self.manager))
    self.class_data_off = Offset(ClassDataItem(DexClass,manager))
    ##self.static_values_off
    

class ClassDataItem(DexWriteItem):
  descriptor = {
    'static_fields_size': ULEB,
    'instance_fields_size': ULEB,
    'direct_methods_size': ULEB,
    'virtual_methods_size': ULEB,
  }
  def __init__(self,DexClass,manager):
    self.manager = manager
    self.class = DexClass
    self.static_fields = []
    self.instance_fields = []
    self.direct_methods = []
    self.virtual_methods = []
    for f in class.fields:
      pass
    for m in class.methods:
      pass
    
    ## 이거 convert할때 method랑 field 따로 저장하면 안되나요???
    
    self.static_fields_size = len(self.static_fields)
    self.instance_fields_size = len(self.instance_fields)
    self.direct_methods_size = len(self.direct_methods)
    self.virtual_methods_size = len(self.virtual_methods)
  
  def write_byte_remain(self, stream):
    ret = 0
    for f in self.static_fields:
      ret += EncodedField(f,self.manger).write(stream)
    for f in self.instance_fields:
      ret += EncodedField(f,self.manager).write(stream)
    for m in self.direct_methods:
      ret += EncodedMethod(m,self.manager).write(stream)
    for m in self.virtual_methods:
      ret += EncodedMethod(m,self.manager).write(stream)
    return ret
  
class EncodedField(DexWriteItem):
  descriptor = {
    'field_idx_diff': ULEB,
    'access_flags': ULEB
  }
  def __init__(self,DexField,manager,pre_idx):
    self.field_idx_diff = FieldSection.get_id(DexField) - pre_idx
    self.access_flags = value.access_flags
    
class EncodedMethod(DexWriteItem):
  descriptor = {
    'method_idx_diff': ULEB,
    'access_flags': ULEB,
    'code_off': ULEB # OFFSET이 ULEB 타입
  }
  def __init__(self,DexMethod,manager,pre_idx):
    self.method_idx_diff = manager.MethodSection.get_id(DexMethod) - pre_idx
    self.access_flags = DexMethod.access_flags
    self.code_off = Offset(CodeItem(DexMethod.editor),self,manager) # OFFSET이 ULEB 타입
  
class CallSiteIdItem(DexWriteItem): ##callsiteitem
  descriptor = {
    'call_site_off': UINT
  }
  def __init__(self,value,manager):
    self.call_site_off = Offset(CallSiteItem(value,manager))
    pass

class CallSiteItem(DexWriteItem): 
  def __init__(self,value,manager):
    pass
  
class MethodHandleItem(DexWriteItem):
  descriptor = {
    'method_handle_type': USHORT,
    'unused1': USHORT,
    'field_or_method_id': USHORT,
    'unused2': USHORT
  }
  def __init__(self,value,manager):
    self.method_handle_type = value.type 
    self.unused1 = 0
    self.field_or_method_id = 0
    self.unused2 = 0
    
class TypeList(DexWriteItem):
  descriptor = {
    'size': UINT
  }  
  def __init__(self,value,manager):
    ##value대신에 TypeSection을 쓰는것도 괜찮아 보임 다만 Section 쪽 구현이 안되어 있음
    self.manager = manager
    self.list = value
    self.size = len(value)
  def write_byte_remain(self,stream):
    ret = 0
    for it in self.list:
      ret += TypeItem(it,self.manager).write(strem)
    return ret

class TypeItem(DexWriteItem):
  descriptor = {
    'type_idx': USHORT
  } 
  def __init__(self,type_value,manager):
    self.type_idx = manager.StringSection.get_id(type_value)
    
   

class CodeItem(DexWriteItem):
  descriptor = {
    'registers_size': USHORT,
    'ins_size':	USHORT,
    'outs_size': USHORT,
    'tries_size': USHORT,
    'debug_info_off': UINT,
    'insns_size': UINT,
  } 
  def __init__(self,editor,manager):
    self.manager = manager
    self.tries = editor.tries
    self.opcodes = editor.opcode_list
    ## self.registers_size
    ## self.ins_size
    ## self.outs_size 
    self.tries_size = len(editor.tries)
    ## self.degub_info_off 
    self.insns_size = 0
    for it in editor.opcode_list:
      self.insns_size += len(it)/2
    
  def write_byte_remain(self,stream):
    ret = 0
    for it in self.opcodes:
      it.write_byte_stream(stream)
    for it in self.tries:
      ret += TryItem(it,self.manager).write(stream)
    ##handler쪽 문제
    return ret

class TryItem(DexWriteItem):
  descriptor = {
    'start_addr': UINT,
    'ins_count':	USHORT,
    'handler_off': USHORT
  }
  def __init__(self,Editor_Try,manager):
    ##self.start_addr 시작주소를 어떻게 해야할지 모르겠네요
    self.ins_count = Editor_Try.end - Editor_Try.start + 1 ##이거 try의 start와 end를 수정할 떄도 update 해줘야 할거 같아요
    self.handler_off = Offset(EncodedCatchHandler(Editor_Try.catch_handlers,manager))

class EncodedCatchHandlerList(DexWriteItem): ##이건 0으로 초기화 시켜두고 해야 할거 같아요 직접 wrtie하는 부분에서 해결해야 할것 같아요
  descriptor = {
    'size': ULEB
  }  
  def __init__(self):
    self.size = 0

  
class EncodedCatchHandler(DexWriteItem): 
  descriptor = {
    'size': SLEB
  }  
  def __init__(self,Editor_Try,manager): ##catch handler_all_adr이부분 잘못 파싱된거 같아요
    self.size = len(Editor_Try.handler)
    self.catch_all_adr
  def write_byte_remain(self,stream):
    ret = 0
    ret += 
    ret += 
    return ret
  
class EncodedTypeAddrPair(DexWriteItem):
  descriptor = {
    'type_idx': ULEB
    'addr': ULEB
  }  
  def __init__(self,TryCatch_handler_item,manager):
    self.type_idx = manager.TypeSection.get_id(TryCatch_handler_item[0])
    ##self.addr ##주소로 되있는 것들은 어떻게 처리할지 모르겠네요
  
class DebugInfoItem(DexWriteItem):
  descriptor = {
    'line_start': ULEB,
    'parameters_size': ULEB
  }
  
  def __init__(self, value):
    self.line_start = 0
    self.parameters_size = 0
    
  def write_byte_remain(self,stream):
    ret = 0
    return ret


class AnnotationsDirectoryItem(DexWriteItem):
  descriptor = {
    'class_annotations_off': UINT,
    'fields_size': UINT,
    'annotated_methods_size': UINT,
    'annotated_parameters_size': UINT
  }
  
  def __init__(self, DexClass,manager):
    self.class_annotations_off = Offset(AnnotationSetItem(DexClass.annotations,manager))
    self.fields = []
    self.method_annotations = []
    self.parameter_annotations = []  
    for it in DexClass.fields:
      for f_anno in it.annotations:
        self.field.append(f_anno)
    for it in DexClass.methods:
      for m_anno in it.annotations:
        self.field.append(m_anno)      
      for para_it in it.params:
        self.parameter_annotations.append(para_it)
    self.fields_size = len(self.fields)
    self.annotated_methods_size = len(self.method_annotations)
    self.annotated_parameters_size = len(self.parameter_annotations)
    
  def write_byte_remain(self,stream):
    ret = 0
    for a in self.fields:
      ret += FieldAnnotation(a,manager).write(stream)
    for a in self.method_annotations:
      ret += MethodAnnotation(a,manager).write(stream)
    for a in self.parameter_annotations:
      ret += ParameterAnnotation(a,manager).write(stream)
    return ret


class FieldAnnotation(DexWriteItem):
  descriptor = {
    'field_idx': UINT,
    'annotations_off': UINT
  }
  def __init__(self,DexField,manager):
    self.field_idx = manager.FieldSection.get_id(DexField)
    self.annotations = DexField.annotatations
    self.annotations_off = Offset(AnnotationSetItem(DexField.annotations,manager))
  
class MethodAnnotation(DexWriteItem):
  descriptor = {
    'method_idx': UINT,
    'annotations_off': UINT
  }
  def __init__(self,DexMethod,manager):
    self.method_idx = manager.MethodSection.get_id(DexMethod)
    self.annotations = DexMethod.annotatations
    self.annotations_off = Offset(AnnotationSetItem(DexMethod.annotations,manager))


class ParameterAnnotation(DexWriteItem):
  descriptor = {
    'method_idx': UINT,
    'annotations_off': UINT
  }
  def __init__(self,DexMethod,manager):
    self.method_idx = manager.MethodSection.get_id(DexMethod)
    self.annotations_off = Offset(AnnotationSetRefList(DexMethod.params,manager))

class AnnotationSetRefList(DexWriteItem):
  descriptor = {
    'size': UINT
  }
  def __init__(self,params,manager):
    self.list = params
    self.size = len(list)
      
  def write_byte_remain(self,stream,manager):
    ret = 0
    for a in self.list:
      ret += AnnotationSetRefItem(a,manager).write(stream)
    return ret

class AnnotationSetRefItem(DexWriteItem):
  descriptor = {
    'annotations_off': UINT
  }
  def __init__(self,value,manager):
    self.annotations_off = Offset(AnnotationSetItem(value,manager))
      

class AnnotationSetItem(DexWriteItem):
  descriptor = {
    'size': UINT
  }
  def __init__(self,value,manager):
    self.entries = value    
    self.size = len(self.entries)
   
    
  def write_byte_remain(self,stream):
    ret = 0
    for a in self.entries:
      ret += AnnotationOffItem(a,manager).write(stream)
    return ret



class AnnotationOffItem(DexWriteItem):
  descriptor = {
    'annotation_off': UINT
  }
  def __init__(self,value,manager):
    self.annotations_off = Offset(AnnotationItem(value,manager))

class AnnotationItem(DexWriteItem):
  descriptor = {
    'visibility': UBYTE
  }
  def __init__(self,DexAnnotation,manager):
    self.annotation = DexAnnotation.target
    self.visibility = DexAnnotation.visibility
    
  def write_byte_remain(self,stream):
    ret = 0
    for a in self.annotations:
      ret += EncodedAnnotation(a,manager).write(stream)
    return ret  

  
### Encoded Value 타입에 따라서 쓰는 거 만들어야 함 미구현 상태

class HiddenapiClassDataItem(DexWriteItem):
  descriptor = {
    'size': UINT
  }
  def __init__(self,value,manager):
    self.offsets = []
    self.flags = []
  def write_byte_remain(self,stream):
    ret = 0
    return ret 
