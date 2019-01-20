from sensapex import SensapexDevice
import time 
dev = SensapexDevice(2)

pos1 = dev.get_pos()
print("start: %s" % pos1)
#print (dev.set_custom_slow_speed(1))
pos4 = pos1[:]
#dev.goto_pos(pos1, speed=100, block=True, linear=False)
for speed in range(1, 20):
    pos2 = pos1[:]
    pos2[0] += 5000 * speed  # ~3 second move
    pos2[1] += 10000 * speed  # ~3 second move
    
    
 #   dev.set_custom_slow_speed(1)
    
    dev.goto_pos(pos2, [speed,1000,0,0],block=True)
   
    #dev.goto_pos(pos4, speed=1000, block=False, linear=True)
    #time.sleep(0.3)  # wait to be sure uMp has settled
    #pos3 = dev.get_pos()
    #print("Speed: %d um/s   x error: %0.2f um" % (speed, 1e-3 * (pos3[0] - pos2[0])))
    #print("   start: %d   target: %d  end: %d" % (pos1[0], pos2[0], pos3[0]))
 #   dev.set_custom_slow_speed(0)
    #dev.goto_pos(pos1, speed=100, block=True)

