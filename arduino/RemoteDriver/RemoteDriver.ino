#define ROLL_PWM_PORT 5
#define PITCH_PWM_PORT 6
#define LOG_NONE 0
#define LOG_INFO 1
#define LOG_ERROR 1
#define LOG_DEBUG 2
#define LOGLEVEL LOG_NONE

/*
 * ...
 */
void setup()
{
  Serial.begin(115200);
  
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
  int startIndex = data.indexOf('$');
  int endIndex = data.indexOf('#');
  int delim = data.indexOf('|');

  Log(LOG_DEBUG, "Indexes: " + String(startIndex) + ", " 
                             + String(endIndex) + ", "
                             + String(delim) + "\n");

  // Sanity check - search for start of chunk, and for existance of delims
  if ((startIndex == 0) && (endIndex != -1) && (delim != -1)) {

    // Do the splitting with delims we found
    // Format of chunk is "$rollVal|pitchVal#"
    String rollStr = data.substring(startIndex + 1, delim);
    String pitchStr = data.substring(delim + 1, endIndex);

    Log(LOG_INFO, "Got roll: " + rollStr + "\n");
    Log(LOG_INFO, "Got pitch " + pitchStr + "\n");

    // Convert and send to PWM
    int rollVal = rollStr.toInt();
    int pitchVal = pitchStr.toInt();
    outputVoltage(ROLL_PWM_PORT, rollVal);
    outputVoltage(PITCH_PWM_PORT, pitchVal);
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

