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
      console.log('routine report:')
      console.log(msg)
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
router.get('/logger/experiment_logs', (req, res) => {
  res.send(im.experiment_logs)
})


module.exports = function (app) {
  initializeUsingApp(app)
  return router
}
