
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

class DexWriter(object):
  def __init__(self, dex_class_pool):
    self.dex_class_pool = dex_class_pool
    self.multidex_policy = DefaultMultiDexPolicy()
    self.dex_pool_dict = {}
  def calc_multidex(self):
    for clazz in self.dex_class_pool:
      index = self.multidex_policy.get_multidex_index(clazz)
      if index not in self.dex_pool_dict:
        self.dex_pool_dict[index] = []
      self.dex_pool_dict[index].append(clazz)

  def build_dex(self, dex_pool):
    string_table = self.get_string_table(dex_pool)
  
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