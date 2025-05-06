# Tools & Technologies


---

## 1. Programming Languages

- **Python**  
  - **Use Cases:** Backend services (logging, cluster API, scheduler), scripting, rapid prototyping  
  - **Strengths:** Concise syntax, rich standard library (file I/O, JSON, async), large community and docs  
  - **Alternatives Considered:** Java (rejected due to heavier boilerplate and weaker support for FastAPI/Streamlit)  

- **TypeScript**  
  - **Use Cases:** Frontend & client‑side services  
  - **Strengths:** Compile‑time type safety, superior IDE support, seamless integration with React  
  - **Alternatives Considered:** Plain JavaScript (higher error risk)  

---

## 2. Backend Frameworks & APIs

- **FastAPI**  
  - **Use Cases:** Cluster Core Web API  
  - **Strengths:** High performance, Python type hints, automatic Swagger UI & validation  
  - **Alternatives Considered:** Flask (slower under concurrency, no built‑in docs)  

---

## 3. Datastores & Persistence

- **etcd**  
  - **Use Cases:** Cluster state storage, worker heartbeats, service assignments, watch notifications  
  - **Strengths:** Key‑value store with built‑in watch functionality, Kubernetes‑aligned  
  - **Alternatives Considered:** Redis (strong cache but lacked native watches, less “cloud‑native” for this use case)  

- **SQLite / Local File System**  
  - **Use Cases:** Job assignment persistence, log storage (initial phase)  
  - **Strengths:** Zero‑configuration, lightweight, direct file access  
  - **Log Rotation:** Managed via `logrotate` to archive old logs and control disk usage  

- **Redis (Future / Caching)**  
  - **Use Cases:** Hot‑path caching of frequently accessed node/Pod metadata  
  - **Planned Use:** Reduce etcd load with short‑term lookups  

---

## 4. Containerization & Orchestration

- **Docker**  
  - **Use Cases:** Packaging and running containers across pods and nodes  
  - **Strengths:** Industry standard, rich ecosystem, cross‑platform consistency  
  - **Alternatives Considered:** containerd (more lightweight but less familiar to team)  

---

## 5. Communication & Messaging

- **ZeroMQ**  
  - **Use Cases:** Queueing and event notifications between Cluster Manager ↔ Pod Managers  
  - **Strengths:** Low-latency, brokerless, scalable for dynamic workloads  

- **gRPC**  
  - **Use Cases:** Language‑agnostic, high‑performance RPC between services  
  - **Strengths:** Protobuf serialization, built‑in codegen  

- **TCP**  
  - **Use Cases:** Heartbeats and low‑latency runtime request routing directly to Pods  

---

## 6. Logging & Data Forwarding

- **Direct Log Shipping**  
  - **Use Cases:** Immediate write of container logs to local disk  
  - **Strengths:** Simplicity, low latency, minimal overhead  
  - **Future Enhancements:** Centralized aggregation (e.g., ELK, Fluentd) in later phases  

---

## 7. Frontend & Visualization

- **React**  
  - **Use Cases:** Dashboard UI for cluster state and logs  
  - **Strengths:** Component‑based, vast ecosystem  

- **Streamlit**  
  - **Use Cases:** Rapid‑development data dashboards for real‑time cluster monitoring  
  - **Strengths:** Minimal boilerplate, auto‑refresh on data changes  
  - **Alternatives Considered:** Dash/Plotly (more setup overhead)  

---

## 8. Build Tools & Styling

- **Vite**  
  - **Use Cases:** Frontend build and development server  
  - **Strengths:** Fast cold starts, hot module reloading  

- **Tailwind CSS**  
  - **Use Cases:** Utility‑first styling of web dashboard  
  - **Strengths:** Rapid prototyping, ready‑made admin templates  
  - **Alternatives Considered:** Emotion, CSS‑in‑JS (rejected due to runtime overhead)  

---

## Summary

This integrated stack ensures:

- **Rapid iteration** on both backend (Python + FastAPI) and frontend (TypeScript + React/Streamlit)  
- **Reliable persistence** with etcd (cluster state) and SQLite/logrotate (jobs & logs)  
- **Efficient container management** via Docker  
- **Scalable communication** through ZeroMQ, gRPC, and TCP  
- **Flexible logging** with direct file shipping and planned aggregation  
- **Modern developer experience** using Vite and Tailwind CSS  

Together, these technologies provide a robust, maintainable platform for distributed container orchestration, logging, and real‑time cluster management, with clear paths for future enhancements.
