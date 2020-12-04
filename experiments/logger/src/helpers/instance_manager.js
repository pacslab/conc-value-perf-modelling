
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

  if(client.conc_hists) { // update
    client.conc_hists.push(conc_histogram)
  } else { // create new one
    client.conc_hists = [ conc_histogram ]
  }

  if(client.service_time_hists) { // update
    client.service_time_hists.push(service_time_hist)
  } else { // create new one
    client.service_time_hists = [ service_time_hist ]
  }
}


module.exports = {
    experiment_logs,
    recordConnection,
    recordDisconnection,
    recordKilled,
    recordRoutineReport,
}
