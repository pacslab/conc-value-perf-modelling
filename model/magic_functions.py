
from concperf import general_model

def parse_arrival_rate(arrival_rate, model_config, update_config):
    config = {**model_config}
    config.update({
        'arrival_rate_total': arrival_rate,
    })
    res = general_model.solve_general_model(config, update_config)
    res_params = general_model.calculate_general_params(res, config)
    res.update(res_params)
    res.update(config)
    return res

