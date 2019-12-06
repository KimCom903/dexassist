import struct
try:
  from dexassist.writer.multidex.multidex import DefaultMultiDexPolicy
  from dexassist.writer.dex.section import *
except:
  from writer.multidex.multidex import DefaultMultiDexPolicy
  from writer.dex.section import *

from writer.dex.util import InstructionUtil

NO_INDEX = -1
NO_OFFSET = 0

INSTRUCT_TYPE_METHOD = 2

LITTLE_ENDIAN_TAG = 0x12345678
# item type
HEADER_ITEM = 0x0000
STRING_ID_ITEM = 0x0001
TYPE_ID_ITEM = 0x0002
PROTO_ID_ITEM = 0x0003
FIELD_ID_ITEM = 0x0004
METHOD_ID_ITEM = 0x0005
CLASS_DEF_ITEM = 0x0006
CALL_SITE_ID_ITEM = 0x0007
METHOD_HANDLE_ITEM = 0x0008
MAP_LIST = 0x1000
TYPE_LIST = 0x1001
ANNOTATION_SET_REF_LIST = 0x1002
ANNOTATION_SET_ITEM = 0x1003
CLASS_DATA_ITEM = 0x2000
CODE_ITEM = 0x2001
STRING_DATA_ITEM = 0x2002
DEBUG_INFO_ITEM = 0x2003
ANNOTATION_ITEM = 0x2004
ENCODED_ARRAY_ITEM = 0x2005
ANNOTATION_DIRECTORY_ITEM = 0x2006
HIDDENAPI_CLASS_DATA_ITEM = 0xf000


SIZE_CLASS_DEF_ITEM = 32
SIZE_HEADER_ITEM = 112
SIZE_MAP_ITEM = 12
SIZE_MEMBER_ID_ITEM = 8
SIZE_PROTO_ID_ITEM = 12
SIZE_SIGNATURE = 20
SIZE_STRING_ID_ITEM = 4
SIZE_TRY_ITEM = 8
SIZE_TYPE_ID_ITEM = 4
SIZE_TYPE_ITEM = 2
SIZE_UBYTE = 1
SIZE_UINT = 4
SIZE_USHORT = 2



STRING_ID_ITEM_SIZE = 4
TYPE_ID_ITEM_SIZE = 4
PROTO_ID_ITEM_SIZE = 4 + 4 + 4
FIELD_ID_ITEM_SIZE = 2 + 2 + 4
METHOD_ID_ITEM_SIZE = 2 + 2 + 4
CLASS_DEF_ITEM_SIZE = 4 + 4 + 4 + 4 + 4 + 4 + 4 + 4
CALL_SITE_ID_ITEM_SIZE = 4
METHOD_HANDLE_ITEM_SIZE = 2 + 2 + 2 + 2


def get_method_register_count(method):
  return get_parameter_register_count(method.parameters, method.is_static())
  
def get_parameter_register_count(parameters, is_static):

  reg_count = 0
  for param_type in parameters:
    reg_count += 1
    if param_type[0] in ['J', 'D']:
      reg_count += 1

  if not is_static: reg_count += 1
  return reg_count

class SectionManager(object):
  def __init__(self):
    self.section_map = {}
  def get_section(self, key):
    return self.section_map[key]

  def build_string_section(self, dex_pool):
    x = set()
    section = StringSection(self)
    for clazz in dex_pool:
      p = clazz.get_related_strings()
      x.update(p)
    x = list(x)
    x.sort()
    for strings in x:
      section.add_item(strings)
    self.section_map[SECTION_STRING] = section

  def build_type_section(self, dex_pool):
    section = TypeSection(self)
    type_list = set()
    for clazz in dex_pool:
      type_list.add(clazz.type)
      for field in clazz.fields:
        type_list.add(field.type)
      for method in clazz.methods:
        type_list.add(method.type)
    x = list(type_list)
    x.sort()
    for types in x:
      section.add_item(types)
    self.section_map[SECTION_TYPE] = section

  def build_proto_section(self, dex_pool):
    section = ProtoSection(self)
    proto_list = set()
    for clazz in dex_pool:
      for method in clazz.methods:
        proto_list.add(method.signature)
    x = list(proto_list)
    x.sort()
    for protos in x:
      section.add_item(protos)
    self.section_map[SECTION_PROTO] = section

  def build_field_section(self, dex_pool):
    section = FieldSection(self)
    field_list = set()
    for clazz in dex_pool:
      for field in clazz.fields:
        field_list.add(field)
    x = list(field_list)
    for field in x:
      section.add_item(field)
    self.section_map[SECTION_FIELD] = section
  
  def build_method_section(self, dex_pool):
    section = MethodSection(self)
    method_list = set()
    for clazz in dex_pool:
      for method in clazz.methods:
        method_list.add(method)
    x = list(method_list)
    for method in x:
      section.add_item(method)
    self.section_map[SECTION_METHOD] = section

  def get_data_section_offset(self):
    ret = 0x70 # header_item_size
    ret += self.get_section(SECTION_STRING).get_item_count() * STRING_ID_ITEM_SIZE
    ret += self.get_section(SECTION_TYPE).get_item_count() * TYPE_ID_ITEM_SIZE
    ret += self.get_section(SECTION_PROTO).get_item_count() * PROTO_ID_ITEM_SIZE
    ret += self.get_section(SECTION_FIELD).get_item_count() * FIELD_ID_ITEM_SIZE
    ret += self.get_section(SECTION_METHOD).get_item_count() * METHOD_ID_ITEM_SIZE
    ret += self.get_section(SECTION_CLASS).get_item_count() * CLASS_DEF_ITEM_SIZE
    ret += self.get_section(SECTION_CALL_SITE).get_item_count() * CALL_SITE_ID_ITEM_SIZE
    ret += self.get_section(SECTION_METHOD_HANDLE).get_item_count() * METHOD_HANDLE_ITEM_SIZE
    return ret
  
  def build_class_def_section(self, dex_pool):
    section = ClassSection(self)
    clazz_list = set()
    for clazz in dex_pool:
      clazz_list.add(clazz)
    for clazz in clazz_list:
      section.add_item(clazz)
    self.section_map[SECTION_CLASS] = section
  
  def build_call_site_id_section(self, dex_pool): # pass, for reflection
    pass

  def build_method_handle_section(self, dex_pool): # pass, for reflection
    pass

  def build_map_list_section(self, dex_pool):
    pass

  def build_type_list_section(self, dex_pool):
    pass

  def build_annotation_set_ref_list_section(self, dex_pool):
    pass

  def build_annotation_set_item(self, dex_pool):
    pass

  def build_class_data_item_section(self, dex_pool):
    pass

  def build_code_item_section(self, dex_pool):
    pass

  def build_string_data_item_section(self, dex_pool):
    pass


  def build_debug_info_item_section(self, dex_pool):
    pass

  def build_annotation_item_section(self, dex_pool):
    pass

  def build_encoded_array_item_section(self, dex_pool):
    pass

  def build_annotations_directory_item_section(self, dex_pool):
    pass

  def build_hiddenapi_class_data_item_section(self, dex_pool): # pass, for reflection
    pass
  

class DexWriter(object):
  def __init__(self, dex_class_pool):
    self.manager = SectionManager()
    self.dex_class_pool = dex_class_pool
    self.multidex_policy = DefaultMultiDexPolicy()
    self.dex_pool_dict = {}
    self.string_index_section_offset = NO_OFFSET
    self.type_section_offset = NO_OFFSET
    self.proto_section_offset = NO_OFFSET
    self.field_section_offset = NO_OFFSET
    self.method_section_offset = NO_OFFSET
    self.class_index_section_offset = NO_OFFSET
    self.call_site_section_offset = NO_OFFSET
    self.method_handle_section_offset = NO_OFFSET

    self.string_data_section_offset = NO_OFFSET
    self.class_data_section_offset = NO_OFFSET
    self.type_list_section_offset = NO_OFFSET
    self.encoded_array_section_offset = NO_OFFSET
    self.annotation_section_offset = NO_OFFSET
    self.annotation_set_section_offset = NO_OFFSET
    self.annotation_set_ref_section_offset = NO_OFFSET
    self.annotation_directory_section_offset = NO_OFFSET
    self.debug_section_offset = NO_OFFSET
    self.code_section_offset = NO_OFFSET
    self.map_section_offset = NO_OFFSET

    self.num_annotation_set_ref_items = 0
    self.num_annotation_directory_items = 0
    self.num_debug_info_items = 0
    self.num_code_items = 0
    self.num_class_data_items = 0
  def write(self, stream):
    for clazz in self.dex_class_pool.classes:
      clazz.fix()
      index = self.multidex_policy.get_multidex_index(clazz)
      if index not in self.dex_pool_dict:
        self.dex_pool_dict[index] = []
      self.dex_pool_dict[index].append(clazz)
    for dex_pool_index in self.dex_pool_dict:
      stream.set_output_index(index)
      self.build_dex(self.dex_pool_dict[dex_pool_index], stream)

  def build_dex(self, dex_pool, stream):
    manager = self.manager
    manager.build_string_section(dex_pool)
    manager.build_type_section(dex_pool)
    manager.build_proto_section(dex_pool)
    manager.build_field_section(dex_pool)
    manager.build_method_section(dex_pool)
    manager.build_class_def_section(dex_pool)
    manager.build_call_site_id_section(dex_pool) # pass, for reflection
    manager.build_method_handle_section(dex_pool) # pass, for reflection
    manager.build_map_list_section(dex_pool)
    manager.build_type_list_section(dex_pool)
    manager.build_annotation_set_ref_list_section(dex_pool)
    manager.build_annotation_set_item(dex_pool)
    manager.build_class_data_item_section(dex_pool)
    manager.build_code_item_section(dex_pool)
    manager.build_string_data_item_section(dex_pool)
    manager.build_debug_info_item_section(dex_pool)
    manager.build_annotation_item_section(dex_pool)
    manager.build_encoded_array_item_section(dex_pool)
    manager.build_annotations_directory_item_section(dex_pool)
    manager.build_hiddenapi_class_data_item_section(dex_pool)
    data_section_offset = manager.get_data_section_offset()
    buf = bytearray()
    header_writer = OutputStream(buf, 0)
    index_writer = OutputStream(buf, SIZE_HEADER_ITEM)
    offset_writer = OutputStream(buf, data_section_offset)
    
    self.write_strings(index_writer, offset_writer)
    self.write_types(index_writer)
    self.write_type_lists(offset_writer)
    self.write_protos(index_writer)
    self.write_fields(index_writer)
    self.write_methods(index_writer)

    method_handle_writer = OutputStream(buf, index_writer.get_position() + 
      manager.get_section(SECTION_CLASS).get_item_count() * CLASS_DEF_ITEM_SIZE +
      manager.get_section(SECTION_CALL_SITE).get_item_count() * CALL_SITE_ID_ITEM_SIZE
    )

    self.write_method_handles(method_handle_writer)
    method_handle_writer.close()

    self.write_encoded_arrays(offset_writer)
    call_site_writer = OutputStream(buf, index_writer.get_position() + 
      manager.get_section(SECTION_CLASS).get_item_count() * CLASS_DEF_ITEM_SIZE)
    self.write_call_sites(call_site_writer)
    call_site_writer.close()

    self.write_annotations(offset_writer)
    self.write_annotation_sets(offset_writer)
    self.write_annotation_set_refs(offset_writer, dex_pool)
    self.write_annotation_directories(offset_writer, dex_pool)
    self.write_debug_and_code_items(offset_writer, TempOutputStream())
    self.write_classes(index_writer, offset_writer)
    self.write_map_item(offset_writer)
    self.write_header(header_writer, data_section_offset, offset_writer.get_position())

    header_writer.close()
    index_writer.close()
    offset_writer.close()

    #self.update_signature(buf)
    #self.update_check_sum(buf)
  def get_section(self, key):
    return self.manager.get_section(key)

  def write_strings(self, index_writer, offset_writer):
    self.string_index_section_offset = index_writer.get_position()
    self.string_data_section_offset = offset_writer.get_position()
    for item in self.get_section(SECTION_STRING).get_items():
      index_writer.write_int(offset_writer.get_position())
      string_val = item.get_value()
      offset_writer.write_uleb128(len(string_val))
      offset_writer.write_string(string_val)
      offset_writer.write(0)

  def write_types(self, index_writer):
    self.type_section_offset = index_writer.get_position()
    for item in self.get_section(SECTION_TYPE).get_items():
      index_writer.write_int(self.get_section(SECTION_STRING).get_item_index(
        item.get_value()
      ))

  def write_debug_and_code_items(self, offset_writer, deferred_stream):
    ehbuf = TempOutputStream()
    self.debug_section_offset = offset_writer.get_position()
    # pass write debug section!
    code_writer = deferred_stream
    for clazz in self.get_section(SECTION_CLASS).get_items():
      direct_methods = clazz.get_direct_methods()
      virtual_methods = clazz.get_virtual_methods()
      for method in direct_methods + virtual_methods:
        try_blocks = method.get_try_blocks()
        instructions = method.get_instructions()
        #debug_items = method.get_debug_items()
        #debug_item_offset = write_debug_item(offset_writer, debug_writer,
        #method, debug_items
        #)
        debug_item_offset = 0
        code_item_offset = self.write_code_item(code_writer, ehbuf, method, try_blocks, instructions, debug_item_offset)
        if code_item_offset != 1:
          method.code_item_offset = code_item_offset
          #code_offsets.append(CodeItemOffset(method, code_item_offset))
    
    offset_writer.align()
    self.code_section_offset = offset_writer.get_position()
    code_writer.write_to(offset_writer)

  def write_code_item(self, code_writer, ehbuf, method, try_blocks, instructions, debug_item_offset):
    self.num_code_items += 1
    code_writer.align()
    code_item_offset = code_writer.get_position()
    code_writer.write_ushort(get_method_register_count(method))
    is_static = method.is_static()
    params = self.get_section(SECTION_TYPE_LIST).get_types(
      self.get_section(SECTION_PROTO).get_parameters(method.proto)
    )
    code_writer.write_ushort(
      get_parameter_register_count(params, is_static)
    )
    if instructions is None:
      code_writer.write_ushort(0)
      code_writer.write_ushort(0)
      code_writer.write_int(debug_item_offset)
      code_writer.write_int(0)
      return code_item_offset
    #try_blocks = TryListBuilder.massage_try_blocks(try_blocks)
    out_param_count = 0
    code_unit_count = 0
    param_count = 0
    for ins in instructions:
      code_unit_count += ins.get_code_units()
      if ins.ref_type == INSTRUCT_TYPE_METHOD:
        method_ref = ins.ref
        opcode = ins.get_op()
        if InstructionUtil.is_invoke_polymorphic(opcode):
          param_count = ins.get_register_count()
        else:
          param_count = get_method_register_count(method_ref)
          #param_count = self.get_param_register_count(method_ref, InstructionUtil.is_invoke_static(opcode))

        if param_count > out_param_count: out_param_count = param_count

    code_writer.write_ushort(out_param_count)
    code_writer.write_ushort(len(try_blocks))
    code_writer.write_int(debug_item_offset)

    ins_writer = InstructionWriter.make_ins_writer(instructions, code_writer, self.get_section(SECTION_STRING),
    self.get_section(SECTION_TYPE),
    self.get_section(SECTION_FIELD),
    self.get_section(SECTION_METHOD),
    self.get_section(SECTION_PROTO),
    self.get_section(SECTION_METHOD_HANDLE),
    self.get_section(SECTION_CALL_SITE))

    code_writer.write_int(code_unit_count)
    code_offset = 0

    for ins in instructions:
      ins_writer.write(ins)
      code_offset += ins.get_code_units()
    
    if len(try_blocks) > 0:
      code_writer.align()
      handler_map = dict()
    
    for try_block in try_blocks:
      handler_map[try_block.get_exception_handlers()] = 0
    ehbuf.write_uleb128(len(handler_map))

    for try_block in try_blocks:
      code_writer.write_int(try_block.get_start_addr())
      code_writer.write_ushort(try_block.get_code_count())

      if len(try_block.get_exception_handlers()) == 0:
        raise Exception("try block has no exception handlers")
      
      offset = handler_map[try_block.get_exception_handlers()]
      if offset == 0:
        offset = ehbuf.get_position()
        handler_map[try_block.get_exception_handlers()] = offset
      code_writer.write_ushort(offset)

      eh_size = len(try_block.get_exception_handlers())
      eh_last = try_block.get_exception_handlers()[-1]
      if eh_last.get_exception_type() is None:
        eh_size = -eh_size + 1
      
      ehbuf.write_sleb128(eh_size)
      for eh in try_block.get_exception_handlers():
        exception_type = eh.get_exception_type()
        code_addr = eh.get_handler_addr()
        if exception_type is not None:
          # regular
          ehbuf.write_uleb128(self.get_section(SECTION_TYPE).get_item_index(exception_type))
          ehbuf.write_uleb128(code_addr)
        else:
          #catch(Throwable)
          ehbuf.write_uleb128(code_addr)
    if ehbuf.get_position() > 0:
      eubuf.write_to(code_writer)

  def calc_map_list_item_count(self):
    num_items = 2 # header, map_list_item

    if self.get_section(SECTION_STRING).size(): num_items += 1 # for data

    num_items += len(filter(lambda x : x > 0, [self.get_section(x).size() for x in [SECTION_STRING, SECTION_TYPE, SECTION_PROTO, SECTION_FIELD, SECTION_METHOD, SECTION_CALL_SITE,
    SECTION_METHOD_HANDLE, SECTION_TYPE_LIST, SECTION_ENCODED_ARRAY, SECTION_ANNOTATION, SECTION_CLASS]]))

    if self.get_section(SECTION_ANNOTATION_SET).size() > 0 or self.should_create_empty_annotation_set():
      num_items += 1
    if self.num_annotation_set_ref_items > 0:
      num_items += 1
    if self.num_annotation_directory_items > 0:
      num_items += 1
    if self.num_debug_info_items > 0:
      num_items += 1
    if self.num_code_items > 0:
      num_items += 1
    if self.num_class_data_items > 0:
      num_items += 1
    return num_items


  def write_map_item(self, offset_writer):
    offset_writer.align()
    self.map_section_offset = offset_writer.get_position()
    num_items = self.calc_map_list_item_count()
    offset_writer.write_int(num_items)

    self.write_map_item_object(offset_writer, HEADER_ITEM, 1, 0)
    self.write_map_item_object(offset_writer, STRING_ID_ITEM, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_map_item_object(offset_writer, TYPE_ID_ITEM, self.get_section(SECTION_TYPE).size(), self.type_section_offset)
    self.write_map_item_object(offset_writer, PROTO_ID_ITEM, self.get_section(SECTION_PROTO).size(), self.proto_section_offset)
    self.write_map_item_object(offset_writer, FIELD_ID_ITEM, self.get_section(SECTION_FIELD).size(), self.field_section_offset)
    self.write_map_item_object(offset_writer, METHOD_ID_ITEM, self.get_section(SECTION_METHOD).size(), self.method_section_offset)
    self.write_map_item_object(offset_writer, CLASS_DEF_ITEM, self.get_section(SECTION_CLASS).size(), self.class_index_section_offset)
    self.write_map_item_object(offset_writer, CALL_SITE_ID_ITEM, self.get_section(SECTION_CALL_SITE).size(), self.call_site_section_offset)
    self.write_map_item_object(offset_writer, METHOD_HANDLE_ITEM, self.get_section(SECTION_METHOD_HANDLE).size(), self.method_handle_section_offset)

    # data section
    self.write_map_item_object(offset_writer, STRING_DATA_ITEM, self.get_section(SECTION_STRING).size(), self.string_data_section_offset)
    self.write_map_item_object(offset_writer, TYPE_LIST, self.get_section(SECTION_TYPE_LIST).size(), self.type_list_section_offset)
    self.write_map_item_object(offset_writer, ENCODED_ARRAY_ITEM, self.get_section(SECTION_ENCODED_ARRAY).size(), self.encoded_array_section_offset)
    self.write_map_item_object(offset_writer, ANNOTATION_ITEM, self.get_section(SECTION_ANNOTATION).size(), self.annotation_section_offset)
    self.write_map_item_object(offset_writer, ANNOTATION_SET_ITEM, self.get_section(SECTION_ANNOTATION_SET).size(), self.annotation_set_section_offset)
    self.write_map_item_object(offset_writer, ANNOTATION_SET_REF_LIST, self.get_section(SECTION_ANNOTATION_SET_REF).size(), self.annotation_set_ref_section_offset)
    self.write_map_item_object(offset_writer, ANNOTATION_DIRECTORY_ITEM, self.get_section(SECTION_ANNOTATION_DIRECTORY).size(), self.annotation_directory_section_offset)
    self.write_map_item_object(offset_writer, DEBUG_INFO_ITEM, self.get_section(SECTION_DEBUG).size(), self.debug_section_offset)
    self.write_map_item_object(offset_writer, CODE_ITEM, self.get_section(SECTION_CODE).size(), self.code_section_offset)
    self.write_map_item_object(offset_writer, CLASS_DATA_ITEM, self.get_section(SECTION_CLASS_DATA).size(), self.class_data_section_offset)
    self.write_map_item_object(offset_writer, MAP_LIST, 1, self.map_section_offset)

  def write_map_item_object(self, offset_writer, item_type, size, offset):
    if size > 0:
      offset_writer.write_ushort(item_type)
      offset_writer.write_ushort(0)
      offset_writer.write_int(size)
      offset_writer.write_int(offset)
    
  
  def write_type_lists(self, writer):
    writer.align()
    self.type_list_section_offset = writer.position

    for item in self.get_section(SECTION_TYPE_LIST).get_items():
      writer.align()
      item.offset = writer.position
      types = item.get_types()
      for t in types:
        writer.write_ushort(self.get_section(SECTION_TYPE).get_item_index(t))


  def write_protos(self, writer):
    self.proto_section_offset = writer.position
    index = 0
    for item in self.get_section(SECTION_PROTO).get_items():
      writer.write_int(
        self.get_section(SECTION_STRING).get_item_index(
          item.shorty
        )
      )
      writer.write_int(
        self.get_section(SECTION_TYPE).get_item_index(
          item.return_type()
        )
      )
      writer.write_int(
        self.get_section(SECTION_TYPE_LIST).get_item(
          item.parameters()
        ).offset
      )



  def write_fields(self, writer):
    self.field_section_offset = writer.position
    index = 0
    type_section = self.get_section(SECTION_TYPE)
    string_section = self.get_section(SECTION_STRING)
    for x in self.get_section(SECTION_FIELD).get_items():
      x.index = index
      index += 1
      writer.write_ushort(type_section.get_item_index(x.clazz.type))
      writer.write_ushort(type_section.get_item_index(x.type))
      writer.write_int(string_section.get_item_index(x.name))

  def write_methods(self, writer):
    self.method_section_offset = writer.position
    index = 0
    type_section = self.get_section(SECTION_TYPE)
    string_section = self.get_section(SECTION_STRING)
    proto_section = self.get_section(SECTION_PROTO)
    method_section = self.get_section(SECTION_METHOD)

    for x in method_section.get_items():
      x.index = index
      index += 1
      writer.write_ushort(type_section.get_item_index(x.clazz.type))
      writer.write_ushort(proto_section.get_item_index(x.proto))
      writer.write_int(string_section.get_item_index(x.name))

    
  def write_classes(self, index_writer, offset_writer):
    self.class_index_section_offset = index_writer.position
    self.class_data_section_offset = offset_writer.position

    class_section = self.get_section(SECTION_CLASS)
    index = 0
    for x in class_section.get_items():
      index = self.write_class(index_writer, offset_writer, index, x)

  def write_class(self, index_writer, offset_writer, index, clazz):
    if clazz is None: return index # not in dex
    if clazz.index != NO_INDEX: return index # writed

    clazz.index = 0

    index = self.write_class(index_writer, offset_writer, index, clazz.super)
    for x in clazz.interfaces:
      index = self.write_class(index_writer, offset_writer, index, x)
    clazz.index = index
    index += 1
    type_section = self.get_section(SECTION_TYPE)
    type_list_section = self.get_section(SECTION_TYPE_LIST)
    string_section = self.get_section(SECTION_STRING)
    
    index_writer.write_int(type_section.get_item_index(clazz.type))
    index_writer.write_int(clazz.access_flags)
    index_writer.write_int(type_section.get_item_index(clazz.super.type))
    index_writer.write_int(type_list_section.get_item_index([i.type for i in clazz.interfaces]))
    index_writer.write_int(clazz.annotation_directory_offset)

    static_fields = clazz.get_sorted_static_fields()
    instance_fields = clazz.get_sorted_instance_fields()
    direct_methods = clazz.get_sorted_direct_methods()
    virtual_methods = clazz.get_sorted_virtual_methods()

    offset = offset_writer.position
    clazz_has_data = len(static_fields) > 0 or len(instance_fields) > 0 or len(direct_methods) > 0 or len(virtual_methods) > 0
    if not clazz_has_data:
      offset = NO_OFFSET
    
    index_writer.write_int(offset)
    encoded_array_section = self.get_section(SECTION_ENCODED_ARRAY)
    if clazz.static_initializers is not None:
      offset = encoded_array_section.get_item(clazz.static_initializers).offset
    else:
      offset = None
    index_writer.write_int(offset)

    if not clazz_has_data: return index

    self.num_class_data_items += 1

    offset_writer.write_uleb128(len(static_fields))
    offset_writer.write_uleb128(len(instance_fields))
    offset_writer.write_uleb128(len(direct_methods))
    offset_writer.write_uleb128(len(virtual_methods))

    self.write_encoded_fields(offset_writer, static_fields)
    self.write_encoded_fields(offset_writer, instance_fields)
    self.write_encoded_methods(offset_writer, direct_methods)
    self.write_encoded_methods(offset_writer, virtual_methods)

    return index

  def write_encoded_fields(self, offset_writer, field_list):
    prev_index = 0
    field_section = self.get_section(SECTION_FIELD)
    
    for field in field_list:
      index = field_section.get_item_index(field)
      offset_writer.write_uleb128(index - prev_index)
      offset_writer.write_uleb128(field.access_flags)
      prev_index = index
  
  def write_encoded_methods(self, offset_writer, method_list):
    prev_index = 0
    method_section = self.get_section(SECTION_METHOD)
    for method in method_list:
      index = method_section.get_item_index(method)
      offset_writer.write_uleb128(index - prev_index)
      offset_writer.write_uleb128(method.access_flags)
      offset_writer.write_uleb128(method.code_item_offset)
      prev_index = index

  def write_call_sites(self, writer):
    pass # skip

  def write_method_handles(self, writer):
    pass # skip

  def write_encoded_arrays(self, writer):
    self.encoded_array_section_offset = writer.position

    encoded_array_section = self.get_section(SECTION_ENCODED_ARRAY)

    for arr in encoded_array_section.get_items():
      arr.offset = writer.position
      encoded_array = arr.values
      writer.write_uleb128(len(arr.values))
      for val in encoded_array:
        self.write_encoded_value(writer, val)

  

  def write_annotations(self, writer):
    self.annotation_section_offset = writer.position
    annotation_section = self.get_section(SECTION_ANNOTATION)
    type_section = self.get_section(SECTION_TYPE)
    string_section = self.get_section(SECTION_STRING)
    for ann in annotation_section.get_items():
      ann.offset = writer.position
      writer.write_ubyte(ann.visibility)
      writer.write_uleb128(type_section.get_item_index(ann.type))
      elems = ann.elements
      writer.write_uleb128(len(elems))
      for elem in elems:
        writer.write_uleb128(string_section.get_item_index(elem.name))
        self.write_encoded_value(writer, elem.value)    


  def write_annotation_sets(self, writer):
    writer.align()
    self.annotation_set_section_offset = writer.position
    if self.should_create_empty_annotation_set(): writer.write_int(0)

    annotation_set_section = self.get_section(SECTION_ANNOTATION_SET)
    for item in annotation_set_section.get_items():
      annotations = item.annotations
      writer.align()
      item.offset = writer.position
      writer.write_int(len(annotations))
      for annotation in annotations:
        writer.write_int(annotation.offset)

  
  def write_annotation_set_refs(self, writer, dex_pool):
    writer.align()
    self.annotation_set_ref_section_offset = writer.position
    interned = {}
    ann_section = self.get_section(SECTION_ANNOTATION_SET)

    for clazz in dex_pool:
      for method in clazz.methods:
        param_annotation = method.parameter_annotations
        if not param_annotation: continue
        prev = interned.get(param_annotation, -1)
        if prev != -1:
          param_annotation.offset = prev
          continue

        writer.align()
        position = writer.position
        param_annotation.offset = position
        interned[param_annotation] = position
        self.num_annotation_set_ref_items += 1
        writer.write_int(len(param_annotation))
        for ann in param_annotation:
          if ann.offset != NO_OFFSET:
            writer.write_int(ann.offset)
          elif self.should_create_empty_annotation_set():
            writer.write_int(self.annotation_set_section_offset)
          else:
            writer.write_int(NO_OFFSET)


          
    

  def write_annotation_directories(self, writer, dex_buf):
    writer.align()
    self.annotation_directory_section_offset = writer.position
    interned = {}
    tmp_buffer = bytearray(65536) # little endian
    field_section = self.get_section(SECTION_FIELD)
    method_section = self.get_section(SECTION_METHOD)
    annotation_set_section = self.get_section(SECTION_ANNOTATION_SET)

    for clazz in dex_buf:
      max_size = len(clazz.fields) * 8 + len(clazz.methods) * 16
      if max_size > 65536:
        tmp_buffer = bytearray(max_size)
      
      tmp_buffer = BufferStream(tmp_buffer)
      field_annotations = 0
      method_annotations = 0
      param_annotations = 0
      for field in clazz.fields:
        if field.annotations:
          field_annotations += 1
          tmp_buffer.write_int(field_section.get_item_index(field))
          tmp_buffer.write_int(field.annotations.offset)
          
      for method in clazz.methods:
        if method.annotations:
          method_annotations += 1
          tmp_buffer.write_int(method_section.get_item_index(method))
          tmp_buffer.write_int(method.annotations.offset)
      
      for method in clazz.methods:
        if method.annotation_set_ref_list_offset != NO_OFFSET:
          param_annotations += 1
          tmp_buffer.write_int(method_section.get_item_index(method))
          tmp_buffer.write_int(method.annotation_set_ref_list_offset)
      
      if field_annotations == 0 and method_annotations == 0 and param_annotations == 0:
        if clazz.annotations:
          dir_offset = interned.get(clazz.annotations, None)
          if dir_offset:
            clazz.annotation_dir_offset = dir_offset
            continue
          else:
            interned[clazz.annotations] = writer.position
        else:
          continue
      
      self.num_annotation_directory_items += 1
      clazz.annotation_dir_offset = writer.position
      writer.write_int(clazz.annotations.offset)
      writer.write_int(field_annotations)
      writer.write_int(method_annotations)
      writer.write_int(param_annotations)
      writer.write(tmp_buffer.buf[0:tmp_buffer.position])

  def write_encoded_value(self, writer, val):
    writer.write(val.as_byte())

  def get_magic(self, api_level):
    return 'DEX\n035' + '\x00'
  def write_header(self, writer, data_offset, file_size):
    writer.write(self.get_magic("opcodes.api"))
    writer.write_int(0) # checksum
    writer.write_arrays(bytearray(20))

    writer.write_int(file_size)
    writer.write_int(SIZE_HEADER_ITEM)
    writer.write_int(LITTLE_ENDIAN_TAG)

    writer.write_int(0) # link
    writer.write_int(0) # link

    writer.write_int(self.map_section_offset)

    self.write_section_info(writer, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_section_info(writer, self.get_section(SECTION_TYPE).size(), self.type_section_offset)
    self.write_section_info(writer, self.get_section(SECTION_PROTO).size(), self.proto_section_offset)
    self.write_section_info(writer, self.get_section(SECTION_FIELD).size(), self.field_section_offset)
    self.write_section_info(writer, self.get_section(SECTION_METHOD).size(), self.method_section_offset)
    self.write_section_info(writer, self.get_section(SECTION_CLASS).size(), self.class_index_section_offset)

    writer.write_int(file_size - data_offset)
    writer.write_int(data_offset)

  def write_section_info(self, writer, num_items, offset):
    writer.write_int(num_items)
    if num_items <= 0:
      offset = 0
    writer.write_int(offset)

  def update_signature(self):
    pass

  def update_checksum(self):
    pass
  def should_create_empty_annotation_set(self):
    return False # we don't make dex, just rebuild dex so assert dex is always valid.
    # if opcodes.api < 17, app will be crash before android 4.2