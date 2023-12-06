#include <Wire.h>
#include <BH1750.h>
#include <LiquidCrystal_I2C.h>
#include <Adafruit_INA219.h>
#include <Servo.h>

Adafruit_INA219 ina219;
LiquidCrystal_I2C lcd(0x27,20,4);
Servo myServo1;

#define BH1750_POWER_DOWN 0x00
#define BH1750_POWER_ON 0x01
#define BH1750_RESET 0x07

#define CONTINUOUS_HIGH_RES_MODE 0x10
#define CONTINUOUS_HIGH_RES_MODE_2 0x11
#define CONTINUOUS_LOW_RES_MODE 0x13
#define ONE_TIME_HIGH_RES_MODE 0x20
#define ONE_TIME_HIGH_RES_MODE_2 0x21
#define ONE_TIME_LOW_RES_MODE 0x23

#define BH1750_1_ADDRESS 0x23
#define BH1750_2_ADDRESS 0x5C

#define LED_PIN 13

union {
  struct {
    float send_mode;
    float send_segmentation;
  } param;
  byte packet[8];
} dataRecv;

char chara;
bool valid = false;
int comIndex = 0;
int mode, segmen;

int16_t s_en = 4;
int16_t s0 = 5;
int16_t s1 = 6;
int16_t s2 = 7;

double lux_dalam, lux_luar;

int16_t RawData;
int16_t SensorValue[4];

const int setpoint = 300;
const int lamp_f = 3;
const int lamp_m =2;
const int lamp_b =8;
const int PWM = 11;

int angle;

float error, cumError, lastError, output; 

long currentTime_sensor, elapsedTime_sensor;
long currentTime_i,  previousTime_i;
long serialtime, timebefore;
double elapsedTime_i;
long time_ina219, Prevtime_ina219;
float power;
float power_mW = 0;

void setup() {
  Wire.begin();
  Serial.begin(9600);
  myServo1.attach(9);
  myServo1.write(0);
 
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0,1);
  lcd.print("    RUANG  KELAS  ");
  lcd.setCursor(0,2);
  lcd.print("       PINTAR     ");
  delay(2000);
  lcd.clear();

  pinMode(s_en, OUTPUT);
  pinMode(s0, OUTPUT);
  pinMode(s1, OUTPUT);
  pinMode(s2, OUTPUT);

  pinMode(lamp_f,OUTPUT);
  pinMode(lamp_m,OUTPUT);
  pinMode(lamp_b,OUTPUT);
  pinMode(PWM,OUTPUT);

  digitalWrite(s_en, HIGH);
  digitalWrite(s0, HIGH);
  digitalWrite(s1, HIGH);
  digitalWrite(s2, HIGH);

  if (! ina219.begin()) {
    Serial.println("Failed to find INA219 chip");
    while (1) { delay(10); }
  }
}


void loop() {
  digitalWrite(s_en, LOW);
  read_bh1750();
  recvData();

  lcd.setCursor(0,1);
  lcd.print ("Lux Dalam= ");
  lcd.print(lux_dalam);
  lcd.setCursor(0,2);
  lcd.print ("Out i = ");
  lcd.print(output);
  lcd.setCursor(0,3);
  lcd.print ("Lux Luar = ");
  lcd.print(lux_luar);

  if (mode == 0 && segmen == 0) {
    lcd.setCursor(0,0);
    lcd.print("Mode = ");
    lcd.print("Off       ");
    digitalWrite(lamp_f,  1);
    digitalWrite(lamp_m,  1);
    digitalWrite(lamp_b,  1);
  }
  else if (mode == 1 && segmen == 0) {
    power = ((output/255*5)*(output/255*5))/33.3333333333333*1000;
    lcd.setCursor(0,0);
    lcd.print("Mode = ");
    lcd.print("Default  ");
    analogWrite(PWM, 150);
    digitalWrite(lamp_f,  0);
    digitalWrite(lamp_m,  1);
    digitalWrite(lamp_b,  1);
  }
  else if (mode == 2 && segmen == 1) {
    power = ((output/255*5)*(output/255*5))/33.3333333333333*1000;
    Servo();
    lcd.setCursor(0,0);
    lcd.print("Mode = ");
    lcd.print("Smart D  ");
    integral(0.278);
    analogWrite(PWM, output);
    digitalWrite(lamp_f,  0);
    digitalWrite(lamp_m,  1);
    digitalWrite(lamp_b,  1);
  }
  else if (mode == 2 && segmen == 2) {
    power = ((output/255*5)*(output/255*5))/16.66666667*1000;
    Servo();
    lcd.setCursor(0,0);
    lcd.print("Mode = ");
    lcd.print("Smart DT ");
    integral(0.255);
    analogWrite(PWM, output);
    digitalWrite(lamp_f,  0);
    digitalWrite(lamp_m,  0);
    digitalWrite(lamp_b,  1);
  }
  else if (mode == 2 && segmen == 3){
    power = ((output/255*5)*(output/255*5))/11.11111*1000;
    Servo();
    lcd.setCursor(0,0);
    lcd.print("Mode = ");
    lcd.print("Smart DTB");
    integral(0.222);
    analogWrite(PWM, output);
    digitalWrite(lamp_f,  0);
    digitalWrite(lamp_m,  0);
    digitalWrite(lamp_b,  0);
  }
}

void Servo() {
  if (lux_luar>=3000){
      angle = 45;
      myServo1.write(angle);
    }
    else {
      angle = 0;
      myServo1.write(angle);
    }
}

void init_BH1750(int ADDRESS, int MODE){
  Wire.beginTransmission(ADDRESS);
  Wire.write(MODE);
  Wire.endTransmission(true);
}


void RawData_BH1750(int ADDRESS){
  Wire.beginTransmission(ADDRESS);
  Wire.requestFrom(ADDRESS,2,true);
  RawData = Wire.read() << 8 | Wire.read();
  Wire.endTransmission(true);
}


int readMux(int channel) { 
  int controlPin[] = {s0, s1, s2}; 
  int muxChannel[8][3] = { 
    {0,0,0},
    {1,0,0},
    {0,1,0},
    {1,1,0},
    {0,0,1},
    {1,0,1},
    {0,1,1},
    {1,1,1},
  };
  for(int i = 0; i < 3; i++){
    digitalWrite(controlPin[i], muxChannel[channel][i]); 
  }   
}


void read_bh1750() {
    currentTime_sensor = millis();
    if ((currentTime_sensor - elapsedTime_sensor >= 1) && (currentTime_sensor - elapsedTime_sensor <= 200)){
    readMux(0);
    init_BH1750(BH1750_1_ADDRESS, CONTINUOUS_HIGH_RES_MODE);
    RawData_BH1750(BH1750_1_ADDRESS);
    SensorValue[0] = RawData;  
    lux_dalam =  (SensorValue[0])*1.1;
  }
  else if ((currentTime_sensor - elapsedTime_sensor >= 210) && (currentTime_sensor - elapsedTime_sensor <= 400)){
    readMux(2);
    init_BH1750(BH1750_1_ADDRESS, CONTINUOUS_HIGH_RES_MODE);
    RawData_BH1750(BH1750_1_ADDRESS);
    SensorValue[2] = RawData;
    lux_luar = SensorValue[2]* 1.0606;
    
  }
  else if (currentTime_sensor - elapsedTime_sensor > 400) {
    elapsedTime_sensor = currentTime_sensor;
  }
}


void integral(float Ki) {
  currentTime_i = millis();
  elapsedTime_i = double (currentTime_i - previousTime_i)/1000 ;
  error = setpoint - lux_dalam;
  output = output + (Ki * error *elapsedTime_i) ;
  if (output >255) {
    output = 255;
  }
  else if (output <0){
    output = 0;
  }
  previousTime_i = currentTime_i;
}


void recvData() {
  if(Serial.available()) {
    chara = Serial.read();
    if (chara == '$') {
      comIndex = 0;
      valid = true;
      mode = dataRecv.param.send_mode;
      segmen = dataRecv.param.send_segmentation;
    }
    else if (valid) {
      dataRecv.packet[comIndex] = chara;
      comIndex++;
      if (comIndex >= sizeof(dataRecv.packet)) {
        valid = false;}
    }
  }
}