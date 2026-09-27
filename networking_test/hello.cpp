#include <iostream>
#include <winsock2.h>
#include <cstring>
#include <thread>
#include <chrono>

#pragma comment(lib, "ws2_32.lib")

int main()
{
    std::cout << "Client started......\n";

    // 1. Start Windows networking
    WSADATA wsaData;

    int result = WSAStartup(
        MAKEWORD(2, 2),
        &wsaData
    );

    if (result != 0)
    {
        std::cout << "WSAStartup failed.\n";
        return 1;
    }

    std::cout << "Winsock started successfully.\n";


    // 2. Create client socket
    for (int i = 0; i < 6;i++){
    SOCKET clientSocket = socket(
        AF_INET,
        SOCK_STREAM,
        0
    );

    if (clientSocket == INVALID_SOCKET)
    {
        std::cout << "Socket creation failed.\n";

        WSACleanup();
        return 1;
    }


    std::cout << "Client socket created.\n";


    // 3. Tell the client where the server is
    sockaddr_in serverAddress{};

    serverAddress.sin_family = AF_INET;
    serverAddress.sin_addr.s_addr = inet_addr("127.0.0.1");
    serverAddress.sin_port = htons(5000);


    // 4. Connect to the server
    if (connect(
        clientSocket,
        (sockaddr*)&serverAddress,
        sizeof(serverAddress)
    ) == SOCKET_ERROR)
    {
        std::cout << "Connection failed.\n";

        closesocket(clientSocket);
        WSACleanup();

        return 1;
    }


    std::cout << "Connected to server!\n";
    std::this_thread::sleep_for(
    std::chrono::seconds(1)
);
    const char* message = "HELOOW WORLD 3 ";
    send(
        clientSocket,
        message,
        strlen(message),
        0
    );

    std::cout<< "message send\n" ;

    // respond message 
    char buffer[1024];
    int respond = recv(
        clientSocket,
        buffer,
        sizeof(buffer) - 1,
        0
    );

    if( respond > 0){
        buffer[respond] = '\0' ;
         std::cout << "server said: "
              << buffer
              << "\n";
    }
    
    // 5. Close client socket
    closesocket(clientSocket);

    // 6. Shut down Winsock
   
    }
     WSACleanup();
    
    return 0;
}