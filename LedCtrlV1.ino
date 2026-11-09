
int FREQUENCY = 100;

void setup()
{
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);

  Serial.begin(9600);
  Serial.setTimeout(20);

  digitalWrite(5, HIGH);
}

void updateFrequency()
{
  if (Serial.available() > 0) {
    int value = Serial.parseInt();

    if (value >= 1 && value <= 1000) {
      FREQUENCY = value;

      Serial.print("FREQUENCY = ");
      Serial.println(FREQUENCY);
    }
  }
}

void loop()
{
  for (int brightness = 0; brightness <= 255; brightness += 10) {
    updateFrequency();
    analogWrite(6, brightness);
    delay(FREQUENCY);
  }

  for (int brightness = 255; brightness >= 0; brightness -= 10) {
    updateFrequency();
    analogWrite(6, brightness);
    delay(FREQUENCY);
  }
}
