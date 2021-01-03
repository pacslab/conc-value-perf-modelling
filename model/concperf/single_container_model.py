import itertools

# generate states and encode/decode between idx and state
class StateCoder:
  def __init__(self, config, ):
    self.state_list = StateCoder.generate_state_list(config['max_conc'])

  # Generate State List
  @staticmethod
  def generate_state_list(max_conc):
    cont_counts = list(range(max_conc + 1))
    state_list = list(itertools.product(cont_counts, ))
    return state_list

  # Encode State to idx
  def to_idx(self, state):
    idx = self.state_list.index(state)
    if idx < 0:
      raise ValueError('state not found')

    return idx

  # Decode State from idx to state
  def to_state(self, idx):
    return self.state_list[idx]

  def get_state_list(self):
    return self.state_list

  def get_state_count(self):
    return len(self.state_list)

  def get_state_name_list(self):
    return [f"{s[0]},{s[1]},{s[2]}" for s in self.state_list]

