from zlib import adler32
import struct
import inspect


BYTE = 1
UBYTE = 2
SHORT = 3
USHORT = 4
INT = 5
UINT = 6
LONG = 7
ULONG = 8
SLEB = 9
ULEB = 10
ULEBP1 = 11
STRING = 12

MAGIC = 13
SIGNATURE = 14

MOD_ADLER = 65521

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

class BaseStream(object):
  def __init__(self):
    self.buf = bytearray()
  def write(self, arr):
    self.buf += arr

class DexWriteStream(object):

  def count_bytes(self, value, is_short_length):
    result = 0
    length = len(value)
    i = 0
    while(i < length):
      ch = value[i]
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
    return 1
  def write_short(self, value):
    self.write_byte_array( as_byte(SHORT_FMT, value))
    return 2
  def write_ushort(self, value):
    self.write_byte_array( as_byte(USHORT_FMT, value))
    return 2
  def write_int(self, value):
    self.write_byte_array( as_byte(INT_FMT, value))
    return 4
  def write_uint(self, value):
    self.write_byte_array( as_byte(UINT_FMT, value))
    return 4
  def write_ulong(self, value):
    self.write_byte_array( as_byte(ULONGLONG_FMT, value))
    return 8
  def write_long(self, value):
    self.write_byte_array( as_byte(LONGLONG_FMT, value))
    return 8
  def write_string(self, value):
    val = self.encode(value)
    self.write_byte_array( val)
    return len(val)

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
    return size
  def write_ulebp1(self, value):
    return self.write_uleb(value + 1)

  def __init__(self):

    self.write_map = {
      BYTE: self.write_ubyte,
      UBYTE: self.write_ubyte,

      SHORT: self.write_short,
      USHORT: self.write_ushort,

      INT: self.write_int,
      UINT: self.write_uint,

      LONG: self.write_long,
      ULONG: self.write_ulong,

      SLEB: self.write_sleb,

      ULEB: self.write_uleb,
      ULEBP1: self.write_ulebp1,
      STRING: self.write_string,

      MAGIC: self.write_magic,
      SIGNATURE: self.write_signature

    }
  def write_object(self, offset, item):
    """
    return item.size
    """
    self.base_stream.tell(offset)
    return item.write(self.base_stream, offset)
  def write_object(self, item):
    return item.write(self.base_stream, offset)
  def write_byte_array(self, byte_arr):
    self.base_stream.write(byte_arr)

  def get_current_offset(self):
    return self.offset
  def __init__(self, base_stream):
    self.offset = 0
    self.base_stream = base_stream
  
  def set_offset(self, offset):
    self.offset = offset

class DexWriteItem(object):
  descriptor = {}
  def __init__(self):
    pass

  def as_byte(self, stream):
    ret = self.write_byte_descriptor(stream)
    ret += self.write_byte_remain(stream)
    return ret

  def write_byte_remain(self, stream):
    return 0

  def write_byte_descriptor(self, stream):
    ret = 0
    for x in self.descriptor:
      ret += stream.write_map[self.descriptor[x]](getattr(self, x))
    return ret

  def write(self, stream):
    ret = self.write_byte_descriptor(stream)
    ret += self.write_byte_remain(stream)
    return ret






class StringDataItem(DexWriteItem):
  descriptor = {
    'utf16_size': ULEB
  }


  def __init__(self, value):
    self.string_value = value

  def write_byte_remain(self, stream):
    pass