// A simple concurrency testing script that will make concurrent request to the web server

// library imports
const axios = require('axios');

const postData = {
    "cmds": {
        "sleep": 0,
        "sleep_till": 0,
        "run": {
            "cmd": "ls"
        },
        "cpu": {
            "n": 10000
        },
        "io": {
            "rd": 3,
            "size": "1M",
            "cnt": 5
        },
        "stat": {
            "argv": 1
        }
    }
}


// send a single request to the server
const sendRequest = async () => {
    const res = await axios.post("http://localhost:8080", postData)
    return res.data;
}

const sendBatchRequest = async (conc) => {
    console.log(`Sending ${conc} requests...`)

    const reqs = []
    for(let i=0; i<conc; i++) {
        reqs.push(sendRequest())
    }

    await Promise.all(reqs)

    console.log('done!')
}


console.log('Starting the test...')
sendBatchRequest(5)


