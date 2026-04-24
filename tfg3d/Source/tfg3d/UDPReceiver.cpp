// Fill out your copyright notice in the Description page of Project Settings.


#include "UDPReceiver.h"

// Sets default values
AUDPReceiver::AUDPReceiver()
{
 	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;

}

// Called when the game starts or when spawned
void AUDPReceiver::BeginPlay()
{
	Super::BeginPlay();
	
}

// Called every frame
void AUDPReceiver::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

}

