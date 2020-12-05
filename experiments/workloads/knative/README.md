# Knative Installation

source: https://dev.to/jonatasbaldin/three-solutions-to-run-knative-locally-5615

## Change Hostname

```sh
sudo hostnamectl set-hostname cy1
sudo reboot
```

## Install Kubernetes and Development Basics

```sh
# install docker
curl -sSL  https://nimamahmoudi.github.io/cicd-cheatsheet/sh/install-docker.sh | bash
# install docker-compose
sudo apt-get update && sudo apt install -qy python3-pip && pip3 install docker-compose

# install arkade
curl -SLfs https://dl.get-arkade.dev | sudo sh
echo "export PATH=\$HOME/.arkade/bin:\$PATH" >> ~/.bashrc
arkade completion bash > ~/.arkade_bash_completion.sh
echo "source ~/.arkade_bash_completion.sh" >> ~/.bashrc
source ~/.bashrc

# install kubernetes basics
arkade get kubectl
echo 'source <(kubectl completion bash)' >>~/.bashrc
arkade get kustomize
arkade get helm
arkade get k3sup
# kompose
curl -L https://github.com/kubernetes/kompose/releases/download/v1.22.0/kompose-linux-amd64 -o kompose
chmod +x kompose
sudo mv ./kompose /usr/local/bin/kompose
echo 'source <(kompose completion bash)' >>~/.bashrc
source ~/.bashrc

# install k3s
mkdir ~/.kube
k3sup install --local --k3s-channel stable --local-path ~/.kube/config --k3s-extra-args '--no-deploy traefik --write-kubeconfig-mode 644'
```

## Install Knative

```sh
export KNATIVE_VERSION="0.19.0"
export KUBECONFIG="/home/ubuntu/.kube/config"

# Install Knative Serving
kubectl apply --filename "https://github.com/knative/serving/releases/download/v$KNATIVE_VERSION/serving-crds.yaml"
kubectl apply --filename "https://github.com/knative/serving/releases/download/v$KNATIVE_VERSION/serving-core.yaml"

# Configure the magic xip.io DNS name
kubectl apply --filename "https://github.com/knative/serving/releases/download/v$KNATIVE_VERSION/serving-default-domain.yaml"

# Install and configure Kourier
kubectl apply --filename https://raw.githubusercontent.com/knative/serving/v$KNATIVE_VERSION/third_party/kourier-latest/kourier.yaml
kubectl patch configmap/config-network --namespace knative-serving --type merge --patch '{"data":{"ingress.class":"kourier.ingress.networking.knative.dev"}}'
```

Next, we need to fix the external url we get for knative services:

```sh
kubectl patch configmap config-domain --namespace knative-serving --patch \
  '{"data": {"example.com": null, "[EXTERNAL-IP].xip.io": ""}}'
```

Make sure to replace `[EXTERNAL-IP]` with the external ip of the VM (or whatever ip you will be accessing the service from).

Next, we can double check our installation with a `hello-world` application:

```sh
# deploy
kubectl apply -f https://gist.githubusercontent.com/jonatasbaldin/bc04de2e376be23f75bb5815041fdd61/raw/d2345ac9aa01d0f3c771e9b3d4a1421dd766e0f9/service.yaml
# get service information
kubectl get ksvc
# curl the url you get
curl ....
```

If you get `Hello Go Sample v1!` as a result, everything is fine. Sometimes, the first couple of tries will fail, but it will back up soon (because of xip.io).

## Knative CLI (kn)

- [Kn Documentation](https://github.com/knative/client/blob/master/docs/cmd/kn.md)

```sh
# install kn
curl -L https://storage.googleapis.com/knative-nightly/client/latest/kn-linux-amd64 -o kn
chmod +x ./kn
sudo mv ./kn /usr/local/bin/kn

# test installation
kn service ls
```

To create services using `kn` check out the [kn apply documentations](https://github.com/knative/client/blob/master/docs/cmd/kn_service_apply.md).

