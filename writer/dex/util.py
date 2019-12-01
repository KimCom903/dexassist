
OP_INVOKE_POLYMORPHIC_RANGE = 0xfb
OP_INVOKE_POLYMORPHIC = 0xfa

OP_INVOKE_STATIC = 0x71
OP_INVOKE_STATIC_RANGE = 0x77
class InstructionUtil(object):

    @staticmethod
    def is_invoke_polymorphic(opcode):
        return opcode in [OP_INVOKE_POLYMORPHIC, OP_INVOKE_POLYMORPHIC_RANGE]
    
    @staticmethod
    def is_invoke_static(opcode):
        return opcode in [OP_INVOKE_STATIC, OP_INVOKE_STATIC_RANGE]
