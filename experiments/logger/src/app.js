
"use strict"

const express = require('express')
const config = require('./config')

// create app and set port
const app = express()
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

app.listen(port, () => {
  console.log(`Server is up on port ${port}: http://localhost:${port}`)
})
