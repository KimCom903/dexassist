from collections import OrderedDict
from dexassist.normalize import DexProto, DexValue, VALUE_TYPE_ARRAY
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
    self.tmp_list = set()
    self.index = 0
    self.section_ = section_
    self.frozen = False
    self.string_reverse_map = {}
  def add_item(self, value):
    # decode mutf8
    if self.frozen:
      raise Exception('section is frozen')
    #if value in self.string_map: return self.string_map[value]
    self.tmp_list.add(value)

    #self.string_map[value] = self.index # set id
    #self.index += 1
  def get_item(self, value):
    return self.string_reverse_map[value]
  def get_items(self):
    return list(self.string_map.keys())
  def get_item_index(self, value):
    return self.string_map[value]    
  def freeze(self):
    x = list(self.tmp_list)

    x.sort()
    for item in x:
      self.string_map[item] = self.index
      self.string_reverse_map[self.index] = item
      self.index += 1
    
    self.frozen = True
class TypeSection(Section):
  def __init__(self, section_manager):
    self.type_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
    self.offset = 0
    self.frozen = False
    self.type_reverse_map = {}
  def add_item(self, dex_type):
    if self.frozen:
      raise Exception('section is frozen')

    if dex_type in self.type_map:
      return

    self.type_map[dex_type] = self.index # set id
    self.type_reverse_map[self.index] = dex_type
    self.index += 1
  def get_item(self, value):
    return self.type_reverse_map[value]

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
    self.reverse_proto_map = {}
  def add_interfaces(self, interfaces):
    self.add_item(DexProto(''.join(interfaces), None, None))
  def add_item(self, dex_proto):
    if self.frozen:
      raise Exception('section is frozen')
  
    if dex_proto in self.proto_map: return
    self.reverse_proto_map[self.index] = dex_proto

    self.proto_map[dex_proto] = self.index # set id
    self.index += 1
    
  def get_item(self, value):
    return self.reverse_proto_map[value]

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
    self.reverse_field_map = {}
  def add_item(self, dex_field):
    if self.frozen:
      raise Exception('section is frozen')

    if dex_field in self.field_map: 
      return
    self.field_map[dex_field] = self.index # set id
    self.reverse_field_map[self.index] = dex_field
    try:
      clazz_type = dex_field.clazz.type
    except:
      clazz_type = dex_field.clazz
    self.section_.type_section.add_item(clazz_type)
    self.section_.type_section.add_item(dex_field.type)
    self.section_.string_section.add_item(dex_field.name)
    self.index += 1
  def get_item(self, value):
    return self.reverse_field_map[value]
  def get_items(self):
    return list(self.field_map.keys())
  def get_item_index(self, value):
    return self.field_map[value]

class MethodSection(Section):
  def __init__(self, section_manager):
    self.method_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
    self.reverse_method_map = {}
    self.frozen = False
  def add_item(self, dex_method):
    if self.frozen:
      raise Exception('section is frozen')
    if dex_method in self.method_map:
      return
    self.method_map[dex_method] = self.index # set id
    self.reverse_method_map[self.index] = dex_method

    self.section_.string_section.add_item(dex_method.name)
    self.index += 1
  def get_item(self, value):
    return self.reverse_method_map[value]

  def get_item_index(self, value):
    try:
      return self.method_map[value]  
    except:
      raise Exception('method {} not found'.format(value))
  def get_items(self):
    return list(self.method_map.keys())

class ClassSection(Section):
  def __init__(self, section_manager):
    self.class_map = OrderedDict()
    self.reverse_class_map = {}
    self.index = 0
    self.section_ = section_manager
    self.frozen = False
  def add_item(self, dex_class):
    if self.frozen:
      raise Exception('section is frozen')
    self.class_map[dex_class] = self.index # set id
    self.reverse_class_map[self.index] = dex_class
    self.index += 1
  def get_item(self, value):
    return self.reverse_class_map[value]

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
    self.reverse_code_map = {}
    self.index = 0
    self.section_ = section_manager
    self.frozen = False
  def add_item(self, value):
    if self.frozen:
      raise Exception('section is frozen')
    self.code_map[value] = self.index # set id
    self.reverse_code_map[self.index] = value
    self.index += 1
  def get_item(self, value):
    return self.reverse_code_map[value]

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
    self.reverse_class_map = {}
  def freeze(self):
    self.frozen = True

  def add_item(self, value):
    if self.frozen:
      raise Exception('section is frozen')
    self.class_data_map[value] = self.index # set id
    self.reverse_class_map[self.index] = value
    self.index += 1
  def get_item(self, value):
    return self.reverse_class_map[value]

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
    self.offset_map = dict()
    self.section_ = section_manager
    self.index = 0
    self.frozen = False
  def add_item(self, value):
    if self.frozen:
      raise Exception('section is frozen')
    key = self.hash(value)
    if key in self.encoded_array_map: return
    self.encoded_array_map[key] = value # set id
    self.index += 1
    for v in value:
      if isinstance(v, list):
        self.add_item(v)
        continue
      if isinstance(v, DexValue) and v.get_type() == VALUE_TYPE_ARRAY:
        self.add_item(v)
        continue

      self.section_.add_encoded_value(v)

  def hash(self, item):
    return '|'.join(str(x) for x in item)

  def get_item(self, value):
    return self.encoded_array_map[self.hash(value)]

  def get_items(self):
    return list(self.encoded_array_map.values())
  
  def set_offset_by_item(self, item, offset):
    key = self.hash(item)
    self.offset_map[key] = offset

  def get_offset_by_item(self, item):
    key = self.hash(item)
    return self.offset_map[key]
class AnnotationSection(Section):
  def __init__(self, section_manager):
    self.annotation_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
    self.frozen = False
  def add_item(self, dex_annotation):
    if self.frozen:
      raise Exception('section is frozen')
    if dex_annotation in self.annotation_map: return
    self.annotation_map[dex_annotation] = self.index # set id
    self.get_section(SECTION_TYPE).add_item(dex_annotation.type)
    for elem in dex_annotation.elements:
      self.get_section(SECTION_STRING).add_item(elem[0])
      x = elem[1]
      self.add_encoded_value(x)
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
    self.reverse_annotation_set_map = dict()
    self.frozen = False
  def add_item(self, value):
    if self.frozen:
      raise Exception('section is frozen')
    if value is None: return


    key = self.hash(value)
    #print('add annotation set {}'.format(key))
    if key in self.annotation_set_map: return
    self.annotation_set_map[key] = self.index # set id
    self.reverse_annotation_set_map[self.index] = value
    self.index += 1

    for x in value:
      if x:
        if isinstance(x, list):
          for _x in x:
            self.get_section(SECTION_ANNOTATION).add_item(_x)
        else:
          self.get_section(SECTION_ANNOTATION).add_item(x)

  def get_dex_value_hash(self, val):
    ret = ''
    if isinstance(val, list):
      for i in val:
        ret += self.get_dex_value_hash(i)
      return ret
    else:
      return str(val.get_type())

  def hash(self, item):
    key = ''
    if item is None: return 'None'
    if isinstance(item, list):
      for x in item:
        key += self.hash(x)   
      return key
    key += item.type_name
    for elem in item.elements:
      key += elem[0] + ',' + self.get_dex_value_hash(elem[1])
    return key
    


  def get_items(self):
    return self.reverse_annotation_set_map
    #return list(self.annotation_set_map.values())
  def get_item_by_index(self, index):
    return self.reverse_annotation_set_map[index]
  def set_offset_by_index(self, index, offset):
    self.annotation_offset_map[index] = offset
  def get_index_by_item(self, item):
    key = self.hash(item)
    return self.annotation_set_map[key]

  def get_offset_by_item(self, item):
    index = self.get_index_by_item(item)
    return self.annotation_offset_map[index]

  def set_offset_by_item(self, item, offset):
    index = self.get_index_by_item(item)
    self.annotation_offset_map[index] = item
