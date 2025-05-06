import asyncio
import os
import websockets
import docker
import requests
from requests.exceptions import RequestException
from urllib.parse import urlencode
from docker.errors import ImageNotFound, APIError
from aio_pika import connect, Channel, Message, DeliveryMode
from aio_pika.abc import AbstractIncomingMessage
import json


# {
#     "serviceDetails": {"serviceName": "payment-service"},
#     "httpRequest": {
#         "method": "POST",
#         "path": "/transactions",
#         "port": 8080,
#         "queryParams": {"idempotencyKey": "tx-9876543210"},
#         "headers": {
#             "Content-Type": "application/json",
#             "Accept": "application/json",
#             "X-Request-ID": "req-123e4567-e89b-12d3-a456-426614174000",
#         },
#         "body": {
#             "amount": 100.0,
#             "currency": "USD",
#             "description": "Monthly subscription",
#             "customer": "cust_12345",
#         },
#         "timeout": 5000,
#         "retryPolicy": {
#             "maxRetries": 2,
#             "retryInterval": 1000,
#             "retryStatusCodes": [500, 502, 503],
#         },
#     },
# }

async def on_message(message: AbstractIncomingMessage):
    async with message.process():
        correlation_id = message.correlation_id
        print(f"Received message with correlation ID: {correlation_id}")
        reply_to = message.reply_to
        print(f"Reply to: {reply_to}")
        print(f"Received message: {message.body}")

        message_body = json.loads(message.body)
        print(f"Message body: {message_body}")

        service_name = message_body["serviceDetails"]["serviceName"]
        http_request = message_body["httpRequest"]
        method = http_request["method"]
        path = http_request["path"]
        port = http_request["port"]

        query_params = http_request.get("queryParams", {})
        headers = http_request.get("headers", {})
        body = http_request.get("body", None)
        timeout = http_request.get("timeout", 7000) / 1000  

        # Handle optional retry policy
        retry_policy = http_request.get("retryPolicy", {
            "maxRetries": 0,
            "retryInterval": 1000,
            "retryStatusCodes": []
        })
        max_retries = retry_policy.get("maxRetries", 0)
        retry_interval = retry_policy.get("retryInterval", 1000)
        retry_status_codes = retry_policy.get("retryStatusCodes", [])

        print(f"Service name: {service_name}")
        print(f"HTTP request: {method} {path} {port}")
        print(f"Query params: {query_params}")
        print(f"Headers: {headers}")
        print(f"Body: {body}")
        print(f"Timeout: {timeout}")
        print(f"Retry policy: {max_retries} {retry_interval} {retry_status_codes}")

        # Prepare the URL
        domain = os.environ.get("CLIENT_CONTAINER_NAME")
        base_url = f"http://{domain}:{port}"
        url = f"{base_url}{path}"
        if query_params:
            url = f"{url}?{urlencode(query_params)}"

        print(f"Making request to URL: {url}")

        # Prepare the response data
        response_data = {}

        # Perform the HTTP request with retry logic
        current_retry = 0
        while True:
            try:
                if method == "POST":
                    print("Performing HTTP POST request")
                    response = requests.post(url, headers=headers, json=body, timeout=timeout)
                elif method == "GET":
                    print("Performing HTTP GET request")
                    response = requests.get(url, headers=headers, timeout=timeout)
                elif method == "PUT":
                    print("Performing HTTP PUT request")
                    response = requests.put(url, headers=headers, json=body, timeout=timeout)
                elif method == "DELETE":
                    print("Performing HTTP DELETE request")
                    response = requests.delete(url, headers=headers, timeout=timeout)
                else:
                    print(f"Unsupported HTTP method: {method}")
                    response_data = {
                        "success": False,
                        "error": f"Unsupported HTTP method: {method}"
                    }
                    break

                # Check if we need to retry
                if response.status_code in retry_status_codes and current_retry < max_retries:
                    current_retry += 1
                    print(f"Received status code {response.status_code}, retrying ({current_retry}/{max_retries})...")
                    await asyncio.sleep(retry_interval / 1000)  # Convert from ms to seconds
                    continue

                # Process the response
                try:
                    json_response = response.json()
                    response_data = {
                        "success": response.status_code < 400,
                        "statusCode": response.status_code,
                        "headers": dict(response.headers),
                        "body": json_response
                    }
                except ValueError:
                    # Response is not JSON
                    response_data = {
                        "success": response.status_code < 400,
                        "statusCode": response.status_code,
                        "headers": dict(response.headers),
                        "body": response.text
                    }
                break

            except RequestException as e:
                print(f"Request error: {e}")
                if current_retry < max_retries:
                    current_retry += 1
                    print(f"Retrying ({current_retry}/{max_retries})...")
                    await asyncio.sleep(retry_interval / 1000)  # Convert from ms to seconds
                else:
                    response_data = {
                        "success": False,
                        "error": str(e)
                    }
                    break

        # Send the response back to the reply_to queue if it exists
        if reply_to:
            print(f"Sending response to {reply_to}")
            # Get the channel from the same connection
            connection = await connect("amqp://guest:guest@rabbitmq/")
            channel = await connection.channel()

            # Create a response message
            response_message = Message(
                body=json.dumps(response_data).encode(),
                correlation_id=correlation_id,
                delivery_mode=DeliveryMode.PERSISTENT
            )

            # Publish the response
            await channel.default_exchange.publish(
                response_message, routing_key=reply_to
            )
            print(f"Response sent to {reply_to}")
        else:
            print("No reply_to queue specified, not sending a response")

async def rabbitmq_consumer():
    connection = await connect("amqp://guest:guest@rabbitmq/")

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        queue_name = os.environ.get("QUEUE_NAME", "task_queue")

        queue = await channel.declare_queue(
            queue_name,
            durable=True,
        )

        await queue.consume(on_message)

        print(" [*] Waiting for messages.")
        await asyncio.Future()


async def simple_client():
    pod_manager_ip = os.environ.get("POD_MANAGER_IP", "pod-manager")
    ws_server_port = os.environ.get("WS_SERVER_PORT", "8000")
    pod_id = os.environ.get("POD_ID")
    print(f"Pod ID: {pod_id}")

    uri = f"ws://pod-manager:{ws_server_port}/ws/{pod_id}"
    print(f"Connecting to {uri}")

    client = docker.from_env()
    # examples of messages received from the pod manager
    # {"type": "deploy", "data": {"image_url": "docker.io/library/nginx:latest", "resources": {"cpu": 1, "memory": 1024}, "client_container_name": "nginx"}}
    # {"type": "stop", "data": {}}
    # {"type": "run", "data": {}}
    # {"type": "restart", "data": {}}
    # {"type": "status", "data": {}}

    # examples of messages sent to the pod manager
    # {"type": "status", "data": {"status": "created", "message": <"The container is created">}}
    # {"type": "status", "data": {"status": "running", "message": <"The container is running">}}
    # {"type": "status", "data": {"status": "stopped", "message": <"The container is stopped">}}
    # {"type": "status", "data": {"status": "restarting", "message": <"The container is restarting">}}
    # {"type": "status", "data": {"status": "deploying", "message": <"The container is being deployed">}}
    # {"type": "status", "data": {"status": "error", "message": <"The container failed to start">}}

    container = None
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to the websocket server.")

            while True:
                response = await websocket.recv()
                data = json.loads(response)
                print(f"Received: {response}")

                if data["type"] == "deploy":
                    image_url = data["data"]["image_url"]
                    resources = data["data"]["resources"]

                    client_container_name = data["data"]["client_container_name"]
                    os.environ["CLIENT_CONTAINER_NAME"] = client_container_name

                    network_name = os.environ.get("DOCKER_NETWORK", "bridge")
                    print(f"Deploying image: {image_url} with resources: {resources}")

                    try:
                        container = await asyncio.to_thread(
                            client.containers.run,
                            image_url,
                            name=client_container_name,
                            detach=True,
                            auto_remove=False,
                            network=network_name,
                        )

                        created_message = {"type": "status", "data": {"status": "created", "message": f"The container is created"}}
                        await websocket.send(json.dumps(created_message))
                    except ImageNotFound:
                        print(f"Image not found: {image_url}")
                        error_message = {"type": "status", "data": {"status": "error", "message": f"Image not found: {image_url}"}}
                        await websocket.send(json.dumps(error_message))
                    except Exception as e:
                        print(f"Error deploying image: {e}")
                        error_message = {"type": "status", "data": {"status": "error", "message": f"Error deploying image: {e}"}}
                        await websocket.send(json.dumps(error_message))

                elif data["type"] == "stop":
                    print("Stopping the container")
                    if container is not None:
                        container.stop()
                        stopped_message = {"type": "status", "data": {"status": "stopped", "message": f"The container is stopped"}}
                        await websocket.send(json.dumps(stopped_message))
                    else:
                        error_message = {"type": "status", "data": {"status": "error", "message": "Container not found"}}
                        await websocket.send(json.dumps(error_message))
                elif data["type"] == "run":
                    print("Starting the container")
                    if container is not None:
                        container.start()
                        running_message = {"type": "status", "data": {"status": "running", "message": f"The container is running"}}
                        await websocket.send(json.dumps(running_message))
                    else:
                        error_message = {"type": "status", "data": {"status": "error", "message": "Container not found"}}
                        await websocket.send(json.dumps(error_message))
                elif data["type"] == "restart":
                    print("Restarting the container")
                    if container is not None:
                        container.restart()
                        running_message = {"type": "status", "data": {"status": "running", "message": f"The container is running"}}
                        await websocket.send(json.dumps(running_message))
                    else:
                        error_message = {"type": "status", "data": {"status": "error", "message": "Container not found"}}
                        await websocket.send(json.dumps(error_message))
                elif data["type"] == "status":
                    print("Getting the status of the container")
                    if container is not None:
                        status = container.status
                        running_message = {"type": "status", "data": {"status": status}}
                        await websocket.send(json.dumps(running_message))
                    else:
                        error_message = {"type": "status", "data": {"status": "error", "message": "Container not found"}}
                        await websocket.send(json.dumps(error_message))

    except Exception as e:
        print(f"Websocket connection error: {e}")


if __name__ == "__main__":
    # Run both the WebSocket client and RabbitMQ consumer in parallel
    async def main():
        # Create tasks for both the simple client and RabbitMQ consumer
        ws_task = asyncio.create_task(simple_client())
        rabbitmq_task = asyncio.create_task(rabbitmq_consumer())
        
        # Wait for both tasks to complete (which should be never as both have infinite loops)
        try:
            await asyncio.gather(ws_task, rabbitmq_task)
        except Exception as e:
            print(f"Error in main loop: {e}")
    
    asyncio.run(main())
