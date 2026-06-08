// PieceSpawnerComponent.h: gestiona el spawneo de actores a partir de piezas recibidas
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "UDPReceiver.h"
#include "PieceSpawnerComponent.generated.h"


UCLASS( ClassGroup=(Custom), meta=(BlueprintSpawnableComponent) )
class TFG3D_API UPieceSpawnerComponent : public UActorComponent {
	GENERATED_BODY()

public:
	UPieceSpawnerComponent();

public:
    //------------------------ VARIABLES ------------------------
    /* Mapeo de color(string) de la pieza a clase actor que se spawnea(configurable en editor) */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Piece Spawner")
    TMap<FString, TSubclassOf<AActor>> ColorToActor;

    /* Tamaño de celda en unidades Unreal (distancia entre centros) */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Piece Spawner", meta = (ClampMin = "1"))
    float CellSize = 100.0f;

    /* Altura Z a la que spawnearán los actores */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Piece Spawner")
    float SpawnHeight = 0.0f;

    //------------------------ FUNCIONES ------------------------
    /* Actualiza el nivel a partir del array de piezas: elimina actores en celdas que ya no
     * tienen pieza, spawnea nuevos actores o mantiene los existentes si la clase coincide */
    UFUNCTION(BlueprintCallable, Category = "Piece Spawner")
    void UpdatePieces(const TArray<FPieceData>& Pieces);

    // Limpia todas las piezas spawneadas (destruye todos los actores)
    UFUNCTION(BlueprintCallable, Category = "Piece Spawner")
    void ClearAllPieces();

private:
    // Almacena qué actor está en cada celda (clave = celda, valor = actor)
    TMap<FIntPoint, AActor*> CurrentActorsByCell;

    // Convierte coordenadas de celda (X,Y) a posición en el mundo (centro de la celda)
    FVector CellToWorld(int32 X, int32 Y) const;		
};