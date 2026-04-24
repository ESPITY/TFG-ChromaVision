#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Networking.h"
#include "UDPReceiver.generated.h"

UCLASS()
class TFG3D_API AUDPReceiver : public AActor
{
    GENERATED_BODY()

public:
    AUDPReceiver();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // Inicia el receptor UDP (devuelve True si el receptor y el socket se iniciaron correctamente)
    UFUNCTION(BlueprintCallable, Category = "UDP")
    bool StartUDPReceiver(const FString& SocketName = TEXT("UDPReceiver"),
                            const FString& IP = TEXT("127.0.0.1"),
                            int32 Port = 5005,
                            int32 BufferSize = 2097152);    // 2*1024*1024 = 2MB

    // Callback que se ejecuta cuando llegan datos (en hilo secundario)
    void OnDataReceived(const FArrayReaderPtr& Message, const FIPv4Endpoint& EndPt);

private:
    FSocket* Socket;
    FUdpSocketReceiver* UDPReceiver;

    // Procesa el mensaje (en hilo principal)
    void ProcessMessage(const FString& Message);
};