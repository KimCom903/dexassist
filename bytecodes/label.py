
class Label(object):
  def __init__(self, editor, target_opcode):
    self.target = target_opcode
    self.editor = editor

  def get_offset(self):
      return self.editor.get_offset(self.target)
