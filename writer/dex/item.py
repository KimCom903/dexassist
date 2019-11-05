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
  def __init__(self,value):
    self.string_data_off = Offset(value)
    pass

class StringDataItem(DexWriteItem):
  descriptor = {
    'utf16_size': ULEB
  }

  def __init__(self, value):
    self.string_value = value
    self.utf16_size = len(value)

  def write_byte_remain(self, stream):
    ret = stream.write_string(self.string_value)
    return ret
    
class MaplistItem(DexWriteItem):
  descriptor = {
    'size': UINT
  }
  
  def __init__(self, value):
    self.map_list = value
    self.uint_size = len(value)

  def write_byte_remain(self, stream):
    ret = 0
    for it in self.map_list:
      ret = MapItem(it).write(stream)
    return ret
  
class MapItem(DexWriteItem):
  descriptor = {
    'type': USHORT,
    'unused': USHORT,
    'size': UINT,
    'offset': UINT
  }
  
  def __init__(self,value):
    self.type - value.type
    self.unused = 0
    self.size = value.size
    self.offset = Offset(value)

## MapItem이랑 Maplist는 header file writer가 있는 writer.py에서 하는게 좋을 거 같아요 저희가 class화 시킨 쪽에선 없는 거 같은데
## 일단은 있다고 가정하고 만들어 두겠습니다.



class TypeIdItem(DexWriteItem):
  descriptor = {
    'descriptor_idx': UINT
  }
  def __init__(self,type_value,StringSection):
    self.descriptor_idx = StringSection.get_id(type_value)
    
class ProtoIdItem(DexWriteItem):
  descriptor = {
    'shorty_idx': UINT,
    'return_type_idx': UINT,
    'parameters_off': UINT
  }
  def __init__(self, proto_value, StringSection, TypeSection):
    self.shorty_idx = StringSection.get_id(proto_value)
    self.return_type_idx = TypeSection.get_id(proto_value)
    ## self.parameters_off

class FieldIdItem(DexWriteItem):
  descriptor = {
    'class_idx': USHORT,
    'type_idx': USHORT,
    'name_idx': UINT
  }
  def __init__(self, DexField, ClassSection, TypeSection, StringSection):
    self.class_idx = ClassSection.get_id(DexField.clazz) 
    self.type_idx = TypeSection.get_id(DexField.type)
    self.name_idx = StringSection.get_id(DexField.name)

class MethodIdItem(object):
  descriptor = {
    'class_idx': USHORT,
    'proto_idx': USHORT,
    'name_idx': UINT
  }
  def __init__(self, DexMethod, ClassSection, ProtoSection, StringSection):
    self.class_idx = ClassSection.get_id(DexMethod.clazz)
    self.proto_idx = ProtoSection.get_id(DexMethod.params) ## proto로 따로 저장된게 없어서 param으로 두긴 했는데 가능 할까요??
    self.name_idx = StringSection.get_id(DexMethod.name)

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
  def __init__(self,DexClass, ClassSection):
    self.class_idx = ClassSection.get_id(DexClass)
    self.access_flags = value.access_flag
    self.superclass_idx = ClassSection.get_id(DexClass.superclass)
    self.interfaces_off = Offset(DexClass.interfaces)
    self.source_file_idx = Offset(DexClass.source_file_name)
    self.annotations_off = Offset(DexClass.annotations)
    self.class_data_off = Offset(DexClass)
    self.static_values_off
    

class ClassDataItem(DexWriteItem):
  descriptor = {
    'static_fields_size': ULEB,
    'instance_fields_size': ULEB,
    'direct_methods_size': ULEB,
    'virtual_methods_size': ULEB,
  }
  def __init__(self,DexClass):
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
      ret += EncodedField(f).write(stream)
    for f in self.instance_fields:
      ret += EncodedField(f).write(stream)
    for m in self.direct_methods:
      ret += EncodedMethod(m).write(stream)
    for m in self.virtual_methods:
      ret += EncodedMethod(m).write(stream)
    return ret
  
class EncodedField(DexWriteItem):
  descriptor = {
    'field_idx': ULEB,
    'access_flags': ULEB
  }
  def __init__(self,DexField,FieldSection):
    self.field_idx = FieldSection.get_id(DexField)
    self.access_flags = value.access_flags
    
class EncodedMethod(DexWriteItem):
  descriptor = {
    'method_idx_diff': ULEB,
    'access_flags': ULEB,
    'code_off': ULEB # OFFSET이 ULEB 타입
  }
  def __init__(self,DexMethod,MethodSection,pre_idx):
    self.method_idx_diff = pre_idx - MethodSection.get_id(DexMethod)
    self.access_flags = DexMethod.access_flags
    self.code_off = Offset(DexMethod.editor.opcode_list) # OFFSET이 ULEB 타입
  
class CallSiteIdItem(DexWriteItem):
  descriptor = {
    'call_site_off': UINT
  }
  def __init__(self,value):
    self.call_site_off = Offset(value)
    pass

class MethodHandleItem(DexWriteItem):
  descriptor = {
    'method_handle_type': USHORT,
    'unused1': USHORT,
    'field_or_method_id': USHORT,
    'unused2': USHORT
  }
  def __init__(self,value):
    self.method_handle_type = value.type 
    self.unused1 = 0
    self.field_or_method_id = Offset(value)
    self.unused2 = 0
    
class TypeList(DexWriteItem):
  descriptor = {
    'size': UINT
  }  
  def __init__(self,value):
    ##value대신에 TypeSection을 쓰는것도 괜찮아 보임 다만 Section 쪽 구현이 안되어 있음
    self.list = value
    self.size = len(value)
  def write_byte_remain(self,stream):
    ret = 0
    for it in self.list:
      ret += TypeItem(it).write(strem)
    return ret

class TypeItem(DexWriteItem):
  descriptor = {
    'type_idx': USHORT
  } 
  def __init__(self,type_value,TypeSection):
    self.type_idx = TypeSection.get_id(type_value)
    
   

class CodeItem(DexWriteItem):
  descriptor = {
    'registers_size': USHORT,
    'ins_size':	USHORT,
    'outs_size': USHORT,
    'tries_size': USHORT,
    'debug_info_off': UINT,
    'insns_size': UINT,
  } 
  def __init__(self,editor):
    self.tries = editor.tries
    self.opcodes = editor.opcode_list
    ## self.registers_size
    self.ins_size =
    self.outs_size = 
    self.tries_size = len(editor.tries)
##  self.degub_info_off 
    self.insns_size = 0
    for it in editor.opcode_list:
      self.insns_size += len(it)/2
    
  def write_byte_remain(self,stream):
    ret = 0
    for it in self.opcodes:
      ## opcode를 byte로 해서 다시 쓰는 작업이 필요함
    ##padding
    for it in self.tries:
      ret += TryItem(it).write(stream)
    ##handler쪽 문제
    return ret

class TryItem(DexWriteItem):
  descriptor = {
    'start_addr': UINT,
    'ins_count':	USHORT,
    'handler_off': USHORT
  }
  def __init__(self,Editor_Try):
    self.start_addr = Offset(Editor_Try) ##이게 맞는지 모르겠어요 addr인데 Offset으로 해도 되는지
    self.ins_count = Editor_Try.end - Editor_Try.start + 1 ##이거 try의 start와 end를 수정할 떄도 update 해줘야 할거 같아요
    self.handler_off = Offset(Editor_Try.catch_handlers)

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
  def __init__(self,Editor_Try): ##catch handler_all_adr이부분 잘못 파싱된거 같아요
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
  def __init__(self,TryCatch_handler_item,TypeSection):
    self.type_idx =  TypeSection.get_id(TryCatch_handler_item[0])
    self.addr = Offset(TryCatch_handler_item[1]) ## 이것도 그냥 주소로만 되어있는데 labeling이 되거나 따로 변경 됬어야 하는거 아닌가요?
  
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
  
  def __init__(self, DexClass):
    self.class_annotations_off = Offset(DexClass.annotations)
    self.fields = []
    self.method_annotations = []
    self.parameter_annotations = []  ## 이것들 오름차순인데 순서 대로 들어가겠죠 풀도 똑같은 순서로 만드니까요
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
      ret += FieldAnnotation(a).write(stream)
    for a in self.method_annotations:
      ret += MethodAnnotation(a).write(stream)
    for a in self.parameter_annotations:
      ret += ParameterAnnotation(a).write(stream)
    return ret


class FieldAnnotation(DexWriteItem):
  descriptor = {
    'field_idx': UINT,
    'annotations_off': UINT
  }
  def __init__(self,DexField,FieldSection):
    self.field_idx = FieldSection.get_id(DexField)
    self.annotations = DexField.annotatations
    self.annotations_off = Offset(DexField.annotations)
  
class MethodAnnotation(DexWriteItem):
  descriptor = {
    'method_idx': UINT,
    'annotations_off': UINT
  }
  def __init__(self,DexMethod,MethodSection):
    self.method_idx = MethodSection.get_id(DexMethod)
    self.annotations = DexMethod.annotatations
    self.annotations_off = Offset(DexMethod.annotations)


class ParameterAnnotation(DexWriteItem):
  descriptor = {
    'method_idx': UINT,
    'annotations_off': UINT
  }
  def __init__(self,DexMethod,MethodSection):
    self.method_idx = MethodSection.get_id(DexMethod)
    self.annotations_off = Offset(DexMethod.params)

class AnnotationSetRefList(DexWriteItem):
  descriptor = {
    'size': UINT
  }
  def __init__(self,value):
    self.list = []
    
    ## initpart
    
    self.size = len(list)
   
    
  def write_byte_remain(self,stream):
    ret = 0
    for a in self.list:
      ret += AnnotationSetRefItem(a).write(stream)
    return ret

class AnnotationSetRefItem(DexWriteItem):
  descriptor = {
    'annotations_off': UINT
  }
  def __init__(self,value):
    self.annotations_off = Offset(value)
      

class AnnotationSetItem(DexWriteItem):
  descriptor = {
    'size': UINT
  }
  def __init__(self,value):
    self.entries = []
    
    ## init__part
    
    self.size = len(self.entries)
   
    
  def write_byte_remain(self,stream):
    ret = 0
    for a in self.entries:
      ret += AnnotationOffItem(a).write(stream)
    return ret



class AnnotationOffItem(DexWriteItem):
  descriptor = {
    'annotation_off': UINT
  }
  def __init__(self,value):
    self.annotations_off = Offset(value)

class AnnotationItem(DexWriteItem):
  descriptor = {
    'visibility': UBYTE
  }
  def __init__(self,DexAnnotation):
    self.annotation = DexAnnotation.target
    self.visibility = DexAnnotation.visibility
    
  def write_byte_remain(self,stream):
    ret = 0
    for a in self.annotations:
      ret += EncodedAnnotation(a).write(stream)
    return ret  

  
### Encoded Value 타입에 따라서 쓰는 거 만들어야 함 미구현 상태

class HiddenapiClassDataItem(DexWriteItem):
  descriptor = {
    'size': UINT
  }
  def __init__(self,value):
    self.offsets = []
    self.flags = []
  def write_byte_remain(self,stream):
    ret = 0
    return ret 
  
  
