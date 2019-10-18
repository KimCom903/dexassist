
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
from writer.multidex import DefaultMultiDexPolicy

class DefaultDexWriteStream(object):
  def write_stream(stream):
    pass

class Section(object):
  def get_item(self, value):
    """
    return value of id
    """
    raise Exception('get_item not implemented')
  def get_id(self, value):
    """
    return id of value
    """
    raise Exception('get_id not implemented')
  def add_item(self, value):
    raise Exception('add_item not implemented')
  def get_header_size_offset(self):
    return 0
  def get_header_offset_offset(self):
    return 0

class DataSection(Section):
  def __init__(self):
    self.last_offset = 0
    self.buf = bytearray()
  def write_item(self, item):
    item_byted = item.as_bytes()
    self.buf.extend(item_byted)
    self.last_offset += item_byted
    return self.last_offset

class StringSection(Section):
  def __init__(self, data_section):
    self.string_map = {}
    self.index = 0
    self.data_section = data_section
  def add_item(self, value):
    # decode mutf8
    self.string_map[value] = self.index # set id
    self.index += 1
    # write data_section

  
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
  def calc_multidex(self):
    for clazz in self.dex_class_pool:
      clazz.fix()
      index = self.multidex_policy.get_multidex_index(clazz)
      if index not in self.dex_pool_dict:
        self.dex_pool_dict[index] = []
      self.dex_pool_dict[index].append(clazz)
    for dex_pool_index in self.dex_class_pool:
      build_dex(self.dex_class_pool[dex_pool_index], self.write_stream)

  def build_dex(self, dex_pool, write_stream):
    string_table = self.get_string_table(dex_pool)
    type_table = self.get_type_table(dex_pool)
    proto_table = self.get_proto_table(dex_pool)
    header = bytearray(SIZE_HEADER_ITEM)

    
  
  def get_type_table(self, dex_pool):
    type_pool = set()
    for clazz in dex_pool:
      type_pool.add(clazz.get_type_as_descriptor())
      type_pool.update([x.get_type_as_descriptor() for x in clazz.annotations])

      for method in clazz.methods:
        type_pool.add(method.get_type_as_descriptor())
        type_pool.update([x.get_type_as_descriptor() for x in method.annotations])

      for field in clazz.fields:
        type_pool.add(field.get_type_as_descriptor())
        type_pool.update([x.get_type_as_descriptor() for x in field.annotations])
    return type_pool

  def get_proto_table(self, dex_pool):
    proto_pool = set()
    for clazz in dex_pool:
      proto_pool.update([m.get_proto() for m in clazz.methods])
    return proto_pool

  def get_string_table(self, dex_pool):
    string_pool = set()
    for clazz in dex_pool:
      #string_pool.update(clazz.get_type_as_string())
      #string_pool.update([x.get_signature() for x in clazz.methods])
      #string_pool.update([x.get_name() for x in clazz.methods])

      #string_pool.update([x.get_signature() for x in clazz.fields])
      #string_pool.update([x.get_name() for x in clazz.fields])
      string_pool.update(x.get_ref_strings())
    return string_pool


  def write_strings(self):
    pass

  def write_types(self):
    pass

  def write_type_lists(self):
    pass

  def write_protos(self):
    pass

  def write_fields(self):
    pass

  def write_methods(self):
    pass

  def write_method_handles(self):
    pass

  def write_method_arrays(self):
    pass

  def write_call_sites(self):
    pass

  def write_annotations(self):
    pass

  def write_annotation_sets(self):
    pass

  def write_annotation_set_refs(self):
    pass

  def write_annotation_directories(self):
    pass

  def write_debug_code_items(self):
    pass

  def write_classes(self):
    pass

  def write_map_item(self):
    pass

  def write_header(self):
    pass

  def update_signature(self):
    pass

  def update_checksum(self):
    pass