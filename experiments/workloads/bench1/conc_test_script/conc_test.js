// A simple concurrency testing script that will make concurrent request to the web server

// library imports
const axios = require('axios');
const yargs = require('yargs/yargs')
const { hideBin } = require('yargs/helpers')

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


// process arguments using yargs
console.log('Usage: node conc_test.js --path WORKLOAD_PATH -c CONC_REQUEST_COUNT')
const argv = yargs(hideBin(process.argv))
    .option('path', {
        alias: 'p',
        description: 'The server to send the requests to',
        type: 'string',
        default: 'http://localhost:8080',
    })
    .option('count', {
        alias: 'c',
        description: 'How many requests at the same time?',
        type: 'number',
    })
    .demandOption(['count'], 'Please specify count.')
    .argv

console.log(`sending ${argv.count} requests to path: ${argv.path}\n`)

// send a single request to the server
const sendRequest = async () => {
    const res = await axios.post(argv.path, postData)
    return res.data;
}

const sendBatchRequest = async (conc) => {
    console.log(`Sending ${conc} requests...`)

    const reqs = []
    for (let i = 0; i < conc; i++) {
        reqs.push(sendRequest())
    }

    await Promise.all(reqs)

    console.log('done!')
}


console.log('Starting the test...')
sendBatchRequest(argv.count)


