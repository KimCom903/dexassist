

## define

INSTRUCT_TYPE_STRING = 0
INSTRUCT_TYPE_TYPE = 1
INSTRUCT_TYPE_METHOD = 2
INSTRUCT_TYPE_FIELD = 3
INSTRUCT_TYPE_OFFSET = 4
INSTRUCT_TYPE_KIND = 5

# for odex
INSTRUCT_TYPE_VTABLE_OFFSET = 6
INSTRUCT_TYPE_FIELD_OFFSET = 7

OPCODE_TABLE = {
    0x00: [Instruction10x, "nop"],
    0x01: [Instruction12x, "move"],
    0x02: [Instruction22x, "move/from16"],
    0x03: [Instruction32x, "move/16"],
    0x04: [Instruction12x, "move-wide"],
    0x05: [Instruction22x, "move-wide/from16"],
    0x06: [Instruction32x, "move-wide/16"],
    0x07: [Instruction12x, "move-object"],
    0x08: [Instruction22x, "move-object/from16"],
    0x09: [Instruction32x, "move-object/16"],
    0x0a: [Instruction11x, "move-result"],
    0x0b: [Instruction11x, "move-result-wide"],
    0x0c: [Instruction11x, "move-result-object"],
    0x0d: [Instruction11x, "move-exception"],
    0x0e: [Instruction10x, "return-void"],
    0x0f: [Instruction11x, "return"],
    0x10: [Instruction11x, "return-wide"],
    0x11: [Instruction11x, "return-object"],
    0x12: [Instruction11n, "const/4"],
    0x13: [Instruction21s, "const/16"],
    0x14: [Instruction31i, "const"],
    0x15: [Instruction21h, "const/high16"],
    0x16: [Instruction21s, "const-wide/16"],
    0x17: [Instruction31i, "const-wide/32"],
    0x18: [Instruction51l, "const-wide"],
    0x19: [Instruction21h, "const-wide/high16"],
    0x1a: [Instruction21c, "const-string", INSTRUCT_TYPE_STRING],
    0x1b: [Instruction31c, "const-string/jumbo", INSTRUCT_TYPE_STRING],
    0x1c: [Instruction21c, "const-class", INSTRUCT_TYPE_TYPE],
    0x1d: [Instruction11x, "monitor-enter"],
    0x1e: [Instruction11x, "monitor-exit"],
    0x1f: [Instruction21c, "check-cast", INSTRUCT_TYPE_TYPE],
    0x20: [Instruction22c, "instance-of", INSTRUCT_TYPE_TYPE],
    0x21: [Instruction12x, "array-length"],
    0x22: [Instruction21c, "new-instance", INSTRUCT_TYPE_TYPE],
    0x23: [Instruction22c, "new-array", INSTRUCT_TYPE_TYPE],
    0x24: [Instruction35c, "filled-new-array", INSTRUCT_TYPE_TYPE],
    0x25: [Instruction3rc, "filled-new-array/range", INSTRUCT_TYPE_TYPE],
    0x26: [Instruction31t, "fill-array-data"],
    0x27: [Instruction11x, "throw"],
    0x28: [Instruction10t, "goto"],
    0x29: [Instruction20t, "goto/16"],
    0x2a: [Instruction30t, "goto/32"],
    0x2b: [Instruction31t, "packed-switch"],
    0x2c: [Instruction31t, "sparse-switch"],
    0x2d: [Instruction23x, "cmpl-float"],
    0x2e: [Instruction23x, "cmpg-float"],
    0x2f: [Instruction23x, "cmpl-double"],
    0x30: [Instruction23x, "cmpg-double"],
    0x31: [Instruction23x, "cmp-long"],
    0x32: [Instruction22t, "if-eq"],
    0x33: [Instruction22t, "if-ne"],
    0x34: [Instruction22t, "if-lt"],
    0x35: [Instruction22t, "if-ge"],
    0x36: [Instruction22t, "if-gt"],
    0x37: [Instruction22t, "if-le"],
    0x38: [Instruction21t, "if-eqz"],
    0x39: [Instruction21t, "if-nez"],
    0x3a: [Instruction21t, "if-ltz"],
    0x3b: [Instruction21t, "if-gez"],
    0x3c: [Instruction21t, "if-gtz"],
    0x3d: [Instruction21t, "if-lez"],
    # unused
    0x3e: [Instruction10x, "nop"],
    0x3f: [Instruction10x, "nop"],
    0x40: [Instruction10x, "nop"],
    0x41: [Instruction10x, "nop"],
    0x42: [Instruction10x, "nop"],
    0x43: [Instruction10x, "nop"],
    0x44: [Instruction23x, "aget"],
    0x45: [Instruction23x, "aget-wide"],
    0x46: [Instruction23x, "aget-object"],
    0x47: [Instruction23x, "aget-boolean"],
    0x48: [Instruction23x, "aget-byte"],
    0x49: [Instruction23x, "aget-char"],
    0x4a: [Instruction23x, "aget-short"],
    0x4b: [Instruction23x, "aput"],
    0x4c: [Instruction23x, "aput-wide"],
    0x4d: [Instruction23x, "aput-object"],
    0x4e: [Instruction23x, "aput-boolean"],
    0x4f: [Instruction23x, "aput-byte"],
    0x50: [Instruction23x, "aput-char"],
    0x51: [Instruction23x, "aput-short"],
    0x52: [Instruction22c, "iget", INSTRUCT_TYPE_FIELD],
    0x53: [Instruction22c, "iget-wide", INSTRUCT_TYPE_FIELD],
    0x54: [Instruction22c, "iget-object", INSTRUCT_TYPE_FIELD],
    0x55: [Instruction22c, "iget-boolean", INSTRUCT_TYPE_FIELD],
    0x56: [Instruction22c, "iget-byte", INSTRUCT_TYPE_FIELD],
    0x57: [Instruction22c, "iget-char", INSTRUCT_TYPE_FIELD],
    0x58: [Instruction22c, "iget-short", INSTRUCT_TYPE_FIELD],
    0x59: [Instruction22c, "iput", INSTRUCT_TYPE_FIELD],
    0x5a: [Instruction22c, "iput-wide", INSTRUCT_TYPE_FIELD],
    0x5b: [Instruction22c, "iput-object", INSTRUCT_TYPE_FIELD],
    0x5c: [Instruction22c, "iput-boolean", INSTRUCT_TYPE_FIELD],
    0x5d: [Instruction22c, "iput-byte", INSTRUCT_TYPE_FIELD],
    0x5e: [Instruction22c, "iput-char", INSTRUCT_TYPE_FIELD],
    0x5f: [Instruction22c, "iput-short", INSTRUCT_TYPE_FIELD],
    0x60: [Instruction21c, "sget", INSTRUCT_TYPE_FIELD],
    0x61: [Instruction21c, "sget-wide", INSTRUCT_TYPE_FIELD],
    0x62: [Instruction21c, "sget-object", INSTRUCT_TYPE_FIELD],
    0x63: [Instruction21c, "sget-boolean", INSTRUCT_TYPE_FIELD],
    0x64: [Instruction21c, "sget-byte", INSTRUCT_TYPE_FIELD],
    0x65: [Instruction21c, "sget-char", INSTRUCT_TYPE_FIELD],
    0x66: [Instruction21c, "sget-short", INSTRUCT_TYPE_FIELD],
    0x67: [Instruction21c, "sput", INSTRUCT_TYPE_FIELD],
    0x68: [Instruction21c, "sput-wide", INSTRUCT_TYPE_FIELD],
    0x69: [Instruction21c, "sput-object", INSTRUCT_TYPE_FIELD],
    0x6a: [Instruction21c, "sput-boolean", INSTRUCT_TYPE_FIELD],
    0x6b: [Instruction21c, "sput-byte", INSTRUCT_TYPE_FIELD],
    0x6c: [Instruction21c, "sput-char", INSTRUCT_TYPE_FIELD],
    0x6d: [Instruction21c, "sput-short", INSTRUCT_TYPE_FIELD],
    0x6e: [Instruction35c, "invoke-virtual", INSTRUCT_TYPE_METHOD],
    0x6f: [Instruction35c, "invoke-super", INSTRUCT_TYPE_METHOD],
    0x70: [Instruction35c, "invoke-direct", INSTRUCT_TYPE_METHOD],
    0x71: [Instruction35c, "invoke-static", INSTRUCT_TYPE_METHOD],
    0x72: [Instruction35c, "invoke-interface", INSTRUCT_TYPE_METHOD],
    # unused
    0x73: [Instruction10x, "nop"],
    0x74: [Instruction3rc, "invoke-virtual/range", INSTRUCT_TYPE_METHOD],
    0x75: [Instruction3rc, "invoke-super/range", INSTRUCT_TYPE_METHOD],
    0x76: [Instruction3rc, "invoke-direct/range", INSTRUCT_TYPE_METHOD],
    0x77: [Instruction3rc, "invoke-static/range", INSTRUCT_TYPE_METHOD],
    0x78: [Instruction3rc, "invoke-interface/range", INSTRUCT_TYPE_METHOD],
    # unused
    0x79: [Instruction10x, "nop"],
    0x7a: [Instruction10x, "nop"],
    0x7b: [Instruction12x, "neg-int"],
    0x7c: [Instruction12x, "not-int"],
    0x7d: [Instruction12x, "neg-long"],
    0x7e: [Instruction12x, "not-long"],
    0x7f: [Instruction12x, "neg-float"],
    0x80: [Instruction12x, "neg-double"],
    0x81: [Instruction12x, "int-to-long"],
    0x82: [Instruction12x, "int-to-float"],
    0x83: [Instruction12x, "int-to-double"],
    0x84: [Instruction12x, "long-to-int"],
    0x85: [Instruction12x, "long-to-float"],
    0x86: [Instruction12x, "long-to-double"],
    0x87: [Instruction12x, "float-to-int"],
    0x88: [Instruction12x, "float-to-long"],
    0x89: [Instruction12x, "float-to-double"],
    0x8a: [Instruction12x, "double-to-int"],
    0x8b: [Instruction12x, "double-to-long"],
    0x8c: [Instruction12x, "double-to-float"],
    0x8d: [Instruction12x, "int-to-byte"],
    0x8e: [Instruction12x, "int-to-char"],
    0x8f: [Instruction12x, "int-to-short"],
    0x90: [Instruction23x, "add-int"],
    0x91: [Instruction23x, "sub-int"],
    0x92: [Instruction23x, "mul-int"],
    0x93: [Instruction23x, "div-int"],
    0x94: [Instruction23x, "rem-int"],
    0x95: [Instruction23x, "and-int"],
    0x96: [Instruction23x, "or-int"],
    0x97: [Instruction23x, "xor-int"],
    0x98: [Instruction23x, "shl-int"],
    0x99: [Instruction23x, "shr-int"],
    0x9a: [Instruction23x, "ushr-int"],
    0x9b: [Instruction23x, "add-long"],
    0x9c: [Instruction23x, "sub-long"],
    0x9d: [Instruction23x, "mul-long"],
    0x9e: [Instruction23x, "div-long"],
    0x9f: [Instruction23x, "rem-long"],
    0xa0: [Instruction23x, "and-long"],
    0xa1: [Instruction23x, "or-long"],
    0xa2: [Instruction23x, "xor-long"],
    0xa3: [Instruction23x, "shl-long"],
    0xa4: [Instruction23x, "shr-long"],
    0xa5: [Instruction23x, "ushr-long"],
    0xa6: [Instruction23x, "add-float"],
    0xa7: [Instruction23x, "sub-float"],
    0xa8: [Instruction23x, "mul-float"],
    0xa9: [Instruction23x, "div-float"],
    0xaa: [Instruction23x, "rem-float"],
    0xab: [Instruction23x, "add-double"],
    0xac: [Instruction23x, "sub-double"],
    0xad: [Instruction23x, "mul-double"],
    0xae: [Instruction23x, "div-double"],
    0xaf: [Instruction23x, "rem-double"],
    0xb0: [Instruction12x, "add-int/2addr"],
    0xb1: [Instruction12x, "sub-int/2addr"],
    0xb2: [Instruction12x, "mul-int/2addr"],
    0xb3: [Instruction12x, "div-int/2addr"],
    0xb4: [Instruction12x, "rem-int/2addr"],
    0xb5: [Instruction12x, "and-int/2addr"],
    0xb6: [Instruction12x, "or-int/2addr"],
    0xb7: [Instruction12x, "xor-int/2addr"],
    0xb8: [Instruction12x, "shl-int/2addr"],
    0xb9: [Instruction12x, "shr-int/2addr"],
    0xba: [Instruction12x, "ushr-int/2addr"],
    0xbb: [Instruction12x, "add-long/2addr"],
    0xbc: [Instruction12x, "sub-long/2addr"],
    0xbd: [Instruction12x, "mul-long/2addr"],
    0xbe: [Instruction12x, "div-long/2addr"],
    0xbf: [Instruction12x, "rem-long/2addr"],
    0xc0: [Instruction12x, "and-long/2addr"],
    0xc1: [Instruction12x, "or-long/2addr"],
    0xc2: [Instruction12x, "xor-long/2addr"],
    0xc3: [Instruction12x, "shl-long/2addr"],
    0xc4: [Instruction12x, "shr-long/2addr"],
    0xc5: [Instruction12x, "ushr-long/2addr"],
    0xc6: [Instruction12x, "add-float/2addr"],
    0xc7: [Instruction12x, "sub-float/2addr"],
    0xc8: [Instruction12x, "mul-float/2addr"],
    0xc9: [Instruction12x, "div-float/2addr"],
    0xca: [Instruction12x, "rem-float/2addr"],
    0xcb: [Instruction12x, "add-double/2addr"],
    0xcc: [Instruction12x, "sub-double/2addr"],
    0xcd: [Instruction12x, "mul-double/2addr"],
    0xce: [Instruction12x, "div-double/2addr"],
    0xcf: [Instruction12x, "rem-double/2addr"],
    0xd0: [Instruction22s, "add-int/lit16"],
    0xd1: [Instruction22s, "rsub-int"],
    0xd2: [Instruction22s, "mul-int/lit16"],
    0xd3: [Instruction22s, "div-int/lit16"],
    0xd4: [Instruction22s, "rem-int/lit16"],
    0xd5: [Instruction22s, "and-int/lit16"],
    0xd6: [Instruction22s, "or-int/lit16"],
    0xd7: [Instruction22s, "xor-int/lit16"],
    0xd8: [Instruction22b, "add-int/lit8"],
    0xd9: [Instruction22b, "rsub-int/lit8"],
    0xda: [Instruction22b, "mul-int/lit8"],
    0xdb: [Instruction22b, "div-int/lit8"],
    0xdc: [Instruction22b, "rem-int/lit8"],
    0xdd: [Instruction22b, "and-int/lit8"],
    0xde: [Instruction22b, "or-int/lit8"],
    0xdf: [Instruction22b, "xor-int/lit8"],
    0xe0: [Instruction22b, "shl-int/lit8"],
    0xe1: [Instruction22b, "shr-int/lit8"],
    0xe2: [Instruction22b, "ushr-int/lit8"],


    # expanded opcodes, for odex
    0xe3: [Instruction22c, "iget-volatile", INSTRUCT_TYPE_FIELD],
    0xe4: [Instruction22c, "iput-volatile", INSTRUCT_TYPE_FIELD],
    0xe5: [Instruction21c, "sget-volatile", INSTRUCT_TYPE_FIELD],
    0xe6: [Instruction21c, "sput-volatile", INSTRUCT_TYPE_FIELD],
    0xe7: [Instruction22c, "iget-object-volatile", INSTRUCT_TYPE_FIELD],
    0xe8: [Instruction22c, "iget-wide-volatile", INSTRUCT_TYPE_FIELD],
    0xe9: [Instruction22c, "iput-wide-volatile", INSTRUCT_TYPE_FIELD],
    0xea: [Instruction21c, "sget-wide-volatile", INSTRUCT_TYPE_FIELD],
    0xeb: [Instruction21c, "sput-wide-volatile", INSTRUCT_TYPE_FIELD],
    0xec: [Instruction10x, "breakpoint"],
    0xed: [Instruction20bc, "throw-verification-error", INSTRUCT_TYPE_KIND],
    0xee: [Instruction35mi, "execute-inline", INLINE_METHOD],
    0xef: [Instruction3rmi, "execute-inline/range", INLINE_METHOD],
    0xf0: [Instruction35c, "invoke-object-init/range", INSTRUCT_TYPE_METHOD],
    0xf1: [Instruction10x, "return-void-barrier"],
    0xf2: [Instruction22cs, "iget-quick", INSTRUCT_TYPE_FIELD_OFFSET],
    0xf3: [Instruction22cs, "iget-wide-quick", INSTRUCT_TYPE_FIELD_OFFSET],
    0xf4: [Instruction22cs, "iget-object-quick", INSTRUCT_TYPE_FIELD_OFFSET],
    0xf5: [Instruction22cs, "iput-quick", INSTRUCT_TYPE_FIELD_OFFSET],
    0xf6: [Instruction22cs, "iput-wide-quick", INSTRUCT_TYPE_FIELD_OFFSET],
    0xf7: [Instruction22cs, "iput-object-quick", INSTRUCT_TYPE_FIELD_OFFSET],
    0xf8: [Instruction35ms, "invoke-virtual-quick", INSTRUCT_TYPE_VTABLE_OFFSET],
    0xf9: [Instruction3rms, "invoke-virtual-quick/range", INSTRUCT_TYPE_VTABLE_OFFSET],
    0xfa: [Instruction35ms, "invoke-super-quick", INSTRUCT_TYPE_VTABLE_OFFSET],
    0xfb: [Instruction3rms, "invoke-super-quick/range", VTABLE_OFFSET],
    0xfc: [Instruction22c, "iput-object-volatile", INSTRUCT_TYPE_FIELD],
    0xfd: [Instruction21c, "sget-object-volatile", INSTRUCT_TYPE_FIELD],
    0xfe: [Instruction21c, "sput-object-volatile", INSTRUCT_TYPE_FIELD],
}




def translate_opcode(opcode):
  return OPCODE_TABLE.get(opcode, [None, 'undefined'])[1]


class ByteCodeHelper(object):

  @staticmethod
  def to_string(self, opcode):
    pass

  def to_opcode(self, string):
    pass





class Instruction(object):

  def __init__(self, manager, stream):
    self.manager = manager
    self.stream = stream

  def get_op(self):
    raise Exception('get_op is not implemented')

  def __len__(self):
    raise Exception('length not defined')
  def __str__(self):
    return self.as_string()
  def read(self):
    raise Exception('read not implemented')
  def as_string(self):
    raise Exception('as_string not implemented')


  def as_byte_stream(self):
    raise Exception('byte_stream not implemented')
  def from_string(self):
    pass
  def from_byte(self):
    pass

  def op_as_byte(self):
    return bytes(self.get_op())
  def op_as_string(self):
    return translate_opcode(self.get_op())

# N/A 	00x 	N/A
class Instruction00x(Instruction):
  def as_byte_stream(self):
    return bytes()
  
  def as_string(self):
    pass

  def from_string(self):
    pass

  def from_byte(self):
    pass


# ØØ|op 	10x 	op
class Instruction10x(Instruction):
  def as_byte_stream(self):
    return b'\x00' + self.op_as_byte()

  def as_string(self):
    return self.get_opcode_string()

  def from_string(self):
    pass

  def from_byte(self):
    pass


# B|A|op 	12x 	op vA, vB
class Instruction12x(Instruction):
  def as_byte_stream(self):
    return self.get_b_raw() + self.get_a_raw() + self.op_as_byte()
  
  def as_string(self):
    return '{} v{:1x}, v{:1x}'.format(self.get_opcode_string(), self.get_a(), self.get_b())
  
  def from_string(self):
    pass

  def from_byte(self):    
    self.B = self.stream.readbyte()
    self.A = self.stream.readbyte()
    self.op = self.stream.readshort()

# B|A|op 	11n 	op vA, #+B
class Instruction11n(Instruction):
  def as_byte_stream(self):
    return self.get_b_raw() + self.get_a_raw() + self.op_as_byte()
  
  def as_string(self):
    return '{} v{:1x}, #+{:1x}'.format(self.get_opcode_string(), self.get_a(), self.get_b())

# AA|op 	11x 	op vAA
class Instruction11x(Instruction):
  def as_byte_stream(self):
    return self.get_a() + self.op_as_byte()
  
  def as_string(self):
    return '{} v{:02x}'.format(self.get_opcode_string(), self.get_a())

# AA|op 	10t 	op +AA
class Instruction10t(Instruction):
  def as_byte_stream(self):
    return self.get_a() + self.op_as_byte()
  
  def as_string(self):
    return '{} +{:02x}'.format(self.get_opcode_string(), self.get_a())

# ØØ|op AAAA 	20t 	op +AAAA
class Instruction20t(Instruction):
  def as_byte_stream(self):
    return '\x00' + self.op_as_byte() + self.get_a()
  
  def as_string(self):
    return '{} +{:04x}'.format(self.get_opcode_string(), self.get_a())

# AA|op BBBB 	20bc 	op AA, kind@BBBB
class Instruction20bc(Instruction):
  def as_byte_stream(self):
    return self.get_a() + self.op_as_byte() + self.get_b()
  
  def as_string(self):
    return '{} {:02x}, kind@{:04x}'.format(self.get_opcode_string, self.get_a(), self.get_b())

# AA|op BBBB 	22x 	op vAA, vBBBB
class Instruction22x(Instruction):
  def as_byte_stream(self):
    return self.get_a() + self.op_as_byte() + self.get_b()
