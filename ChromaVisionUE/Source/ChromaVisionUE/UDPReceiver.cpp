// UDPReceiver.cpp
#include "UDPReceiver.h"
#include "Async/Async.h"
#include "Json.h"
#include "PieceSpawnerComponent.h"

AUDPReceiver::AUDPReceiver() {
    PrimaryActorTick.bCanEverTick = false;
    Socket = nullptr;
    UDPReceiver = nullptr;
}

void AUDPReceiver::BeginPlay() {
    Super::BeginPlay();

    // Obtiene el componente que spawnea piezas
    PieceSpawner = FindComponentByClass<UPieceSpawnerComponent>();
    if (!PieceSpawner) {
        UE_LOG(LogTemp, Warning, TEXT("No se encontró PieceSpawnerComponent"));
    }

    // Si está activo inicia el receptor UDP en el Begin Play
    if (bAutoStart) {
        bool bSuccess = StartUDPReceiver();
        if (!bSuccess) {
            UE_LOG(LogTemp, Error, TEXT("No se pudo iniciar el receptor UDP"));
        }
    }
}

/* Inicia el receptor UDP: crea un socket UDP (IP, puerto),
 * configura el receptor asíncrono en un hilo secundario
 * y anlaza el callback OnPiecesReceived */
bool AUDPReceiver::StartUDPReceiver() {
    // Comprobar si el receptor UDP ya está activo
    if (UDPReceiver) {
        UE_LOG(LogTemp, Warning, TEXT("Receptor UDP ya está activo"));
        return true;
    }

    // Validar la dirección IP
    FIPv4Address Addr;
    if (!FIPv4Address::Parse(IP, Addr)) {
        UE_LOG(LogTemp, Error, TEXT("IP inválida: %s"), *IP);
        return false;
    }

    FIPv4Endpoint Endpoint(Addr, Port);

    // Crear el socket UDP
    Socket = FUdpSocketBuilder(*SocketName)
        .AsNonBlocking()
        .AsReusable()
        .BoundToEndpoint(Endpoint)
        .WithReceiveBufferSize(BufferSize);

    if (!Socket) {
        UE_LOG(LogTemp, Error, TEXT("No se pudo crear el socket"));
        return false;
    }

    // Crear el receptor UDP asíncrono (hiilo secundario)
    FTimespan ThreadWaitTime = FTimespan::FromMilliseconds(100);
    UDPReceiver = new FUdpSocketReceiver(Socket, ThreadWaitTime, TEXT("UDP RECEIVER"));
    UDPReceiver->OnDataReceived().BindUObject(this, &AUDPReceiver::OnDataReceived);
    UDPReceiver->Start();

    UE_LOG(LogTemp, Warning, TEXT("Receptor UDP iniciado en %s:%d"), *IP, Port);
    return true;
}

/* Callback ejecutado en el hilo secundario cuando llega datos: convierte bytes a FString y
 * llama a ProcessMessage en el hilo principal */
void AUDPReceiver::OnDataReceived(const FArrayReaderPtr& Message, const FIPv4Endpoint& EndPt) {
    int32 NumBytes = Message->Num();
    const uint8* RawData = Message->GetData();
    FString ReceivedData = FString(NumBytes, UTF8_TO_TCHAR(reinterpret_cast<const char*>(RawData)));

    // Limpiar todos los caracteres que haya después de la última llave "}" (aparece basura durante la comunicación UDP)
    int32 LastBracket = -1;
    if (!ReceivedData.FindLastChar('}', LastBracket)) return;
    ReceivedData = ReceivedData.Left(LastBracket + 1);

    AsyncTask(ENamedThreads::GameThread, [this, ReceivedData]() { ProcessMessage(ReceivedData); });
}

/* Procesa el mensaje JSON en el hilo principal: parsea, extrae array "pieces", convierte cada objeto a
 * FPieceData, notifica a Blueprint mediante OnPiecesReceived y actualiza el PieceSpawnerComponent si existe */
void AUDPReceiver::ProcessMessage(const FString& JsonRaw) {
    // Verificar que el objeto sigue vivo y que el mundo no está siendo desmontado
    if (!IsValid(this) || !GetWorld() || GetWorld()->bIsTearingDown) {
        UE_LOG(LogTemp, Warning, TEXT("ProcessMessage abortado: objeto inválido o mundo en destruído"));
        return;
    }

    // Almacenará el objeto JSON parseado
    TSharedPtr<FJsonObject> JsonParsed;
    // Lee el mensaje
    TSharedRef<TJsonReader<>> JsonReader = TJsonReaderFactory<>::Create(JsonRaw);

    // Deserializar (convertir texto a JSON)
    if (!FJsonSerializer::Deserialize(JsonReader, JsonParsed) || !JsonParsed.IsValid()) {
        UE_LOG(LogTemp, Warning, TEXT("JSON inválido: %s"), *JsonRaw);
        return;
    }

    // Extraer el array "pieces"
    const TArray<TSharedPtr<FJsonValue>> *PiecesArray;
    if (!JsonParsed->TryGetArrayField(TEXT("pieces"), PiecesArray)) {
        UE_LOG(LogTemp, Warning, TEXT("No se encontró el campo 'pieces' en el JSON"));
        return;
    }

    // Convertir el array JSON a un array de estructuras de piezas
    TArray<FPieceData> PiecesStruct;
    for (const TSharedPtr<FJsonValue>& PieceValue : *PiecesArray) {
        // Cada elemento del array debe ser un objeto JSON (color, x, y)
        const TSharedPtr<FJsonObject>* PieceObj;
        if (!PieceValue->TryGetObject(PieceObj))
            continue;

        // Extraer datos del objeto JSON (si el campo no existe, deja el valor sin cambios)
        FPieceData Piece;
        (*PieceObj)->TryGetStringField(TEXT("color"), Piece.Color);
        (*PieceObj)->TryGetNumberField(TEXT("x"), Piece.X);
        (*PieceObj)->TryGetNumberField(TEXT("y"), Piece.Y);

        PiecesStruct.Add(Piece);    // Añadir la pieza al array final
    }

    // Array vacío, no se han recibido piezas
    if (PiecesStruct.Num() == 0) {
        UE_LOG(LogTemp, Warning, TEXT("No se ha recibido ninguna pieza"));
    }

    // Llamar al evento del BP pasándole el array de estructuras
    OnPiecesReceived(PiecesStruct);

    // Si existe el componente PieceSpawnerComponent actualizarlo
    if (PieceSpawner && IsValid(PieceSpawner)) {
        PieceSpawner->UpdatePieces(PiecesStruct);
    }
}

// Detiene el receptor UDP y cierra y destruye el socket UDP
void AUDPReceiver::StopUDPReceiver() {
    if (UDPReceiver) {
        UDPReceiver->Stop();
        delete UDPReceiver;
        UDPReceiver = nullptr;
        UE_LOG(LogTemp, Warning, TEXT("Receptor UDP detenido"));
    }

    if (Socket) {
        Socket->Close();
        ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM)->DestroySocket(Socket);
        Socket = nullptr;
    }
}

// Se llama cuando el actor se destruye o se cambia de nivel, asegura el cierre
void AUDPReceiver::EndPlay(const EEndPlayReason::Type EndPlayReason) {
    StopUDPReceiver();  // Detener el receptor UDP inmediatamente para evitar la llegada de mensajes
    PieceSpawner = nullptr;
    Super::EndPlay(EndPlayReason);
}