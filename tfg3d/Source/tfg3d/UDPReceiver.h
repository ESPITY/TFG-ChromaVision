#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Networking.h"
#include "UDPReceiver.generated.h"

// Struct de 
USTRUCT(BlueprintType)
struct FPieceData {
    GENERATED_USTRUCT_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Piece")
    FString Color;

    UPROPERTY(BlueprintReadWrite, Category = "Piece")
    float X;

    UPROPERTY(BlueprintReadWrite, Category = "Piece")
    float Y;
};

UCLASS()
class TFG3D_API AUDPReceiver : public AActor {
    GENERATED_BODY()

public:
    AUDPReceiver();

protected:
    virtual void BeginPlay() override;

public:
    //------------------------ VARIABLES ------------------------
    // Iniciar el UDPReceiver en el BeginPlay
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UDP")
    bool bAutoStart = true;

    // Nombre del socket
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UDP")
    FString SocketName = TEXT("UDPReceiver");

    // Dirección IP
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UDP")
    FString IP = TEXT("127.0.0.1");

    // Puerto UDP
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UDP")
    int32 Port = 5005;

    // Tamaño del buffer de recepción (en bytes)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UDP")
    int32 BufferSize = 2097152; // 2 MB

    //------------------------ FUNCIONES ------------------------
    // Inicia el receptor UDP (devuelve True si el receptor y el socket se iniciaron correctamente)
    UFUNCTION(BlueprintCallable, Category = "UDP")
    bool StartUDPReceiver();

    // Detiene el UDPReceiver y libera el socket
    UFUNCTION(BlueprintCallable, Category = "UDP")
    void StopUDPReceiver();

    UFUNCTION(BlueprintImplementableEvent, Category = "UDP")
    void OnPiecesReceived(const TArray<FPieceData>& Pieces);

    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    FSocket* Socket;
    FUdpSocketReceiver* UDPReceiver;

    // Callback que se ejecuta cuando llegan datos (en hilo secundario)
    void OnDataReceived(const FArrayReaderPtr& Message, const FIPv4Endpoint& EndPt);

    // Procesa el mensaje (en hilo principal)
    void ProcessMessage(const FString& Message);
};