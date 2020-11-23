
"use strict"

const http = require('http')
const express = require('express')
const socketio = require('socket.io')

// configurations
const config = require('./config')

// create app and set port
const app = express()
const server = http.createServer(app)
const io = socketio(server)
const port = process.env.PORT || 3000

// Parse incoming json
app.use(express.json())

// Parse form data
const bodyParser = require('body-parser')
app.use(bodyParser.urlencoded({ extended: true }))

// CORS
const cors = require('cors')
app.use(cors())

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

io.on('connection', (socket) => {
  console.log('a user connected');
  socket.on('disconnect', () => {
    console.log('user disconnected');
  });
});

app.listen(port, () => {
  console.log(`\nServer is up:\n\n\thttp://localhost:${port}\n\n`)
})
