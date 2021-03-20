# Autoscale-Go

- Information: https://knative.dev/docs/serving/autoscaling/autoscale-go/
- Docker Image: gcr.io/knative-samples/autoscale-go:0.1

Sample Deployment:

```sh
git clone https://github.com/knative/docs knative-docs
cd knative-docs
kubectl apply --filename docs/serving/autoscaling/autoscale-go/service.yaml
```

Getting the url:

```command
$ kubectl get ksvc autoscale-go
NAME            URL                                                LATESTCREATED         LATESTREADY           READY   REASON
autoscale-go    http://autoscale-go.default.1.2.3.4.xip.io    autoscale-go-96dtk    autoscale-go-96dtk    True
```

Sample execution using curl:

```sh
curl "http://autoscale-go.default.1.2.3.4.xip.io?sleep=100&prime=10000&bloat=5"
```
