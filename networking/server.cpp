#include <iostream>
#include <winsock2.h>
#include <cstring>

#pragma comment(lib, "ws2_32.lib")

int main()
{
    std::cout << "Control server starting...\n";

    // Start Winsock
    WSADATA wsaData;

    if (WSAStartup(
            MAKEWORD(2, 2),
            &wsaData) != 0)
    {
        std::cout << "WSAStartup failed.\n";
        return 1;
    }

    // Create socket
    SOCKET serverSocket = socket(
        AF_INET,
        SOCK_STREAM,
        0
    );

    if (serverSocket == INVALID_SOCKET)
    {
        std::cout << "Socket creation failed.\n";
        WSACleanup();
        return 1;
    }

    // Server address
    sockaddr_in serverAddress{};

    serverAddress.sin_family = AF_INET;
    serverAddress.sin_addr.s_addr = inet_addr("127.0.0.1");
    serverAddress.sin_port = htons(5000);

    // Bind
    if (bind(
            serverSocket,
            (sockaddr*)&serverAddress,
            sizeof(serverAddress)) == SOCKET_ERROR)
    {
        std::cout << "Bind failed.\n";

        closesocket(serverSocket);
        WSACleanup();

        return 1;
    }

    // Listen
    if (listen(serverSocket, 10) == SOCKET_ERROR)
    {
        std::cout << "Listen failed.\n";

        closesocket(serverSocket);
        WSACleanup();

        return 1;
    }

    std::cout << "Control server listening on port 5000...\n";


    // Accept client
    SOCKET clientSocket = accept(
        serverSocket,
        nullptr,
        nullptr
    );

    if (clientSocket == INVALID_SOCKET)
    {
        std::cout << "Accept failed.\n";

        closesocket(serverSocket);
        WSACleanup();

        return 1;
    }

    std::cout << "FastAPI/client connected.\n";


    // Receive command
    char buffer[1024];

    int received = recv(
        clientSocket,
        buffer,
        sizeof(buffer) - 1,
        0
    );

    if (received > 0)
    {
        buffer[received] = '\0';

        std::cout << "Received: "
                  << buffer
                  << "\n";


        // Send response
        const char* response = "OK";

        send(
            clientSocket,
            response,
            strlen(response),
            0
        );
    }


    closesocket(clientSocket);
    closesocket(serverSocket);

    WSACleanup();

    return 0;
}