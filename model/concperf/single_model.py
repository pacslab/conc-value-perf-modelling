import itertools
import numpy as np

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


# calculate Q for states
def get_single_container_q(single_coder, config):
    state_count = single_coder.get_state_count()
    Q = np.zeros((state_count, state_count))

    def encode_state(req_count):
        return (req_count,)

    # for each source state calculate rate of destination state
    for from_state in single_coder.get_state_list():
        from_state_idx = single_coder.to_idx(from_state)
        # decode the state
        (from_req_count, ) = from_state
        # rate of exiting this state
        exit_rate = 0
        # one count below
        if from_req_count > 0:
            to_req_count = from_req_count - 1
            to_state = encode_state(to_req_count)
            to_state_idx = single_coder.to_idx(to_state)
            Q[from_state_idx, to_state_idx] = from_req_count / \
                (1+(from_req_count - 1) *
                 config['alpha']) / config['base_service_time']
            exit_rate += Q[from_state_idx, to_state_idx]
        if from_req_count < config['max_conc']:
            to_req_count = from_req_count + 1
            to_state = encode_state(to_req_count)
            to_state_idx = single_coder.to_idx(to_state)
            Q[from_state_idx, to_state_idx] = config['arrival_rate_server']
            exit_rate += Q[from_state_idx, to_state_idx]

        Q[from_state_idx, from_state_idx] = -1 * exit_rate

    return Q
