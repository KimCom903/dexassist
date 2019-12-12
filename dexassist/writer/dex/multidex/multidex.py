
class MultiDexPolicy(object):
  def get_multidex_name(self, index):
    raise Exception('get_multidex_name not implemented')
  def get_multidex_index(self, clazz):
    raise Exception('get_multidex_index not implemented')

class DefaultMultiDexPolicy(MultiDexPolicy):
  def __init__(self):
    self.method_count = 0
    self.string_count = 0
    self.index = 1
  def next_dex(self):
    self.method_count = 0
    self.string_count = 0
    self.index += 1
  def get_multidex_name(self, index):
    return 'classes.dex' if index == 1 else 'classes{}.dex'.format(index)

  def get_multidex_index(self, clazz):
    clazz_method_count = len(clazz.methods)
    clazz_string_count = len(clazz.get_ref_strings())
    if self.method_count + clazz_method_count >= 65535:
      self.next_dex()
    if self.string_count + clazz_string_count >= 65535:
      self.next_dex()
    self.method_count += clazz_method_count
    self.string_count += clazz_string_count

    return self.index