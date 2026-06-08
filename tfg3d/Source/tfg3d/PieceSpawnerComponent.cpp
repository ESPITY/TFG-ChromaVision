// PieceSpawnerComponent.cpp
#include "PieceSpawnerComponent.h"

UPieceSpawnerComponent::UPieceSpawnerComponent() {
	PrimaryComponentTick.bCanEverTick = false;
}

// Convierte coordenadas de celda a absolutas en el mundo y centra el actor en la celda
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
        // Mirar que clase de actor está asginada al color de la pieza
        FIntPoint Cell(Piece.X, Piece.Y);
        TSubclassOf<AActor>* ActorClass = ColorToActor.Find(Piece.Color);
        if (!ActorClass) {
            UE_LOG(LogTemp, Warning, TEXT("Color no mapeado: %s"), *Piece.Color);
            continue;
        }

        AActor *ExistingActor = CurrentActorsByCell.FindRef(Cell); // Buscar si ya existe un actor en la celda

        // Si la clase asignada es None, no debe haber actor en esa celda. Si ya había uno se borra y no se hace nada más
        if (!*ActorClass) {
            if (ExistingActor) {
                ExistingActor->Destroy();
                CurrentActorsByCell.Remove(Cell);
            }
            continue;
        }

        // Si ya existe y es de la misma clase, se mantiene
        if (ExistingActor && ExistingActor->GetClass() == *ActorClass)
            continue;

        // Si ya existe pero cmabió de clase, se sestruye
        if (ExistingActor)
            ExistingActor->Destroy();

        // Spawnear nuevo actor
        if (!GetWorld()) {
            UE_LOG(LogTemp, Error, TEXT("No se pudo obtener el mundo para spawnear el actor"));
            continue;
        }
        AActor* NewActor = GetWorld()->SpawnActor<AActor>(*ActorClass, CellToWorld(Cell.X, Cell.Y), FRotator::ZeroRotator);
        if (NewActor) {
            CurrentActorsByCell.Add(Cell, NewActor);
        } else {
            UE_LOG(LogTemp, Error, TEXT("Fallo al spawnear actor de clase %s"), *(*ActorClass)->GetName());
        }
    }
}

// Elimina todos los actores spawneados y vacía el mapa
void UPieceSpawnerComponent::ClearAllPieces() {
    for (auto& Pair : CurrentActorsByCell) {
        if (Pair.Value)
            Pair.Value->Destroy();
    }
    CurrentActorsByCell.Empty();
}