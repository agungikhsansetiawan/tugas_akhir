#include <LiquidCrystal_I2C.h>
#include <OneWire.h>
#include <DallasTemperature.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

OneWire oneWire1(7);
DallasTemperature sensors1(&oneWire1);

union {
  struct {
    float send_mode;
    float send_people;
  } param;
  byte packet[8];
} dataRecv;

char chara;
bool valid = false;
int comIndex = 0;
int mode, people;

const int MOTOR_PIN_R_EN =  9;
const int MOTOR_PIN_L_EN = 10;
const int MOTOR_PIN_R = 11;
const int MOTOR_PIN_L = 12;

const int MOTOR_PIN_R_EN_2 = 4;
const int MOTOR_PIN_L_EN_2 = 5;
const int MOTOR_PIN_R_2 = 6;
const int MOTOR_PIN_L_2 = 7;

const int HEATER_PIN = 3;
int pwmValues[] = {136, 136, 136, 136, 136, 136, 140, 145, 152, 158, 164, 168, 174, 178, 182, 186, 189, 193, 197, 200};
int pwm;

float suhu;

unsigned long currentTime, previousTime;
double deltaTime;
double error, lasterror, delta_error;

double integral, proportional, derivative;
int out_pi, pi_total;


void setup() {
  Serial.begin(9600);
  sensors1.begin();

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("  RUANG  KELAS  ");
  lcd.setCursor(0,1);
  lcd.print("     PINTAR     ");
  delay(2000);
  lcd.clear();

  pinMode(MOTOR_PIN_R, OUTPUT);
  pinMode(MOTOR_PIN_L, OUTPUT);
  pinMode(MOTOR_PIN_R_EN, OUTPUT);
  pinMode(MOTOR_PIN_L_EN, OUTPUT);
  pinMode(MOTOR_PIN_R_2, OUTPUT);
  pinMode(MOTOR_PIN_L_2, OUTPUT);
  pinMode(MOTOR_PIN_R_EN_2, OUTPUT);
  pinMode(MOTOR_PIN_L_EN_2, OUTPUT);
  analogWrite(MOTOR_PIN_R, 0);
  analogWrite(MOTOR_PIN_L, 0);
  analogWrite(MOTOR_PIN_R_2, 0);
  analogWrite(MOTOR_PIN_L_2, 0);
  digitalWrite(MOTOR_PIN_R_EN, HIGH);
  digitalWrite(MOTOR_PIN_L_EN, HIGH); 
  digitalWrite(MOTOR_PIN_R_EN_2, HIGH);
  digitalWrite(MOTOR_PIN_L_EN_2, HIGH);

  pinMode(HEATER_PIN, OUTPUT);
  analogWrite(HEATER_PIN, 0);
}


void loop() {
  sensors1.requestTemperatures();
  suhu = sensors1.getTempCByIndex(0);
  recvData();

  lcd.setCursor(0,1);
  lcd.print ("Suhu = ");
  lcd.print(suhu);


  if (mode == 0) {
    lcd.setCursor(0,0);
    lcd.print("Mode = ");
    lcd.print("Off    ");
    analogWrite(MOTOR_PIN_R, 0);
    analogWrite(MOTOR_PIN_R_2, 0);
    analogWrite(HEATER_PIN, 0);
  }
  else if (mode == 1) {
    lcd.setCursor(0,0);
    lcd.print("Mode = ");
    lcd.print("Default");
    HEATER();
    COOLER(25, 298.4, 4.07, 0);
    analogWrite(MOTOR_PIN_R, pi_total);
    analogWrite(MOTOR_PIN_R_2, 0);
  }
  else if (mode == 2) {
    lcd.setCursor(0,0);
    lcd.print("Mode = ");
    lcd.print("Smart  ");
    HEATER();
    COOLER(23, 169.8, 1.08, 0);
    analogWrite(MOTOR_PIN_R, pi_total);
    analogWrite(MOTOR_PIN_R_2, pi_total);
  }
}


void COOLER(int spsuhu, float kp, float ki, float kd) {
  currentTime = millis();
  deltaTime = double(currentTime - previousTime) / 1000;
  error = suhu - spsuhu;
  delta_error = error - lasterror;
  proportional = kp * error;
  integral = integral + (ki * error * deltaTime);
  derivative = kd * (delta_error/deltaTime);
  if (integral > 254){
    integral = 254;
    }
  else if (integral < 0){
    integral = 0;
    }
  previousTime = currentTime;
  out_pi = proportional + integral + derivative ;
  pi_total = out_pi;
  pi_total = constrain(pi_total, 30, 254);
}


void HEATER() {
  if (people < 1) {
    analogWrite(HEATER_PIN, 0);
  }
  else if (people >= 1 && people <= 40 && people % 2 == 1) {
    pwm = pwmValues[((people - 1) / 2) - 1];
    analogWrite(HEATER_PIN, pwm);
  }
  else if (people >= 1 && people <= 40 && people % 2 == 0) {
    pwm = pwmValues[((people) / 2) - 1];
    analogWrite(HEATER_PIN, pwm);
  }
}


void recvData() {
  if(Serial.available()) {
    chara = Serial.read();
    if (chara == '$') {
      comIndex = 0;
      valid = true;
      mode = dataRecv.param.send_mode;
      people = dataRecv.param.send_people;
    }
    else if (valid) {
      dataRecv.packet[comIndex] = chara;
      comIndex++;
      if (comIndex >= sizeof(dataRecv.packet)) {
        valid = false;}
    }
  }
}