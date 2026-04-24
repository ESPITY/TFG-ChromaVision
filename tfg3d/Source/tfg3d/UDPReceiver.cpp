#include "UDPReceiver.h"
#include "Async/Async.h"
#include "Common/UdpSocketReceiver.h"
#include "Json.h"

AUDPReceiver::AUDPReceiver() {
    PrimaryActorTick.bCanEverTick = false;
    Socket = nullptr;
    UDPReceiver = nullptr;
}

void AUDPReceiver::BeginPlay() {
    Super::BeginPlay();

    bool bSuccess = StartUDPReceiver();
    if (!bSuccess) {
        UE_LOG(LogTemp, Error, TEXT("No se pudo iniciar el receptor UDP"));
    }
}

void AUDPReceiver::Tick(float DeltaTime) {
    Super::Tick(DeltaTime);
}

// BufferSize = 2 MB
bool AUDPReceiver::StartUDPReceiver(const FString& SocketName, const FString& IP, const int32 Port, const int32 BufferSize) {
    FIPv4Address Addr;
    FIPv4Address::Parse(IP, Addr);
    FIPv4Endpoint Endpoint(Addr, Port);

    // Crear el socket
    Socket = FUdpSocketBuilder(*SocketName)
        .AsNonBlocking()
        .AsReusable()
        .BoundToEndpoint(Endpoint)
        .WithReceiveBufferSize(BufferSize);

    if (!Socket) {
        UE_LOG(LogTemp, Error, TEXT("Error: No se pudo crear el socket"));
        return false;
    }

    // Crear el receptor asíncrono
    FTimespan ThreadWaitTime = FTimespan::FromMilliseconds(100);
    UDPReceiver = new FUdpSocketReceiver(Socket, ThreadWaitTime, TEXT("UDP RECEIVER"));
    UDPReceiver->OnDataReceived().BindUObject(this, &AUDPReceiver::OnDataReceived);
    UDPReceiver->Start();

    UE_LOG(LogTemp, Warning, TEXT("Receptor UDP iniciado en %s:%d"), *IP, Port);
    return true;
}

void AUDPReceiver::OnDataReceived(const FArrayReaderPtr& Message, const FIPv4Endpoint& EndPt) {
    // Convertir los datos recibidos a FString (UTF8)
    FString ReceivedData = FString(UTF8_TO_TCHAR(Message->GetData()));

    AsyncTask(ENamedThreads::GameThread, [this, ReceivedData]() {
            ProcessMessage(ReceivedData);
        });
}

// Parsear el JSON
void AUDPReceiver::ProcessMessage(const FString& Message) {
    // Mostrar el mensaje en pantalla
    if (GEngine) {
        GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Green, Message);
    }
    UE_LOG(LogTemp, Log, TEXT("Mensaje recibido: %s"), *Message);
}

void AUDPReceiver::EndPlay(const EEndPlayReason::Type EndPlayReason) {
    if (UDPReceiver) {
        UDPReceiver->Stop();
        delete UDPReceiver;
        UDPReceiver = nullptr;
    }

    if (Socket) {
        Socket->Close();
        ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM)->DestroySocket(Socket);
        Socket = nullptr;
    }

    Super::EndPlay(EndPlayReason);
}