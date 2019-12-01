class BaseWriteStream(object):
  def __init__(self,buf,base_offset):
    self.position = base_offset
    self.buf = buf

  def encode(self, value):
    ret = bytearray(self.count_bytes(True))
    length = len(value)
    i = 0
    offset = 0
    offset2 = 0
    while i < length:
      ch = value[i]
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
    return ret

  def as_byte(self, fmt, value):
    return struct.pack(fmt, value)
  
  def write_ubyte(self, value):
    self.write_byte_array( as_byte(UBYTE_FMT, value))
    self.position += 1
  def write_short(self, value):
    self.write_byte_array( as_byte(SHORT_FMT, value))
    self.position += 2
  def write_ushort(self, value):
    self.write_byte_array( as_byte(USHORT_FMT, value))
    self.position += 2
  def write_int(self, value):
    self.write_byte_array( as_byte(INT_FMT, value))
    self.position += 4
  def write_uint(self, value):
    self.write_byte_array( as_byte(UINT_FMT, value))
    self.position += 4
  def write_ulong(self, value):
    self.write_byte_array( as_byte(ULONGLONG_FMT, value))
    self.position += 8
  def write_long(self, value):
    self.write_byte_array( as_byte(LONGLONG_FMT, value))
    self.position += 8
  def write_string(self, value):
    val = self.encode(value)
    self.write_byte_array( val)
    self.position += len(val)

  def write_uleb(self, value):
    ret = bytearray()
    remaining = value >> 7
    size = 0
    while remaining:
      ret.append((value & 127) | 128)
      value = remaining
    ret.append(value & 127)
    size += 1
    self.write_byte_array(ret)
    self.position += size
    return size

  def write_sleb(self, value):
    ret = bytearray()
    remaining = value >> 7
    has_more = 128
    end = 0 if 0x7fffffff & value == 0 else 1
    size = 0
    while has_more:
      has_more = 0 if remaining == end and (remaining & 1) == ((value >> 6) & 1) else 128
      ret.append(has_more | (value & 127))
      value = remaining
      remaining >>= 7
      size += 1
    self.write_byte_array(ret)
    self.position += size

  def write_ulebp1(self, value):
    self.position += self.write_uleb(value + 1)

  def write_byte_array(self, byte_arr):
    self.buf += byte_arr

  def set_output_index(self, index):
    self.index = index




class OutputStream(BaseWriteStream):
  def close(self):
    pass

  def get_position(self):
    return self.position

  def align(self):
    pass


class DeferredOutputStream(BaseWriteStream):
  def __init__(self):
    pass
  
  def write_to(self,writer):
    pass
 
  def close(self):
    pass

class ByteArrayStream(BaseWriteStream):
  def __init__(self):
    pass

  def get_position(self):
    return self.position

  def size(self):
    return 0

  def reset(self):
    pass

class BufferStream(BaseWriteStream):
  def __init__(self, buffer):
    self.buf = buffer
    self.position = 0

class DataWriter(object):
  def write_uleb(self, buf, value):
    buf.write_uleb(value)

  def write_sleb(self, buf, value):
    buf.write_sleb(value)

class InstructionWriter(BaseWriteStream):
  def make_ins_writer(self, instructions, code_writer, string_section, type_section, field_section, method_section, proto_section, method_handle_section, call_site_section):
    pass


