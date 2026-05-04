#include "PieceSpawnerComponent.h"

// Sets default values for this component's properties
UPieceSpawnerComponent::UPieceSpawnerComponent() {
	PrimaryComponentTick.bCanEverTick = false;
}

// ubicar los modelos en el centro de la pieza
FVector UPieceSpawnerComponent::CellToWorld(int32 X, int32 Y) const {
    float CenterX = (X + 0.5f) * CellSize;
    float CenterY = (Y + 0.5f) * CellSize;
    return FVector(CenterX, CenterY, SpawnHeight);
}

// Spawneo de piezas: borra las que sobram, deja las que permanecen y spawnea las que faltan
void UPieceSpawnerComponent::UpdatePieces(const TArray<FPieceData> &Pieces) {
    // Si llega un array vacío, no hay piezas, limpiar todo y salir
    if (Pieces.Num() == 0) {
        ClearAllPieces();
        return;
    }

    // Guardar las coordenadas de las nuevas celdas en un set sin duplicados y más fácil de recorrer
    TSet<FIntPoint> NewCells;
    for (const FPieceData& Piece : Pieces)
        NewCells.Add(FIntPoint(Piece.X, Piece.Y));

    // Destruir actores que ya no están en las nuevas piezas
    for (auto ActorIt = CurrentActorsByCell.CreateIterator(); ActorIt; ++ActorIt) {
        auto CellKey = ActorIt->Key;
        auto ActorValue = ActorIt->Value;
        if (!NewCells.Contains(CellKey)) {
            if (ActorValue)
                ActorValue->Destroy();
            ActorIt.RemoveCurrent();
        }
    }

    // Spawnear o mantener los que sí están
    for (const FPieceData& Piece : Pieces) {
        // Mirar que actor corresponde a cada pieza (color)
        FIntPoint Cell(Piece.X, Piece.Y);
        TSubclassOf<AActor>* ActorClass = ColorToActor.Find(Piece.Color);
        if (!ActorClass) {
            UE_LOG(LogTemp, Warning, TEXT("Color no mapeado: %s"), *Piece.Color);
            continue;
        }

        AActor *ExistingActor = CurrentActorsByCell.FindRef(Cell); // Buscar si ya existe un actor en la celda

        // Si ya existe y es de la misma clase, se mantiene
        if (ExistingActor && ExistingActor->GetClass() == *ActorClass)
            continue;

        // Si ya existe pero cmabió de clase, se sestruye
        if (ExistingActor)
            ExistingActor->Destroy();

        // Spawnear nuevo
        AActor* NewActor = GetWorld()->SpawnActor<AActor>(*ActorClass, CellToWorld(Cell.X, Cell.Y), FRotator::ZeroRotator);
        CurrentActorsByCell.Add(Cell, NewActor);
    }
}

void UPieceSpawnerComponent::ClearAllPieces() {
    for (auto& Pair : CurrentActorsByCell) {
        if (Pair.Value)
            Pair.Value->Destroy();
    }
    CurrentActorsByCell.Empty();
}