
class DexFileWriteStream(object):
  def __init__(self):
    self.index = 1

  def set_output_index(self, index):
    self.index = index