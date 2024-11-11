int pirPin = 2;


void setup() {
  pinMode(pirPin, INPUT);

  Serial.begin(9600);
  delay(100);  // Esperar 10 segundos para estabilizar el PIR
}

void loop() {
  int pirState = digitalRead(pirPin);
  Serial.print("Estado del sensor PIR: "); // Imprimir el estado del sensor en el Serial Monitor
  Serial.println(pirState);

  if (pirState == HIGH) {

    Serial.println("Movimiento detectado");
  } else {

  }
  delay(100); // Esperar 100 ms
}
