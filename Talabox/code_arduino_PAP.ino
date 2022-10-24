// les pins
const int stepX = 2;
const int dirX  = 5;

const int stepY = 3;
const int dirY  = 6;

const int enPin = 8;

const int stepX2 = 4;
const int dirX2  = 7;

const int stepY2 = 12;
const int dirY2  = 13;

// variables pour plus tard
const int Vmax = 100; // taux de rafraichissement max des moteurs

int vitX = 0; //vitesse horizontale
int vitY = 0; //vitesse verticale
int vitX2 = 0;
int vitY2 = 0;
char message[25];
int d = 0;
int d2 = 0;
int dir1 = 0;
int dir2 = 0;
int dir3 = 0;
int dir4 = 0;
int dir12 = 0;
int dir22 = 0;
int dir32 = 0;
int dir42 = 0;


void gauche(){
  digitalWrite(dirX,LOW);
}

void droite(){
  digitalWrite(dirX,HIGH);
}

void monter(){
  digitalWrite(dirY,LOW);
}

void descendre(){
  digitalWrite(dirY,HIGH);
}

void gauche2(){
  digitalWrite(dirX2,HIGH);
}

void droite2(){
  digitalWrite(dirX2,LOW);
}

void monter2(){
  digitalWrite(dirY2,LOW);
}

void descendre2(){
  digitalWrite(dirY2,HIGH);
}

void stop(int dirA, int dirB, int dirC, int dirD, int dirA2, int dirB2, int dirC2, int dirD2){
  if(dirA == 1){
    gauche();
  }
  if(dirB == 1){
    droite();
  }
  if(dirC == 1){
    monter();
  }
  if(dirD == 1){
    descendre();
  }
  if(dirA2 == 1){
    gauche2();
  }
  if(dirB2 == 1){
    droite2();
  }
  if(dirC2 == 1){
    monter2();
  }
  if(dirD2 == 1){
    descendre2();
  }
}


int vitesse(int a){
  if (a == 0){
    return 0;
  }
  else{
    return Vmax*99/a; // on donne la vitesse comme un facteur de la vitesse max, sauf que c'est en fréquence donc on divise par le coef
  }
}

void deplacement(int vitX,int vitY,int vitX2,int vitY2){
  int t1 = vitX;
  int t2 = vitY;
  int t1current = t1;
  int t2current = t2;
  int t12 = vitX2;
  int t22 = vitY2;
  int t12current = t12;
  int t22current = t22;
  int mini = 32000;
  if (t1current == 0){t1current = 32000;}
  if (t2current == 0){t2current = 32000;}
  if (t12current == 0){t12current = 32000;}
  if (t22current == 0){t22current = 32000;}
  while (Serial.available() < 11) { //  le serial.available check si un message arrive, ce qui signifie que nos 0.1s sont finies
    if(t1current==0 && vitX != 0){
      t1current = t1;
      digitalWrite(stepX,HIGH-digitalRead(stepX));
    }
    if(t2current == 0 && vitY !=0){
      t2current = t2;
      digitalWrite(stepY,HIGH-digitalRead(stepY));
    }
    if(t12current==0 && vitX2 != 0){
      t12current = t12;
      digitalWrite(stepX2,HIGH-digitalRead(stepX2));
    }
    if(t22current == 0 && vitY2 !=0){
      t22current = t22;
      digitalWrite(stepY2,HIGH-digitalRead(stepY2));
    }
    mini = min(min(t1current,t2current),min(t12current,t22current));
    if (mini == 32000){
      delayMicroseconds(100);
    }
    else{
      delayMicroseconds(mini);
      t1current = t1current - mini;
      t2current = t2current - mini;
      t12current = t12current - mini;
      t22current = t22current - mini;
    }
  }
}

void setup() {
  // Sets the two pins as Outputs
  pinMode(stepX,OUTPUT);
  pinMode(dirX,OUTPUT);

  pinMode(stepY,OUTPUT);
  pinMode(dirY,OUTPUT);
  
  pinMode(stepX2,OUTPUT);
  pinMode(dirX2,OUTPUT);

  pinMode(stepY2,OUTPUT);
  pinMode(dirY2,OUTPUT);

  pinMode(enPin,OUTPUT);
  
  digitalWrite(enPin,LOW);
  digitalWrite(dirX,HIGH);
  digitalWrite(dirY,LOW);
  digitalWrite(dirX2,HIGH);
  digitalWrite(dirY2,LOW);

   Serial.begin(9600); 
}


void loop()
{  
  //on lit les entrée de serial, si ya 5 chiffres en entré ça veut dire que ya un message
  //on utilise la bonne technique d'internet pour récup deux valeurs de 0 à 99
  //la 1ere est la vitesse du moteur longitudinal
  //la 2eme est vitesse du moteur vertical
  //la direction est donnée par le 1er chiffre selon 4 cas (0,1,2 ou 3)
  //si le 1er chiffre vaut 9 alors c'est qu'on est en butée dans une des directions, donc on stop

  if (Serial.available() > 11) {
    Serial.readBytesUntil('E',message,15);
    for (int i = 0;i <= 10 ; i++){
      if (message[i]=='S'){
        message[0]=message[i+1];
        message[1]=message[i+2];
        message[2]=message[i+3];
        message[3]=message[i+4];
        message[4]=message[i+5];
        message[5]=message[i+6];
        message[6]=message[i+7];
        message[7]=message[i+8];
        message[8]=message[i+9];
        message[9]=message[i+10];
        break;
      }
    }
    d= (message[0]-48);// lis le 1er bit
    //Si le message et 9 ca veut dire un buttee est active
    //On change de direction par rapport au buttee
    
    if(d==9){
      dir1 = message[1]-48;
      dir2 = message[2]-48;
      dir3 = message[3]-48;
      dir4 = message[4]-48;
      dir12 = message[6]-48;
      dir22 = message[7]-48;
      dir32 = message[8]-48;
      dir42 = message[9]-48;
      
      stop(dir1,dir2,dir3,dir4,dir12,dir22,dir32,dir42);
      deplacement(vitX,vitY,vitX2,vitY2);
    }
    else{
      d2 = (message[5]-48);
      
      vitX= (message[1]-48)*10 + message[2]-48; 
      vitX2= (message[6]-48)*10 + message[7]-48;
  
      vitY= (message[3]-48)*10 + message[4]-48;
      vitY2= (message[8]-48)*10 + message[9]-48;
       
      if(d==0) {
        gauche();
        monter();
      }
      if(d==1){
        gauche();
        descendre();
      }
      if(d==2){
        droite();
        monter();
      }
      if(d==3){
        droite();
        descendre();
      }
      if(d2==0) {
        gauche2();
        monter2();
      }
      if(d2==1){
        gauche2();
        descendre2();
      }
      if(d2==2){
        droite2();
        monter2();
      }
      if(d2==3){
        droite2();
        descendre2();
      }
      vitX= vitesse(vitX);
      vitY= vitesse(vitY);
      vitX2= vitesse(vitX2);
      vitY2= vitesse(vitY2);
      deplacement(vitX,vitY,vitX2,vitY2);
    }
  }
}
