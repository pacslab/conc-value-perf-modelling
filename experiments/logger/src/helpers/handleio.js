const express = require('express')
const router = new express.Router()

// application configurations
const config = require('../config')
const im = require('./instance_manager')

// app and io placeholder before being initialized
var app
var io

// get logger info
const logger = global.logger

initializeUsingApp = (_app) => {
  app = _app
  io = app.io

  io.on('connection', (socket) => {
    logger.info('a user connected');
    let client_info

    socket.on('conn_client_info', (msg) => {
      client_info = msg
      im.recordConnection(socket, msg)
    })

    socket.on('disc_client_info', (msg) => {
      im.recordKilled(socket, msg)
    })

    socket.on('routine_report', (msg) => {
      // console.log('routine report:')
      // console.log(msg)
      im.recordRoutineReport(msg)
    })

    socket.on('disconnect', () => {
      // if we have already received client's info
      if (client_info) {
        im.recordDisconnection(socket, client_info)
      }
    });
  });

  logger.info('SocketIO server started')
}

// expose the logs on the web server
router.get('/logger/experiment_logs/:exp_name/stats', (req, res) => {
  const exp_name = req.params.exp_name
  if (im.experiment_logs[exp_name]) {
    const result = im.getExperimentStats(exp_name)
    res.send(result)
  } else {
    res.status(404).send({
      err: 'Page Not Found!',
    })
  }
})

// expose the logs on the web server
router.get('/logger/experiment_logs/:exp_name', (req, res) => {
  const exp_name = req.params.exp_name
  if (im.experiment_logs[exp_name]) {
    res.send(im.experiment_logs[exp_name])
  } else {
    res.status(404).send({
      err: 'Page Not Found!',
    })
  }
})

// expose the logs on the web server
router.get('/logger/experiment_logs', (req, res) => {
  const result = Object.keys(im.experiment_logs).map((k) => {
    return {
      name: k,
      logs: `/logger/experiment_logs/${k}`,

    }
  })

  res.send(result)
})

// allow clearing the data
router.get('/logger/clear', (req, res) => {
  for (let exp_name in im.experiment_logs) {
    for (let node_id in im.experiment_logs[exp_name]) {
      // remove node if already killed
      if (im.experiment_logs[exp_name][node_id].kill_time) {
        delete(im.experiment_logs[exp_name][node_id])
      }
      else {
        for (let field of ['conc_hists', 'service_time_hists', 'latest_service_time_hist', 'latest_conc_hist']) {
          delete(im.experiment_logs[exp_name][node_id][field])
        }
      }
    }
  }
  res.send('OK')
})


module.exports = function (app) {
  initializeUsingApp(app)
  return router
}
