from collections import OrderedDict
from normalize import DexProto
SECTION_STRING = 1
SECTION_TYPE = 2
SECTION_PROTO = 3
SECTION_FIELD = 4
SECTION_METHOD = 5
SECTION_CLASS = 6
SECTION_CALL_SITE = 7
SECTION_METHOD_HANDLE = 8
SECTION_TYPE_LIST = 9
SECTION_ENCODED_ARRAY = 10
SECTION_ANNOTATION = 11
SECTION_ANNOTATION_SET = 12

SECTION_DEBUG = 15
SECTION_CODE = 16

SECTION_MAP = 18


"""
NOTT writable!
just provide classes
"""
class Section(object):
  def __init__(self, section_manager):
    self.type_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
    self.frozen = False

  def get_section(self, key):
    return self.section_.get_section(key)

  def get_item(self, value):
    """
    return value of id
    """
    raise Exception('get_item not implemented')
  def get_item_index(self, value):
    """
    return id of value
    """
    raise Exception('get_id not implemented')

  def add_item(self, value):
    raise Exception('add_item not implemented')
  
  def get_item_count(self):
    return self.index
  def add_encoded_value(self, value):
    return self.section_.add_encoded_value(value)
  def size(self):
    return self.get_item_count()
  def freeze(self):
    self.frozen = True

class StringSection(Section):
  def __init__(self, section_):
    self.string_map = OrderedDict()
    self.index = 0
    self.section_ = section_
    self.frozen = False
  def add_item(self, value):
    # decode mutf8
    if self.frozen:
      raise Exception('section is frozen')
    if value in self.string_map: return self.string_map[value]

    self.string_map[value] = self.index # set id
    self.index += 1
  def get_item(self, value):
    return list(self.string_map.keys())[value]
  def get_items(self):
    return list(self.string_map.keys())
  def get_item_index(self, value):
    return self.string_map[value]    
     
class TypeSection(Section):
  def __init__(self, section_manager):
    self.type_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
    self.offset = 0
    self.frozen = False
  def add_item(self, dex_type):
    if self.frozen:
      raise Exception('section is frozen')

    if dex_type in self.type_map: return self.type_map[dex_type]

    self.type_map[dex_type] = self.index # set id
    self.index += 1
  def get_item(self, value):
    return list(self.type_map.keys())[value]
  def get_items(self):
    return list(self.type_map.keys())
  def get_item_index(self, value):
    return self.type_map[value]    

class ProtoSection(Section):
  def __init__(self, section_manager):
    self.proto_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
    self.frozen = False
  def add_interfaces(self, interfaces):
    self.add_item(DexProto(''.join(interfaces), None, None))
  def add_item(self, dex_proto):
    if self.frozen:
      raise Exception('section is frozen')
  
    if dex_proto in self.proto_map: return

    self.proto_map[dex_proto] = self.index # set id
    self.index += 1
  def get_item(self, value):
    return list(self.proto_map.keys())[value]
  def get_items(self):
    x = list(self.proto_map.keys())
    return x
  def get_item_index(self, value):
    return self.proto_map[value]
    
class FieldSection(Section):
  def __init__(self, section_manager):
    self.field_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
    self.frozen = False
  def add_item(self, dex_field):
    if self.frozen:
      raise Exception('section is frozen')

    if dex_field in self.field_map: 
      return
    self.field_map[dex_field] = self.index # set id
    self.index += 1
  def get_item(self, value):
    return list(self.field_map.keys())[value]
  def get_items(self):
    return list(self.field_map.keys())
  def get_item_index(self, value):
    return self.field_map[value]

class MethodSection(Section):
  def __init__(self, section_manager):
    self.method_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
    self.frozen = False
  def add_item(self, dex_method):
    if self.frozen:
      raise Exception('section is frozen')
    if dex_method in self.method_map:
      return
    self.method_map[dex_method] = self.index # set id
    self.index += 1
  def get_item(self, value):
    for object_item, idx in self.method_map.items():
      if idx == value:
        return object_item
  def get_item_index(self, value):
    return self.method_map[value]  
  def get_items(self):
    return list(self.method_map.keys())

class ClassSection(Section):
  def __init__(self, section_manager):
    self.class_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
    self.frozen = False
  def add_item(self, dex_class):
    if self.frozen:
      raise Exception('section is frozen')
    self.class_map[dex_class] = self.index # set id
    self.index += 1
  def get_item(self, value):
    return list(self.class_map.keys())[value]
  def get_items(self):
    x = list(self.class_map.keys())
    x.sort()
    return x
  def get_item_index(self, value):
    return self.class_map[value]    

class CallSiteSection(Section):
  def __init__(self, section_manager):
    self.call_site_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
    self.frozen = False

class MethodHandleSection(Section):
  def __init__(self, section_manager):
    self.method_handle_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
    self.frozen = False

class TypeListSection(Section):
  def __init__(self, section_manager):
    self.type_list_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
    self.type_index_map = dict()
    self.offset_map = dict()
    self.frozen = False
  def add_item(self, types):
    if self.frozen:
      raise Exception('section is frozen')
    if len(types) == 0: return

    types = TypeListItem(types)
    if types in self.type_index_map: return
    self.type_list_map[self.index] = types # set id
    
    self.type_index_map[types] = self.index
    self.index += 1
  def set_offset_by_item(self, item, offset):
    self.offset_map[item] = offset
  def get_offset_by_item(self, item):
    if len(item) == 0: return 0
    key = TypeListItem(item)

    return self.offset_map[key]
  def get_item(self, value):
    value = TypeListItem(value)
    return self.type_list_map[value]
  def get_items(self):
    return self.type_list_map.values()
  def get_item_index(self, value):

    if isinstance(value, list):
      value = TypeListItem(value)
    return self.type_index_map[value]   
  def get_types(self, type_list):
    #print(type_list)
    return type_list



class TypeListItem(object):
  def __init__(self, value):
    self.list = value
    self.offset = 0
    self.frozen = False
  def __hash__(self):
    return hash("".join(self.list))
  def __eq__(self,othr):
    if hash(self) == hash(othr):
      return True
    return False
  def get_types(self):
    return self.list
    
class DebugSection(Section):
  pass

class CodeSection(Section):
  def __init__(self, section_manager):
    self.code_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
    self.frozen = False
  def add_item(self, value):
    if self.frozen:
      raise Exception('section is frozen')
    self.code_map[value] = self.index # set id
    self.index += 1
  def get_item(self, value):
    return list(self.code_map.keys())[value]
  def get_items(self):
    return list(self.code_map.keys())
  def get_item_index(self, value):
    return self.code_map[value]    

class ClassDataSection(Section):
  def __init__(self, section_manager):
    self.class_data_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
    self.frozen = False
  def freeze(self):
    self.frozen = True

  def add_item(self, value):
    if self.frozen:
      raise Exception('section is frozen')
    self.class_data_map[value] = self.index # set id
    self.index += 1
  def get_item(self, value):
    return list(self.class_data_map.keys())[value]
  def get_items(self):
    x = list(self.class_data_map.keys())
    return x
  def get_item_index(self, value):
    return self.class_data_map[value]    

class MapSection(Section):
  pass

class EncodedArraySection(Section):
  def __init__(self, section_manager):
    self.encoded_array_map = OrderedDict()
    self.section_ = section_manager
    self.index = 0
    self.frozen = False
  def add_item(self, value):
    if self.frozen:
      raise Exception('section is frozen')
    self.encoded_array_map[value] = value # set id
    self.index += 1
    for value in value.value_list:
      self.section_.add_encoded_value(value)

  def hash(self, item):
    return ''.join(str(x) for x in item)

  def get_item(self, value):
    print(value)
    return self.encoded_array_map[value]

  def get_items(self):
    return list(self.encoded_array_map.values())
  
class AnnotationSection(Section):
  def __init__(self, section_manager):
    self.annotation_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
    self.frozen = False
  def add_item(self, dex_annotation):
    if self.frozen:
      raise Exception('section is frozen')
    print(dex_annotation)
    if dex_annotation in self.annotation_map: return
    self.annotation_map[dex_annotation] = self.index # set id
    self.get_section(SECTION_TYPE).add_item(dex_annotation.type)
    for elem in dex_annotation.elements:
      self.get_section(SECTION_STRING).add_item(elem[0])
      print('add elem')
      print(elem[1])
      self.add_encoded_value(elem[1])
    self.index += 1 
  def get_items(self):
    ret = [x for x in self.annotation_map]

    return ret

class AnnotationSetSection(Section):
  def __init__(self, section_manager):
    self.annotation_set_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
    self.annotation_offset_map = dict()
    self.frozen = False
  def add_item(self, value):
    if self.frozen:
      raise Exception('section is frozen')
    self.annotation_set_map[self.index] = value # set id
    self.index += 1
    for x in value:
      if x:
        if isinstance(x, list):
          for _x in x:
            self.get_section(SECTION_ANNOTATION).add_item(_x)
        else:
          self.get_section(SECTION_ANNOTATION).add_item(x)
  def get_items(self):
    return self.annotation_set_map
    #return list(self.annotation_set_map.values())
  def get_item_by_index(self, index):
    return self.annotation_set_map[index]
  def set_offset_by_index(self, index, offset):
    self.annotation_offset_map[index] = offset
  def get_index_by_item(self, item):
    return 1
  def get_offset_by_item(self, item):
    index = self.get_index_by_item(item)
    return self.annotation_offset_map[index]
