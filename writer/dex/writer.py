import struct
try:
  from dexassist.writer.multidex.multidex import DefaultMultiDexPolicy
  from dexassist.writer.dex.section import *
except:
  from writer.multidex.multidex import DefaultMultiDexPolicy
  from writer.dex.section import *

NO_INDEX = -1
NO_OFFSET = 0

# item type
HEADER_ITEM = 1
STRING_ID_ITEM = 1
TYPE_ID_ITEM = 1
PROTO_ID_ITEM = 1
FIELD_ID_ITEM = 1
METHOD_ID_ITEM = 1
CLASS_DEF_ITEM = 1
CALL_SITE_ID_ITEM = 1
METHOD_HANDLE_ITEM = 1
STRING_DATA_ITEM = 1
TYPE_LIST = 1
ENCODED_ARRAY_ITEM = 1
ANNOTATION_ITEM = 1
ANNOTATION_SET_ITEM = 1
ANNOTATION_SET_REF_LIST = 1
ANNOTATION_DIRECTORY_ITEM = 1
DEBUG_INFO_ITEM = 1
CODE_ITEM = 1
CLASS_DATA_ITEM = 1
MAP_LIST = 1

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
    ret += self.get_section[SECTION_STRING].get_item_count() * STRING_ID_ITEM_SIZE
    ret += self.get_section[SECTION_TYPE].get_item_count() * TYPE_ID_ITEM_SIZE
    ret += self.get_section[SECTION_PROTO].get_item_count() * PROTO_ID_ITEM_SIZE
    ret += self.get_section[SECTION_FIELD].get_item_count() * FIELD_ID_ITEM_SIZE
    ret += self.get_section[SECTION_METHOD].get_item_count() * METHOD_ID_ITEM_SIZE
    ret += self.get_section[SECTION_CLASS_DEF].get_item_count() * CLASS_DEF_ITEM_SIZE
    ret += self.get_section[SECTION_CALL_SITE].get_item_count() * CALL_SITE_ID_ITEM_SIZE
    ret += self.get_section[SECTION_METHOD_HANDLE].get_item_count() * METHOD_HANDLE_ITEM_SIZE
    return ret
  
  def build_class_def_section(self, dex_pool):
    section = ClassDefSection(self)
    clazz_list = set()
    for clazz in dex_pool:
      clazz_list.add(clazz)
    for clazz in clazz_list:
      section.add_item(clazz)
    self.section_map[SECTION_CLASS_DEF] = section
  
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
  
class HeaderWriter(object):
  def __init__(self):
    self.buf = bytearray(SIZE_HEADER_ITEM)
    buf[0] = 0x64 # d
    buf[1] = 0x65 # e
    buf[2] = 0x78 # x
    buf[3] = 0x0a # \n
    buf[4] = 0x30 # 0
    buf[5] = 0x33 # 3
    buf[6] = 0x35 # 5
    buf[7] = 0x00 # \0
  def set_dex_verison(self, version_int):
    if version_int == 35:
      self.buf[6] = 0x35
    if version_int == 37:
      self.buf[6] = 0x37
    if version_int == 38:
      self.buf[6] = 0x38
    if version_int == 39:
      self.buf[6] = 0x39
    return
  def write_checksum(self, checksum):
    self.write_array(8, checksum)
  def write_signature(self, signature):
    self.write_array(12, signature)
  def write_file_size(self, file_size):
    self.write_array(32, file_size)
  def write_header_size(self):
    self.write_int(36, 0x70)
  def write_endian_tab(self, endian_tag = 0x12345678):
    self.write_int(40, endian_tag)
  def write_section(self, section):
    section_header_size_offset = section.get_header_size_offset()
    section_header_offset_offset = section.get_header_offset_offset()
  

  def write_array(self, start_offset, value):
    pass
  def write_uint(self, start_offset, value):
    self.write_array(start_offset, struct.unpack('I', value)[0])


class DexWriter(object):
  def __init__(self, dex_class_pool):
    self.dex_class_pool = dex_class_pool
    self.multidex_policy = DefaultMultiDexPolicy()
    self.dex_pool_dict = {}
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
    manager = SectionManager()
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
    index_writer = OutputStream(buf, HEADER_SIZE)
    offset_writer = OutputStream(buf, data_section_offset)
    
    self.write_strings(index_writer, offset_writer)
    self.write_types(index_writer)
    self.write_type_lists(offset_writer)
    self.write_protos(index_writer)
    self.write_fields(index_writer)
    self.write_methods(index_writer)

    method_handle_writer = OutputStream(buf, index_writer.get_position() + 
      manager.get_section(SECTION_CLASS_DEF).get_item_count() * CLASS_DEF_ITEM_SIZE +
      manager.get_section(SECTION_CALL_SITE).get_item_count() * CALL_SITE_ITEM_SIZE
    )

    self.write_method_handles(method_handle_writer)
    method_handle_writer.close()

    self.write_encoded_arrays(offset_writer)
    call_site_writer = OutputStream(buf, index_writer.get_position() + 
      manager.get_section(SECTION_CLASS_DEF).get_item_count() * CLASS_DEF_ITEM_SIZE)
    self.write_call_sites(call_site_writer)
    call_site_writer.close()

    self.write_annotations(offset_writer)
    self.write_annotation_sets(offset_writer)
    self.write_annotation_set_refs(offset_writer)
    self.write_annotation_directories(offset_writer)
    self.write_debug_and_code_items(offset_writer, DeferredOutputStream())
    self.write_classes(index_writer, offset_writer)
    self.write_map_item(offset_writer)
    self.write_header(header_writer, data_section_offset, offset_writer.get_position())

    header_writer.close()
    index_writer.close()
    offset_writer.close()

    self.update_signature(buf)
    self.update_check_sum(buf)

  def write_strings(self, index_writer, offset_writer):
    index_section_offset = index_writer.get_position()
    data_section_offset = offset_writer.get_position()
    index = 0
    for item in self.get_section[SECTION_STRING].get_items():
      index_writer.write_int(offset_writer.get_position())
      string_val = item.get_value()
      offset_writer.write_uleb128(len(string_val))
      offset_writer.write_string(string_val)
      offset_writer.write(0)

  def write_types(self, index_writer):
    type_section_offset = index_writer.get_position()
    for item in self.get_section[SECTION_TYPE].get_items():
      index_writer.write_int(self.get_section[SECTION_STRING].get_item_index(
        item.get_value()
      ))

  def write_debug_and_code_items(self, offset_writer, deferred_stream):
    ehbuf = ByteArrayStream()
    debug_section_offset = offset_writer.get_position()
    # pass write debug section!
    code_writer = OutputStream(deferred_stream, 0)
    code_offsets = []
    for clazz in self.get_section[SECTION_CLASS_DEF].get_items():
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
    code_section_offset = offset_writer.get_position()
    code_writer.close()
    deferred_stream.write_to(offset_writer)
    deferred_stream.close()

  def write_code_item(self, code_writer, ehbuf, method, try_blocks, instructions, debug_item_offset):
    num_code_items += 1
    code_writer.align()
    code_item_offset = code_writer.get_position()
    code_writer.write_ushort(method.get_register_count())
    is_static = method.is_static()
    params = self.get_section(SECTION_TYPE_LIST).get_types(
      self.get_section(SECTION_PROTO).get_parameters(method.proto)
    )
    code_writer.write_ushort(
      self.get_param_register_count(params, is_static)
    )
    if istructions is None:
      code_writer.write_ushort(0)
      code_writer.write_ushort(0)
      code_writer.write_int(debug_item_offset)
      code_writer.write_int(0)
      return code_item_offset
    try_blocks = TryListBuilder.massage_try_blocks(try_blocks)
    out_param_count = 0
    code_unit_count = 0
    param_count = 0
    for ins in instructions:
      code_unit_count += ins.get_code_units()
      if ins.ref_type == ReferenceType.METHOD:
        method_ref = ins.ref
        opcode = ins.get_op()
        if InstructionUtil.is_invoke_polymorphic(opcode):
          param_count = ins.get_register_count()
        else:
          param_count = self.get_param_register_count(method_ref, InstructionUtil.is_invoke_static(opcode))

        if param_count > out_param_count: out_param_count = param_count

    code_writer.write_ushort(out_param_count)
    code_writer.write_ushort(len(try_blocks))
    code_writer.write_int(debug_item_offset)

    ins_writer = InstructionWriter.make_ins_writer(opcodes, code_writer, self.get_section(SECTION_STRING),
    self.get_section(SECTION_TYPE),
    self.get_seciton(SECTION_FIELD),
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
    DataWriter.write_uleb128(ehbuf, len(handler_map))

    for try_block in try_blocks:
      start_addr = try_block.get_start_addr()
      code_count = try_block.get_code_count()
      end_addr = start_addr + code_count

      code_writer.write_int(start_addr)
      code_writer.write_ushort(code_count)

      if len(try_block.get_exception_handlers()) == 0:
        raise Exception("try block has no exception handlers")
      
      offset = handler_map[try_block.get_exception_handlers()]
      if offset == 0:
        offset = ehbuf.get_position()
        handler_map[try_block.get_exception_handlers()] = offset
      writer.write_ushort(offset)

      eh_size = len(try_block.get_exception_handlers())
      eh_last = try_block.get_exception_handlers()[-1]
      if eh_last.get_exception_type() is None:
        eh_size = -eh_size + 1
      
      DataWriter.write_sleb128(ehbuf, eh_size)
      for eh in try_block.get_exception_handlers():
        exception_type = eh.get_exception_type()
        code_addr = eh.get_handler_addr()
        if exception_type is not None:
          # regular
          DataWriter.write_uleb128(ehbuf, self.get_section(SECTION_TYPE).get_item_index(exception_type))
          DataWriter.write_uleb128(ehbuf, code_addr)
        else:
          #catch(Throwable)
          DataWriter.write_uleb128(ehbuf, code_addr)
    if ehbuf.size() > 0:
      code_writer.write_stream(ehbuf)
      ehbuf.reset()

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
    map_section_offset = offset_writer.get_position()
    num_items = self.calc_map_list_item_count()
    offset_writer.write_int(num_items)

    self.write_map_item_object(offset_writer, HEADER_ITEM, 1, 0)
    self.write_map_item_object(offset_writer, STRING_ID_ITEM, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_map_item_object(offset_writer, TYPE_ID_ITEM, self.get_section(SECTION_TYPE).size(), self.string_index_section_offset)
    self.write_map_item_object(offset_writer, PROTO_ID_ITEM, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_map_item_object(offset_writer, FIELD_ID_ITEM, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_map_item_object(offset_writer, METHOD_ID_ITEM, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_map_item_object(offset_writer, CLASS_DEF_ITEM, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_map_item_object(offset_writer, CALL_SITE_ID_ITEM, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_map_item_object(offset_writer, METHOD_HANDLE_ITEM, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)

    # data section
    self.write_map_item_object(offset_writer, STRING_DATA_ITEM, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_map_item_object(offset_writer, TYPE_LIST, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_map_item_object(offset_writer, ENCODED_ARRAY_ITEM, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_map_item_object(offset_writer, ANNOTATION_ITEM, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_map_item_object(offset_writer, ANNOTATION_SET_ITEM, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_map_item_object(offset_writer, ANNOTATION_SET_REF_ITEM, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_map_item_object(offset_writer, ANNOTATION_DIRECTORY_ITEM, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_map_item_object(offset_writer, DEBUG_INFO_ITEM, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_map_item_object(offset_writer, CODE_ITEM, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_map_item_object(offset_writer, CLASS_DATA_ITEM, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_map_item_object(offset_writer, MAP_LIST, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)

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
        writer.write_ushort(self.get_section(SECTION_TYPE_LIST).get_item_index(item))


  def write_protos(self):
    self.proto_section_offset = writer.position
    index = 0
    for item in self.get_section(SECTION_PROTO).get_items():
      writer.write_int(
        self.get_section(SECTION_STRING).get_item_index(
          item.get_shorty()
        )
      )
      writer.write_int(
        self.get_section(SECTION_TYPE).get_item_index(
          item.get_return_type()
        )
      )
      writer.write_int(
        self.get_section(SECTION_TYPE_LIST).get_item(
          item.get_parameters()
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
      writer.write_ushort(proto_Section.get_item_index(x.proto))
      writer.write_int(string_section.get_item_index(x.name))

    
  def write_classes(self, index_writer, offset_writer):
    self.class_index_section_offset = index_writer.position
    self.class_data_section_offset = offset_writer.position

    class_section = self.get_section(SECTION_CLASS)
    index = 0
    for x in class_section.get_items():
      index = self.write_class(index_writer, offset_writer, index, x)

  def write_class(self, index_writer, offset_writer, index, clazz):
    if clazz in None: return index # not in dex
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
      writer.write_uleb128(index - prev_index)
      writer.write_uleb128(method.access_flags)
      writer.write_uleb128(method.code_item_offset)
      prev_index = index

  def write_call_sites(self):
    pass # skip

  def write_method_handles(self):
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
    annotation_section = self.get_seciton(SECTION_ANNOTATION)
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


          
    

  def write_annotation_directories(self):
    pass


  def write_header(self, writer, data_offset, file_size):
    writer.write(self.get_magic(opcodes.api))
    writer.write_int(0) # checksum
    writer.write_arrays(bytearray(20))

    writer.write_int(file_size)
    writer.write_int(HEADER_SIZE)
    writer.write_int(LITTLE_ENDIAN_TAG)

    writer.write_int(0) # link
    writer.write(int(0) # link

    writer.write_int(self.map_section_offset)

    self.write_section_info(writer, self.get_section(SECTION_STRING).size(), self.string_index_section_offset)
    self.write_section_info(writer, self.get_section(SECTION_TYPE).size(), self.type_section_offset)
    self.write_section_info(writer, self.get_section(SECTION_PROTO).size(), self.proto_section_offset)
    self.write_section_info(writer, self.get_section(SECTION_FIELD).size(), self.field_section_offset)
    self.write_section_info(writer, self.get_section(SECTION_METHOD).size(), self.method_section_offset)
    self.write_section_info(writer, self.get_section(SECTION_CLASS).size(), self.class_section_offset)

    writer.write_int(file_size - self.data_offset)
    writer.write_int(self.data_offset)

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