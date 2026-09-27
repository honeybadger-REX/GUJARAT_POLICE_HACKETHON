#include <iostream>
#include <winsock2.h>
#include <cstring>
#include <queue>
#include <thread>
#include <mutex>
#include <print>
#include <condition_variable>

#pragma comment(lib, "ws2_32.lib")

// =====================================
// SHARED RESOURCES
// =====================================
const int MAX_QUEUE_SIZE = 10;
std::queue<SOCKET> clientQueue;
std::mutex queueMutex;
std::condition_variable queueCondition;

// ================================
// WORKER FUNCTION
// ================================

void worker()
{
    while (true)
    {
        SOCKET clientSocket;

        // GET CLIENT FROM QUEUE
        {
            std::unique_lock<std::mutex> lock(queueMutex);

            queueCondition.wait(lock, []
                                { return !clientQueue.empty(); });

            clientSocket = clientQueue.front();
            clientQueue.pop();
        }

        std::cout << "Worker handling client......\n";

        // ====================================
        // RECEIVE DATA
        // ====================================

        char buffer[1024];

        int bytesReceived = recv(
            clientSocket,
            buffer,
            sizeof(buffer) - 1,
            0);

        if (bytesReceived > 0)
        {
            buffer[bytesReceived] = '\0';

            std::cout << "Client said: "
                      << buffer
                      << "\n";
            std::this_thread::sleep_for(std::chrono::seconds(10));

            // ===================================
            // SEND DATA
            // ===================================

            const char *response = "HELLO FROM SERVER";
            std::this_thread::sleep_for(
                std::chrono::seconds(10));

            send(
                clientSocket,
                response,
                strlen(response),
                0);
        }

        // Close this client's connection
        closesocket(clientSocket);

        std::cout << "Worker finished client.\n";
    }
}

// ======================================================
// MAIN FUNCTION
// ======================================================

int main()
{
    std::cout << "Server started yo\n";

    // ========================================
    // START WINSOCK
    // ========================================

    WSADATA wsaData;

    int result = WSAStartup(
        MAKEWORD(2, 2),
        &wsaData);

    if (result != 0)
    {
        std::cout << "WSAStartup not working\n";
        return 1;
    }

    std::cout << "Winsock started\n";

    // ========================================
    // CREATE SERVER SOCKET
    // ========================================

    SOCKET serverSocket = socket(
        AF_INET,
        SOCK_STREAM,
        0);

    if (serverSocket == INVALID_SOCKET)
    {
        std::cout << "Socket connection failed\n";

        WSACleanup();
        return 1;
    }

    std::cout << "Socket created successfully.\n";

    // ===================================================
    // SERVER ADDRESS
    // ===================================================

    sockaddr_in serverAddress{};

    serverAddress.sin_family = AF_INET;
    serverAddress.sin_addr.s_addr = inet_addr("127.0.0.1");
    serverAddress.sin_port = htons(5000);

    // ===========================================
    // BIND
    // ===========================================

    if (bind(
            serverSocket,
            (sockaddr *)&serverAddress,
            sizeof(serverAddress)) == SOCKET_ERROR)
    {
        std::cout << "Bind failed\n";

        closesocket(serverSocket);
        WSACleanup();

        return 1;
    }

    std::cout << "Socket bound to 127.0.0.1:5000\n";

    // ===================================
    // LISTEN
    // ===================================

    if (listen(serverSocket, 10) == SOCKET_ERROR)
    {
        std::cout << "Listen failed.\n";

        closesocket(serverSocket);
        WSACleanup();

        return 1;
    }

    std::cout << "Server is listening on 127.0.0.1:5000\n";

    // ================================================
    // CREATE WORKER THREADS
    // ================================================

    const int WORKER_COUNT = 4;

    for (int i = 0; i < WORKER_COUNT; i++)
    {
        std::thread(worker).detach();
    }

    std::cout << "Workers started: "
              << WORKER_COUNT
              << '\n';

    // =================================================
    // ACCEPT CLIENTS
    // =================================================

    while (true)
    {
        SOCKET clientSocket = accept(
            serverSocket,
            nullptr,
            nullptr);

        if (clientSocket == INVALID_SOCKET)
        {
            std::cout << "Accept failed.\n";
            continue;
        }

        std::cout << "Client connected\n";

        {
            std::lock_guard<std::mutex> locked(queueMutex);
            if (clientQueue.size() >= MAX_QUEUE_SIZE)
            {
                std::cout << "Queue full. Rejecting client.\n";
                const char* message = "BUSY" ;
                send(
                    clientSocket,
                    message,
                    strlen(message),0
                );


                closesocket(clientSocket);
            }
            else
            {
                clientQueue.push(clientSocket);

                std::cout << "Client added to queue. Queue size: "
                          << clientQueue.size()
                          << "\n";
                 const char* message = "OK" ;
                send(
                    clientSocket,
                    message,
                    strlen(message),0
                );

                queueCondition.notify_one();
            }
        }
    }

    // We won't reach here yet
    closesocket(serverSocket);

    WSACleanup();

    return 0;
}