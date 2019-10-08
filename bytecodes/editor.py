
class Editor(object):
  def __init__(self, code_item):
    self.tries = []
    self.opcodes = []

  def commit(self):
    pass

  def get_opcode_list(self):
    pass

  def is_in_try(self, opcode):
    pass

  def get_opcode_offset(self, opcode):
    pass

  def update_string_offset(self):
    pass

  def update_method_offset(self):
    pass

  def update_field_offset(self):
    pass
