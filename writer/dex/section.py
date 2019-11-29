
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
  def get_id(self, value):
    """
    return id of value
    """
    raise Exception('get_id not implemented')

  def add_item(self, value):
    raise Exception('add_item not implemented')

  def size(self):
    return 0



class StringSection(Section):
  def __init__(self, section_namager):
    self.string_map = {}
    self.index = 0
    self.section_manager = section_namager
  def add_item(self, value):
    # decode mutf8
    self.string_map[value] = self.index # set id
    self.index += 1
    

class TypeSection(Section):
  pass

class ProtoSection(Section):
  pass

class FieldSection(Section):
  pass

class MethodSection(Section):
  pass

class ClassSection(Section):
  pass

class CallSiteSection(Section):
  pass

class MethodHandleSection(Section):
  pass

class TypeListSection(Section):
  pass

class EncodedArraySection(Section):
  pass

class AnnotationSection(Section):
  pass

class AnnotationSetSection(Section):
  pass

class AnnotationDirectorySection(Section):
  pass

class AnnotationSetRefSection(Section):
  pass

class DebugSection(Section):
  pass

class CodeSection(Section):
  pass

class ClassDataSection(Section):
  pass

class MapSection(Section):
  pass

