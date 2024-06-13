#include <Stepper.h>


// 스텝 모터 설정
int STEPS_PER_REVOLUTION = 200;
#define STEP_PIN1 8
#define STEP_PIN2 9
#define STEP_PIN3 10
#define STEP_PIN4 11

Stepper stepper(STEPS_PER_REVOLUTION, STEP_PIN1, STEP_PIN3, STEP_PIN2, STEP_PIN4);

int led_1 = 3;
int led_2 = 5;

int TRIG1 = 7;
int ECHO1 = 6;

//int TRIG2 = 3;
//int ECHO2 = 2;

int led_run = 0;

// 타이머 설정
unsigned long previous_time = 0;
const unsigned long check = 400; // 초음파 센서를 체크하는 주기
const unsigned long motor_stop = 5000;

bool motor_running = true;
bool motor_direction_forward = true;

bool shouldrun = false;



void setup() {
  Serial.begin(9600);
  
  //stepper.setSpeed(80); // 모터 속도 설정 (RPM)
  pinMode(TRIG1, OUTPUT);
  pinMode(ECHO1, INPUT);

  //pinMode(TRIG2, OUTPUT);
  //pinMode(ECHO2, INPUT);

  pinMode(led_1, OUTPUT);
  pinMode(led_2, OUTPUT);

  while (!shouldrun) {
    if (Serial.available()){
      String cmd = Serial.readString();
      cmd.trim();
      if (cmd == "login"){
        shouldrun = true;
      }
    }
  }
}

void loop() {
  if (shouldrun){
    if(Serial.available()){
     String cmd = Serial.readString(); // 명령어를 문자열로 읽음
     if(cmd.indexOf(" ") != -1){               // cmd에 띄어쓰기가 있으면 
      int split = cmd.indexOf(" ");
      //Serial.println(cmd.substring(0,split));
      if (cmd.substring(0,split) == "led"){
        led_run = cmd.substring(split+1).toInt();
        // led_run이 커질수록 민감해짐
        // 500~600 정도가 적당
      }
      if (cmd.substring(0,split) == "motor"){
        int speed = cmd.substring(split+1).toInt();
        stepper.setSpeed(speed);
        // 150까지 기본 80
      }
     }
     else if(cmd == "stop"){                   // 모터 정지
      motor_running = false;
      //Serial.println("stop");
     }
     else if(cmd == "run"){               // 모터 작동
      motor_running = true;
      motor_direction_forward = true;
      //Serial.println("run");
     }
     else if(cmd == "back"){              // 모터 반대로 작동
      motor_running = true;
      motor_direction_forward = false;
      //Serial.println("back");
     }
     else if(cmd == "end"){
      shouldrun = false;
     }

     else{
      //Serial.println("no message");
     }
    }
    unsigned long current_time = millis();   // unsigned: 양의 타입만 표시
    unsigned long timer = timer + current_time;
    Serial.print("timer ");
    Serial.println(timer/1000);
    int light = analogRead(A0);   // 조도센서
    //int light2 = analogRead(A1);
    int ledLight = map(light,0,2047,0,led_run);
    //Serial.print("led");
    //Serial.print(" ");
    //Serial.print(light);
    //Serial.print(" ");
    //Serial.println(ledLight);
    //ledLight = pow(ledLight, 2) / 255;
    
    analogWrite(led_1,ledLight);
    analogWrite(led_2,ledLight);

    // 초음파 센서를 주기적으로 읽음
    if (current_time - previous_time >= check) {
      previous_time = current_time;   
      long duration1, distance1;
      digitalWrite(TRIG1, LOW);
      delay(2);
      digitalWrite(TRIG1, HIGH);
      delay(10);
      digitalWrite(TRIG1, LOW);
      duration1 = pulseIn(ECHO1, HIGH);   
      //digitalWrite(TRIG2, LOW);
      //delay(2);
      //digitalWrite(TRIG2, HIGH);  
      //delay(10);
      //digitalWrite(TRIG2, LOW);
      //duration2 = pulseIn(ECHO2, HIGH);   
      distance1 = ((float)(340*duration1) / 10000) / 2;
      Serial.print("dis");
      Serial.println(distance1);
      //distance2 = ((float)(340*duration2) / 10000) / 2;
      if (distance1 != 0 && distance1 < 9) {
        // motor_running = false;
        Serial.print("capture");
        Serial.print(' ');
        Serial.println(distance1);
        // Serial.println(distance2);
      }
    }   
    // 카메라가 pcb기판검출을 완료하고 특정 메시지를 보내면 다시 시작
    if (!motor_running && Serial.readString() == "restart") {
      motor_running = true;
      motor_direction_forward = true;
      //Serial.println("restart");
    }   
    // 모터 실행
    if (motor_running) {
      if(motor_direction_forward){
        stepper.step(STEPS_PER_REVOLUTION); // 한 스텝 이동
      }
      else{
        stepper.step(-STEPS_PER_REVOLUTION);
      }
    }
  }
}