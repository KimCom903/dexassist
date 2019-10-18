

class DexWriteItem(object):
  descriptor = {}
  def __init__(self):
    pass
  def as_byte(self):
    self.as_byte_by_descriptor()
    self.as_byte_remain()

  def as_byte_by_descriptor(self):
    pass


class MUtf8(object):

class StringDataItem(DexWriteItem):
  descriptor = {
    'utf16_size': uleb128
  }

  def count_bytes(self, is_short_length):
    result = 0
    length = len(self.value)
    i = 0
    while(i < length):
      ch = self.value[i]
      if ch != 0 and ch <= 127: 
        result += 1
      elif ch <= 2047:
        result += 2
      else:
        result += 3
      
      if not is_short_length or result <= 65535:
        i += 1
    
    return result
  
  def encode(self):
    ret = bytearray(self.count_bytes( True))
    length = len(self.value)
    i = 0
    offset = 0
    offset2 = 0
    while i < length:
      ch = self.value[i]
      if ch != 0 and ch <= 127:
        offset = offset2 + 1
        ret[offset2] = ch
      elif ch <= 2047:
        offset = offset2 + 1
        ret[offset2] = ((ch >> 6) & 31) | 192
        offset2 = offset + 1
        ret[offset] = ((ch & 63) | 128)
        offset = offset2
      else:
        offset = offset2 + 1
        ret[offset2] = ((ch >> 12) & 15) | 224
        offset2 = offset + 1
        ret[offset] = ((ch >> 6) & 63 | 128)
        offset = offset2 + 1
        ret[offset2] = ((ch & 63) | 128)
      i += 1
      offset2 = offset


  def __init__(self, value):
    self.string_value = value

  def as_byte_remain(self):
    pass