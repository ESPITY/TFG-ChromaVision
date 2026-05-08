#include "ColorCalibrationComponent.h"
#include "Sockets.h"
#include "Common/UdpSocketBuilder.h"
#include "Json.h"
#include "JsonUtilities.h"
#include "TimerManager.h"

UColorCalibrationComponent::UColorCalibrationComponent() {
    PrimaryComponentTick.bCanEverTick = false;
}

void UColorCalibrationComponent::BeginPlay() {
    Super::BeginPlay();

    // Si se quiere enviar automáticamente al inicio (delay de medio segundo)
    if (bAutoSendOnStart) {
        FTimerHandle TimerHandle;
        GetWorld()->GetTimerManager().SetTimer(TimerHandle, [this]() {
                SendAllColorsToPython();
            }, 0.5f, false);
    }
}

// Enviar todos los colores
void UColorCalibrationComponent::SendAllColorsToPython() {
    SendColorsToPython(Colors);
}

// Enviar un color
void UColorCalibrationComponent::SendSingleColorToPython(int32 Index) {
    if (!Colors.IsValidIndex(Index)) return;
    TArray<FColorCalibrationEntry> SingleArray;
    SingleArray.Add(Colors[Index]);
    SendColorsToPython(SingleArray);
}

// Envío de color/es
void UColorCalibrationComponent::SendColorsToPython(const TArray<FColorCalibrationEntry>& ColorsToSend) {
    if (ColorsToSend.Num() == 0) return;

    FIPv4Address PythonAddr;
    FIPv4Address::Parse(TEXT("127.0.0.1"), PythonAddr);
    FIPv4Endpoint Endpoint(PythonAddr, 5006);

    // Socket
    FSocket* SendSocket = FUdpSocketBuilder(TEXT("ColorCalibrationSender")).AsReusable().Build();
    if (!SendSocket) {
        //UE_LOG(LogTemp, Error, TEXT("ColorCalibrationComponent: No se pudo crear el socket de envío"));
        return;
    }

    // Construir objeto JSON raíz
    TSharedPtr<FJsonObject> RootObj = MakeShareable(new FJsonObject);
    RootObj->SetStringField("command", "set_multiple_ranges");
    TArray<TSharedPtr<FJsonValue>> ColorsArray;

    for (const FColorCalibrationEntry& Entry : ColorsToSend) {
        TSharedPtr<FJsonObject> ColorObj = BuildColorJsonObject(Entry);
        if (ColorObj.IsValid()) {
            ColorsArray.Add(MakeShareable(new FJsonValueObject(ColorObj)));
        }
    }

    if (ColorsArray.Num() == 0) return;

    RootObj->SetArrayField("colors", ColorsArray);

    // Serializar JSON
    FString OutputString;
    TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutputString);
    FJsonSerializer::Serialize(RootObj.ToSharedRef(), Writer);

    // Enviar (bSuccess indica si se envió bien)
    int32 BytesSent;
    bool bSuccess = SendSocket->SendTo(
        (uint8*)TCHAR_TO_UTF8(*OutputString),
        OutputString.Len(),
        BytesSent,
        *Endpoint.ToInternetAddr()
    );

    SendSocket->Close();
    ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM)->DestroySocket(SendSocket);
}

// Crear el objeto JSON de un color
TSharedPtr<FJsonObject> UColorCalibrationComponent::BuildColorJsonObject(const FColorCalibrationEntry& Entry) {
    TSharedPtr<FJsonObject> JsonObj = MakeShareable(new FJsonObject);

    // Nombre
    if (Entry.ColorName.IsEmpty()) return nullptr;
    JsonObj->SetStringField("name", Entry.ColorName);

    // Rango inferior (H, S, V) – usar los canales R,G,B de FLinearColor
    FLinearColor HSVLower = Entry.ColorLower.LinearRGBToHSV();
    JsonObj->SetNumberField("lower_h", HSVLower.R);
    JsonObj->SetNumberField("lower_s", HSVLower.G);
    JsonObj->SetNumberField("lower_v", HSVLower.B);

    // Rango superior
    FLinearColor HSVUpper = Entry.ColorUpper.LinearRGBToHSV();
    JsonObj->SetNumberField("upper_h", HSVUpper.R);
    JsonObj->SetNumberField("upper_s", HSVUpper.G);
    JsonObj->SetNumberField("upper_v", HSVUpper.B);

    // Color representativo (RGB)
    JsonObj->SetNumberField("r", Entry.ColorRGB.R * 255.0f);
    JsonObj->SetNumberField("g", Entry.ColorRGB.G * 255.0f);
    JsonObj->SetNumberField("b", Entry.ColorRGB.B * 255.0f);

    return JsonObj;
}