
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

  def add_annotation(self, annotation):
    self.annotations.append(annotation)
class DexField(object):
  def __init__(self, parent, type_name, access_flags):
    self.annotations = []
    self.type = type_name
    self.clazz = parent
    self.access_flags = access_flags



def create_dex_method(self, parent, method_name, access_flags, signature, code):
  pass

class DexMethod(object):
  def __init__(self):
    self.annotations = []
    self.type = ''
    self.return_type = ''
    self.codes = None

class DexAnnotation(object):
  def __init__(self, target, visibility, type_name, key_name_tuples):
    pass


class DexCodeItem(object):
  def __init__(self):
    self.editor = None


class DexCodeEditor(object):
  def __init__(self):
    self.bytecodes = []
  
  def set_label(self, bytecode):
    pass

