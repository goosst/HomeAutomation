// sg 6 may 2019
// started from: https://github.com/esp8266-examples/ota-mqtt/blob/master/ota-mqtt/ota-mqtt.ino
// broadcasts an mqtt message corresponding the high or low state of the input (to the home assistant broker)
// allows over the air software update through the arduino ide

#include <ESP8266WiFi.h>  //For ESP8266
#include <PubSubClient.h> //For MQTT
#include <ESP8266mDNS.h>  //For OTA
#include <WiFiUdp.h>      //For OTA
#include <ArduinoOTA.h>   //For OTA

#include "configuration.h" // to store passwords of mqtt and wifi


String mqtt_client_id = "ESP8266-"; //This text is concatenated with ChipId to get unique client_id
//MQTT Topic configuration
String mqtt_base_topic = "/sensor/" + mqtt_client_id + "/data";
//#define humidity_topic "/humidity"
//#define temperature_topic "/temperature"

//MQTT client
WiFiClient espClient;
PubSubClient mqtt_client(espClient);

//Necesary to make Arduino Software autodetect OTA device
WiFiServer TelnetServer(8266);

const int pin_alarm = D8;

void setup_wifi() {
  delay(10);
  Serial.print("Connecting to ");
  Serial.print(wifi_ssid);
  WiFi.begin(wifi_ssid, wifi_password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("OK");
  Serial.print("   IP address: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);
  Serial.println("\r\nBooting...");

  setup_wifi();

  Serial.print("Configuring OTA device...");
  TelnetServer.begin();   //Necesary to make Arduino Software autodetect OTA device
  ArduinoOTA.onStart([]() {
    Serial.println("OTA starting...");
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("OTA update finished!");
    Serial.println("Rebooting...");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("OTA in progress: %u%%\r\n", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
    else if (error == OTA_END_ERROR) Serial.println("End Failed");
  });
  ArduinoOTA.begin();
  Serial.println("OK");

  Serial.println("Configuring MQTT server...");
  mqtt_client_id = mqtt_client_id + ESP.getChipId();
  mqtt_base_topic = "/sensor/" + mqtt_client_id + "/data";
  mqtt_client.setServer(mqtt_server, 1883);
  Serial.printf("   Server IP: %s\r\n", mqtt_server);
  Serial.printf("   Username:  %s\r\n", mqtt_user);
  Serial.println("   Cliend Id: " + mqtt_client_id);
  Serial.println("   MQTT configured!");

  Serial.println("Setup completed! Running app...");


  pinMode(pin_alarm, INPUT_PULLUP);
}


void mqtt_reconnect() {
  // Loop until we're reconnected
  while (!mqtt_client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    // If you do not want to use a username and password, change next line to
    // if (client.connect("ESP8266Client")) {
    if (mqtt_client.connect(mqtt_client_id.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqtt_client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}


bool checkBound(float newValue, float prevValue, float maxDiff) {
  return (true);
  return newValue < prevValue - maxDiff || newValue > prevValue + maxDiff;
}



long now = 0; //in ms
long lastMsg = 0;
float diff = 1.0;
int min_timeout = 5000; //in ms

void loop() {

  ArduinoOTA.handle();

  if (!mqtt_client.connected()) {
    mqtt_reconnect();
  }
  mqtt_client.loop();

  now = millis();
  if (now - lastMsg > min_timeout) {
    lastMsg = now;
    now = millis();
    int alarm_state = digitalRead(pin_alarm);
    //Serial.println(alarm_state);
    //Serial.println(String(alarm_state).c_str());

    mqtt_client.publish("sensor/alarm", String(alarm_state).c_str(), true);

  }
}
