import oscP5.*;
import netP5.*;

OscP5 oscP5;

// Estado visual
color figuraColor = color(255);
float angulo = 0;
boolean animar = true;

// Texto en pantalla (BONUS)
String ultimo = "";

void setup() {
  size(800, 600);
  oscP5 = new OscP5(this, 12000);

  textAlign(CENTER, CENTER);
  textSize(32);
}

void draw() {
  background(30);

  translate(width/2, height/2);

  // Animación
  if (animar) {
    angulo += 0.03;
  }

  rotate(angulo);

  // Figura
  fill(figuraColor);
  rectMode(CENTER);
  rect(0, 0, 200, 200);

  // Reset transformación para texto
  resetMatrix();

  // Texto en pantalla (último comando)
  fill(255);
  text("Comando: " + ultimo, width/2, 50);
}

void oscEvent(OscMessage msg) {

  // 🎨 CAMBIO DE COLOR
  if (msg.checkAddrPattern("/color")) {

    String valor = msg.get(0).stringValue();
    ultimo = valor;

    if (valor.equals("rojo")) {
      figuraColor = color(255, 0, 0);
    }
    else if (valor.equals("azul")) {
      figuraColor = color(0, 0, 255);
    }
    else if (valor.equals("verde")) {
      figuraColor = color(0, 255, 0);
    }
  }

  // ⚙️ ACCIONES
  if (msg.checkAddrPattern("/accion")) {

    String cmd = msg.get(0).stringValue();
    ultimo = cmd;

    if (cmd.equals("girar")) {
      angulo += 1;
    }
    else if (cmd.equals("iniciar")) {
      animar = true;
    }
    else if (cmd.equals("detener")) {
      animar = false;
    }
  }
}
