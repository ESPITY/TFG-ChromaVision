// ChromaVision - Lucía García Bobillo
// UDPReceiver.h: recibe y parsea la info de las piezas que recibe por UDP
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Networking.h"
#include "UDPReceiver.generated.h"

class UPieceSpawnerComponent;   // Forward Declaration

// Estructura de una pieza (color, x, y)
USTRUCT(BlueprintType)
struct FPieceData {
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Piece")
    FString Color;

    UPROPERTY(BlueprintReadWrite, Category = "Piece")
    int32 X = 0;

    UPROPERTY(BlueprintReadWrite, Category = "Piece")
    int32 Y = 0;
};

UCLASS()
class CHROMAVISIONUE_API AUDPReceiver : public AActor {
    GENERATED_BODY()

public:
    AUDPReceiver();

protected:
    virtual void BeginPlay() override;

public:
    //------------------------ VARIABLES ------------------------
    /* Iniciar el receptor UDP en el BeginPlay */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UDP")
    bool bAutoStart = true;

    /* Nombre del socket */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UDP")
    FString SocketName = TEXT("UDPReceiver");

    /* Direccion IP */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UDP")
    FString IP = TEXT("127.0.0.1");

    /* Puerto UDP */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UDP")
    int32 Port = 5005;

    /* Tamano del buffer de recepcion (bytes) - 2 MB */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UDP")
    int32 BufferSize = 2097152;

    // Referencia al componente que spawnea las piezas
    UPROPERTY(BlueprintReadOnly, Category = "UDP")
    UPieceSpawnerComponent* PieceSpawner = nullptr;

    //------------------------ FUNCIONES ------------------------
    /* Inicia el receptor UDP (devuelve true si el socket y el receptor se crearon correctamente) */
    UFUNCTION(BlueprintCallable, Category = "UDP")
    bool StartUDPReceiver();

    /* Detiene el receptor UDP y libera el socket */
    UFUNCTION(BlueprintCallable, Category = "UDP")
    void StopUDPReceiver();

    /* Devuelve true si el receptor UDP est� actualmente activo y escuchando */
    UFUNCTION(BlueprintPure, Category = "UDP")
    bool IsReceiving() const { return UDPReceiver != nullptr; }

    /* Evento que se dispara cuando se recibe un nuevo array de piezas (incluso vacio) (hilo principal) */
    UFUNCTION(BlueprintImplementableEvent, Category = "UDP")
    void OnPiecesReceived(const TArray<FPieceData>& Pieces);

    // Ejecutado cuando se destruye el actor, detiene el receptor UDP y cierra el socket
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    FSocket* Socket;
    FUdpSocketReceiver* UDPReceiver;

    // Callback que se ejecuta en el hilo secundario cuando llegan datos
    void OnDataReceived(const FArrayReaderPtr& Message, const FIPv4Endpoint& EndPt);

    // Procesa el mensaje (en hilo principal)
    void ProcessMessage(const FString& Message);
};