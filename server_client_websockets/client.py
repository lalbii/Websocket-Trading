# scalability_client.py
import asyncio
import websockets
import json
import time
import matplotlib.pyplot as plt
async def listen_for_messages(uri, client_id):
    async with websockets.connect(uri) as websocket:
        total_latency = 0
        message_count = 0
        start_time = time.time()
        while time.time() - start_time < 10:  # Listen for messages for 10 seconds
            message = await websocket.recv()
            message_data = json.loads(message)
            print(f"client id received by {client_id}", message)
            
            received_time = time.time()
            latency = received_time - message_data['time']
            total_latency += latency
            message_count += 1
        return client_id, total_latency / message_count if message_count else 0, message_count

async def simulate_multiple_clients(uri, number_of_clients):
    tasks = []
    for client_id in range(number_of_clients):
        task = asyncio.create_task(listen_for_messages(uri, client_id))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    total_messages = sum(result[2] for result in results)
    average_latency = sum(result[1] for result in results) / number_of_clients
    print(f"Total messages received by {number_of_clients} clients: {total_messages}")
    print(f"Average latency across all clients: {average_latency:.3f} seconds")
    throughput = total_messages / 10  # Total messages received divided by the duration
    print(f"Total throughput: {throughput:.2f} messages per second")

    return number_of_clients, average_latency, throughput

uri = "ws://localhost:8765"
result_ = []
for i in [10,20,40,80,160]:
    print("number of clients:",i)
    number_of_clients, ave_latencty, through = asyncio.run(simulate_multiple_clients(uri, i))
    result_.append((number_of_clients,ave_latencty,through))

print(result_)

# Unpack the results
clients, latency, throughput = zip(*result_)

sending_frequency = 0.1  ##it should be the same with server frquency
throughput_perfect = [x/sending_frequency for x in [10,20,40,80,160]]

# Convert latency to milliseconds for better readability
latency_ms = [lat * 1000 for lat in latency]

# Create a figure and a set of subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))

# Plot latency on the first subplot
ax1.plot(clients, latency_ms, 'r-o')  # 'r-o' specifies red color with circle markers
ax1.set_title('Latency vs. Number of Clients')
ax1.set_xlabel('Number of Clients')
ax1.set_ylabel('Latency (ms)')
ax1.grid(True)

# Plot throughput on the second subplot
ax2.plot(clients, throughput, 'b-s',label="Throughput")
ax2.plot(clients,throughput_perfect,"r:o",label="Benchmark Throughput")
ax2.legend()
ax2.set_title('Throughput vs. Number of Clients')
ax2.set_xlabel('Number of Clients')
ax2.set_ylabel('Throughput (messages/sec)')
ax2.grid(True)

# Adjust layout to prevent overlapping
plt.tight_layout()

# Show plot
plt.show()