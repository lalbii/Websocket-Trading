
#importing required libraries
import asyncio
import socketio
import time
import matplotlib.pyplot as plt


async def connect_and_listen(server_url, client_id, duration=30):
    local_sio = socketio.AsyncClient()
    latencies = []
    message_count = 0
    start_time = time.time()

    @local_sio.event
    async def connect():
        print(f'Client {client_id}: Connected to the server.')

    @local_sio.event
    async def stream(data):
        nonlocal message_count
        print(f'Client {client_id}:',data['timestamp'])

        receive_time = time.time()
        latency = receive_time - data['timestamp']
        latencies.append(latency)
        message_count += 1

    @local_sio.event
    async def disconnect():
        print(f'Client {client_id}: Disconnected from the server.')

    await local_sio.connect(server_url)
    
    # Run for a specified duration
    await asyncio.sleep(duration)
    await local_sio.disconnect()
    
    # Calculate metrics
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    throughput = message_count / duration
    return avg_latency, throughput, message_count

async def measure_performance(server_url, num_clients, duration=10):
    tasks = [connect_and_listen(server_url, i, duration) for i in range(num_clients)]
    results = await asyncio.gather(*tasks) #concurently call the clients
    
    avg_latencies = [result[0] for result in results]
    total_throughput = sum(result[1] for result in results)
    total_messages = sum(result[2] for result in results)
    avg_latencies_over_clients = sum(avg_latencies) / len(avg_latencies)

    return avg_latencies_over_clients, total_throughput, total_messages

if __name__ == '__main__':
    server_url = 'http://localhost:8765'
    num_clients = 5  # Number of simulated clients for scalability testing
    duration = 10    # Duration to run each client and measure performance
    result_ = []
    for num_client in [10,20,40,80,160]:
        print(f"{num_client} clients connected")
        avg_latencies_over_clients,throughput_,total_messages = asyncio.run(measure_performance(server_url, num_client, duration))
        result_.append((num_client,avg_latencies_over_clients,throughput_))

    print(result_)

    ################################################################
    ##For plotting the results:

    # Unpack the results
    clients, latency, throughput = zip(*result_)

    sending_frequency = 0.1 #it is reuired for calculation benchmark throughput
                            #it should be the same with server frequency
    throughput_perfect = [x/sending_frequency for x in [10,20,40,80,160]]

    # Convert latency to milliseconds for better readability
    latency_ms = [lat * 1000 for lat in latency]

    # Create a figure and a set of subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))

    # Plot latency on the first subplot
    ax1.plot(clients, latency_ms, 'r-o')  
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