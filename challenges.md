# Distributed System Challenges

Large and complex programs often require significant resources and time to execute efficiently. Distributed systems help mitigate these challenges by breaking down larger workloads into smaller components that run on separate machines, optimizing both performance and resource utilization.

## Use Cases and Reasons for Going Distributed

- **Scalability**  
  Handling multiple user job requests and ensuring efficient workload distribution across worker nodes requires a distributed architecture to scale resources dynamically.

- **Fault Tolerance**  
  Distributing jobs across multiple worker nodes ensures uninterrupted execution and protects against single points of failure. If a pod or worker node goes down, its jobs can be recovered and reassigned.

- **High Availability**  
  Ensuring continuous system operation even in the face of failures requires distributing cluster management, job scheduling, and worker-node monitoring across multiple instances.

- **Load Balancing**  
  Dynamically distributing workloads across worker nodes prevents overloading any single node and ensures efficient resource utilization.

## How Going Distributed Addresses These Issues

1. **Scalability**  
   - Jobs are executed across multiple worker nodes, allowing horizontal scaling to handle more concurrent workloads.  
   - Worker nodes dynamically register with the Cluster Manager and fetch configuration from a central config server, enabling seamless scaling without manual intervention.

2. **Fault Tolerance**  
   - Redundancy and failure isolation: if a pod fails, its worker node restarts it; if a node becomes unavailable, the Cluster Manager redistributes its jobs to healthy nodes.

3. **High Availability**  
   - The Cluster Manager itself runs in a distributed mode to eliminate single points of failure.  
   - etcd is deployed as a clustered datastore to ensure continuous availability even if one or more nodes fail.

4. **Load Balancing**  
   - Jobs are assigned based on real‑time resource availability (CPU, RAM) on each node.  
   - Worker nodes subscribe to etcd watchers to detect job updates dynamically, reducing the need for inefficient polling.

## Key Challenges and Proposed Solutions

- **Node or Component Failures**  
  - *Challenge:* Individual nodes or components (e.g., pod managers) may fail unexpectedly.  
  - *Solution:* Persist job assignments in a lightweight database (e.g., SQLite) so they can be recovered and reassigned after a failure.

- **Ensuring Container Availability**  
  - *Challenge:* It’s crucial to verify that all containers remain operational.  
  - *Solution:* Establish a TCP “heartbeat” connection between each Pod and its Pod Manager to monitor container health in real time.

- **Routing Jobs to the Correct Container**  
  - *Challenge:* Jobs must be directed to the appropriate container within each node.  
  - *Solution:* Assign a unique ID to every container, enabling precise job allocation and tracking.

- **Preventing Communication Bottlenecks**  
  - *Challenge:* Unoptimized external communication can overload a node, degrading overall performance.  
  - *Solution:* Delegate all external communications to a dedicated node manager, reducing contention and streamlining interactions with the rest of the cluster.

- **Reliable Heartbeat Tracking**  
  - *Challenge:* Temporary network failures can cause false‑positives, marking healthy nodes as down.  
  - *Solution:* Introduce a grace period before marking nodes unavailable and implement retry mechanisms for transient network errors.

- **Efficient Job Status Updates from Pods**  
  - *Challenge:* Pods must communicate status only to their assigned worker node, which then forwards updates to the Cluster Manager.  
  - *Solution:* Expose a worker‑side API endpoint (`POST /pod-status`) to collect updates, and forward only critical state changes (`POST /job-status`) upstream to minimize traffic.

- **Scaling etcd for Large Deployments**  
  - *Challenge:* Frequent heartbeat and status updates can overload etcd, slowing down the system.  
  - *Solution:* Batch writes to etcd, cache hot‑path data in Redis, and periodically clean up stale entries.

- **Automatic Job Redistribution on Worker Failure**  
  - *Challenge:* Detecting node failures quickly and rescheduling jobs without inconsistency is complex.  
  - *Solution:* Implement a leader‑election mechanism to coordinate failover, and use checkpointing so jobs can resume from their last known state.

- **Preventing Cluster Overload from Frequent Heartbeats**  
  - *Challenge:* High‑frequency heartbeats generate excessive network traffic and storage usage.  
  - *Solution:* Dynamically adjust heartbeat frequency based on node activity and remove stale records from etcd to reduce overhead.

- **Security and Authentication**  
  - *Challenge:* Unauthorized nodes could inject fake heartbeats or job updates.  
  - *Solution:* Enforce JWT authentication for all worker nodes and pods, and secure API endpoints with TLS encryption.

- **Dynamic Auto‑Scaling**  
  - *Challenge:* Worker nodes currently require manual registration with the Cluster Manager.  
  - *Solution:* Use etcd watchers to detect new nodes automatically and have the scheduler rebalance jobs as nodes join or leave.

## Phase Two Enhancements

1. **Job Reassignment on Worker Failure**  
   Implement the leader‑election and job‑redistribution mechanisms to seamlessly reassign jobs when a node goes down.

2. **Handling Network Partitions Gracefully**  
   Introduce a message‑queuing layer (e.g., Kafka or RabbitMQ) to buffer job status updates during temporary disconnections.

3. **Authentication and Security Enhancements**  
   Roll out stricter API‑key validation for workers and enforce mandatory TLS encryption for all communications.

4. **Full Dynamic Scaling Support**  
   Enable true auto‑scaling by allowing worker nodes to join or leave the cluster at will, with the Cluster Manager automatically adjusting assignments accordingly.
