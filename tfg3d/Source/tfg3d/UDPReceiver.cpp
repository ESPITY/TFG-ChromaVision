#include "UDPReceiver.h"
#include "Async/Async.h"
#include "Json.h"

AUDPReceiver::AUDPReceiver() {
    PrimaryActorTick.bCanEverTick = false;
    Socket = nullptr;
    UDPReceiver = nullptr;
}

void AUDPReceiver::BeginPlay() {
    Super::BeginPlay();

    if (bAutoStart) {
        bool bSuccess = StartUDPReceiver();
        if (!bSuccess) {
            UE_LOG(LogTemp, Error, TEXT("No se pudo iniciar el receptor UDP"));
        }
    }
}

// BufferSize = 2 MB
bool AUDPReceiver::StartUDPReceiver() {
    if (UDPReceiver) {
        UE_LOG(LogTemp, Warning, TEXT("UDPReceiver ya está corriendo"));
        return true;
    }

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
    //FString ReceivedData = FString(UTF8_TO_TCHAR(Message->GetData()));

    int32 NumBytes = Message->Num();
    const uint8* RawData = Message->GetData();
    FString ReceivedData = FString(NumBytes, UTF8_TO_TCHAR(reinterpret_cast<const char*>(RawData)));

    AsyncTask(ENamedThreads::GameThread, [this, ReceivedData]() {
            ProcessMessage(ReceivedData);
        });
}

// Parsear el JSON
void AUDPReceiver::ProcessMessage(const FString& JsonRaw) {
    // Mostrar el mensaje en pantalla
    if (GEngine) {
        //GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Green, JsonRaw);
    }
    //UE_LOG(LogTemp, Log, TEXT("Mensaje recibido: %s"), *JsonRaw);


    // Almacenará el objeto JSON en un puntero compartido
    TSharedPtr<FJsonObject> JsonParsed;
    // Lee el mensaje
    TSharedRef<TJsonReader<>> JsonReader = TJsonReaderFactory<>::Create(JsonRaw);

    // Desserializar (convertir texto a JSON)
    if (!FJsonSerializer::Deserialize(JsonReader, JsonParsed) || !JsonParsed.IsValid()) {
        //FString ExampleString = JsonParsed->GetStringField("exampleString");

        UE_LOG(LogTemp, Warning, TEXT("JSON inválido: %s"), *JsonRaw);
        return;
    }

    // Extraer el PiecesArray
    const TArray<TSharedPtr<FJsonValue>> *PiecesArray;
    if (!JsonParsed->TryGetArrayField(TEXT("pieces"), PiecesArray)) {
        UE_LOG(LogTemp, Warning, TEXT("No se encontró el campo 'pieces'"));
        return;
    }

    // Recorrer cada elemento del PiecesArray
    TArray<FPieceData> PiecesStruct;
    for (const TSharedPtr<FJsonValue> &PieceValue : *PiecesArray) {
        // Cada elemento es un objeto JSON (color, x, y)
        const TSharedPtr<FJsonObject>* PieceObj;
        if (!PieceValue->TryGetObject(PieceObj))
            continue;

        // Guardar el objeto JSON como un elemento del struct - Si el campo no existe, dejan el valor sin cambiar (0 o vacío)
        FPieceData Piece;
        (*PieceObj)->TryGetStringField(TEXT("color"), Piece.Color);
        (*PieceObj)->TryGetNumberField(TEXT("x"), Piece.X);
        (*PieceObj)->TryGetNumberField(TEXT("y"), Piece.Y);

        // Guardar la pieza en el array final
        PiecesStruct.Add(Piece);
    }

    // Si no se ha añadido ninguna pieza salimos
    if (PiecesStruct.Num() == 0) {
        UE_LOG(LogTemp, Warning, TEXT("No se ha recibido ninguna pieza"));
        return;
    }

    // Llamar al evento del BP pasándole el array de estructuras
    OnPiecesReceived(PiecesStruct);
}

void AUDPReceiver::StopUDPReceiver() {
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
}

void AUDPReceiver::EndPlay(const EEndPlayReason::Type EndPlayReason) {
    Super::EndPlay(EndPlayReason);
    StopUDPReceiver();
}