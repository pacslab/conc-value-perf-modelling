# Workloads for Testing Performance Model

This folder includes workloads used for testing performance models. We used a set of
configurable benchmarks with different types of workload integrated in them. Thus, by modifying
the requests made to each benchmark set, we can get a range of workloads that are a combination
of different types of tasks common in serverless computing. Here are a list of the benchmarks
used in this work:

- [Bench1](./bench1/)
- [Autoscale-Go](./autoscale-go/)

## List of Workloads

Here is a list of workloads used in this study:

| Workload | Benchmarks | Parameters | RPS? |
|----------|------------|------------|------|
| Workload1 | Bench1 | sleep_base=1000, sleep_rand=200 | No |
| Workload2 | Autoscale-Go | sleep=500, prime=10000, bloat=5 | No |
| Workload3 | Autoscale-Go | sleep=500, prime=10000, bloat=5 | Yes |
| Workload4 | Bench1 | io={"rd": 3, "size": "200K", "cnt": 2}, <br> cpu=10000, sleep=1000 | Yes |

## References

- [“Shutdown Signals with Docker Entry-point Scripts” by Benjamin Cane](https://link.medium.com/gIUHyPHzzbb)
- [Google CloudRun: Container Runtime Contract](https://cloud.google.com/run/docs/reference/container-contract)
