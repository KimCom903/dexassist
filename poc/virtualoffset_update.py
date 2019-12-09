import inspect

class DexItem(object):
  pass

class VirtualOffset(object):
  VIRTUAL_TABLE = []
  def __init__(self, item):
    self.base_item = item
    item.virtual_offset = self


  def update_offset(self, offset_value):
    buf[offset]= offset_value


"""
usage


code_off = VirtualOffset(x)

...


x.save()
 -> update code_off




"""

