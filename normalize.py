
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
  def __str__(self):
    return self.name
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
    return ret



class DexMethod(object):
  def __init__(self, parent, method_name, access_flags, signature, editor):
    self.annotations = []
    self.name = method_name
    self.clazz = parent
    self.return_type, self.params = self.parse_signature(signature)
    self.signature = signature
    self.editor = editor

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
    return ret

class DexAnnotation(object):
  def __init__(self, target, visibility, type_name, key_name_tuples):
    self.target = target
    self.visibility = visibility
    self.type_name = type_name
    self.key_name_tuples = key_name_tuples

  def __str__(self):
    return '{}({})'.format(self.type_name, self.key_name_tuples)

class DexCodeEditor(object):
  def __init__(self):
    self.bytecodes = []
  
  def set_label(self, bytecode):
    pass
