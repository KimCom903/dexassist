from collections import OrderedDict

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
SECTION_ANNOTATION_DIRECTORY = 13
SECTION_ANNOTATION_SET_REF = 14
SECTION_DEBUG = 15
SECTION_CODE = 16
SECTION_CLASS_DATA = 17
SECTION_MAP = 18


"""
NOTT writable!
just provide classes
"""
class Section(object):
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
  
  def size(self):
    return self.get_item_count()

class StringSection(Section):
  def __init__(self, section_):
    self.string_map = OrderedDict()
    self.index = 0
    self.section_ = section_
  def add_item(self, value):
    # decode mutf8
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
  def add_item(self, dex_type):
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
  def add_item(self, dex_proto):
    self.proto_map[dex_proto] = self.index # set id
    self.index += 1
  def get_item(self, value):
    return list(self.proto_map.keys())[value]
  def get_items(self):
    return list(self.proto_map.keys())
  def get_item_index(self, value):
    return self.proto_map[value]

class FieldSection(Section):
  def __init__(self, section_manager):
    self.field_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
  def add_item(self, dex_field):
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
  def add_item(self, dex_method):
    self.method_map[dex_method] = self.index # set id
    self.index += 1
  def get_item(self, value):
    for object_item, idx in self.method_map.items():
      if idx == value:
        return object_item
  def get_item_index(self, value):
    return self.method_map[value]  

class ClassSection(Section):
  def __init__(self, section_manager):
    self.class_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
  def add_item(self, dex_class):
    self.class_map[dex_class] = self.index # set id
    self.index += 1
  def get_item(self, value):
    return list(self.class_map.keys())[value]
  def get_items(self):
    return list(self.class_map.keys())
  def get_item_index(self, value):
    return self.class_map[value]    

class CallSiteSection(Section):
  pass

class MethodHandleSection(Section):
  pass

class TypeListSection(Section):
  def __init__(self, section_manager):
    self.type_list_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
  def add_item(self, types):
    self.type_list_map[types] = self.index # set id
    self.index += 1
  def get_item(self, value):
    return list(self.type_list_map.keys())[value]
  def get_items(self):
    return list(self.type_list_map.keys())
  def get_item_index(self, value):
    return self.type_list_map[value]    
    
class DebugSection(Section):
  pass

class CodeSection(Section):
  def __init__(self, section_manager):
    self.code_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
  def add_item(self, value):
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
  def add_item(self, value):
    self.class_data_map[value] = self.index # set id
    self.index += 1
  def get_item(self, value):
    return list(self.class_data_map.keys())[value]
  def get_items(self):
    return list(self.class_data_map.keys())
  def get_item_index(self, value):
    return self.class_data_map[value]    

class MapSection(Section):
  pass

class EncodedArraySection(Section):
  def __init__(self, section_manager):
    self.encoded_array_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
  def add_item(self, value):
    self.encoded_array_map[value] = self.index # set id
    self.index += 1

class AnnotationSection(Section):
  def __init__(self, section_manager):
    self.annotation_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
  def add_item(self, dex_annotation):
    self.annotation_map[dex_annotation] = self.index # set id
    self.index += 1 

class AnnotationSetSection(Section):
  def __init__(self, section_manager):
    self.annotation_set_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
  def add_item(self, value):
    self.annotation_set_map[value] = self.index # set id
    self.index += 1

class AnnotationDirectorySection(Section):
  def __init__(self, section_manager):
    self.annotation_dir_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
  def add_item(self, value):
    self.annotation_dir_map[value] = self.index # set id
    self.index += 1

class AnnotationSetRefSection(Section):
  def __init__(self, section_manager):
    self.annotation_set_ref_map = OrderedDict()
    self.index = 0
    self.section_ = section_manager
  def add_item(self, value):
    self.annotation_set_ref_map[value] = self.index # set id
    self.index += 1
