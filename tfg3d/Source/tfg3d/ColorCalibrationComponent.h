#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "ColorCalibrationComponent.generated.h"

// Struct del color que detecta OpenCV
USTRUCT(BlueprintType)
struct FColorCalibrationEntry {
    GENERATED_BODY()

    // Nombre del color
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Color")
    FString ColorName = "";

    // Color del rango inferior
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Color")
    FLinearColor ColorLower = FLinearColor::White;

    // Color del rango superior
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Color")
    FLinearColor ColorUpper = FLinearColor::White;

    // Color representativo en RGB (UI)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Color")
    FLinearColor ColorRGB = FLinearColor::White;
};

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class TFG3D_API UColorCalibrationComponent : public UActorComponent {
    GENERATED_BODY()

public:
    UColorCalibrationComponent();

protected:
    virtual void BeginPlay() override;

public:
    // Lista de colores (editable en editor)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calibration")
    TArray<FColorCalibrationEntry> Colors;

    // Si se quiere enviar automáticamente al inicio (delay de medio segundo)
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calibration")
    bool bAutoSendOnStart = true;

    // Envía todos los colores
    UFUNCTION(BlueprintCallable, Category = "Calibration")
    void SendAllColorsToPython();

    // Envía un solo color según su índice
    UFUNCTION(BlueprintCallable, Category = "Calibration")
    void SendSingleColorToPython(int32 Index);

private:
    // Envia un array de colores (JSON)
    void SendColorsToPython(const TArray<FColorCalibrationEntry>& ColorsToSend);

    // Crea el objeto JSON de un color
    TSharedPtr<FJsonObject> BuildColorJsonObject(const FColorCalibrationEntry& Entry);
};