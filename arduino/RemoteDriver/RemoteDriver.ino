#define XAXIS_PWM_PORT 5
#define YAXIS_PWM_PORT 6
#define ROTATION_PWM_PORT 3
#define THROTTLE_PWM_PORT 9
#define LOG_NONE 0
#define LOG_INFO 1
#define LOG_ERROR 1
#define LOG_DEBUG 2
#define LOGLEVEL LOG_NONE

/*
 * Sets PWM frequency for given channel
 */
void setPwmFrequency(int pin, int divisor) {
  byte mode;
  if(pin == 5 || pin == 6 || pin == 9 || pin == 10) {
    switch(divisor) {
      case 1: mode = 0x01; break;
      case 8: mode = 0x02; break;
      case 64: mode = 0x03; break;
      case 256: mode = 0x04; break;
      case 1024: mode = 0x05; break;
      default: return;
    }
    if(pin == 5 || pin == 6) {
      TCCR0B = TCCR0B & 0b11111000 | mode;
    } else {
      TCCR1B = TCCR1B & 0b11111000 | mode;
    }
  } else if(pin == 3 || pin == 11) {
    switch(divisor) {
      case 1: mode = 0x01; break;
      case 8: mode = 0x02; break;
      case 32: mode = 0x03; break;
      case 64: mode = 0x04; break;
      case 128: mode = 0x05; break;
      case 256: mode = 0x06; break;
      case 1024: mode = 0x7; break;
      default: return;
    }
    TCCR2B = TCCR2B & 0b11111000 | mode;
  }
}

/*
 * ...
 */
void setup()
{
  Serial.begin(115200);

  setPwmFrequency(XAXIS_PWM_PORT, 1);
  setPwmFrequency(YAXIS_PWM_PORT, 1);
  setPwmFrequency(ROTATION_PWM_PORT, 1);
  setPwmFrequency(THROTTLE_PWM_PORT, 1);
  
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
}

/*
 * Logs stuff
 */
void Log(int LogLevel, String str)
{
  if (LOGLEVEL >= LogLevel)
    Serial.print(str);
}

/*
 * Reads data chunks from Serial port (RPi)
 * Decodes those chunks according to format
 * Performs sanity checks on data
 * Sends data to PWM outputs
 */
void loop()
{
  static char buffer[80];

  // Read a chunk of data from RPi
  String data  = Serial.readStringUntil('\n');
  Serial.read(); //read the \n

  Log(LOG_DEBUG, "Data: " + data + "\n");

  // Get all delimeters
  int xIndex = data.indexOf('X');
  int yIndex = data.indexOf('Y');
  int rIndex = data.indexOf('R');
  int tIndex = data.indexOf('T');
  int endIndex = data.indexOf('#');

  Log(LOG_DEBUG, "Indexes: " + String(xIndex) + ", " 
                             + String(yIndex) + ", "
                             + String(rIndex) + ", "
                             + String(tIndex) + ", "
                             + String(endIndex) + "\n");

  // Sanity check - search for start of chunk, and for existance of delimeters
  if ((xIndex == 0) && (yIndex != -1) && (rIndex != -1) && (tIndex != -1)  && (endIndex != -1) ) {

    // Do the splitting with delimeters we found
    // Format of chunk is "XxaxisvalYyaxisvalRrotationvalTthrottleval#"
    String xAxis = data.substring(xIndex + 1, yIndex);
    String yAxis = data.substring(yIndex + 1, rIndex);
    String rotation = data.substring(rIndex + 1, tIndex);
    String throttle = data.substring(tIndex + 1, endIndex);    

    Log(LOG_INFO, "Got xAxis: " + xAxis + "\n");
    Log(LOG_INFO, "Got yAxis: " + yAxis + "\n");
    Log(LOG_INFO, "Got rotation: " + rotation + "\n");
    Log(LOG_INFO, "Got throttle: " + throttle + "\n");

    // Convert and send to PWM
    int xAxisVal = xAxis.toInt();
    int yAxisVal = yAxis.toInt();
    int rotationVal = rotation.toInt();
    int throttleVal = throttle.toInt();
    outputVoltage(XAXIS_PWM_PORT, xAxisVal);
    outputVoltage(YAXIS_PWM_PORT, yAxisVal);
    outputVoltage(ROTATION_PWM_PORT, rotationVal);
    outputVoltage(THROTTLE_PWM_PORT, throttleVal);
  } else {
    Log(LOG_ERROR, "Timeout!\n");
  }
}

/* 
 *  Outputs given percentage as corresponding duty cycle to
 *  given PWM output. 
 *  A filter should be connected to the PWM outputs to convert them
 *  to "DAC" ports.
 */
void outputVoltage(int port, int percentage)
{
  // Maximum PWM value is 255 (byte), hence this calculation
  int pwmValue = (255 * percentage) / 100;

  Log(LOG_DEBUG, "Writing to port [" + String(port)
               + "] value: " + String(pwmValue) + "\n");
  
  analogWrite(port, pwmValue);
}

