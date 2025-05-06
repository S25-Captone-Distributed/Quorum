# Execution & Runtime Scope

**Authors**: David K, Sam S, Yoni S, Yoni Z, Yosef B  
**Project**: Container Management System

---

## 1. Overview

We are building a **container management system** that handles **execution and runtime** for distributed services across multiple nodes. Our team is responsible for managing the execution and runtime components, including:

- **Pod Management**: Creating and managing Pods that encapsulate one or more containers.
- **Node Management**: Coordinating how Pods are deployed across nodes.
- **Logging and Monitoring**: Capturing container logs and monitoring service health through heartbeats.
- **Communication & Routing**: Facilitating data exchange between the Node Manager, Pod Manager, and Pods using ZeroMQ and TCP, while efficiently routing runtime requests to the appropriate services.

Our design is clearly illustrated in our **Flowchart** and **Execution System C4** diagram. The Flowchart shows the step-by-step process for deployment and execution, while the C4 diagram highlights the relationships between the Node Manager, Pod Manager, Pods, Logging, and Queue components.

---

## 3. What Are We Doing?

### High-Level Summary
1. **Node Manager**: Receives deployment and runtime requests, sends jobs to the Pod Manager, schedules requests to the correct Pods, and monitors node status.
2. **Pod Manager**: Creates and manages Pods on each node, communicates with containers, and orchestrates container lifecycle actions (pull, start, stop).
3. **Pods**: Each Pod contains one or more containers. The Pod Manager sets up these containers as needed.
4. **Logging**: Captures stdout/stderr from containers for monitoring and debugging.
5. **Communication & Routing**: Uses ZeroMQ for messaging between the Node Manager and Pod Manager, and TCP for direct communication with Pods. This layer also handles the dynamic routing of runtime requests to the appropriate container or Pod.

---

## 4. Scope

- **Deployment and Execution**: Support for deploying new services, starting containers, stopping containers, and reporting status updates.
- **Inter-Service Communication**: Robust communication channels between the Node Manager, Pod Manager, and Pods via ZeroMQ and TCP.
- **Runtime Request Handling & Routing**: Efficiently handle and route execution requests in real time, ensuring that runtime requests are processed by the correct Pods.
- **Logging & Monitoring**: Capture container logs and monitor service health through periodic heartbeats.
- **Error Handling**: Define clear responses for timeouts, connection failures, and pull errors.
- **Load Balancing & Resource Management**: Implement scheduling algorithms and resource limits once the basic system is operational.

---

## 5. Features

1. **Execute Services**: Run containers (or sets of containers) as services.
2. **Deploy**: Pull container images, create Pods, and start containers.
3. **Start**: Initiate container processes within a Pod.
4. **Stop**: Gracefully stop containers or force-terminate them if unresponsive.
5. **Logging**: Capture and store container logs (stdout/stderr) for debugging and audit purposes.
6. **Monitoring & Heartbeats**: Maintain service health via regular heartbeats from Pods to the Pod Manager.
7. **Runtime Request Handling & Routing**: Accept runtime requests (e.g., job submissions), route them dynamically to the appropriate Pod/container, and manage responses.

---

## 6. Use Cases

### 6.1 Deploy a New Service
1. **Request**: A user sends a “Deploy” command to the **Node Manager** with container image details.
2. **Queueing**: The Node Manager places a deployment event on a messaging queue (using ZeroMQ).
3. **Processing**: The **Pod Manager** receives the event, pulls the container image via Docker, and creates a new Pod with the container.
4. **Confirmation**: The Pod starts up and sends a heartbeat or status update back to the Pod Manager.
5. **Error Handling**:
    - **Pull Failure**: If the image pull fails (e.g., due to invalid image name), the Pod Manager reports the error to the Node Manager, which notifies the user.
    - **Timeout**: If the Pod does not send a heartbeat within the expected timeframe, the Node Manager retries the deployment or raises an alert.
6. **Status Update**: The Pod Manager updates the Node Manager (or a central database) about the successful or failed deployment.

### 6.2 Start a Container
1. **Request**: A user sends a “Start Container” command to the **Node Manager**.
2. **Delegation**: The Node Manager instructs the **Pod Manager** to start the container by its ID.
3. **Execution**: The Pod Manager executes `docker start <container_id>`.
4. **Acknowledgement**: The container confirms it has started and sends its status back to the Pod Manager.
5. **Error Handling**:
    - **No Response**: If the container fails to start or confirm within a set timeout, the system will retry the start command or escalate the error.
    - **Connection Failure**: If the TCP/ZeroMQ connection is lost during startup, the system logs the error and attempts to re-establish communication.

### 6.3 Stop a Container
1. **Request**: A user sends a “Stop Container” command to the **Node Manager**.
2. **Delegation**: The Node Manager instructs the **Pod Manager** to stop the specified container.
3. **Action**: The Pod Manager attempts a graceful shutdown of the container, or forcefully stops it if unresponsive.
4. **Status Update**: The container sends its updated status (Stopped) back to the Pod Manager.
5. **Error Handling**:
    - **Graceful Shutdown Failure**: If the container does not stop gracefully within a timeout, the Pod Manager forces a stop and logs the incident.
    - **Lost Communication**: If the connection to the container is lost during the stop command, the system logs the event and marks the container for further inspection.

### 6.4 Runtime Request Handling & Routing
#### 6.4.1 Submit a Runtime Request
1. **Request**: A user submits a runtime request (e.g., a job submission) to the **Node Manager**.
2. **Initial Routing**: The Node Manager logs the request and assigns it a job ID.
3. **Error Handling**: If the request is malformed or missing critical data, an error is immediately returned to the user.

#### 6.4.2 Route the Request
1. **Evaluation**: The Node Manager evaluates the request, considering current load, available ports, and Pod capacity.
2. **Routing Decision**: Based on the evaluation, the Node Manager selects an appropriate Pod and communicates the routing decision to the Pod Manager.
3. **Error Handling**: If no suitable Pod is found, the request is queued for retry and an error is logged.

#### 6.4.3 Process the Request
1. **Forwarding**: The Pod Manager forwards the runtime request to the selected Pod using TCP or ZeroMQ.
2. **Execution**: The Pod processes the request, performing the necessary computations or service operations.
3. **Error Handling**: If processing fails (e.g., due to internal errors), the Pod logs the error and returns a failure status.

#### 6.4.4 Return the Response
1. **Response Transmission**: The Pod sends the result or status update back to the Pod Manager.
2. **Final Relay**: The Pod Manager relays the response back to the Node Manager, which then communicates it to the user.
3. **Error Handling**: If the response is not received within a set timeout, the system retries the request or escalates the error.

---

## 7. Request Routing & Service Communication

1. **Track jobs in memory:** In memory, we maintain a reference to each job, which includes a job ID. This ID allows us to track the status and execution of each job. The other team provides a key, which we associate with the job ID for retrieval and validation.
2. **Communication between components:** All communication between system components occurs over TCP. The execution team ensures that messages are routed reliably between the Node Manager, Pod Manager, and service instances.
3. **Ensure failed services do not receive traffic:** We implement a failure-aware request handling system that monitors service health through heartbeats and logs. If a service becomes unresponsive or fails, we dynamically reroute requests to healthy instances.
4. **Handle newly added services and replicas:** New service instances and replicas are discovered in real time through a service discovery mechanism. This allows the system to automatically adjust routing decisions as new instances become available.
5. **Optimize request handling for fault tolerance:** To ensure fault tolerance, we implement:
    - Health checks to verify service availability before routing requests.
    - Retry mechanisms to reattempt failed requests.
    - Load balancing to distribute traffic evenly across available services.

---

## 8. Interactions with Other Components

- **UI / Frontend**: Provides a dashboard for users to deploy, start, and stop containers, submit runtime requests, and view system logs/status.
- **Database / Persistence**: Manages the centralized database for storing container states, logs, heartbeats, and routing data.
- **Networking / Infrastructure**: Ensures the underlying network supports stable TCP/ZeroMQ connections among the Node Manager, Pod Manager, and Pods.
