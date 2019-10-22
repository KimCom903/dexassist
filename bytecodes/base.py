## define
INSTRUCT_TYPE_STRING = 0
INSTRUCT_TYPE_TYPE = 1
INSTRUCT_TYPE_METHOD = 2
INSTRUCT_TYPE_FIELD = 3
INSTRUCT_TYPE_OFFSET = 4
INSTRUCT_TYPE_KIND = 5
INSTRUCT_TYPE_PROTO = 6

# for odex
INSTRUCT_TYPE_CALL_SITE = 7
INSTRUCT_TYPE_METHOD_HANDLE = 8
INSTRUCT_TYPE_CALL_METHOD = 9
INSTRUCT_TYPE_CALL_PROTO = 10

def translate_opcode(opcode):
  return OPCODE_TABLE[opcode][1]
def translate_operand_type(opcode):
  return OPCODE_TABLE[opcode][2]
class Instruction(object):
  def __init__(self, manager):
    self.manager = manager
    
  def get_typeindex_string(self, opcode, index):
    op_type = translate_operand_type(opcode)
    if op_type == INSTRUCT_TYPE_STRING:
      return '"' + self.manager.get_string_by_index(index) + '"'
    elif op_type == INSTRUCT_TYPE_TYPE:
      ret = self.manager.get_type_by_index(index)
      if len(ret) > 1: return ret
      if ret == 'v':
        return 'void'
      if ret == 'i':
        return 'int'
      return ret
    elif op_type == INSTRUCT_TYPE_METHOD:
      method = self.manager.get_method_by_index(index)
      return method.repr()
    elif op_type == INSTRUCT_TYPE_FIELD:
      return self.manager.get_field_by_index(index).get_name()
    elif op_type == INSTRUCT_TYPE_OFFSET:
      return self.manager.get_offset_by_index(index).get_name()
    elif op_type == INSTRUCT_TYPE_KIND:
      return self.manager.get_kind_by_index(index).get_name()
    elif op_type == INSTRUCT_TYPE_PROTO:
      return self.manager.get_proto_by_index(index).get_name()
    elif op_type == INSTRUCT_TYPE_CALL_SITE:
      return self.manager.get_site_by_index(index).get_name()
    elif op_type == INSTRUCT_TYPE_METHOD_HANDLE:
      return self.manager.get_method_handle_by_index(index).get_name()

  def __len__(self):
    raise Exception('length not defined')
    
  def __str__(self):
    return self.as_string()
  def read(self):
    raise Exception('read not implemented')
    
  def as_string(self):
    raise Exception('as_string not implemented')
    
  def as_byte_stream(self):
    raise Exception('as_byte_stream not implemented')
    
  def from_string(self):
    pass

  def from_byte(self, stream):
    raise Exception('from_byte not implemented')
  def get_op(self):
    return self.op
  def op_as_byte(self):
    return bytes(self.get_op())

  def from_stream(self, stream):
    return self.from_byte(stream)

  def op_as_string(self):
    return translate_opcode(self.get_op())
  def get_opcode_string(self):
    return self.op_as_string()
# N/A 	00x 	N/A
class Instruction00x(Instruction):
  def as_byte_stream(self):
    return bytes()
  
  def as_string(self):
    return 'N/A'

  def __len__(self):
    return 0

# ØØ|op 	10x 	op
class Instruction10x(Instruction):
  def as_byte_stream(self):
    return b'\x00' + self.op_as_byte()

  def as_string(self):
    return self.get_opcode_string()

  def get_op(self):
    return self.op
    
  def from_string(self):
    pass
  def from_byte(self, stream):
    self.op = stream.read() & 0xff
    
  def __len__(self):
    return 2

# B|A|op 	12x 	op vA, vB
class Instruction12x(Instruction):
  def as_byte_stream(self):
    pass
  
  def as_string(self):
    return '{} v{:1x}, v{:1x}'.format(self.get_opcode_string(), self.A, self.B)
  
  def from_string(self):
    pass

  def from_byte(self, stream):
    temp = stream.read()
    self.B = temp >> 12 & 0xf
    self.A = temp >> 8 & 0xf
    self.op = temp & 0xff
    
  def __len__(self):
    return 2

# B|A|op 	11n 	op vA, #+B
class Instruction11n(Instruction12x):
  def as_byte_stream(self):
    pass
  
  def as_string(self):
    return '{} v{:1x}, #+{:1x}'.format(self.get_opcode_string(), self.A, self.B)

# AA|op 	11x 	op vAA
class Instruction11x(Instruction):
  def as_byte_stream(self):
    pass
  
  def as_string(self): 
    return '{} v{:02x}'.format(self.get_opcode_string(), self.AA)

  def from_byte(self, stream):
    temp = stream.read()
    self.AA = temp >> 8 & 0xff
    self.op = temp & 0xff
       
  def __len__(self):
    return 2

# AA|op 	10t 	op +AA
class Instruction10t(Instruction):
  def as_byte_stream(self):
    pass
  
  def as_string(self):
    return '{} +{:02x}'.format(self.get_opcode_string(), self.AA)

  def from_byte(self, stream):
    temp = stream.read()
    self.AA = temp >> 8 & 0xff
    self.op = temp & 0xff

  def __len__(self):
    return 2   

# ØØ|op AAAA 	20t 	op +AAAA
class Instruction20t(Instruction):
  def as_byte_stream(self):
    pass
  
  def as_string(self):
    return '{} +{:04x}'.format(self.get_opcode_string(), self.AAAA)

  def from_byte(self, stream):
    self.op = stream.read() & 0xff
    self.AAAA = stream.read()
        
  def __len__(self):
    return 4

# AA|op BBBB 	20bc 	op AA, kind@BBBB
class Instruction20bc(Instruction):
  def as_byte_stream(self):
    return self.AA + self.op_as_byte() + self.BBBB
  
  def as_string(self):
    str = '{} {:02x}, '.format(self.get_opcode_string(), self.AA) + self.get_typeindex_string(self.get_op(), self.BBBB)
    return str

  def from_byte(self, stream):
    temp = stream.read()
    self.AA = temp >> 8  &0xff
    self.op = temp & 0xff
    self.BBBB = stream.read()
        
  def __len__(self):
    return 4         

# AA|op BBBB 	22x 	op vAA, vBBBB
class Instruction22x(Instruction):
  def as_byte_stream(self):
    pass

  def as_string(self):
    return '{} v{:02x}, v{:04x}'.format(self.get_opcode_string(), self.AA, self.BBBB)    

  def from_byte(self, stream):
    temp = stream.read()
    self.AA = temp >> 8 & 0xff
    self.op = temp & 0xff
    self.BBBB = stream.read()
        
  def __len__(self):
    return 4        
# AA|op BBBB    21t	    op vAA, +BBBB
class Instruction21t(Instruction22x):
  def as_string(self):
    return '{} v{:02x}, +{:04x}'.format(self.get_opcode_string(), self.AA, self.BBBB) 

# AA|op BBBB    21s	    op vAA, #+BBBB    
class Instruction21s(Instruction22x):
  def as_string(self):
    return '{} v{:02x}, #+{:04x}'.format(self.get_opcode_string(), self.AA, self.BBBB)

# AA|op BBBB    21h	    op vAA, #+BBBB0000
#                  	    op vAA, #+BBBB000000000000
class Instruction21h(Instruction22x):
  def as_string(self):
    return { 0x15 :  '{} v{:02x}, #+{:04x}0000'.format(self.get_opcode_string(), self.AA, self.BBBB),
           0x19 : '{} v{:02x}, #+{:04x}000000000000'.format(self.get_opcode_string(), self.AA, self.BBBB)
           }[self.get_op()]

# AA|op BBBB    21c	    op vAA, type@BBBB
#                               field@BBBB
#                               method_handle@BBBB
#                               proto@BBBB
#                               string@BBBB
class Instruction21c(Instruction22x):
  def as_string(self):
    str = '{} v{:02x}, '.format(self.get_opcode_string(), self.AA) + self.get_typeindex_string(self.get_op() ,self.BBBB)  
    return str

# AA|op CC|BB	23x	    op vAA, vBB, vCC
class Instruction23x(Instruction):
  def as_byte_stream(self):
    pass
  
  def as_string(self):
    return '{} v{:02x}, v{:02x}, v{:02x}'.format(self.get_opcode_string(), self.AA, self.BB, self.CC)

  def from_string(self):
    pass

  def from_byte(self, stream):
    temp1 = stream.read()
    temp2 = stream.read()
    self.AA = temp1 >> 8 & 0xff
    self.op = temp1 & 0xff
    self.CC = temp2 >> 8 & 0xff
    self.BB = temp2 & 0xff
        
  def __len__(self):
    return 4

# AA|op CC|BB   22b     op vAA, vBB, #+CC
class Instruction22b(Instruction23x):
  def as_string(self):
    return '{} v{:02x}, v{:02x}, #+{:02x}'.format(self.get_opcode_string(), self.AA, self.BB, self.CC)

# B|A|op CCCC	22t	    op vA, vB, +CCCC    
class Instruction22t(Instruction):
  def as_byte_stream(self):
    pass
  
  def as_string(self):
    return '{} v{:01x}, v{:01x}, +{:04x}'.format(self.get_opcode_string(), self.A, self.B, self.CCCC)

  def from_string(self):
    pass

  def from_byte(self, stream):
    temp = stream.read()
    self.B = temp >> 12 & 0x0f
    self.A = temp >> 8 & 0x0f
    self.op = temp & 0xff
    self.CCCC = stream.read()
    
  def __len__(self):
    return 4

# B|A|op CCCC   22s     op vA, vB, #+CCCC
class Instruction22s(Instruction22t):
  def as_string(self):
    return '{} v{:01x}, v{:01x}, #+{:04x}'.format(self.get_opcode_string(), self.A, self.B, self.CCCC)
                                                 
# B|A|op CCCC   22c     op vA, vB, type@CCCC
#                                  field@CCCC                                                  
class Instruction22c(Instruction22t):
  def as_string(self):
    str = '{} v{:01x}, v{:01x}, '.format(self.get_opcode_string(), self.A, self.B) + self.get_typeindex_string(self.get_op() ,self.CCCC) 
    return str

# B|A|op CCCC   22cs    op vA, vB, fieldoff@CCCC
# not used instruction
class Instruction22cs(Instruction22t):
  def as_string(self):
    str = '{} v{:01x}, v{:01x}, '.format(self.get_opcode_string(), self.A, self.B) + self.get_typeindex_string(self.get_op() ,self.CCCC)
    return str

# ØØ|op AAAAlo AAAAhi	30t	    op +AAAAAAAA
class Instruction30t(Instruction):
  def as_byte_stream(self):
    pass
  
  def as_string(self):
    return '{} +{:08x}'.format(self.get_opcode_string(), self.get_AAAAAAAA())

  def from_string(self):
    pass

  def from_byte(self, stream):
    self.op = stream.read() & 0xff
    self.AAAAlo = stream.read()
    self.AAAAhi = stream.read()
    self.AAAAAAAA = self.AAAAhi << 16 + self.AAAAlo
                                                         
  def __len__(self):
    return 6

# ØØ|op AAAA BBBB	32x	    op vAAAA, vBBBB
class Instruction32x(Instruction):
  def as_byte_stream(self):
    pass
  
  def as_string(self):
   return '{} v{:04x}, v{:04x}'.format(self.get_opcode_string(), self.AAAA, self.BBBB)

  def from_string(self):
    pass

  def from_byte(self, stream):
    self.op = stream.read() & 0xff
    self.AAAA = stream.read()
    self.BBBB = stream.read()
    
  def __len__(self):
    return 6

# AA|op BBBBlo BBBBhi	31i	    op vAA, #+BBBBBBBB    
class Instruction31i(Instruction):
  def as_byte_stream(self):
    pass
  
  def as_string(self):
   return '{} v{:02x}, #+{:08x}'.format(self.get_opcode_string(), self.AA, self.BBBBBBBB)

  def from_string(self):
    pass

  def from_byte(self, stream):
    temp = stream.read()
    self.AA = temp >> 8 & 0xff
    self.op = temp & 0xff
    self.BBBBlo = stream.read()
    self.BBBBhi = stream.read()
    self.BBBBBBBB = self.BBBBhi << 16 + self.BBBBlo
                                                         
  def __len__(self):
    return 6

# AA|op BBBBlo BBBBhi   31t	op vAA, +BBBBBBBB
class Instruction31t(Instruction31i):
  def as_string(self):
   return '{} v{:02x}, +{:08x}'.format(self.get_opcode_string(), self.AAAA, self.BBBBBBBB)

# AA|op BBBBlo BBBBhi   31c	op vAA, string@BBBBBBBB
class Instruction31c(Instruction31i):
  def as_string(self):
   str = '{} v{:02x}, '.format(self.get_opcode_string(), self.AAAA) + self.get_typeindex_string(self.get_op(), self.BBBBBBBB)
   return str

# A|G|op BBBB F|E|D|C	35c	    [A=5] op {vC, vD, vE, vF, vG}, meth@BBBB
#                               [A=5] op {vC, vD, vE, vF, vG}, call_site@BBBB
#                               [A=5] op {vC, vD, vE, vF, vG}, type@BBBB
#                               [A=4] op {vC, vD, vE, vF}, kind@BBBB
#                               [A=3] op {vC, vD, vE}, kind@BBBB
#                               [A=2] op {vC, vD}, kind@BBBB
#                               [A=1] op {vC}, kind@BBBB
#                               [A=0] op {}, kind@BBBB
class Instruction35c(Instruction):
  def as_byte_stream(self):
    pass
  def as_string(self):
    if self.A==5:
      str = '{} '.format(self.get_opcode_string()) + '{' + 'v{:01x}, v{:01x}, v{:01x}, v{:01x}, v{:01x}'.format(self.C, self.D, self.E, self.F, self.G) + '}, ' + self.get_typeindex_string(self.get_op() ,self.BBBB)
    elif self.A==4:
      str = '{} '.format(self.get_opcode_string()) + '{' + 'v{:01x}, v{:01x}, v{:01x}, v{:01x}'.format(self.C, self.D, self.E, self.F) + '}, ' + self.get_typeindex_string(self.get_op() ,self.BBBB)
    elif self.A==3:
      str = '{} '.format(self.get_opcode_string()) + '{' + 'v{:01x}, v{:01x}, v{:01x}'.format(self.C, self.D, self.E) + '}, ' + self.get_typeindex_string(self.get_op() ,self.BBBB)
    elif self.A==2:
      str = '{} '.format(self.get_opcode_string()) + '{' + 'v{:01x}, v{:01x}'.format(self.C, self.D) + '}, ' + self.get_typeindex_string(self.get_op() ,self.BBBB) 
    elif self.A==1:
      str = '{} '.format(self.get_opcode_string()) + '{' + 'v{:01x}'.format(self.C) + '}, ' + self.get_typeindex_string(self.get_op() ,self.BBBB)
    elif self.A==0:
      str = '{} '.format(self.get_opcode_string()) + '{}, ' + self.get_typeindex_string(self.get_op() ,self.BBBB)                                                         
    return str

  def from_string(self):
    pass

  def from_byte(self, stream):
    temp = stream.read()
    self.A = temp >> 12 & 0x0f
    self.G = temp >> 8 & 0x0f
    self.op = temp & 0xff
    self.BBBB = stream.read()
    temp = stream.read()
    self.F = temp >> 12 & 0x0f
    self.E = temp >> 8 & 0x0f
    self.D = temp >> 4 & 0x0f
    self.C = temp & 0x0f  
    
  def __len__(self):
    return 6

# A|G|op BBBB F|E|D|C      35ms	    [A=5] op {vC, vD, vE, vF, vG}, vtaboff@BBBB
#                                   [A=4] op {vC, vD, vE, vF}, vtaboff@BBBB
#                                   [A=3] op {vC, vD, vE}, vtaboff@BBBB
#                                   [A=2] op {vC, vD}, vtaboff@BBBB
#                                   [A=1] op {vC}, vtaboff@BBBB
# NOT USED                                                         
class Instruction35ms(Instruction35c):
  pass

# A|G|op BBBB F|E|D|C      35mi     [A=5] op {vC, vD, vE, vF, vG}, inline@BBBB
#                                   [A=4] op {vC, vD, vE, vF}, inline@BBBB
#                                   [A=3] op {vC, vD, vE}, inline@BBBB
#                                   [A=2] op {vC, vD}, inline@BBBB
#                                   [A=1] op {vC}, inline@BBBB
# NOT USED                                                         
class Instruction35mi(Instruction35c):
  pass

# AA|op BBBB CCCC	3rc	    op {vCCCC .. vNNNN}, meth@BBBB
#                           op {vCCCC .. vNNNN}, call_site@BBBB
#                           op {vCCCC .. vNNNN}, type@BBBB
class Instruction3rc(Instruction):
  def as_byte_stream(self):
    pass
  
  def as_string(self):
    str = '{} '.format(self.get_opcode_string()) + '{' + 'v{:04x} .. v{:04x}'.format(self.CCCC, self.CCCC + self.AA -1) + '}, ' + self.get_typeindex_string(self.get_op() ,self.BBBB)                                              
    return str

  def from_string(self):
    pass

  def from_byte(self, stream):
    temp = stream.read()
    self.AA = temp >> 8 & 0xff
    self.op = temp & 0xff
    self.BBBB = stream.read()
    self.CCCC = stream.read()
    
  def __len__(self):
    return 6

# AA|op BBBB CCCC	3rms    op {vCCCC .. vNNNN}, vtaboff@BBBB
class Instruction3rms(Instruction3rc):
  pass

# AA|op BBBB CCCC	3rmi    op {vCCCC .. vNNNN}, inline@BBBB  
class instruction3rmi(Instruction3rc):
  pass

# A|G|op BBBB F|E|D|C HHHH	    45cc	[A=5] op {vC, vD, vE, vF, vG}, meth@BBBB, proto@HHHH
#                                       [A=4] op {vC, vD, vE, vF}, meth@BBBB, proto@HHHH
#                                       [A=3] op {vC, vD, vE}, meth@BBBB, proto@HHHH
#                                       [A=2] op {vC, vD}, meth@BBBB, proto@HHHH
#                                       [A=1] op {vC}, meth@BBBB, proto@HHHH  
class Instruction45cc(Instruction):
  def as_byte_stream(self):
    pass
  
  def as_string(self):
    if self.A == 5:
      return '{} '.format(self.get_opcode_string()) + '{' + 'v{:01x}, v{:01x}, v{:01x}, v{:01x}, v{:01x}'.format(self.C, self.D, self.E, self.F, self.G) + '}, ' + self.manager.get_method_by_index(self.BBBB).get_name() + ', ' + self.manager.get_proto_by_index(self.get_HHHH()).get_name()
    if self.A == 4:
      return '{} '.format(self.get_opcode_string()) + '{' + 'v{:01x}, v{:01x}, v{:01x}, v{:01x}'.format(self.C, self.D, self.E, self.F) + '}, ' + self.manager.get_method_by_index(self.BBBB).get_name() + ', ' + self.manager.get_proto_by_index(self.get_HHHH()).get_name()
    if self.A == 3:
      return '{} '.format(self.get_opcode_string()) + '{' + 'v{:01x}, v{:01x}, v{:01x}'.format(self.C, self.D, self.E) + '}, ' + self.manager.get_method_by_index(self.BBBB).get_name() + ', ' + self.manager.get_proto_by_index(self.get_HHHH()).get_name()
    if self.A == 2:
      return '{} '.format(self.get_opcode_string()) + '{' + 'v{:01x}, v{:01x}'.format(self.C, self.D) + '}, ' + self.manager.get_method_by_index(self.BBBB).get_name() + ', ' + self.manager.get_proto_by_index(self.get_HHHH()).get_name()
    if self.A == 1:
      return '{} '.format(self.get_opcode_string()) + '{' + 'v{:01x}'.format(self.C) + '}, ' + self.manager.get_method_by_index(self.BBBB).get_name() + ', ' + self.manager.get_proto_by_index(self.get_HHHH()).get_name()                                                   
    return 'INVALID FORMAT INSTRUCTION45CC'

  def from_string(self):
    pass

  def from_byte(self, stream):
    temp = stream.readbyte()
    self.A = temp >> 4 & 0x0f
    self.G = temp & 0x0f
    self.op = stream.readbyte()
    self.BBBB = stream.readbyte() << 8 + stream.readbyte()
    temp = stream.readbyte()
    self.F = temp >> 4 & 0x0f
    self.E = temp & 0x0f
    temp = stream.readbyte()
    self.D = temp >> 4 & 0x0f
    self.C = temp & 0x0f
    self.HHHH = stream.readbyte() << 8 + stream.readbyte()
    
  def __len__(self):
    return 8

# AA|op BBBB CCCC HHHH	4rcc	op> {vCCCC .. vNNNN}, meth@BBBB, proto@HHHH   
class Instruction4rcc(Instruction):
  def as_byte_stream(self):
    pass
  
  def as_string(self):
    str = '{} '.format(self.get_opcode_string()) + '{' + 'v{:04x} .. v{:04x}'.format(self.CCCC, self.CCCC + self.AA -1) + '}' + self.manager.get_method_by_index(self.BBBB).get_name() + ', ' + self.manager.get_proto_by_index(self.get_HHHH()).get_name()                                             
    return str

  def from_string(self):
    pass

  def from_byte(self, stream):
    self.AA = stream.readbyte()
    self.op = stream.readbyte()
    self.BBBB = stream.readbyte() << 8 + stream.readbyte()
    self.CCCC = stream.readbyte() << 8 + stream.readbyte()
    self.HHHH = stream.readbyte() << 8 + stream.readbyte()
    
  def __len__(self):
    return 8

# AA|op BBBBlo BBBB BBBB BBBBhi	51l	op vAA, #+BBBBBBBBBBBBBBBB
class Instruction51l(Instruction):
  def as_byte_stream(self):
    pass
  
  def as_string(self):
   return '{} v{:02x}, #+{:16x}'.format(self.get_opcode_string(), self.AAAA, self.get_BBBBBBBBBBBBBBBB())

  def from_string(self):
    pass

  def from_byte(self, stream):
    self.AA = stream.readbyte()
    self.op = stream.readbyte()
    self.BBBBlo = stream.readbyte()
    self.BBBBmidlo = stream.readbyte()
    self.BBBBmidhi = stream.readbyte()
    self.BBBBhi = stream.readbyte()
    
  def __len__(self):
    return 10


class OpcodeFactory(object):
  @staticmethod
  def from_stream(opcode, manager, stream):
    bytecode = OPCODE_TABLE[opcode][0](manager)
    bytecode.from_stream(stream)
    return bytecode



OPCODE_TABLE = [
    [Instruction10x, "nop"],
    [Instruction12x, "move"],
    [Instruction22x, "move/from16"],
    [Instruction32x, "move/16"],
    [Instruction12x, "move-wide"],
    [Instruction22x, "move-wide/from16"],
    [Instruction32x, "move-wide/16"],
    [Instruction12x, "move-object"],
    [Instruction22x, "move-object/from16"],
    [Instruction32x, "move-object/16"],
    [Instruction11x, "move-result"],
    [Instruction11x, "move-result-wide"],
    [Instruction11x, "move-result-object"],
    [Instruction11x, "move-exception"],
    [Instruction10x, "return-void"],
    [Instruction11x, "return"],
    [Instruction11x, "return-wide"],
    [Instruction11x, "return-object"],
    [Instruction11n, "const/4"],
    [Instruction21s, "const/16"],
    [Instruction31i, "const"],
    [Instruction21h, "const/high16"],
    [Instruction21s, "const-wide/16"],
    [Instruction31i, "const-wide/32"],
    [Instruction51l, "const-wide"],
    [Instruction21h, "const-wide/high16"],
    [Instruction21c, "const-string", INSTRUCT_TYPE_STRING],
    [Instruction31c, "const-string/jumbo", INSTRUCT_TYPE_STRING],
    [Instruction21c, "const-class", INSTRUCT_TYPE_TYPE],
    [Instruction11x, "monitor-enter"],
    [Instruction11x, "monitor-exit"],
    [Instruction21c, "check-cast", INSTRUCT_TYPE_TYPE],
    [Instruction22c, "instance-of", INSTRUCT_TYPE_TYPE],
    [Instruction12x, "array-length"],
    [Instruction21c, "new-instance", INSTRUCT_TYPE_TYPE],
    [Instruction22c, "new-array", INSTRUCT_TYPE_TYPE],
    [Instruction35c, "filled-new-array", INSTRUCT_TYPE_TYPE],
    [Instruction3rc, "filled-new-array/range", INSTRUCT_TYPE_TYPE],
    [Instruction31t, "fill-array-data"],
    [Instruction11x, "throw"],
    [Instruction10t, "goto"],
    [Instruction20t, "goto/16"],
    [Instruction30t, "goto/32"],
    [Instruction31t, "packed-switch"],
    [Instruction31t, "sparse-switch"],
    [Instruction23x, "cmpl-float"],
    [Instruction23x, "cmpg-float"],
    [Instruction23x, "cmpl-double"],
    [Instruction23x, "cmpg-double"],
    [Instruction23x, "cmp-long"],
    [Instruction22t, "if-eq"],
    [Instruction22t, "if-ne"],
    [Instruction22t, "if-lt"],
    [Instruction22t, "if-ge"],
    [Instruction22t, "if-gt"],
    [Instruction22t, "if-le"],
    [Instruction21t, "if-eqz"],
    [Instruction21t, "if-nez"],
    [Instruction21t, "if-ltz"],
    [Instruction21t, "if-gez"],
    [Instruction21t, "if-gtz"],
    [Instruction21t, "if-lez"],
    # unused
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction23x, "aget"],
    [Instruction23x, "aget-wide"],
    [Instruction23x, "aget-object"],
    [Instruction23x, "aget-boolean"],
    [Instruction23x, "aget-byte"],
    [Instruction23x, "aget-char"],
    [Instruction23x, "aget-short"],
    [Instruction23x, "aput"],
    [Instruction23x, "aput-wide"],
    [Instruction23x, "aput-object"],
    [Instruction23x, "aput-boolean"],
    [Instruction23x, "aput-byte"],
    [Instruction23x, "aput-char"],
    [Instruction23x, "aput-short"],
    [Instruction22c, "iget", INSTRUCT_TYPE_FIELD],
    [Instruction22c, "iget-wide", INSTRUCT_TYPE_FIELD],
    [Instruction22c, "iget-object", INSTRUCT_TYPE_FIELD],
    [Instruction22c, "iget-boolean", INSTRUCT_TYPE_FIELD],
    [Instruction22c, "iget-byte", INSTRUCT_TYPE_FIELD],
    [Instruction22c, "iget-char", INSTRUCT_TYPE_FIELD],
    [Instruction22c, "iget-short", INSTRUCT_TYPE_FIELD],
    [Instruction22c, "iput", INSTRUCT_TYPE_FIELD],
    [Instruction22c, "iput-wide", INSTRUCT_TYPE_FIELD],
    [Instruction22c, "iput-object", INSTRUCT_TYPE_FIELD],
    [Instruction22c, "iput-boolean", INSTRUCT_TYPE_FIELD],
    [Instruction22c, "iput-byte", INSTRUCT_TYPE_FIELD],
    [Instruction22c, "iput-char", INSTRUCT_TYPE_FIELD],
    [Instruction22c, "iput-short", INSTRUCT_TYPE_FIELD],
    [Instruction21c, "sget", INSTRUCT_TYPE_FIELD],
    [Instruction21c, "sget-wide", INSTRUCT_TYPE_FIELD],
    [Instruction21c, "sget-object", INSTRUCT_TYPE_FIELD],
    [Instruction21c, "sget-boolean", INSTRUCT_TYPE_FIELD],
    [Instruction21c, "sget-byte", INSTRUCT_TYPE_FIELD],
    [Instruction21c, "sget-char", INSTRUCT_TYPE_FIELD],
    [Instruction21c, "sget-short", INSTRUCT_TYPE_FIELD],
    [Instruction21c, "sput", INSTRUCT_TYPE_FIELD],
    [Instruction21c, "sput-wide", INSTRUCT_TYPE_FIELD],
    [Instruction21c, "sput-object", INSTRUCT_TYPE_FIELD],
    [Instruction21c, "sput-boolean", INSTRUCT_TYPE_FIELD],
    [Instruction21c, "sput-byte", INSTRUCT_TYPE_FIELD],
    [Instruction21c, "sput-char", INSTRUCT_TYPE_FIELD],
    [Instruction21c, "sput-short", INSTRUCT_TYPE_FIELD],
    [Instruction35c, "invoke-virtual", INSTRUCT_TYPE_METHOD],
    [Instruction35c, "invoke-super", INSTRUCT_TYPE_METHOD],
    [Instruction35c, "invoke-direct", INSTRUCT_TYPE_METHOD],
    [Instruction35c, "invoke-static", INSTRUCT_TYPE_METHOD],
    [Instruction35c, "invoke-interface", INSTRUCT_TYPE_METHOD],
    # unused
    [Instruction10x, "nop"],
    [Instruction3rc, "invoke-virtual/range", INSTRUCT_TYPE_METHOD],
    [Instruction3rc, "invoke-super/range", INSTRUCT_TYPE_METHOD],
    [Instruction3rc, "invoke-direct/range", INSTRUCT_TYPE_METHOD],
    [Instruction3rc, "invoke-static/range", INSTRUCT_TYPE_METHOD],
    [Instruction3rc, "invoke-interface/range", INSTRUCT_TYPE_METHOD],
    # unused
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction12x, "neg-int"],
    [Instruction12x, "not-int"],
    [Instruction12x, "neg-long"],
    [Instruction12x, "not-long"],
    [Instruction12x, "neg-float"],
    [Instruction12x, "neg-double"],
    [Instruction12x, "int-to-long"],
    [Instruction12x, "int-to-float"],
    [Instruction12x, "int-to-double"],
    [Instruction12x, "long-to-int"],
    [Instruction12x, "long-to-float"],
    [Instruction12x, "long-to-double"],
    [Instruction12x, "float-to-int"],
    [Instruction12x, "float-to-long"],
    [Instruction12x, "float-to-double"],
    [Instruction12x, "double-to-int"],
    [Instruction12x, "double-to-long"],
    [Instruction12x, "double-to-float"],
    [Instruction12x, "int-to-byte"],
    [Instruction12x, "int-to-char"],
    [Instruction12x, "int-to-short"],
    [Instruction23x, "add-int"],
    [Instruction23x, "sub-int"],
    [Instruction23x, "mul-int"],
    [Instruction23x, "div-int"],
    [Instruction23x, "rem-int"],
    [Instruction23x, "and-int"],
    [Instruction23x, "or-int"],
    [Instruction23x, "xor-int"],
    [Instruction23x, "shl-int"],
    [Instruction23x, "shr-int"],
    [Instruction23x, "ushr-int"],
    [Instruction23x, "add-long"],
    [Instruction23x, "sub-long"],
    [Instruction23x, "mul-long"],
    [Instruction23x, "div-long"],
    [Instruction23x, "rem-long"],
    [Instruction23x, "and-long"],
    [Instruction23x, "or-long"],
    [Instruction23x, "xor-long"],
    [Instruction23x, "shl-long"],
    [Instruction23x, "shr-long"],
    [Instruction23x, "ushr-long"],
    [Instruction23x, "add-float"],
    [Instruction23x, "sub-float"],
    [Instruction23x, "mul-float"],
    [Instruction23x, "div-float"],
    [Instruction23x, "rem-float"],
    [Instruction23x, "add-double"],
    [Instruction23x, "sub-double"],
    [Instruction23x, "mul-double"],
    [Instruction23x, "div-double"],
    [Instruction23x, "rem-double"],
    [Instruction12x, "add-int/2addr"],
    [Instruction12x, "sub-int/2addr"],
    [Instruction12x, "mul-int/2addr"],
    [Instruction12x, "div-int/2addr"],
    [Instruction12x, "rem-int/2addr"],
    [Instruction12x, "and-int/2addr"],
    [Instruction12x, "or-int/2addr"],
    [Instruction12x, "xor-int/2addr"],
    [Instruction12x, "shl-int/2addr"],
    [Instruction12x, "shr-int/2addr"],
    [Instruction12x, "ushr-int/2addr"],
    [Instruction12x, "add-long/2addr"],
    [Instruction12x, "sub-long/2addr"],
    [Instruction12x, "mul-long/2addr"],
    [Instruction12x, "div-long/2addr"],
    [Instruction12x, "rem-long/2addr"],
    [Instruction12x, "and-long/2addr"],
    [Instruction12x, "or-long/2addr"],
    [Instruction12x, "xor-long/2addr"],
    [Instruction12x, "shl-long/2addr"],
    [Instruction12x, "shr-long/2addr"],
    [Instruction12x, "ushr-long/2addr"],
    [Instruction12x, "add-float/2addr"],
    [Instruction12x, "sub-float/2addr"],
    [Instruction12x, "mul-float/2addr"],
    [Instruction12x, "div-float/2addr"],
    [Instruction12x, "rem-float/2addr"],
    [Instruction12x, "add-double/2addr"],
    [Instruction12x, "sub-double/2addr"],
    [Instruction12x, "mul-double/2addr"],
    [Instruction12x, "div-double/2addr"],
    [Instruction12x, "rem-double/2addr"],
    [Instruction22s, "add-int/lit16"],
    [Instruction22s, "rsub-int"],
    [Instruction22s, "mul-int/lit16"],
    [Instruction22s, "div-int/lit16"],
    [Instruction22s, "rem-int/lit16"],
    [Instruction22s, "and-int/lit16"],
    [Instruction22s, "or-int/lit16"],
    [Instruction22s, "xor-int/lit16"],
    [Instruction22b, "add-int/lit8"],
    [Instruction22b, "rsub-int/lit8"],
    [Instruction22b, "mul-int/lit8"],
    [Instruction22b, "div-int/lit8"],
    [Instruction22b, "rem-int/lit8"],
    [Instruction22b, "and-int/lit8"],
    [Instruction22b, "or-int/lit8"],
    [Instruction22b, "xor-int/lit8"],
    [Instruction22b, "shl-int/lit8"],
    [Instruction22b, "shr-int/lit8"],
    [Instruction22b, "ushr-int/lit8"],
#e3, e4, e5, e6, e7, e8, e9, ea, eb, ec, ed, ee, ef

    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
#f0, f1, f2, f3, f4, f5, f6, f7, f8, f9, 
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction10x, "nop"],
    [Instruction35ms, "invoke-polymorphic", INSTRUCT_TYPE_CALL_METHOD, INSTRUCT_TYPE_CALL_PROTO],
    [Instruction3rms, "invoke-custom", INSTRUCT_TYPE_CALL_METHOD, INSTRUCT_TYPE_CALL_PROTO],
    [Instruction22c, "invoke-polymorphic/range", INSTRUCT_TYPE_CALL_SITE],
    [Instruction21c, "invoke-custom/range", INSTRUCT_TYPE_CALL_SITE],
    [Instruction21c, "const-method-handle", INSTRUCT_TYPE_METHOD_HANDLE],
    [Instruction21c, "const-method-type", INSTRUCT_TYPE_PROTO],

]
    #unused
    
    # for odex
