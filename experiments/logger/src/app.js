
"use strict"

const http = require('http')
const express = require('express')
const socketio = require('socket.io')

const winston = require('winston')
const myformat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp(),
  winston.format.align(),
  winston.format.printf(info => `${info.timestamp} ${info.level}: ${info.message}`)
);
const consoleTransport = new winston.transports.Console({
  format: myformat
})
const myWinstonOptions = {
  transports: [consoleTransport]
}
const logger = new winston.createLogger(myWinstonOptions)

// configurations
const config = require('./config')

// create app and set port
const app = express()
const server = http.createServer(app)
const io = socketio(server)
app.io = io
app.logger = logger
global.logger = logger
const port = process.env.PORT || 3000

// Parse incoming json
app.use(express.json())

// Parse form data
const bodyParser = require('body-parser')
app.use(bodyParser.urlencoded({ extended: true }))

// CORS
const cors = require('cors')
app.use(cors())

// add routers
const handleioRouter = require('./helpers/handleio')(app)
app.use(handleioRouter)

// Home Page
app.get('', (req, res) => {
  res.send({
    "msg": "this is a test!",
  })
})

// 404 Page
app.get('*', (req, res) => {
  res.status(404).send({
    "err": "not found!",
  })
})

server.listen(port, () => {
  console.log(`\nServer is up:\n\n\thttp://localhost:${port}\n\n`)
})
