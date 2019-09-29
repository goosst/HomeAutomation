// author: goosst
// creation date: 29 sep 2019
//
// Downloads bmp file from local site (here: raspberry pi running home assistant)
// named black1.bmp and black2.bmp, plots on two 7.5 inch e-paper
// Based on GxEPD2_GFX_MultiDisplayExample.ino

#define ENABLE_GxEPD2_GFX 1
#include <GxEPD2_BW.h>
#include <Fonts/FreeMonoBold9pt7b.h>

#include <WiFiClient.h>
#include <WiFiClientSecure.h>
#include "Credentials.h"


//SPI pins, common for both displays
static const uint8_t EPD_DC   = 22; // to EPD DC
static const uint8_t EPD_SCK  = 18; // to EPD CLK
static const uint8_t EPD_MISO = 19; // Master-In Slave-Out not used, as no data from display
static const uint8_t EPD_MOSI = 23; // to EPD DIN

// display two:
static const uint8_t EPD_BUSY2 = 4;  // to EPD BUSY
static const uint8_t EPD_CS2   = 5;  // to EPD CS
static const uint8_t EPD_RST2  = 21; // to EPD RST
GxEPD2_BW<GxEPD2_750, GxEPD2_750::HEIGHT> display2(GxEPD2_750(/*CS=*/ EPD_CS2, /*DC=*/ EPD_DC, /*RST=*/ EPD_RST2, /*BUSY=*/ EPD_BUSY2));   // B/W display

//display one:
static const uint8_t EPD_BUSY1 = 25;  // to EPD BUSY
static const uint8_t EPD_RST1  = 34; // to EPD RST
static const uint8_t EPD_CS1   = 15;  // to EPD CS
GxEPD2_BW<GxEPD2_750, GxEPD2_750::HEIGHT> display1(GxEPD2_750(/*CS=*/ EPD_CS1, /*DC=*/ EPD_DC, /*RST=*/ EPD_RST1, /*BUSY=*/ EPD_BUSY1));   // B/W display

#include "bitmaps/Bitmaps640x384.h" // 7.5"  b/w

long SleepDuration = 7; // Sleep time in minutes, aligned to the nearest minute boundary, so if 30 will always update at 00 or 30 past the hour
int  WakeupTime    = 5;  // Don't wakeup until after 07:00 to save battery power
int  SleepTime     = 23; // Sleep after (23+1) 00:00 to save battery power
int CurrentHour = 0, CurrentMin = 0, CurrentSec = 0;
long StartTime = 0;

void setup()
{
  Serial.begin(115200);
  Serial.println();
  Serial.println("initialize wifi");

#ifdef RE_INIT_NEEDED
  WiFi.persistent(true);
  WiFi.mode(WIFI_STA); // switch off AP
  WiFi.setAutoConnect(true);
  WiFi.setAutoReconnect(true);
  WiFi.disconnect();
#endif

  if (!WiFi.getAutoConnect() || ( WiFi.getMode() != WIFI_STA) || ((WiFi.SSID() != ssid) && String(ssid) != "........"))
  {
    Serial.println();
    Serial.print("WiFi.getAutoConnect()=");
    Serial.println(WiFi.getAutoConnect());
    Serial.print("WiFi.SSID()=");
    Serial.println(WiFi.SSID());
    WiFi.mode(WIFI_STA); // switch off AP
    Serial.print("Connecting to ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);
  }
  int ConnectTimeout = 180; // 15 seconds
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
    Serial.print(WiFi.status());
    if (--ConnectTimeout <= 0)
    {
      Serial.println();
      Serial.println("WiFi connect timeout");
      return;
    }
  }
  Serial.println();
  Serial.println("WiFi connected");

  // Print the IP address
  Serial.println(WiFi.localIP());



  // Start updating screens
  delay(1000);
  //  float voltage = analogRead(35) / 4096.0 * 7.46;
  //  Serial.println("Voltage = " + String(voltage));

  Serial.println("Reset pins, set high");
  pinMode(EPD_RST1, OUTPUT);
  pinMode(EPD_RST2, OUTPUT);
  digitalWrite(EPD_RST2, LOW);
  delay(200);
  digitalWrite(EPD_RST1, HIGH);
  delay(200);
  digitalWrite(EPD_RST1, LOW);
  delay(20);
  digitalWrite(EPD_RST1, HIGH);
  //  delay(200);

  Serial.println("start disp 1");

  delay(200);
  display1.init(115200); // enable diagnostic output on Serial
  Serial.println("disp 1 initialized");
  delay(1000);
  drawBitmaps_hass(display1, "black1.bmp");
  delay(1000);
  display1.powerOff();
  delay(200);

  float voltage = analogRead(35) / 4096.0 * 7.46;
  Serial.println("Voltage = " + String(voltage));

  digitalWrite(EPD_RST2, HIGH);
  delay(200);
  digitalWrite(EPD_RST2, LOW);
  delay(20);
  digitalWrite(EPD_RST2, HIGH);
  delay(200);
  Serial.println("Reset pin 2 toggled");

  display2.init(115200); // enable diagnostic output on Serial
  Serial.println("disp 2 initialized");
  delay(1000);
  drawBitmaps_hass(display2, "black2.bmp");
  delay(1000);
  display2.powerOff();
  delay(200);

  Serial.println("display updating done");

  BeginSleep();
}

void loop()
{
}

void drawBitmaps_hass(GxEPD2_GFX& display, const char* filename)
{
  //  int16_t w2 = display.width() / 2;
  //  int16_t h2 = display.height() / 2;

  IPAddress hass(192, 168, 0, 205);
  showBitmapFrom_HTTP_fubar(hass, ":8123/local/", filename,  false, display);
  delay(4000);

}


static const uint16_t input_buffer_pixels = 640; // may affect performance

static const uint16_t max_row_width = 640; // for up to 7.5" display
static const uint16_t max_palette_pixels = 256; // for depth <= 8

uint8_t input_buffer[3 * input_buffer_pixels]; // up to depth 24
uint8_t output_row_mono_buffer[max_row_width / 8]; // buffer for at least one row of b/w bits
uint8_t output_row_color_buffer[max_row_width / 8]; // buffer for at least one row of color bits
uint8_t mono_palette_buffer[max_palette_pixels / 8]; // palette buffer for depth <= 8 b/w
uint8_t color_palette_buffer[max_palette_pixels / 8]; // palette buffer for depth <= 8 c/w

void showBitmapFrom_HTTP_fubar(IPAddress hass, const char* path, const char* filename, bool with_color, GxEPD2_GFX& display)
{
  WiFiClient client;

  int port_fub = 8123;
  bool connection_ok = false;
  bool valid = false; // valid format to be handled
  bool flip = true; // bitmap is stored bottom-to-top
  uint32_t startTime = millis();
  //  if ((x >= display.width()) || (y >= display.height())) return;
  Serial.println(); Serial.print("downloading file \""); Serial.print(filename);  Serial.println("\"");
  Serial.print("connecting to "); Serial.println(hass);

  int downloadAttempts = 0;
  while (!valid && downloadAttempts < 5)
  {

    downloadAttempts = downloadAttempts + 1;
    Serial.println("download attempt:");
    Serial.println(downloadAttempts);
    if (!client.connect(hass, port_fub))
    {
      Serial.println("connection failed");
      return;
    }
    Serial.print("requesting URL: ");

    //  String fubar = String("GET ") + "http://192.168.0.205:8123/local/" + filename  + " HTTP/1.1\r\n" +
    //                 "Connection: close\r\n\r\n";

    String fubar = String("GET ") + "http://" + hass.toString() + path + filename  + " HTTP/1.1\r\n" +
                   "Connection: close\r\n\r\n";

    client.print(fubar);

    int i = 0;
    while (client.connected() && i < 500)
    {
      Serial.println("connected to client");
      //    Serial.println(client)
      //    Serial.println(read32(client));
      String line = client.readStringUntil('\n');
      i = i + 1;
      //    Serial.println("line stuff");
      //    Serial.println(line);
      if (!connection_ok)
      {
        connection_ok = line.startsWith("HTTP/1.1 200 OK");
        if (connection_ok) Serial.println(line);
        //if (!connection_ok) Serial.println(line);
      }
      if (!connection_ok) Serial.println(line);
      //Serial.println(line);
      if (line == "\r")
      {
        Serial.println("headers received");
        i = 9999;
      }
    }

    if (!connection_ok) return;

    // Parse BMP header
    uint16_t fub = read16(client);
    Serial.println(fub);
    if (fub == 0x4D42) // BMP signature
    {
      uint32_t fileSize = read32(client);
      uint32_t creatorBytes = read32(client);
      uint32_t imageOffset = read32(client); // Start of image data
      uint32_t headerSize = read32(client);
      uint32_t width  = read32(client);
      uint32_t height = read32(client);
      uint16_t planes = read16(client);
      uint16_t depth = read16(client); // bits per pixel
      uint32_t format = read32(client);
      uint32_t bytes_read = 7 * 4 + 3 * 2; // read so far
      if ((planes == 1) && ((format == 0) || (format == 3))) // uncompressed is handled, 565 also
      {
        Serial.print("File size: "); Serial.println(fileSize);
        Serial.print("Image Offset: "); Serial.println(imageOffset);
        Serial.print("Header size: "); Serial.println(headerSize);
        Serial.print("Bit Depth: "); Serial.println(depth);
        Serial.print("Image size: ");
        Serial.print(width);
        Serial.print('x');
        Serial.println(height);
        // BMP rows are padded (if needed) to 4-byte boundary
        uint32_t rowSize = (width * depth / 8 + 3) & ~3;
        if (depth < 8) rowSize = ((width * depth + 8 - depth) / 8 + 3) & ~3;
        if (height < 0)
        {
          height = -height;
          flip = false;
        }
        uint16_t w = width;
        uint16_t h = height;

        int16_t x = display.width() / 2 - w / 2;
        int16_t y = display.height() / 2 - h / 2;
        Serial.println("x:");
        Serial.println(x);
        Serial.println("y:");
        Serial.println(y);

        if ((x + w - 1) >= display.width())  w = display.width()  - x;
        if ((y + h - 1) >= display.height()) h = display.height() - y;
        Serial.println("w (width):");
        Serial.println(w);
        Serial.println("max row width:");
        Serial.println(max_row_width);

        if (w <= max_row_width) // handle with direct drawing
        {
          valid = true;
          uint8_t bitmask = 0xFF;
          uint8_t bitshift = 8 - depth;
          uint16_t red, green, blue;
          bool whitish, colored;
          if (depth == 1) with_color = false;
          if (depth <= 8)
          {
            if (depth < 8) bitmask >>= depth;
            bytes_read += skip(client, 54 - bytes_read); //palette is always @ 54
            for (uint16_t pn = 0; pn < (1 << depth); pn++)
            {
              blue  = client.read();
              green = client.read();
              red   = client.read();
              client.read();
              bytes_read += 4;
              whitish = with_color ? ((red > 0x80) && (green > 0x80) && (blue > 0x80)) : ((red + green + blue) > 3 * 0x80); // whitish
              colored = (red > 0xF0) || ((green > 0xF0) && (blue > 0xF0)); // reddish or yellowish?
              if (0 == pn % 8) mono_palette_buffer[pn / 8] = 0;
              mono_palette_buffer[pn / 8] |= whitish << pn % 8;
              if (0 == pn % 8) color_palette_buffer[pn / 8] = 0;
              color_palette_buffer[pn / 8] |= colored << pn % 8;
            }
          }
          display.clearScreen();
          uint32_t rowPosition = flip ? imageOffset + (height - h) * rowSize : imageOffset;
          //Serial.print("skip "); Serial.println(rowPosition - bytes_read);
          bytes_read += skip(client, rowPosition - bytes_read);
          for (uint16_t row = 0; row < h; row++, rowPosition += rowSize) // for each line
          {
            if (!connection_ok || !(client.connected() || client.available())) break;
            delay(1); // yield() to avoid WDT
            uint32_t in_remain = rowSize;
            uint32_t in_idx = 0;
            uint32_t in_bytes = 0;
            uint8_t in_byte = 0; // for depth <= 8
            uint8_t in_bits = 0; // for depth <= 8
            uint8_t out_byte = 0xFF; // white (for w%8!=0 boarder)
            uint8_t out_color_byte = 0xFF; // white (for w%8!=0 boarder)
            uint32_t out_idx = 0;
            for (uint16_t col = 0; col < w; col++) // for each pixel
            {
              yield();
              if (!connection_ok || !(client.connected() || client.available())) break;
              // Time to read more pixel data?
              if (in_idx >= in_bytes) // ok, exact match for 24bit also (size IS multiple of 3)
              {
                uint32_t get = in_remain > sizeof(input_buffer) ? sizeof(input_buffer) : in_remain;
                uint32_t got = read(client, input_buffer, get);
                while ((got < get) && connection_ok)
                {
                  //Serial.print("got "); Serial.print(got); Serial.print(" < "); Serial.print(get); Serial.print(" @ "); Serial.println(bytes_read);
                  uint32_t gotmore = read(client, input_buffer + got, get - got);
                  got += gotmore;
                  connection_ok = gotmore > 0;
                }
                in_bytes = got;
                in_remain -= got;
                bytes_read += got;
              }
              if (!connection_ok)
              {
                Serial.print("Error: got no more after "); Serial.print(bytes_read); Serial.println(" bytes read!");
                break;
              }
              switch (depth)
              {
                case 24:
                  blue = input_buffer[in_idx++];
                  green = input_buffer[in_idx++];
                  red = input_buffer[in_idx++];
                  whitish = with_color ? ((red > 0x80) && (green > 0x80) && (blue > 0x80)) : ((red + green + blue) > 3 * 0x80); // whitish
                  colored = (red > 0xF0) || ((green > 0xF0) && (blue > 0xF0)); // reddish or yellowish?
                  break;
                case 16:
                  {
                    uint8_t lsb = input_buffer[in_idx++];
                    uint8_t msb = input_buffer[in_idx++];
                    if (format == 0) // 555
                    {
                      blue  = (lsb & 0x1F) << 3;
                      green = ((msb & 0x03) << 6) | ((lsb & 0xE0) >> 2);
                      red   = (msb & 0x7C) << 1;
                    }
                    else // 565
                    {
                      blue  = (lsb & 0x1F) << 3;
                      green = ((msb & 0x07) << 5) | ((lsb & 0xE0) >> 3);
                      red   = (msb & 0xF8);
                    }
                    whitish = with_color ? ((red > 0x80) && (green > 0x80) && (blue > 0x80)) : ((red + green + blue) > 3 * 0x80); // whitish
                    colored = (red > 0xF0) || ((green > 0xF0) && (blue > 0xF0)); // reddish or yellowish?
                  }
                  break;
                case 1:
                case 4:
                case 8:
                  {
                    if (0 == in_bits)
                    {
                      in_byte = input_buffer[in_idx++];
                      in_bits = 8;
                    }
                    uint16_t pn = (in_byte >> bitshift) & bitmask;
                    whitish = mono_palette_buffer[pn / 8] & (0x1 << pn % 8);
                    colored = color_palette_buffer[pn / 8] & (0x1 << pn % 8);
                    in_byte <<= depth;
                    in_bits -= depth;
                  }
                  break;
              }
              if (whitish)
              {
                // keep white
              }
              else if (colored && with_color)
              {
                out_color_byte &= ~(0x80 >> col % 8); // colored
              }
              else
              {
                out_byte &= ~(0x80 >> col % 8); // black
              }
              if ((7 == col % 8) || (col == w - 1)) // write that last byte! (for w%8!=0 boarder)
              {
                output_row_color_buffer[out_idx] = out_color_byte;
                output_row_mono_buffer[out_idx++] = out_byte;
                out_byte = 0xFF; // white (for w%8!=0 boarder)
                out_color_byte = 0xFF; // white (for w%8!=0 boarder)
              }
            } // end pixel
            int16_t yrow = y + (flip ? h - row - 1 : row);
            display.writeImage(output_row_mono_buffer, output_row_color_buffer, x, yrow, w, 1);
          } // end line
          Serial.print("downloaded in ");
          Serial.print(millis() - startTime);
          Serial.println(" ms");
          display.refresh();
        }
        Serial.print("bytes read "); Serial.println(bytes_read);
      }
    }
    if (!valid)
    {
      Serial.println("bitmap format not handled.");
    }
  }
}


uint16_t read16(WiFiClient& client)
{
  // BMP data is stored little-endian, same as Arduino.
  uint16_t result;
  ((uint8_t *)&result)[0] = client.read(); // LSB
  ((uint8_t *)&result)[1] = client.read(); // MSB
  return result;
}

uint32_t read32(WiFiClient& client)
{
  // BMP data is stored little-endian, same as Arduino.
  uint32_t result;
  ((uint8_t *)&result)[0] = client.read(); // LSB
  ((uint8_t *)&result)[1] = client.read();
  ((uint8_t *)&result)[2] = client.read();
  ((uint8_t *)&result)[3] = client.read(); // MSB
  return result;
}


#if USE_BearSSL

uint32_t skip(BearSSL::WiFiClientSecure& client, int32_t bytes)
{
  int32_t remain = bytes;
  uint32_t start = millis();
  while ((client.connected() || client.available()) && (remain > 0))
  {
    if (client.available())
    {
      int16_t v = client.read();
      remain--;
    }
    else delay(1);
    if (millis() - start > 2000) break; // don't hang forever
  }
  return bytes - remain;
}

uint32_t read(BearSSL::WiFiClientSecure& client, uint8_t* buffer, int32_t bytes)
{
  int32_t remain = bytes;
  uint32_t start = millis();
  while ((client.connected() || client.available()) && (remain > 0))
  {
    if (client.available())
    {
      int16_t v = client.read();
      *buffer++ = uint8_t(v);
      remain--;
    }
    else delay(1);
    if (millis() - start > 2000) break; // don't hang forever
  }
  return bytes - remain;
}

#endif

uint32_t skip(WiFiClient& client, int32_t bytes)
{
  int32_t remain = bytes;
  uint32_t start = millis();
  while ((client.connected() || client.available()) && (remain > 0))
  {
    if (client.available())
    {
      int16_t v = client.read();
      remain--;
    }
    else delay(1);
    if (millis() - start > 2000) break; // don't hang forever
  }
  return bytes - remain;
}

uint32_t read(WiFiClient& client, uint8_t* buffer, int32_t bytes)
{
  int32_t remain = bytes;
  uint32_t start = millis();
  while ((client.connected() || client.available()) && (remain > 0))
  {
    if (client.available())
    {
      int16_t v = client.read();
      *buffer++ = uint8_t(v);
      remain--;
    }
    else delay(1);
    if (millis() - start > 2000) break; // don't hang forever
  }
  return bytes - remain;
}

void BeginSleep() {
  //  display.powerOff();
  long SleepTimer = (SleepDuration * 60 - ((CurrentMin % SleepDuration) * 60 + CurrentSec)); //Some ESP32 are too fast to maintain accurate time
  esp_sleep_enable_timer_wakeup(SleepTimer * 1000000LL);
#ifdef BUILTIN_LED
  pinMode(BUILTIN_LED, INPUT); // If it's On, turn it off and some boards use GPIO-5 for SPI-SS, which remains low after screen use
  digitalWrite(BUILTIN_LED, HIGH);
#endif
  Serial.println("Entering " + String(SleepTimer) + "-secs of sleep time");
  Serial.println("Awake for : " + String((millis() - StartTime) / 1000.0, 3) + "-secs");
  Serial.println("Starting deep-sleep period...");
  esp_deep_sleep_start();      // Sleep for e.g. 30 minutes
}

void helloWorld(GxEPD2_GFX& display)
{
  //Serial.println("helloWorld");
  display.setRotation(1);
  display.setFont(&FreeMonoBold9pt7b);
  display.setTextColor(GxEPD_BLACK);
  uint16_t x = (display.width() - 160) / 2;
  uint16_t y = display.height() / 2;
  display.setFullWindow();
  display.firstPage();
  do
  {
    display.fillScreen(GxEPD_WHITE);
    display.setCursor(x, y);
    display.println("Hello World!");
  }
  while (display.nextPage());
  //Serial.println("helloWorld done");
}


void helloFullScreenPartialMode(GxEPD2_GFX& display)
{
  //Serial.println("helloFullScreenPartialMode");
  display.setPartialWindow(0, 0, display.width(), display.height());
  display.setRotation(1);
  display.setFont(&FreeMonoBold9pt7b);
  display.setTextColor(GxEPD_BLACK);
  display.firstPage();
  do
  {
    uint16_t x = (display.width() - 160) / 2;
    uint16_t y = display.height() / 2;
    display.fillScreen(GxEPD_WHITE);
    display.setCursor(x, y);
    display.println("Hello World!");
    y = display.height() / 4;
    display.setCursor(x, y);
    display.println("full screen");
    y = display.height() * 3 / 4;
    if (display.width() <= 200) x = 0;
    display.setCursor(x, y);
    if (display.epd2.hasFastPartialUpdate)
    {
      display.println("fast partial mode");
    }
    else if (display.epd2.hasPartialUpdate)
    {
      display.println("slow partial mode");
    }
    else
    {
      display.println("no partial mode");
    }
  }
  while (display.nextPage());
  //Serial.println("helloFullScreenPartialMode done");
}


void helloArduino(GxEPD2_GFX& display)
{
  //Serial.println("helloArduino");
  display.setRotation(1);
  display.setFont(&FreeMonoBold9pt7b);
  display.setTextColor(display.epd2.hasColor ? GxEPD_RED : GxEPD_BLACK);
  uint16_t x = (display.width() - 160) / 2;
  uint16_t y = display.height() / 4;
  display.setPartialWindow(0, y - 14, display.width(), 20);
  display.firstPage();
  do
  {
    display.fillScreen(GxEPD_WHITE);
    display.setCursor(x, y);
    display.println("Hello Arduino!");
  }
  while (display.nextPage());
  delay(1000);
  //Serial.println("helloArduino done");
}


void helloEpaper(GxEPD2_GFX& display)
{
  //Serial.println("helloEpaper");
  display.setRotation(1);
  display.setFont(&FreeMonoBold9pt7b);
  display.setTextColor(display.epd2.hasColor ? GxEPD_RED : GxEPD_BLACK);
  uint16_t x = (display.width() - 160) / 2;
  uint16_t y = display.height() * 3 / 4;
  display.setPartialWindow(0, y - 14, display.width(), 20);
  display.firstPage();
  do
  {
    display.fillScreen(GxEPD_WHITE);
    display.setCursor(x, y);
    display.println("Hello E-Paper!");
  }
  while (display.nextPage());
  //Serial.println("helloEpaper done");
}


void showBox(GxEPD2_GFX& display, uint16_t x, uint16_t y, uint16_t w, uint16_t h, bool partial)
{
  //Serial.println("showBox");
  display.setRotation(1);
  if (partial)
  {
    display.setPartialWindow(x, y, w, h);
  }
  else
  {
    display.setFullWindow();
  }
  display.firstPage();
  do
  {
    display.fillScreen(GxEPD_WHITE);
    display.fillRect(x, y, w, h, GxEPD_BLACK);
  }
  while (display.nextPage());
  //Serial.println("showBox done");
}


void drawCornerTest(GxEPD2_GFX& display)
{
  display.setFullWindow();
  display.setFont(&FreeMonoBold9pt7b);
  display.setTextColor(GxEPD_BLACK);
  for (uint16_t r = 0; r <= 4; r++)
  {
    display.setRotation(r);
    display.firstPage();
    do
    {
      display.fillScreen(GxEPD_WHITE);
      display.fillRect(0, 0, 8, 8, GxEPD_BLACK);
      display.fillRect(display.width() - 18, 0, 16, 16, GxEPD_BLACK);
      display.fillRect(display.width() - 25, display.height() - 25, 24, 24, GxEPD_BLACK);
      display.fillRect(0, display.height() - 33, 32, 32, GxEPD_BLACK);
      display.setCursor(display.width() / 2, display.height() / 2);
      display.print(display.getRotation());
    }
    while (display.nextPage());
    delay(2000);
  }
}


void showFont(GxEPD2_GFX& display, const char name[], const GFXfont* f)
{
  display.setFullWindow();
  display.setRotation(0);
  display.setTextColor(GxEPD_BLACK);
  display.firstPage();
  do
  {
    drawFont(display, name, f);
  }
  while (display.nextPage());
}


//void drawFont(GxEPD2_GFX& display, const char name[], const GFXfont* f);


void drawFont(GxEPD2_GFX& display, const char name[], const GFXfont* f)
{
  //display.setRotation(0);
  display.fillScreen(GxEPD_WHITE);
  display.setTextColor(GxEPD_BLACK);
  display.setFont(f);
  display.setCursor(0, 0);
  display.println();
  display.println(name);
  display.println(" !\"#$%&'()*+,-./");
  display.println("0123456789:;<=>?");
  display.println("@ABCDEFGHIJKLMNO");
  display.println("PQRSTUVWXYZ[\\]^_");
  if (display.epd2.hasColor)
  {
    display.setTextColor(GxEPD_RED);
  }
  display.println("`abcdefghijklmno");
  display.println("pqrstuvwxyz{|}~ ");
}


void showPartialUpdate(GxEPD2_GFX& display)
{
  // some useful background
  helloWorld(display);
  // use asymmetric values for test
  uint16_t box_x = 10;
  uint16_t box_y = 15;
  uint16_t box_w = 70;
  uint16_t box_h = 20;
  uint16_t cursor_y = box_y + box_h - 6;
  float value = 13.95;
  uint16_t incr = display.epd2.hasFastPartialUpdate ? 1 : 3;
  display.setFont(&FreeMonoBold9pt7b);
  display.setTextColor(GxEPD_BLACK);
  // show where the update box is
  for (uint16_t r = 0; r < 4; r++)
  {
    display.setRotation(r);
    display.setPartialWindow(box_x, box_y, box_w, box_h);
    display.firstPage();
    do
    {
      display.fillRect(box_x, box_y, box_w, box_h, GxEPD_BLACK);
      //display.fillScreen(GxEPD_BLACK);
    }
    while (display.nextPage());
    delay(2000);
    display.firstPage();
    do
    {
      display.fillRect(box_x, box_y, box_w, box_h, GxEPD_WHITE);
    }
    while (display.nextPage());
    delay(1000);
  }
  //return;
  // show updates in the update box
  for (uint16_t r = 0; r < 4; r++)
  {
    display.setRotation(r);
    display.setPartialWindow(box_x, box_y, box_w, box_h);
    for (uint16_t i = 1; i <= 10; i += incr)
    {
      display.firstPage();
      do
      {
        display.fillRect(box_x, box_y, box_w, box_h, GxEPD_WHITE);
        display.setCursor(box_x, cursor_y);
        display.print(value * i, 2);
      }
      while (display.nextPage());
      delay(500);
    }
    delay(1000);
    display.firstPage();
    do
    {
      display.fillRect(box_x, box_y, box_w, box_h, GxEPD_WHITE);
    }
    while (display.nextPage());
    delay(1000);
  }
}


#ifdef _GxBitmaps200x200_H_

void drawBitmaps200x200(GxEPD2_GFX& display);

void drawBitmaps200x200(GxEPD2_GFX& display)
{
#if defined(__AVR)
  const unsigned char* bitmaps[] =
  {
    logo200x200, first200x200 //, second200x200, third200x200, fourth200x200, fifth200x200, sixth200x200, senventh200x200, eighth200x200
  };
#elif defined(_BOARD_GENERIC_STM32F103C_H_)
  const unsigned char* bitmaps[] =
  {
    logo200x200, first200x200, second200x200, third200x200, fourth200x200, fifth200x200 //, sixth200x200, senventh200x200, eighth200x200
  };
#else
  const unsigned char* bitmaps[] =
  {
    logo200x200, first200x200, second200x200, third200x200, fourth200x200, fifth200x200, sixth200x200, senventh200x200, eighth200x200
  };
#endif
  if (display.epd2.panel == GxEPD2::GDEP015OC1)
  {
    bool m = display.mirror(true);
    for (uint16_t i = 0; i < sizeof(bitmaps) / sizeof(char*); i++)
    {
      display.firstPage();
      do
      {
        display.fillScreen(GxEPD_WHITE);
        display.drawInvertedBitmap(0, 0, bitmaps[i], display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_BLACK);
      }
      while (display.nextPage());
      delay(2000);
    }
    display.mirror(m);
  }
  //else
  {
    bool mirror_y = (display.epd2.panel != GxEPD2::GDE0213B1);
    display.clearScreen(); // use default for white
    int16_t x = (int16_t(display.epd2.WIDTH) - 200) / 2;
    int16_t y = (int16_t(display.epd2.HEIGHT) - 200) / 2;
    for (uint16_t i = 0; i < sizeof(bitmaps) / sizeof(char*); i++)
    {
      display.drawImage(bitmaps[i], x, y, 200, 200, false, mirror_y, true);
      delay(2000);
    }
  }
  bool mirror_y = (display.epd2.panel != GxEPD2::GDE0213B1);
  for (uint16_t i = 0; i < sizeof(bitmaps) / sizeof(char*); i++)
  {
    int16_t x = -60;
    int16_t y = -60;
    for (uint16_t j = 0; j < 10; j++)
    {
      display.writeScreenBuffer(); // use default for white
      display.writeImage(bitmaps[i], x, y, 200, 200, false, mirror_y, true);
      display.refresh(true);
      delay(2000);
      x += 40;
      y += 40;
      if ((x >= int16_t(display.epd2.WIDTH)) || (y >= int16_t(display.epd2.HEIGHT))) break;
    }
    if (!display.epd2.hasFastPartialUpdate) break; // comment out for full show
    break; // comment out for full show
  }
  display.writeScreenBuffer(); // use default for white
  display.writeImage(bitmaps[0], int16_t(0), 0, 200, 200, false, mirror_y, true);
  display.writeImage(bitmaps[0], int16_t(int16_t(display.epd2.WIDTH) - 200), int16_t(display.epd2.HEIGHT) - 200, 200, 200, false, mirror_y, true);
  display.refresh(true);
  delay(2000);
}
#endif

#ifdef _GxBitmaps128x250_H_

void drawBitmaps128x250(GxEPD2_GFX& display);

void drawBitmaps128x250(GxEPD2_GFX& display)
{
#if !defined(__AVR)
  const unsigned char* bitmaps[] =
  {
    Bitmap128x250_1, logo128x250, first128x250, second128x250, third128x250
  };
#else
  const unsigned char* bitmaps[] =
  {
    Bitmap128x250_1, logo128x250, first128x250, second128x250, third128x250
  };
#endif
  if (display.epd2.panel == GxEPD2::GDE0213B1)
  {
    bool m = display.mirror(true);
    for (uint16_t i = 0; i < sizeof(bitmaps) / sizeof(char*); i++)
    {
      display.firstPage();
      do
      {
        display.fillScreen(GxEPD_WHITE);
        display.drawInvertedBitmap(0, 0, bitmaps[i], display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_BLACK);
      }
      while (display.nextPage());
      delay(2000);
    }
    display.mirror(m);
  }
}
#endif

#ifdef _GxBitmaps128x296_H_

void drawBitmaps128x296(GxEPD2_GFX& display);

void drawBitmaps128x296(GxEPD2_GFX& display)
{
#if !defined(__AVR)
  const unsigned char* bitmaps[] =
  {
    Bitmap128x296_1, logo128x296, first128x296, second128x296, third128x296
  };
#else
  const unsigned char* bitmaps[] =
  {
    Bitmap128x296_1, logo128x296 //, first128x296, second128x296, third128x296
  };
#endif
  if (display.epd2.panel == GxEPD2::GDEH029A1)
  {
    bool m = display.mirror(true);
    for (uint16_t i = 0; i < sizeof(bitmaps) / sizeof(char*); i++)
    {
      display.firstPage();
      do
      {
        display.fillScreen(GxEPD_WHITE);
        display.drawInvertedBitmap(0, 0, bitmaps[i], display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_BLACK);
      }
      while (display.nextPage());
      delay(2000);
    }
    display.mirror(m);
  }
}
#endif

#ifdef _GxBitmaps176x264_H_

void drawBitmaps176x264(GxEPD2_GFX& display);

void drawBitmaps176x264(GxEPD2_GFX& display)
{
  const unsigned char* bitmaps[] =
  {
    Bitmap176x264_1, Bitmap176x264_2
  };
  if (display.epd2.panel == GxEPD2::GDEW027W3)
  {
    for (uint16_t i = 0; i < sizeof(bitmaps) / sizeof(char*); i++)
    {
      display.firstPage();
      do
      {
        display.fillScreen(GxEPD_WHITE);
        display.drawInvertedBitmap(0, 0, bitmaps[i], display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_BLACK);
      }
      while (display.nextPage());
      delay(2000);
    }
  }
}
#endif

#ifdef _GxBitmaps400x300_H_

void drawBitmaps400x300(GxEPD2_GFX& display);

void drawBitmaps400x300(GxEPD2_GFX& display)
{
#if !defined(__AVR)
  const unsigned char* bitmaps[] =
  {
    Bitmap400x300_1, Bitmap400x300_2
  };
#else
  const unsigned char* bitmaps[] = {}; // not enough code space
#endif
  if (display.epd2.panel == GxEPD2::GDEW042T2)
  {
    for (uint16_t i = 0; i < sizeof(bitmaps) / sizeof(char*); i++)
    {
      display.firstPage();
      do
      {
        display.fillScreen(GxEPD_WHITE);
        display.drawInvertedBitmap(0, 0, bitmaps[i], display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_BLACK);
      }
      while (display.nextPage());
      delay(2000);
    }
  }
}
#endif

#ifdef _GxBitmaps640x384_H_

void drawBitmaps640x384(GxEPD2_GFX& display);

void drawBitmaps640x384(GxEPD2_GFX& display)
{
#if !defined(__AVR)
  const unsigned char* bitmaps[] =
  {
    Bitmap640x384_1, Bitmap640x384_2
  };
#else
  const unsigned char* bitmaps[] = {}; // not enough code space
#endif
  if (display.epd2.panel == GxEPD2::GDEW075T8)
  {
    for (uint16_t i = 0; i < sizeof(bitmaps) / sizeof(char*); i++)
    {
      display.firstPage();
      do
      {
        display.fillScreen(GxEPD_WHITE);
        display.drawInvertedBitmap(0, 0, bitmaps[i], display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_BLACK);
      }
      while (display.nextPage());
      delay(2000);
    }
  }
}
#endif

struct bitmap_pair
{
  const unsigned char* black;
  const unsigned char* red;
};

#ifdef _GxBitmaps3c200x200_H_

void drawBitmaps3c200x200(GxEPD2_GFX& display);

void drawBitmaps3c200x200(GxEPD2_GFX& display)
{
  bitmap_pair bitmap_pairs[] =
  {
    //{Bitmap3c200x200_black, Bitmap3c200x200_red},
    {WS_Bitmap3c200x200_black, WS_Bitmap3c200x200_red}
  };
  if (display.epd2.panel == GxEPD2::GDEW0154Z04)
  {
    display.firstPage();
    do
    {
      display.fillScreen(GxEPD_WHITE);
      // Bitmap3c200x200_black has 2 bits per pixel
      // taken from Adafruit_GFX.cpp, modified
      int16_t byteWidth = (display.epd2.WIDTH + 7) / 8; // Bitmap scanline pad = whole byte
      uint8_t byte = 0;
      for (int16_t j = 0; j < display.epd2.HEIGHT; j++)
      {
        for (int16_t i = 0; i < display.epd2.WIDTH; i++)
        {
          if (i & 3) byte <<= 2;
          else
          {
#if defined(__AVR) || defined(ESP8266) || defined(ESP32)
            byte = pgm_read_byte(&Bitmap3c200x200_black[j * byteWidth * 2 + i / 4]);
#else
            byte = Bitmap3c200x200_black[j * byteWidth * 2 + i / 4];
#endif
          }
          if (!(byte & 0x80))
          {
            display.drawPixel(i, j, GxEPD_BLACK);
          }
        }
      }
      display.drawInvertedBitmap(0, 0, Bitmap3c200x200_red, display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_RED);
    }
    while (display.nextPage());
    delay(2000);
    for (uint16_t i = 0; i < sizeof(bitmap_pairs) / sizeof(bitmap_pair); i++)
    {
      display.firstPage();
      do
      {
        display.fillScreen(GxEPD_WHITE);
        display.drawInvertedBitmap(0, 0, bitmap_pairs[i].black, display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_BLACK);
        display.drawInvertedBitmap(0, 0, bitmap_pairs[i].red, display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_RED);
      }
      while (display.nextPage());
      delay(2000);
    }
  }
  if (display.epd2.hasColor)
  {
    display.clearScreen(); // use default for white
    int16_t x = (int16_t(display.epd2.WIDTH) - 200) / 2;
    int16_t y = (int16_t(display.epd2.HEIGHT) - 200) / 2;
    for (uint16_t i = 0; i < sizeof(bitmap_pairs) / sizeof(bitmap_pair); i++)
    {
      display.drawImage(bitmap_pairs[i].black, bitmap_pairs[i].red, x, y, 200, 200, false, false, true);
      delay(2000);
    }
    for (uint16_t i = 0; i < sizeof(bitmap_pairs) / sizeof(bitmap_pair); i++)
    {
      int16_t x = -60;
      int16_t y = -60;
      for (uint16_t j = 0; j < 10; j++)
      {
        display.writeScreenBuffer(); // use default for white
        display.writeImage(bitmap_pairs[i].black, bitmap_pairs[i].red, x, y, 200, 200, false, false, true);
        display.refresh();
        delay(2000);
        x += 40;
        y += 40;
        if ((x >= int16_t(display.epd2.WIDTH)) || (y >= int16_t(display.epd2.HEIGHT))) break;
      }
    }
    display.writeScreenBuffer(); // use default for white
    display.writeImage(bitmap_pairs[0].black, bitmap_pairs[0].red, 0, 0, 200, 200, false, false, true);
    display.writeImage(bitmap_pairs[0].black, bitmap_pairs[0].red, int16_t(display.epd2.WIDTH) - 200, int16_t(display.epd2.HEIGHT) - 200, 200, 200, false, false, true);
    display.refresh();
    delay(2000);
  }
}
#endif

#ifdef _GxBitmaps3c104x212_H_

void drawBitmaps3c104x212(GxEPD2_GFX& display);

void drawBitmaps3c104x212(GxEPD2_GFX& display)
{
#if !defined(__AVR)
  bitmap_pair bitmap_pairs[] =
  {
    {Bitmap3c104x212_1_black, Bitmap3c104x212_1_red},
    {Bitmap3c104x212_2_black, Bitmap3c104x212_2_red},
    {WS_Bitmap3c104x212_black, WS_Bitmap3c104x212_red}
  };
#else
  bitmap_pair bitmap_pairs[] =
  {
    {Bitmap3c104x212_1_black, Bitmap3c104x212_1_red},
    //{Bitmap3c104x212_2_black, Bitmap3c104x212_2_red},
    {WS_Bitmap3c104x212_black, WS_Bitmap3c104x212_red}
  };
#endif
  if (display.epd2.panel == GxEPD2::GDEW0213Z16)
  {
    for (uint16_t i = 0; i < sizeof(bitmap_pairs) / sizeof(bitmap_pair); i++)
    {
      display.firstPage();
      do
      {
        display.fillScreen(GxEPD_WHITE);
        display.drawInvertedBitmap(0, 0, bitmap_pairs[i].black, display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_BLACK);
        if (bitmap_pairs[i].red == WS_Bitmap3c104x212_red)
        {
          display.drawInvertedBitmap(0, 0, bitmap_pairs[i].red, display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_RED);
        }
        else display.drawBitmap(0, 0, bitmap_pairs[i].red, display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_RED);
      }
      while (display.nextPage());
      delay(2000);
    }
  }
}
#endif

#ifdef _GxBitmaps3c128x296_H_

void drawBitmaps3c128x296(GxEPD2_GFX& display);

void drawBitmaps3c128x296(GxEPD2_GFX& display)
{
#if !defined(__AVR)
  bitmap_pair bitmap_pairs[] =
  {
    {Bitmap3c128x296_1_black, Bitmap3c128x296_1_red},
    {Bitmap3c128x296_2_black, Bitmap3c128x296_2_red},
    {WS_Bitmap3c128x296_black, WS_Bitmap3c128x296_red}
  };
#else
  bitmap_pair bitmap_pairs[] =
  {
    //{Bitmap3c128x296_1_black, Bitmap3c128x296_1_red},
    //{Bitmap3c128x296_2_black, Bitmap3c128x296_2_red},
    {WS_Bitmap3c128x296_black, WS_Bitmap3c128x296_red}
  };
#endif
  if (display.epd2.panel == GxEPD2::GDEW029Z10)
  {
    for (uint16_t i = 0; i < sizeof(bitmap_pairs) / sizeof(bitmap_pair); i++)
    {
      display.firstPage();
      do
      {
        display.fillScreen(GxEPD_WHITE);
        display.drawInvertedBitmap(0, 0, bitmap_pairs[i].black, display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_BLACK);
        if (bitmap_pairs[i].red == WS_Bitmap3c128x296_red)
        {
          display.drawInvertedBitmap(0, 0, bitmap_pairs[i].red, display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_RED);
        }
        else display.drawBitmap(0, 0, bitmap_pairs[i].red, display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_RED);
      }
      while (display.nextPage());
      delay(2000);
    }
  }
}
#endif

#ifdef _GxBitmaps3c176x264_H_

void drawBitmaps3c176x264(GxEPD2_GFX& display);

void drawBitmaps3c176x264(GxEPD2_GFX& display)
{
  bitmap_pair bitmap_pairs[] =
  {
    {Bitmap3c176x264_black, Bitmap3c176x264_red}
  };
  if (display.epd2.panel == GxEPD2::GDEW027C44)
  {
    for (uint16_t i = 0; i < sizeof(bitmap_pairs) / sizeof(bitmap_pair); i++)
    {
      display.firstPage();
      do
      {
        display.fillScreen(GxEPD_WHITE);
        display.drawBitmap(0, 0, bitmap_pairs[i].black, display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_BLACK);
        display.drawBitmap(0, 0, bitmap_pairs[i].red, display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_RED);
      }
      while (display.nextPage());
      delay(2000);
    }
  }
}
#endif

#ifdef _GxBitmaps3c400x300_H_

void drawBitmaps3c400x300(GxEPD2_GFX& display);

void drawBitmaps3c400x300(GxEPD2_GFX& display)
{
#if !defined(__AVR)
  bitmap_pair bitmap_pairs[] =
  {
    {Bitmap3c400x300_1_black, Bitmap3c400x300_1_red},
    {Bitmap3c400x300_2_black, Bitmap3c400x300_2_red},
    {WS_Bitmap3c400x300_black, WS_Bitmap3c400x300_red}
  };
#else
  bitmap_pair bitmap_pairs[] = {}; // not enough code space
#endif
  if (display.epd2.panel == GxEPD2::GDEW042Z15)
  {
    for (uint16_t i = 0; i < sizeof(bitmap_pairs) / sizeof(bitmap_pair); i++)
    {
      display.firstPage();
      do
      {
        display.fillScreen(GxEPD_WHITE);
        display.drawInvertedBitmap(0, 0, bitmap_pairs[i].black, display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_BLACK);
        display.drawInvertedBitmap(0, 0, bitmap_pairs[i].red, display.epd2.WIDTH, display.epd2.HEIGHT, GxEPD_RED);
      }
      while (display.nextPage());
      delay(2000);
    }
  }
}
#endif


void drawBitmaps(GxEPD2_GFX& display)
{
  display.setFullWindow();
  display.setRotation(0);
#ifdef _GxBitmaps128x250_H_
  drawBitmaps128x250(display);
#endif
#ifdef _GxBitmaps128x296_H_
  drawBitmaps128x296(display);
#endif
#ifdef _GxBitmaps176x264_H_
  drawBitmaps176x264(display);
#endif
#ifdef _GxBitmaps400x300_H_
  drawBitmaps400x300(display);
#endif
#ifdef _GxBitmaps640x384_H_
  drawBitmaps640x384(display);
#endif
  // 3-color
#ifdef _GxBitmaps3c104x212_H_
  drawBitmaps3c104x212(display);
#endif
#ifdef _GxBitmaps3c128x296_H_
  drawBitmaps3c128x296(display);
#endif
#ifdef _GxBitmaps3c176x264_H_
  drawBitmaps3c176x264(display);
#endif
#ifdef _GxBitmaps3c400x300_H_
  drawBitmaps3c400x300(display);
#endif
  // show these after the specific bitmaps
#ifdef _GxBitmaps200x200_H_
  drawBitmaps200x200(display);
#endif
  // 3-color
#ifdef _GxBitmaps3c200x200_H_
  drawBitmaps3c200x200(display);
#endif
}
