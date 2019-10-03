import normalize

class DexConverter(object):
  def get_dex(self, header, manager):
    dex = normalize.Dex()
    for x in manager.class_def_list:
      dex.add_class(self.create_dex_class(x, manager))
    return dex

  #cdi : class_def_item
  def create_dex_class(self, cdi, manager):
    item = normalize.DexClassItem()
    item.type = manager.type_list[cdi.class_idx]
    item.access_flags = cdi.access_flags
    item.superclass = manager.type_list[cdi.superclass_idx]
    item.interfaces = [manager.type_list[x] for x in cdi.interfaces]
    if cdi.source_file_idx:
      item.source_file_name = cdi.string_list[cdi.source_file_idx]
    if cdi.static_values:
      item.static_values = [x.value for x in cdi.static_values.value.values]
    field_idx = 0
    for f in cdi.data.static_fields:
      field_idx += f.field_idx_diff
      access_flags = f.access_flags
      item.fields.append(
          self.create_dex_field(item, field_idx, access_flags)
      )
    field_idx = 0
    for f in cdi.data.instance_fields:
      field_idx += f.field_idx_diff
      access_flags = f.access_flags
      field_name = manager.string_list[field_idx]
      item.fields.append(
          self.create_dex_field(item, field_name, access_flags)
      )

    method_idx = 0
    for m in cdi.data.direct_methods:
      method_idx += m.method_idx_diff
      method_item = manager.method_list[method_idx]
      class_idx = method_item.class_idx
      proto_idx = method_item.proto_idx
      name_idx = method_item.name_idx

      method_name = manager.string_list[name_idx]
      proto = manager.string_list[proto_idx]
      access_flags = m.access_flags
      code = m.code
      method_signature_idx = proto.shorty_idx
      method_signature = manager.string_list[method_signature_idx]
      item.methods.append(
          self.create_dex_method(item, method_name, access_flags, method_signature, code)
      )
    
    for m in cdi.data.virtual_methods:
      method_idx += m.method_idx_diff
      method_item = manager.method_list[method_idx]
      class_idx = method_item.class_idx
      proto_idx = method_item.proto_idx
      name_idx = method_item.name_idx

      method_name = manager.string_list[name_idx]
      proto = manager.string_list[proto_idx]
      access_flags = m.access_flags
      code = m.code
      method_signature_idx = manager.proto_list[m.proto_idx].shorty_idx
      method_signature = manager.string_list[method_signature_idx]
      item.methods.append(
          self.create_dex_method(item, method_name, access_flags, method_signature, code)
      )
    


    return item
    
  #ef : encodedfield
  def create_dex_field(self, parent, type_name, access_flags):
    pass

  def create_dex_method(self, parent, method_name, access_flags, signature, code):
    pass

