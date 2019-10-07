import normalize

class DexConverter(object):
  def get_dex(self, header, manager):
    dex = normalize.Dex()
    for x in manager.class_def_list:
      dex.add_class(self.create_dex_class(x, manager))
    return dex
  def extract_from_annotation_set_item(self, parent, manager, annotation_set_item):
    ret = []
    for entry in annotation_set_item.entries:
      annotation_item = entry.annotation_off_item.annotation
      visibility = annotation_item.visibility
      type_idx = annotation_item.annotation.type_idx
      elements = []
      type_name = manager.string_list[type_idx]
      for x in range(annotation_item.annotation.size):
        name_idx = annotation_item.annotation.elements[x].name_idx
        value = annotation_item.annotation.elements[x].value
        elements.append((manager.string_list[name_idx],
            value.value
        ))
    ret.append(
      normalize.DexAnnotation(parent, visibility, type_name, elements)
    )

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
            annotation = self.extract_from_annotation_set_item(manager.method_list[param_annotation.method_idx], manager, method_annotation.annotation)
          param_annotation_table[param_annotation.method_idx].append(annotation)


    field_idx = 0
    for f in cdi.data.static_fields:
      field_idx += f.field_idx_diff
      access_flags = f.access_flags
      field_name = manager.string_list[field_idx]
      f = self.create_dex_field(item, field_name, access_flags)
      f.annotations = field_annotation_table.get(field_idx, [])
      item.fields.append(f)
    field_idx = 0
    for f in cdi.data.instance_fields:
      field_idx += f.field_idx_diff
      access_flags = f.access_flags
      field_name = manager.string_list[field_idx]
      f = self.create_dex_field(item, field_name, access_flags)
      f.annotations = field_annotation_table.get(field_idx, [])
      item.fields.append(f)

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
      x = self.create_dex_method(item, method_name, access_flags, method_signature, code)
      x.annotations = method_annotation_table.get(method_idx, [])
      x.param_annotations = param_annotation_table.get(method_idx, [])
      item.methods.append(x)
    
    method_idx = 0
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
      x = self.create_dex_method(item, method_name, access_flags, method_signature, code)
      x.annotations = method_annotation_table.get(method_idx, [])
      x.param_annotations = param_annotation_table.get(method_idx, [])
      item.methods.append(x)    


    return item
    
  #ef : encodedfield
  def create_dex_field(self, parent, type_name, access_flags):
    f = normalize.DexField(parent, type_name, access_flags)
    return f

  def create_dex_method(self, parent, method_name, access_flags, signature, code):
    pass

