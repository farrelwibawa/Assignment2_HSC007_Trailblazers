#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>

// ===================
// Pilih model kamera
// ===================
#define CAMERA_MODEL_AI_THINKER  // AI Thinker ESP32-CAM
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22
#define LED_GPIO_NUM       4

// ===========================
// Masukkan kredensial WiFi
// ===========================
const char *ssid = "trailblazers";
const char *password = "krumhuek";

// Web Server di port 80
WebServer server(80);

// ======================
// Fungsi Setup LED Flash
// ======================
void setupLedFlash(int pin) {
  pinMode(pin, OUTPUT);
  digitalWrite(pin, LOW);
}

// ======================
// SETUP
// ======================
void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_LATEST;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 10;
  config.fb_count = 2;

  // Inisialisasi kamera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t *s = esp_camera_sensor_get();
  if (s->id.PID == OV3660_PID) {
    s->set_brightness(s, 1);
    s->set_saturation(s, -2);
  }
  s->set_vflip(s, 1);
  s->set_hmirror(s, 1);
  s->set_framesize(s, FRAMESIZE_VGA);

  setupLedFlash(LED_GPIO_NUM);

  // Koneksi ke WiFi
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  startCameraServer();

  Serial.print("Camera Ready! Akses lewat: http://");
  Serial.println(WiFi.localIP());
}

// ======================
// LOOP
// ======================
void loop() {
  server.handleClient();
  delay(1);
}

// ======================
// STREAM HANDLER
// ======================
void handle_jpg_stream() {
  WiFiClient client = server.client();
  String response = "HTTP/1.1 200 OK\r\n";
  response += "Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n";
  server.sendContent(response);

  while (1) {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      return;
    }

    response = "--frame\r\n";
    response += "Content-Type: image/jpeg\r\n\r\n";
    server.sendContent(response);
    server.sendContent((const char *)fb->buf, fb->len);
    server.sendContent("\r\n");

    esp_camera_fb_return(fb);
    if (!client.connected()) break;
    delay(100);
  }
}

// ======================
// START SERVER + UI
// ======================
void startCameraServer() {
  server.on("/", HTTP_GET, []() {
    String html = R"rawliteral(
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>MindKeeper Camera</title>
        <style>
          body {
            margin: 0;
            background-color: #121212;
            color: #703f45;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
          }
          h1 {
            margin-bottom: 20px;
            font-size: 2em;
            color: #ffffff;
          }
          img {
            border: 2px solid #703f45;
            border-radius: 10px;
            width: 90vw;
            max-width: 600px;
            height: auto;
          }
        </style>
      </head>
      <body>
        <h1>📷 MindKeeper User Camera</h1>
        <img src="/stream" alt="Live Stream">
      </body>
      </html>
    )rawliteral";

    server.send(200, "text/html", html);
  });

  server.on("/stream", HTTP_GET, handle_jpg_stream);
  server.begin();
  Serial.println("Camera stream server started");
}
