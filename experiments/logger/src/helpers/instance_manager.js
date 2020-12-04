
// get logger info
const logger = global.logger

const experiment_logs = {}

const getExp = (exp_name) => {
  let experiment_obj = experiment_logs[exp_name]
  if (!experiment_obj) {
    experiment_obj = {}
    experiment_logs[exp_name] = experiment_obj
  }

  return experiment_obj
}

const getClient = (exp_name, client_uuid) => {
  exp = getExp(exp_name)

  let client_obj = exp[client_uuid]
  if (!client_obj) {
    client_obj = {}
    exp[client_uuid] = client_obj
  }

  return client_obj
}

const recordConnection = (socket, clientInfo) => {
  const { client_uuid, experiment_name } = clientInfo

  logger.info(`${experiment_name}: Client connected: ${client_uuid}`)

  client = getClient(experiment_name, client_uuid)
  // update socket id
  client.socket_id = socket.id
  // record init time if it is not a reconnection
  if (!client.init_time) {
    client.init_time = Date.now()
  }
}

const recordDisconnection = (socket, clientInfo) => {
  const { client_uuid, experiment_name } = clientInfo

  logger.info(`${experiment_name}: Client disconnected: ${client_uuid}`)

  client = getClient(experiment_name, client_uuid)
  // record init time if it is not a reconnection
  client.disconnect_time = Date.now()
}

const recordKilled = (socket, clientInfo) => {
  const { client_uuid, experiment_name } = clientInfo

  logger.info(`${experiment_name}: Client killed: ${client_uuid}`)

  client = getClient(experiment_name, client_uuid)
  // record init time if it is not a reconnection
  client.kill_time = Date.now()
}

const recordRoutineReport = (msg) => {
  const { client_info, conc_histogram, service_time_hist } = msg
  const report_time = Date.now()

  const { client_uuid, experiment_name } = client_info

  logger.info(`${experiment_name}: Client Reported: ${client_uuid}`)

  client = getClient(experiment_name, client_uuid)

  // update objects with timestamps
  conc_histogram.report_time = report_time
  service_time_hist.report_time = report_time

  // update latest values
  client.latest_conc_hist = conc_histogram
  client.latest_service_time_hist = service_time_hist

  if (client.conc_hists) { // update
    client.conc_hists.push(conc_histogram)
  } else { // create new one
    client.conc_hists = [conc_histogram]
  }

  if (client.service_time_hists) { // update
    client.service_time_hists.push(service_time_hist)
  } else { // create new one
    client.service_time_hists = [service_time_hist]
  }
}

const getExperimentStats = (exp_name) => {
  let instance_stats = []
  let total_req_count = 0;
  let total_last_report_req_count = 0;
  let total_service_time_hist = {};
  let total_conc_hist = {};

  // loop through instances
  for (let i in experiment_logs[exp_name]) {
    let o = experiment_logs[exp_name][i]
    let last_reported_req_count = 0;
    let inst_total_req_count = 0;
    let inst_service_time_hist = {};
    let inst_conc_hist = {};
    if (o.service_time_hists) {
      o.service_time_hists.forEach((v) => {
        inst_total_req_count += v.count
        for (let idx = 0; idx < v.service_time_values.length; idx++) {
          if (!inst_service_time_hist[v.service_time_values[idx]]) {
            inst_service_time_hist[v.service_time_values[idx]] = 0
          }

          if (!total_service_time_hist[v.service_time_values[idx]]) {
            total_service_time_hist[v.service_time_values[idx]] = 0
          }

          inst_service_time_hist[v.service_time_values[idx]] += v.service_time_times[idx]
          total_service_time_hist[v.service_time_values[idx]] += v.service_time_times[idx]
        }
      })
    }
    if (o.conc_hists) {
      o.conc_hists.forEach((v) => {
        for (let idx = 0; idx < v.conc_values.length; idx++) {
          if (!inst_conc_hist[v.conc_values[idx]]) {
            inst_conc_hist[v.conc_values[idx]] = 0
          }

          if (!total_conc_hist[v.conc_values[idx]]) {
            total_conc_hist[v.conc_values[idx]] = 0
          }

          inst_conc_hist[v.conc_values[idx]] += v.conc_times[idx]
          total_conc_hist[v.conc_values[idx]] += v.conc_times[idx]
        }
      })
    }
    if (o.latest_service_time_hist) {
      last_reported_req_count = o.latest_service_time_hist.count
    }

    // perform aggregation tasks
    total_last_report_req_count += last_reported_req_count
    total_req_count += inst_total_req_count

    // push instance stats
    instance_stats.push({
      instance_id: i,
      last_req_count: last_reported_req_count,
      total_req_count: inst_total_req_count,
      service_time_hist: {
        x: Object.keys(inst_service_time_hist).map(Number),
        y: Object.values(inst_service_time_hist).map(Number),
      },
      conc_hist: {
        x: Object.keys(inst_conc_hist).map(Number),
        y: Object.values(inst_conc_hist).map(Number),
      },
    })
  }

  return {
    instance_stats,
    total_req_count,
    total_last_report_req_count,
    service_time_hists: {
      x: Object.keys(total_service_time_hist).map(Number),
      y: Object.values(total_service_time_hist).map(Number),
    },
    conc_hists: {
      x: Object.keys(total_conc_hist).map(Number),
      y: Object.values(total_conc_hist).map(Number),
    },
  }
}


module.exports = {
  experiment_logs,
  recordConnection,
  recordDisconnection,
  recordKilled,
  recordRoutineReport,
  getExperimentStats,
}
