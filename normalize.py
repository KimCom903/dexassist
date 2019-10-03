
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

class DexFieldItem(object):
  def __init__(self):
    self.annotations = []
    self.type = ''
    self.value = ''


class DexMethodItem(object):
  def __init__(self):
    self.annotations = []
    self.type = ''
    self.return_type = ''
    self.codes = None


class DexCodeItem(object):
  def __init__(self):
    self.editor = None


class DexCodeEditor(object):
  def __init__(self):
    self.bytecodes = []
  
  def set_label(self, bytecode):
    pass

