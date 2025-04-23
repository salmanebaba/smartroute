#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "INPT-TEST";
const char* password = "iinnpptt";
const char* serverUrl = "https://becoming-oarfish-luckily.ngrok-free.app/";
const int FILL_LEVEL = 75;

void setup() {
  Serial.begin(115200);
  
  // Connexion WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connexion au WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnecté ! Adresse IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    // Configuration de la requête
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    // Création du payload JSON correct
    String payload = "{\"id\":\"bin_01\",\"fill_level\":" + String(FILL_LEVEL) + "}";
    
    // Envoi de la requête POST
    int httpCode = http.POST(payload);
    
    // Vérification de la réponse
    if (httpCode > 0) {
      Serial.printf("Code HTTP: %d\n", httpCode);
      Serial.println("Réponse: " + http.getString());
    } else {
      Serial.printf("Échec de la requête, erreur: %s\n", http.errorToString(httpCode).c_str());
    }
    
    http.end();
  } else {
    Serial.println("Déconnexion WiFi détectée");
  }
  
  delay(360000); 
}