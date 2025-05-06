# Distributed System Challenges

Large and complex programs often require significant resources and time to execute efficiently. Distributed systems help mitigate these challenges by breaking down larger workloads into smaller components that run on separate machines. This approach optimizes both performance and resource utilization.

Key Challenges and Solutions

- Node or component failures
    - Individual nodes (or components within nodes, such as the pod manager) may fail unexpectedly.
    - Solution: Implement a database (e.g., SQLite) to persist job assignments, ensuring they can be recovered and reassigned if necessary. 
    
- Ensuring container availability
    - It is crucial to verify that all containers remain operational.
    - Solution: Establish a TCP connection between the Pod and Pod Manager to serve as a "heartbeat" signal, monitoring container health in real-time.
    
- Routing jobs to the correct container
    - Jobs must be directed to the appropriate container within each node.
    - Solution: Assign a unique ID to each container, enabling precise job allocation and tracking.
    
- Preventing communication bottlenecks
    - Unoptimized external communication can overload a node, degrading system performance.
    - Solution: Delegate all external communications to a dedicated node manager, reducing contention and streamlining interactions with the broader system.


> *Identify the use cases and reasons why your system and/or components need to be distributed. Explain how and why "going distributed" solves the issues. Identify and list the resultant distributed system challenges that you need to address. For each challenge or issue, explain how you propose to address it. If you do not plan on addressing a particular challenge, explain why it is not critical and out of scope for your project. Indicate how it could be addressed in "phase two" of your project.*



