try:
  from dexassist import normalize
  from dexassist.dex import dex
  from dexassist.bytecodes import editor
  from dexassist.bytecodes import base
except:
  import normalize
  from dex import dex
  from bytecodes import editor, base
  

class DexConverter(object):
  def get_dex(self, header, manager):
    self.dex = normalize.Dex(manager)
    for x in manager.class_def_list:
      self.dex.add_class(self.create_dex_class(x, manager))
    for clazz in self.dex.classes:
      for method in clazz.methods:
        if method.editor is None: continue
        for opcode in method.editor.opcode_list:
          opcode.set_ref_item()

    return self.dex
  def translate_encoded_value(self, parent, manager, encoded_value):

    return translate_encoded_value(self.dex, parent, manager, encoded_value)

  def extract_from_annotation_set_item(self, parent, manager, annotation_set_item):
    ret = []
    for entry in annotation_set_item.entries:
      annotation_item = entry.annotation
      visibility = annotation_item.visibility
      type_idx = annotation_item.annotation.type_idx
      elements = []
      type_name = manager.type_list[type_idx]
      for x in range(annotation_item.annotation.size):
        name_idx = annotation_item.annotation.elements[x].name_idx
        value = annotation_item.annotation.elements[x].value

        elements.append((manager.string_list[name_idx],
            self.translate_encoded_value(parent, manager, value)
        ))
      ret.append(
        normalize.DexAnnotation(parent, visibility, type_name, elements)
      )
    return ret

  #cdi : class_def_item
  def create_dex_class(self, cdi, manager):
    item = normalize.DexClassItem()
    item.type = manager.type_list[cdi.class_idx]
    item.access_flags = cdi.access_flags
    item.superclass = manager.type_list[cdi.superclass_idx]
    item.interfaces = [manager.type_list[x] for x in cdi.interfaces]
    item.name = item.type
    item.values = []

#    if cdi.static_values :
#      for x in cdi.static_values.value.values:
#        item.values.append(normalize.DexValue(x.value, x.type))
    if cdi.source_file_idx and cdi.source_file_idx != 4294967295:
      try:
        item.source_file_name = manager.string_list[cdi.source_file_idx]
      except:
        import traceback
        print("source file idx {} is not in string_list".format(cdi.source_file_idx))

    if cdi.static_values:
      item.static_initializers = [x.value for x in cdi.static_values.value.values]
    field_annotation_table = {}
    method_annotation_table = {}
    param_annotation_table = {}
    if cdi.annotations:
      a = cdi.annotations
      if a.class_item:
        annotations = self.extract_from_annotation_set_item(item, manager, a.class_item)
        item.annotations = annotations
      for field_annotation in a.field_annotations:
        field_annotation_table[field_annotation.field_idx] = self.extract_from_annotation_set_item(manager.field_list[field_annotation.field_idx], manager, field_annotation.annotation)
      for method_annotation in a.method_annotations:
        method_annotation_table[method_annotation.method_idx] = self.extract_from_annotation_set_item(manager.method_list[method_annotation.method_idx], manager, method_annotation.annotation)
      for param_annotation in a.parameter_annotations:
        param_annotation_table[param_annotation.method_idx] = []
        for refitem in param_annotation.annotation_ref.list:
          annotation = refitem.annotation
          if annotation:
            annotation = self.extract_from_annotation_set_item(manager.method_list[param_annotation.method_idx], manager, annotation)
          param_annotation_table[param_annotation.method_idx].append(annotation)


    field_idx = 0
    if cdi.data is None:
      return item

    for f in cdi.data.static_fields:
      field_idx += f.field_idx_diff
      access_flags = f.access_flags
      field = manager.field_list[field_idx]
      field_name = manager.string_list[field.name_idx]
      type_name = manager.type_list[field.type_idx]
      f = self.create_dex_field(item, field_name, type_name, access_flags)
      f.annotations = field_annotation_table.get(field_idx, [])
      item.fields.append(f)
      manager.field_item_list[field_name + item.name] = f
      
    field_idx = 0
    for f in cdi.data.instance_fields:
      field_idx += f.field_idx_diff
      access_flags = f.access_flags
      field = manager.field_list[field_idx]
      field_name = manager.string_list[field.name_idx]
      type_name = manager.type_list[field.type_idx]
      f = self.create_dex_field(item, field_name, type_name, access_flags)
      f.annotations = field_annotation_table.get(field_idx, [])
      item.fields.append(f)
      manager.field_item_list[field_name + item.name] = f

    method_idx = 0
    for m in cdi.data.direct_methods:
      method_idx += m.method_idx_diff
      method_item = manager.method_list[method_idx]
      class_idx = method_item.class_idx
      proto_idx = method_item.proto_idx
      name_idx = method_item.name_idx

      method_name = manager.string_list[name_idx]
      access_flags = m.access_flags
      code = m.code
      proto = manager.proto_list[proto_idx]
      proto_shorty = manager.string_list[proto.shorty_idx]
      return_type_idx = proto.return_type_idx
      parameter = []
      return_type = manager.type_list[return_type_idx]
      if proto.type_list:
        for type_item in proto.type_list.list:
          parameter_type_idx = type_item.type_idx
          type_info = manager.type_list[parameter_type_idx]
          parameter.append(type_info)
      x = self.create_dex_method(manager, item, method_name, access_flags, proto_shorty, parameter, return_type, code)
      x.annotations = method_annotation_table.get(method_idx, [])
      x.param_annotations = param_annotation_table.get(method_idx, [])
      if m.code:
        x.register_count = m.code.registers_size
      item.methods.append(x)
      manager.method_item_list[item.type + method_name + proto_shorty] = x
      manager.proto_item_list[return_type + "".join(parameter)] = x.create_proto()
    
    method_idx = 0
    for m in cdi.data.virtual_methods:
      method_idx += m.method_idx_diff
      method_item = manager.method_list[method_idx]
      class_idx = method_item.class_idx
      proto_idx = method_item.proto_idx
      name_idx = method_item.name_idx

      method_name = manager.string_list[name_idx]
      access_flags = m.access_flags
      code = m.code
      
      proto = manager.proto_list[proto_idx]
      proto_shorty = manager.string_list[proto.shorty_idx]
      dict_key = manager.string_list[proto.shorty_idx]
      return_type_idx = proto.return_type_idx
      parameter = []
      return_type = manager.type_list[return_type_idx]
      if proto.type_list:
        for type_item in proto.type_list.list:
          parameter_type_idx = type_item.type_idx
          type_info = manager.type_list[parameter_type_idx]
          parameter.append(type_info)
      x = self.create_dex_method(manager, item, method_name, access_flags, proto_shorty, parameter, return_type, code)
      x.annotations = method_annotation_table.get(method_idx, [])
      x.param_annotations = param_annotation_table.get(method_idx, [])
      if m.code:
        x.register_count = m.code.registers_size
      item.methods.append(x)
      manager.method_item_list[item.type + method_name + proto_shorty] = x
      manager.proto_item_list[return_type + "".join(parameter)] = x.create_proto()
    return item


  #ef : encodedfield
  def create_dex_field(self, parent, field_name, type_name, access_flags):
    f = normalize.DexField(parent, field_name, type_name, access_flags)
    return f

  def create_dex_method(self, manager, parent, method_name, access_flags, proto_shorty, parameter, return_type, code):
    x = None
    if code:
      #print('method : {}{}'.format(parent, method_name))
      x = code_to_editor(manager, code)
    m = normalize.DexMethod(parent, method_name, access_flags, proto_shorty, parameter, return_type, x)
    return m



def translate_encoded_value(dex_pool, parent, manager, encoded_value):
  #print('translate value(type : {}) : {} -> {}'.format(encoded_value.type, encoded_value, encoded_value.value))
  value = encoded_value.value
  _type = encoded_value.type
  if _type == normalize.VALUE_TYPE_METHOD:
    #todo : get method from method pool
    #create_method(self, class_name, method_name, proto_shorty, parameter, return_type):
    proto = manager.proto_list[value.proto_idx]
    shorty = manager.string_list[proto.shorty_idx]
    return_type = manager.type_list[proto.return_type_idx]
    method_name = manager.string_list[value.name_idx]
    parameters = []
    class_type = manager.type_list[value.class_idx]
    if proto.type_list:
      for type_item in proto.type_list.list:
        pt_idx = type_item.type_idx
        type_info = manager.type_list[pt_idx]
        parameters.append(type_info)
    
    value = manager.create_method(class_type, method_name, shorty, parameters, return_type)

  if _type == normalize.VALUE_TYPE_ANNOTATION:
    #todo : get annotation from annotation pool
    type_name = manager.type_list[value.type_idx]
    key_name_tuples = []
    for x in value.elements:
      key_name_tuples.append((
        manager.string_list[x.name_idx], translate_encoded_value(dex_pool, parent, manager, x.value)
      ))
    value = normalize.DexAnnotation(parent, None, type_name, key_name_tuples)

  if _type == normalize.VALUE_TYPE_FIELD or _type == normalize.VALUE_TYPE_ENUM:
    #todo : get field from field pool
    parent = manager.type_list[value.class_idx]
    #parent = dex_pool.get_class(parent)
    
    field_name = manager.string_list[value.name_idx]
    type_name = manager.type_list[value.type_idx]
    access_flags = 0
    
    value = normalize.DexField(parent, field_name, type_name, access_flags)
  
  if _type == normalize.VALUE_TYPE_BOOLEAN:
    value = normalize.DexValue(True if value else False, value_type=normalize.VALUE_TYPE_BOOLEAN)
  
  if _type == normalize.VALUE_TYPE_ARRAY:
    values = value.values
    ret = [translate_encoded_value(dex_pool, parent, manager, x) for x in values]
    return ret


  return normalize.DexValue(value, _type)

def code_to_editor(manager, code):
  e = editor.Editor()
  e.manager = manager
  ir = CodeItemReader(e, manager, code)
  return e


class ByteCodeConverter(object):
  def __init__(self, manager):
    pass



class DexWriter(object):
  def __init__(self, dex):
    self.dex = dex
  def save_as(self, stream):
    pass



class CodeStream(object):
  def __init__(self, insns_array):
    self.buf = insns_array
    self.index = 0
  def peek(self):
    return self.buf[self.index]
  def read(self):
    ret = self.peek()
    self.index += 1
    return ret
  @property
  def offset(self):
    return self.index

  def at(self, offset):
    self.index = offset

class CodeItemReader(object):
  def __init__(self, editor_, manager, code_item):
    self.tries = []
    self.opcodes = []
    self.editor = editor_
    self.manager = manager
    payload_size = 0
    stream = CodeStream(code_item.insns)
    #print('insns_size : {}'.format(code_item.insns_size))
    insns_size = code_item.insns_size

    while stream.index + payload_size < insns_size:
      #print('stream.index : {}'.format(stream.index))
      opcode = stream.peek() & 0xff

      instruction = base.OpcodeFactory.from_stream(opcode, self.editor.manager, stream)
      if instruction.op == 0x26: # fill-array-data
        payload = base.FillArrayDataPayload(instruction)
        payload.read(stream, instruction.BBBBBBBB + instruction.base_offset)
        payload_size += payload.get_size()
        instruction.payload = payload
      elif instruction.op == 0x2b: #packed-switch
        payload = base.PackedSwitchPayload(instruction)
        payload.read(stream, instruction.BBBBBBBB + instruction.base_offset)
        payload_size += payload.get_size()
        instruction.payload = payload
      elif instruction.op == 0x2c: #sparse-switch
        payload = base.SparseSwitchPayload(instruction)
        payload.read(stream, instruction.BBBBBBBB + instruction.base_offset)
        payload_size += payload.get_size()
        instruction.payload = payload

      self.opcodes.append(instruction)

    type_addrs = []
    if code_item.tries:
      for t in code_item.tries:
        start = t.start_addr
        end = t.start_addr + t.insn_count - 1
        catch_handler = t.handler
        for type_addr_pair in catch_handlers.type_addr_pairs:
          type_idx, addr = type_addr_pair.type_idx, type_addr_pair.addr
          type_addrs.append(editor.DexHandlerTypeAddr(self.manager.type_list[type_idx],type_addr_pair.addr))
        catch_all_addr = catch_handlers.catch_all_addr

        trycatch = editor.TryCatch(self.editor, start, end, type_addrs, catch_all_addr)
        for t_a_pair in type_addrs:
          t_a_pair.handler = trycatch
        self.editor.tries.append(trycatch)
    self.editor.opcode_list = self.opcodes


