from zlib import adler32
import struct
import inspect

UINT_FMT = '<I'
USHORT_FMT = '<H'
INT_FMT = '<i'
SHORT_FMT = '<h'
LONG_FMT = '<l'
ULONG_FMT = '<L'
LONGLONG_FMT = '<q'
ULONGLONG_FMT = '<Q'
UBYTE_FMT = '<B'
BYTE_FMT = '<b'

def calc_adler32(data, length):
  a = 1
  b = 0
  for i in range(length):
    a = (a + ord(data[i])) % MOD_ADLER
    b = (b + a) % MOD_ADLER
  return (b << 16) | a


class BaseWriteStream(object):
  def __init__(self,buf,base_offset):
    self.position = base_offset
    self.buf = buf

  def count_bytes(self, value, is_short_length):
    result = 0
    length = len(value)
    i = 0
    while(i < length):
      ch = ord(value[i])
      if ch != 0 and ch <= 127: 
        result += 1
      elif ch <= 2047:
        result += 2
      else:
        result += 3
      
      if not is_short_length or result <= 65535:
        i += 1
    
    return result

  def encode(self, value):
    value = list(value)
    ret = bytearray(self.count_bytes(value, True))
    length = len(value)
    i = 0
    offset = 0
    offset2 = 0
    while i < length:
      ch = ord(value[i])
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
    self.write_byte_array( self.as_byte(UBYTE_FMT, value))
    self.position += 1
  def write_short(self, value):
    self.write_byte_array( self.as_byte(SHORT_FMT, value))
    self.position += 2
  def write_ushort(self, value):
    self.write_byte_array( self.as_byte(USHORT_FMT, value))
    self.position += 2
  def write_int(self, value):
    self.write_byte_array( self.as_byte(INT_FMT, value))
    self.position += 4
  def write_uint(self, value):
    self.write_byte_array( self.as_byte(UINT_FMT, value))
    self.position += 4
  def write_ulong(self, value):
    self.write_byte_array( self.as_byte(ULONGLONG_FMT, value))
    self.position += 8
  def write_long(self, value):
    self.write_byte_array( self.as_byte(LONGLONG_FMT, value))
    self.position += 8
  def write_string(self, value):
    val = self.encode(value)
    self.write_byte_array(val)
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
  def __init__(self,buf,base_offset):
    self.position = base_offset
    self.buf = buf
  
  def close(self):
    f = open("Classes.dex", 'ab')
    f.write(self.buf)
    f.close()

  def get_position(self):
    return self.position

  def align(self):
    zeros = (-self.get_position()) & 3
    if zeros > 0:
      self.write_ubyte(0)


class TempOutputStream(BaseWriteStream):
  def __init__(self):
    self.buf = bytearray()
    self.position = 0
  
  def write_to(self, stream):
    stream.buf += self.buf
    stream.position += self.position
 
  def get_position(self):
    return self.position

  def close(self):
    pass

  def reset(self):
    pass

  def align(self):
    zeros = (-self.get_position()) & 3
    if zeros > 0:
      self.write_ubyte(0)    


class BufferStream(BaseWriteStream):
  def __init__(self, buffer):
    self.buf = buffer
    self.position = 0


class InstructionWriter(BaseWriteStream):
  @staticmethod
  def __init__(code_writer, section_manager):
    self.stream = code_writer
    self.manager = section_manager

  def write(ins):
    ins.write_byte_stream(self.stream, self.manager)


