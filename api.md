# API Documentation

> The API will be used to interact with the cluster manager.

## Configuration Service

The configuration service returns the backend that will be used throughout the cluster (such as etcd or redis) and list of ports that are being used throughout the control plane (the ip addresses are static). 

### Get the configuration

The endpoint for retrieving the configuration is `{IP Address}:{port}/getConfig/` (as of now it's port 5000)

```
{
    "backend_type": "etcd",
    "control_plane_ports": [100, 200, 300]
}
```


## Cluster Manager

The Cluster Manager API provides endpoints for deploying, managing, and monitoring tasks across worker nodes.

### Deploy Task

Deploys a new task to a worker node.

- **URL:** `/api/tasks/{task_name}/deploy`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "image_url": "docker.io/myimage:latest",
    "number_of_replicas": 1,
    "expected_usage": {
      "cpu": 1.0,
      "memory": 512,
      "disk": 1024
    }
  }
    ```

### Start Task

Starts a task on a worker node.

- **URL:** `/api/tasks/{task_name}/start`
- **Method:** `POST`

### Stop Task

Stops a task on a worker node.

- **URL:** `/api/tasks/{task_name}/stop`
- **Method:** `POST`

### List Worker Tasks

Lists all tasks running on a worker node.

- **URL:** `/api/workers/{worker_name}/tasks`
- **Method:** `GET`

### Get Task Workers

Lists all worker nodes running a task.

- **URL:** `/api/tasks/{task_name}/workers`
- **Method:** `GET`

### List Workers

Lists all worker nodes in the cluster.

- **URL:** `/api/workers`
- **Method:** `GET`
