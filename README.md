# Calculator Microservices on Kubernetes

A self-contained demo showing how to split a simple calculator into five independent microservices—**home**, **add**, **sub**, **mul**, **div**—containerized with Docker and orchestrated on a local Kubernetes cluster (Minikube). Each service is a small Flask app exposed via a NodePort Service, with Horizontal Pod Autoscaling under load.

---

## 📁 Repository Layout

```
MICROSERVICES/
│
├── home/                      # “Welcome” page
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── add/                       # Addition service
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── sub/                       # Subtraction service
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── mul/                       # Multiplication service
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── div/                       # Division service
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── k8s/                       # Kubernetes manifests
│   ├── home-deployment.yaml
│   ├── home-service.yaml
│   ├── add-deployment.yaml
│   ├── add-service.yaml
│   ├── sub-deployment.yaml
│   ├── sub-service.yaml
│   ├── mul-deployment.yaml
│   ├── mul-service.yaml
│   ├── div-deployment.yaml
│   └── div-service.yaml
│
└── README.md                  # This file
```

---

## 1. Prerequisites

- Docker (or Docker Desktop)  
- kubectl  
- Minikube  
- (Optional) Apache Benchmark (`ab`) or use PowerShell loops for stress testing

---

## 2. Microservice Code & Dockerfiles

> **All services listen on port 5000 internally.**

### 2.1 home/app.py
```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Calculator Microservices!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 2.2 add/app.py (similar pattern for sub, mul, div)
```python
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/')
def add():
    a = int(request.args.get('a', 0))
    b = int(request.args.get('b', 0))
    return jsonify(operation='add', result=a + b)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

> Copy this file into `sub/`, `mul/`, `div/` folders, adjusting `result` logic:
> - `sub`: `a - b`  
> - `mul`: `a * b`  
> - `div`: include zero‐check and `a / b`

### 2.3 Dockerfile (same in each folder)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
```

### 2.4 requirements.txt
```
flask
```

---

## 3. Build Docker Images

Point your Docker CLI to Minikube (so images are available to Kubernetes):

```bash
minikube start
eval $(minikube docker-env)      # Linux/macOS
# OR on Windows PowerShell:
& minikube -p minikube docker-env | Invoke-Expression
```

From the repo root:
```bash
docker build -t calc-home:v1 ./home
docker build -t calc-add:v1  ./add
docker build -t calc-sub:v1  ./sub
docker build -t calc-mul:v1  ./mul
docker build -t calc-div:v1  ./div
```

Verify:
```bash
docker images | grep calc-
```

---

## 4. Kubernetes Manifests

Each deployment runs 2 replicas; each service is type **NodePort** forwarding port 80 → container 5000.

### 4.1 home-deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: home-deployment
spec:
  replicas: 2
  selector:
    matchLabels: { app: home }
  template:
    metadata: { labels: { app: home } }
    spec:
      containers:
      - name: home
        image: calc-home:v1
        ports: [{ containerPort: 5000 }]
```

### 4.2 home-service.yaml
```yaml
apiVersion: v1
kind: Service
metadata: { name: home-service }
spec:
  selector: { app: home }
  ports: [{ protocol: TCP, port: 80, targetPort: 5000 }]
  type: NodePort
```

> Repeat the same for **add**, **sub**, **mul**, **div**, updating `name`, `app:`, and `image:` fields.

---

## 5. Deploy & Verify

```bash
kubectl apply -f k8s/
kubectl get pods
kubectl get svc
```

You should see 10 pods (`2×5`) and 5 NodePort services.

---

## 6. Access the Services

1. Get Minikube IP:
   ```bash
   minikube ip   # e.g. 192.168.49.2
   ```
2. Get NodePort per service:
   ```bash
   kubectl get svc
   ```
3. In your browser or curl:
   ```
http://<IP>:<HOME_PORT>/               # Home page
http://<IP>:<ADD_PORT>/?a=10&b=5        # Add
http://<IP>:<SUB_PORT>/?a=10&b=5        # Subtract
http://<IP>:<MUL_PORT>/?a=10&b=5        # Multiply
http://<IP>:<DIV_PORT>/?a=10&b=2        # Divide
``` Or use:
```bash
minikube service home-service
minikube service add-service
# … etc.
```

---

## 7. Enable HPA & Stress Test

### 7.1 Enable metrics-server
```bash
minikube addons enable metrics-server
```

### 7.2 Create a Horizontal Pod Autoscaler
```bash
kubectl autoscale deployment add-deployment \
  --cpu-percent=50 --min=2 --max=5
kubectl get hpa
```

### 7.3 Generate Load
**Apache Benchmark**:
```bash
ab -n 500 -c 20 http://$(minikube ip):$(kubectl get svc add-service -o jsonpath='{.spec.ports[0].nodePort}')/?a=1&b=2
```

**PowerShell loop**:
```powershell
for ($i=0; $i -lt 500; $i++) {
  Invoke-WebRequest "http://$(minikube ip):$(kubectl get svc add-service -o jsonpath='{.spec.ports[0].nodePort}')/?a=1&b=2" > $null
}
```

Watch pods scale:
```bash
kubectl get hpa --watch
kubectl get pods --watch
```

---

## 8. Cleanup
```bash
kubectl delete hpa add-deployment
kubectl delete -f k8s/
minikube stop
minikube delete
```

---

**Happy Deploying!**  
Questions or feedback? Open an issue.

