#include <iostream>
#include <winsock2.h>
#include <cstring>
#include <thread>
#include <chrono>

#pragma comment(lib, "ws2_32.lib")

const int maxattemp = 5;
void simulateClient(int id)

{
    int retryDelay = 1;
    for (int i = 1; i < maxattemp; i++)
    {
        std::cout << "Client " << id << " starting...\n";

        // 1. Create ONE socket for this simulated client
        SOCKET clientSocket = socket(
            AF_INET,
            SOCK_STREAM,
            0);

        if (clientSocket == INVALID_SOCKET)
        {
            std::cout << "Client "
                      << id
                      << ": Socket creation failed.\n";

            return;
        }

        std::cout << "Client "
                  << id
                  << ": Socket created.\n";

        // 2. Server address
        sockaddr_in serverAddress{};

        serverAddress.sin_family = AF_INET;
        serverAddress.sin_addr.s_addr = inet_addr("127.0.0.1");
        serverAddress.sin_port = htons(5000);

        // 3. Connect to server
        if (connect(
                clientSocket,
                (sockaddr *)&serverAddress,
                sizeof(serverAddress)) == SOCKET_ERROR)
        {
            std::cout << "Client "
                      << id
                      << ": Connection failed.\n";

            closesocket(clientSocket);

            return;
        }

        std::cout << "Client "
                  << id
                  << ": Connected to server!\n";

        // Small delay so we can observe multiple clients
        std::this_thread::sleep_for(
            std::chrono::seconds(1));

        // 4. Send message
        const char *message = "HELLO WORLD";

        send(
            clientSocket,
            message,
            strlen(message),
            0);

        std::cout << "Client "
                  << id
                  << ": Message sent.\n";

        // 5. Receive server response

        char buffer[1024];

        int response = recv(
            clientSocket,
            buffer,
            sizeof(buffer) - 1,
            0);

           if (strcmp(buffer, "OK") == 0)
        {
            buffer[response] = '\0';

            std::cout << "Client "
                      << id
                      << ": Server said: "
                      << buffer
                      << "\n";
            for (int i = 0; i < maxattemp; i++)
            {
            }
        }
        if (strcmp(buffer, "BUSY") == 0)
        {
            std::cout << "Server busy. Retry "
                      << i
                      << "\n";

            closesocket(clientSocket);

            std::this_thread::sleep_for(
                std::chrono::seconds(retryDelay));

            retryDelay *= 2;

            continue;
        }
        if (strcmp(buffer, "OK") == 0)
        {

            std::cout << "Client "
                      << id
                      << ": Server accepted.\n";

            // Now send actual message
            const char *message = "HELLO WORLD";

            send(
                clientSocket,
                message,
                strlen(message),
                0);

            std::cout << "Client "
                      << id
                      << ": Message sent.\n";

            // Receive server response
            response = recv(
                clientSocket,
                buffer,
                sizeof(buffer) - 1,
                0);

            if (response > 0)
            {
                buffer[response] = '\0';

                std::cout << "Client "
                          << id
                          << ": Server said: "
                          << buffer
                          << "\n";
            }

            closesocket(clientSocket);

            std::cout << "Client "
                      << id
                      << ": Finished.\n";

            return;
        }
    

    // 6. Close this client's socket
    closesocket(clientSocket);

    std::cout << "Client "
              << id
              << ": Finished.\n";
}
}

int main()
{
    std::cout << "Client simulator started......\n";

    // =================================
    // Start Winsock
    // =================================

    WSADATA wsaData;

    int result = WSAStartup(
        MAKEWORD(2, 2),
        &wsaData);

    if (result != 0)
    {
        std::cout << "WSAStartup failed.\n";
        return 1;
    }

    std::cout << "Winsock started successfully.\n";

    // =================================
    // Create 6 simulated clients
    // =================================

    std::thread clients[6];

    for (int i = 0; i < 6; i++)
    {
        clients[i] =
            std::thread(
                simulateClient,
                i + 1);
    }

    // =================================
    // Wait for all clients
    // =================================

    for (int i = 0; i < 6; i++)
    {
        clients[i].join();
    }

    // =================================
    // Shutdown Winsock
    // =================================

    WSACleanup();

    std::cout << "All simulated clients finished.\n";

    return 0;
}