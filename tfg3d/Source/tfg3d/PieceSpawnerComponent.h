#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "UDPReceiver.h"
#include "PieceSpawnerComponent.generated.h"


UCLASS( ClassGroup=(Custom), meta=(BlueprintSpawnableComponent) )
class TFG3D_API UPieceSpawnerComponent : public UActorComponent {
	GENERATED_BODY()

public:	
	// Sets default values for this component's properties
	UPieceSpawnerComponent();

public:
    // Mapeo Color pieza -> Actor (configurable en editor)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Pieces Spawner")
    TMap<FString, TSubclassOf<AActor>> ColorToActor;

    // Tamaño de celda en unidades Unreal
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Pieces Spawner")
    float CellSize = 100.0f;

    // Altura Z a la que spawnear
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Pieces Spawner")
    float SpawnHeight = 0.0f;

    // Actualiza el nivel a partir del array de piezas
    UFUNCTION(BlueprintCallable, Category = "Pieces Spawner")
    void UpdatePieces(const TArray<FPieceData>& Pieces);

    // Limpia todas las piezas spawneadas
    UFUNCTION(BlueprintCallable, Category = "Pieces Spawner")
    void ClearAllPieces();

private:
    // Almacena qué actor está en cada celda
    TMap<FIntPoint, AActor*> CurrentActorsByCell;

    FVector CellToWorld(int32 X, int32 Y) const;		
};