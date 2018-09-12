/**
 Credit to:
 oscP5sendreceive by Andreas Schlegel
 his example showed me how to send and receive osc messages.
 Extended it to display lidar orginated positions.
 This is incorporated on a mini monitor with my installation.
 oscP5 website at http://www.sojamo.de/oscP5
 ~/python/osc/processingReceiveTest.pde
 James Tregaskis
 james@tregaskis.org
 August 2018
 
 */

import oscP5.*;
import netP5.*;
ArrayList <Circle> points= new ArrayList <Circle>(); 
OscP5 oscP5;
NetAddress myRemoteLocation;
int time;
int wait = 1000;
int messages_per_second =0;
int ALLOWED_MAX_PER_SECOND = 1000;

PImage bg1, bg2, bg3, bg4, bg5, bg6, bg7;
int messages = 0;
void setup() {
  time = millis();
  int message_num =0;

  size(1000, 820);
  frameRate(60);

  //bg1 = loadImage("1.JPG");
  bg2 = loadImage("2.JPG");


  /* start oscP5, listening for incoming messages at port 5005 */
  oscP5 = new OscP5(this, 5005);

  /* myRemoteLocation is a NetAddress. a NetAddress takes 2 parameters,
   * an ip address and a port number. myRemoteLocation is used as parameter in
   * oscP5.send() when sending osc packets to another computer, device, 
   * application. usage see below. for testing purposes the listening port
   * and the port of the remote location address are the same, hence you will
   * send messages back to this sketch.
   */
  myRemoteLocation = new NetAddress("10.10.10.1", 5006);
}

//flush ArrayList of circle objects
void clearDown(int num) {
  //println(points.size());
  if (points.size() >= num) {
    while (points.size() >=num) {
      //println(points.size());
      points.remove(0);
    }
  }
}

void draw() {

  background(bg2);

  if (millis()-time >= wait) {
    time=millis();
    messages_per_second = messages;
    messages = 0;
    messages_per_second=0;
  } else {
    
  }

  noFill();
  stroke(0);
  strokeWeight(4);
  ellipse(width/2, height/2, 10, 10);
  stroke(0);
  ellipse(width/2, height/2, 100, 100);
  ellipse(width/2, height/2, 200, 200);
  ellipse(width/2, height/2, 300, 300);
  ellipse(width/2, height/2, 500, 500);
  ellipse(width/2, height/2, 800, 800);
  ellipse(width/2, height/2, 800, 800);
  fill(0); 
  noStroke();

  pushMatrix();

  translate(width/2, height/2);
  if (points.size() > 0) {
    for (int i = points.size()-1; i > 0; i--) {
      if (points.get(i) != null && points.size()>0) {
        points.get(i).setAge(10);
        if (points.get(i).getAge() >100) {
          points.remove(i);
        } else {
          points.get(i).display();
        }
      }
    }
  }
  popMatrix();
}


///* incoming osc message are forwarded to the oscEvent method. */
void oscEvent(OscMessage theOscMessage) {
  /* check if theOscMessage has the address pattern we are looking for. */
  //
  //println(theOscMessage);
  if (theOscMessage.checkAddrPattern("/st")) {
    if (theOscMessage.checkAddrPattern("/st")==true) {

      // check if the typetag is the right one
      if (theOscMessage.checkTypetag("ii")) {
        /* parse the oscMessage and extract the values from the osc message arguments */
        int secondValue = theOscMessage.get(0).intValue();
        int thirdValue = theOscMessage.get(1).intValue();

        //println("showing ", theOscMessage.get(0).intValue(), "--", theOscMessage.get(1).intValue(), "--", theOscMessage.get(1).intValue());
        ////////////////////////////////////////////////////////////////////////
        // VERY IMPORTANT LINE:
        // this forwards the data with OSC to the python 
        // code to work the servos.
        // this provided me a way of combining
        // display of the Lidar points with this processing sketch
        // as well as work the servos with I2C in python.
        // there is i2c in processing but the python code can run as a 
        // stand-alone program, thus giving
        // a choice of circumventing this processing program
        // if required. The Python port will have to be changed from 5006 to 5005 
        // if this happens, as the forwarding port address isa 5006 in the 'combined' 
        // route.
        
        //println("messages ", messages);
        //throttle messages if over alloted ALLOWED_MAX_PER_SECOND
        // because pythond program cannot process too many as it runs out of threads
        //messages++;
        //if (messages_per_second<ALLOWED_MAX_PER_SECOND) {
          oscP5.send(theOscMessage, myRemoteLocation);
        //}
        //////////////////////////////////////////////////////////////////////
        // conversion to cartesian coordinates
        float x, y;
        x = cos (radians(secondValue))* thirdValue;
        y = sin (radians(secondValue))* thirdValue;
        //&& secondValue > 0 && secondValue <20 &&
        if ((secondValue > 150 && secondValue < 354 && thirdValue > 2400) || (secondValue >= 0 && secondValue < 160 && thirdValue > 3400))
        {

          // do nothing; a column is here
        } else {
          //println (" secondValue ", secondValue, " thirdValue ", thirdValue);

          //println(" values: ", secondValue, thirdValue);
          clearDown(200);
          points.add(new Circle(x/5, y/5));
        }
        return;
      }
    } 
    //println("### received an osc message. with address pattern "+theOscMessage.addrPattern());
  }
}
class Circle {
  float x, y, xSpeed, ySpeed;
  int age = 0;

  Circle(float x, float y) {
    this.x = x;
    this.y = y;
  }
  void move() {
    x += xSpeed;
    y += ySpeed;
  }

  void display() {
    fill(255, 2, 10);

    ellipse(x, y, 20, 20);
  }

  void setAge(int a) {
    age=age+a;
  }

  int getAge() {

    return age;
  }
}
