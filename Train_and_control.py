import time
import serial
import serial.tools.list_ports as porttest
import numpy as np

# fft funciton:
def fast_fft(vec, S_time): #Performs FFT
	f = np.fft.fft(vec)
	t = linspace(0,S_time,lim + 1)
	N = len(t)                            #Number of Samples
	dt = S_time/N                         #Inter-sample length
	w = np.fft.fftfreq(N, dt)             # List of frequencies for the FFT
	ipos = where(w>0)
	freqs = w[ipos]                       # only look at positive frequencies
	mags = abs(f[ipos])                   # magnitude spectrum
	#return f, w, ipos, freqs, mags		
	return mags[1:55]
		
def readVec(ser):
	vec=[]
	cnt=0
	lim = 200
	# Empty the port buffer
	ser.flushInput()
	# Read 'lim' number of samples
	while cnt <= lim:      #ser.read() is not None and cnt <= 100:
		# Wait until header 'H'
		if ser.read() is 'H':
			# Read n bytes for 'ser.read(n)'
			data = ser.read(2) and 0x3FF
			# Add the data to the vector and decode fron hex to integer
			vec.append(int(data.encode('hex'), 16))
			# increment the counter
			cnt += 1
	return vec

	
def fileWriteline(f,npVec):
	npVec.tofile(f,' ','%s')
	f.write('\n')


def saveTrainingFile(cmd, num_vecs):
	fp = open('./train_data/'+cmd+'.log','w')
	for i in range(num_vecs):
		fft_vec = readVec(comm)
		fft_vec = np.fft.fft(fft_vec)
		fileWriteline(fp, fft_vec)
	fp.close()

	
	
#################  Set up Ports  #################
	
ports = list(porttest.comports())
port = []
print ports
# Determine which port is the Arduino
for p in ports:
    if p[1][0:7] == 'Arduino':
        port.append(int(p[0].split('M')[1]) -1)

# Connect to the Arduino ports
for p in port:
	if serial.Serial(p,baudrate=115200).readline() == 'CNTRL':
		control = serial.Serial(p,baudrate=115200)
	else:
		comm = serial.Serial(p,baudrate=115200)

################# TRAIN DATA #################		

input('Press enter to generate baseline training data')
saveTrainingFile('baseline',1000)
print 'Baseline dataset training set record complete\n\n'

input('Press enter to record light on command')
saveTrainingFile('light_on',1000)
print 'Light on command dataset record complete\n\n'

base = []
fp = open('./train_data/baseline.log','r')
for line in fp.readlines():
	base.append(np.array([int(i) for i in line.split(' ')]))
fp.close()
	
light = []
fp = open('./train_data/light_on.log','r')
for line in fp.readlines():
	base.append(np.array([int(i) for i in line.split(' ')]))
fp.close()

################# CONTROL THE LIGHT #################

base_cmd = np.mean(base,axis=0)
light_cmd = np.mean(light,axis=0)

while not KeyboardInterrupt:
	vec = readVec(comm)
	b_com = np.sum(abs(base_cmd - vec))
	l_com = np.sum(abs(light_cmd - vec))
	if l_com < b_com:
		comm.write('X')
	else:
		comm.write('O')
	