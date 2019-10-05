#include <ESP8266WiFi.h> 
#include <ESP8266HTTPClient.h>

String httpResponse;

//  "http://raspberrypi/drysector?startangle=60"

String sectorAngle = "180";
String urlMain = "http://192.168.0.108/drysector?startangle=";



//VARIABLE DECLARATIONS 
//#define SS_PIN 4 connection on rfid reader gpio4
#define RST_PIN 5 //D1 rfid reader
//define GW
const char* ssid = "Tenda_17EA20";//ROUTER SSID
const char* password = "Homeisbetter";       //password
HTTPClient http;  //Declaration of an instance of the HTTPClient 



void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);   // Initiate a serial communication at 115200 baud rate


//  pinMode(00, OUTPUT);             

 WiFi.begin(ssid, password);              
 Serial.println();
 Serial.print("Connecting..");            


 // /*
   while (WiFi.status() != WL_CONNECTED) {  //check if the router is really connected
    delay(1000);
    Serial.print(".");
  }// */


  for(int i=0; i<10;++i){
    if(WiFi.status() == WL_CONNECTED){
        Serial.println("connected to the network");
      }
    }

}

void loop() {
  // put your main code here, to run repeatedly:

  float soilWater = analogRead(A0);
  Serial.println("soil moisture : " + (String)soilWater);

  if(soilWater > 600){
      httpResponse = httpReq(urlMain + sectorAngle);
      Serial.println("response = " + httpResponse);


      delay(30000);
    }




    soilWater = analogRead(A0);
    while(soilWater < 300){
      delay(1000);
       soilWater = analogRead(A0);
      }

}





  String httpReq(String targetURL){
    Serial.println(targetURL);
      String response = "";
      http.begin(targetURL); 
      int httpCode = http.GET(); 
    //while(httpCode < 0);
    if (httpCode > 0) { //Check the returning code
      response = http.getString();   //Get response
     }
    http.end();         //end the http connecton
    return response;    //returns the response to the caller
    }                 //end of request function
