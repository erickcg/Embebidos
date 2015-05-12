import time;
import serial;
import thread;
import sys;

arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1.5);
rapidezActual = 0;
tiempoVariable = time.time();
tiempoInicio = time.time();

#variables de pid
if len(sys.argv) > 1 :
	print(sys.argv[1]);
	velocidadReferencia = float(sys.argv[1]);
else :
	velocidadReferencia = 0.8;

errorOld = 0;
PIDvarOld = 0;
K = 2740.02;
ti = 1.1386;
Ts = 0.033;
#errorActual = 0;

proxSensor = 1024;
velToArduino = 0;
first = True;

def input_thread(L) :
	string = raw_input();
	L.append(string);

def PID(velocidad):
	global velocidadReferencia;
	global errorOld;
	global PIDvarOld;
	global K;
	global ti;
	global Ts;
#	global errorActual;

	errorActual = velocidadReferencia - velocidad;
	respuesta = PIDvarOld + (K/ti)*(Ts+ti)*errorActual - (K*errorOld);
	print( str(errorActual));
	print("," + str(velocidad));

	errorOld = errorActual;
	PIDvarOld = respuesta;

	if respuesta > 100 :
		respuesta = 100;
	elif respuesta < 0 :
		respuesta = 0;

	return respuesta;

L = [];
thread.start_new_thread(input_thread, (L,));

while True:
	#ver velocidad
	serialString = '';
	serialString = arduino.readline();
	if serialString == '':
		rapidezActual = 0;
		pass
	
	if time.time() - tiempoInicio > 1.2 : 
		rapidezActual -= 0.2;
		#PIDvarOld = 0;
		#errorOld = 0;
		pass
		
	#print(serialString);
	if "::prox" in serialString:
		proxSensor = int(serialString.split(' ')[1]);
#		print(int(proxSensor));
	
	if "::velup" in serialString and first == False:
		tiempoVariable = time.time() - tiempoInicio;
		tiempoInicio = time.time();
		#4 cm radio = 12.5664   --- 1mm/ms = 1m/s
		#print("PID: " + str(velToArduino) + " \n ");
		#print("rapidez actual: " + str(rapidezActual));		
		#print("referencia: " + str(velocidadReferencia));
		#print("Error: " + str(errorActual));
		#print("tiempo var: " + str(tiempoVariable));
		rapidezActual = 125.664 / (tiempoVariable*1000);
	else :
		first = False;
	
	if proxSensor > 50: 
		velToArduino = PID(rapidezActual);
		arduino.write("di" + str(velToArduino)+"$");
#		print("PID: " + str(velToArduino));

	elif proxSensor < 50:
		arduino.write("st$");
		#print("detener");
	
		#velToArduino = 0;
		#proxSensor = serialString.split(' ')[1];

		print("Se encontro un obstaculo a:" + str(proxSensor));
		#if proxSensor < 30:
		#	velToArduino = 5;
		#	pass
		#if proxSensor < 25:
		#	velToArduino = 50;
		#	pass

		#print("reversa en: " + str(velToArduino) + " \n ");
		pass
#	rapidezActual -= 0.01;
#	print("\n");
	#manejo de thread para cambiar velocidad
	if L :
		try :
			velocidadReferencia = float(L[0]);
			print("La nueva velocidad de referencia sera: " + str(L[0]));
		except :
			print("no fue un numero valido");

		del L
		L = [];
		thread.start_new_thread(input_thread, (L,));
		pass
