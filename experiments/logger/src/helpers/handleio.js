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
    let instance_stats = []
    let total_req_count = 0;
    let last_reported_req_count = 0;
    for (let i in im.experiment_logs[exp_name]) {
      let o = im.experiment_logs[exp_name][i]
      if(o.service_time_hists){
        o.service_time_hists.forEach((v) => {
          total_req_count += v.count
        })
      }
      if(o.latest_service_time_hist){
        last_reported_req_count = o.latest_service_time_hist.count
      }
      instance_stats.push({
        instance_id: i,
        total_req_count,
        last_reported_req_count,
      })
    }
    res.send({
      instance_stats,
    })
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


module.exports = function (app) {
  initializeUsingApp(app)
  return router
}
