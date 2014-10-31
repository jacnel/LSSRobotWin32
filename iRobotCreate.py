import create
import time
import numpy
import math
import signal
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import matplotlib.lines as Line2D
from matplotlib.ticker import MaxNLocator
from numpy import sin, cos, tan
from datetime import datetime


class iRobotCreate:

    def __init__(self, simulation_mode, update_freq=5, optional_port_number = None):
        """ Constructor
            -simulation_mode should be set to 1 for simlation mode, 0 for actual Create use
            -update_freq should be set to frequency greater than 0
            -optional_port_number should be used when not in simulation mode, should pass the integer port number for Windows
                otherwise pass string for path to port for Linux/Max
        """
        #[cjg] and [clg] 
        #initial values for variables needed for added code
        self.xcoord = np.zeros((6, 11))
        self.ycoord = np.zeros((6, 11))
        self.v = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.omega = np.array([-0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5])
        self.trajectory() #fill in LUT for travel distances
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
	self.vel = 0.0
	self.w = 0.0
        self.simulation = simulation_mode
        if simulation_mode != 1 and simulation_mode !=0 :
            raise InputError('Invalid Simulation Argument: ', simulation_mode)
        if simulation_mode == 1:
            self.mode_handler = iRobotSim(update_freq)
        else:
            if optional_port_number == None:
                raise InputError('No port number detected for non simulation mode.')
	    else:
                self.mode_handler = iRobotCreate_real( update_freq, optional_port_number)


    def sim(self):
        """
            ***Only available in simultion mode***
            Once you give the create the commands, call sim to execute the simulation
        """
        if self.simulation:
            self.mode_handler.sim()
        else:
            raise InputError('Method cannot be called while not in simulation mode')

    def set_noise(self, v, omega):
        """
            ***Only available in simulation mode***
            
        """
        if self.simulation:
            self.mode_handler.set_noise(v, omega)
        else:
            raise InputError('Method cannot be called while not in simulation mode')

    def set_workspace(self, x_min, x_max, y_min, y_max):
        """
            ***Only available in simulation mode***
            
        """
        if self.simulation:
            self.mode_handler.set_workspace(x_min, x_max, y_min, y_max)
        else:
            raise InputError('Method cannot be called while not in simulation mode')
        
    def set_update_rate(self, update_rate):
        """
            ***Only available in simulation mode***
            
        """
        if self.simulation:
            self.mode_handler.set_update_rate(update_rate)
        else:
            raise InputError('Method cannot be called while not in simulation mode')

    def move_roomba(self, x, y, theta):
        """
            ***Only available in simulation mode***
            
        """
        if self.simulation:
            self.mode_handler.move_roomba(x, y, theta)
        else:
            raise InputError('Method cannot be called while not in simulation mode')

    def position(self,i):
        """
            ***Only available in simulation mode***
            
        """
        if self.simulation:
            return self.mode_handler.position(i)
        else:
            raise InputError('Method cannot be called while not in simulation mode')

    def get_pose(self):
        """
            ***Only available in simulation mode***
            
        """
        if self.simulation:
            return self.mode_handler.get_pose()
        else:
            raise InputError('Method cannot be called while not in simulation mode') 
        
    def set_robot_frame(self):
        """
            ***Only available in simulation mode***
            
        """
        if self.simulation:
            self.mode_handler.set_robot_frame()
        else:
            raise InputError('Method cannot be called while not in simulation mode')

    def set_world_frame(self):
        """
            ***Only available in simulation mode***
            
        """
        if self.simulation:
            self.mode_handler.set_world_frame()
        else:
            raise InputError('Method cannot be called while not in simulation mode')

    def set_trail_size(self, trail_size):
        """
            ***Only available in simulation mode***
            
        """
        if self.simulation:
            self.mode_handler.set_trail_size(trail_size)
        else:
            raise InputError('Method cannot be called while not in simulation mode')

    def set_real_time(self, switch):
        """
            ***Only available in simulation mode***
            
        """
        if self.simulation:
            self.mode_handler.set_real_time(switch)
        else:
            raise InputError('Method cannot be called while not in simulation mode')

    def setvel(self, v, omega):
        """
            -v should a in meters/seconds
            -omega should be in radians/seconds
        """
        self.mode_handler.setvel(v, omega)

    def direct_drive(self, v1, v2):
        """
            -v1 and v2 should be in meters/seconds
        """
        self.mode_handler.direct_drive(v1, v2)

   
    def angle_sensor(self):
        """
            Reads Create's angle sensors
            Returns angle in degrees
        """
        return self.mode_handler.angle_sensor()

    def distance_sensor(self):
        """
            Reads Create's distance sensor
            Returns distance in meters
        """
        return self.mode_handler.distance_sensor()


    def isbumped(self):
        """
            ***Not available in Simulation Mode***
            Reads Create's bumper sensors
            Returns true if bumped, otherwise false
        """
        if not self.simulation:
            return self.mode_handler.isbumped()
        else:
            raise InputError('Method cannot be called while in simulation mode')

    def rotate(self, angle_rad):
        """
            -angle_rad should be in radians
        """
        self.mode_handler.rotate(angle_rad)

    def forward(self, distance_m):
        """
            -distance_m should be in meters
        """
        self.mode_handler.forward(distance_m)

    def resume_control(self):
        """
            ***Not available in Simulation Mode***
            Resets the Create so it can be used after it was picked up
        """
        if not self.simulation:
            self.mode_handler.resume_control()
        else:
            raise InputError('Method cannot be called while in simulation mode')

    def delete(self):
        """
            ***Not available in Simulation Mode***
            Destroys the connection to the Create
        """
        if not self.simulation:
            self.mode_handler.delete()
        else:
            raise InputError('Method cannot be called while in simulation mode')

    #Added by CLG
    #returns position in x, y, theta            
    def whereAmI(self):
        """returns current position"""
        coordinates = [self.x, self.y, self.theta]
        return coordinates

    #Added by CJG
    #returns difference between -pi and pi        
    def angleSub(self, startAng, endAng):
        #startAng and endAng must be in radians
        alpha = endAng - startAng
        if(alpha > np.pi):
            alpha -= (2 * np.pi)
        elif(alpha < -np.pi):
            alpha += (2 * np.pi)
        return alpha

    #Added by CJG and CLG
    #move to a point x, y, theta (rads)
    def moveTo(self, nx, ny, ntheta):
        """moves to a point"""
        dX = nx - self.x
        dY = ny - self.y
        #forces ntheta to equivalent angle between -pi and pi
        ntheta = ntheta % (2*np.pi)
        if ntheta > np.pi:
            ntheta -= 2*np.pi
        
        #finds the angle between current and new point
        alpha = math.atan2(dY, dX)
        #decides to rotate and move or stay in place if distance to point is too small
        if not math.fabs(dX) < .01 or not math.fabs(dY) < .01: 
            self.rotate(self.angleSub(self.theta, alpha))
            dist = np.sqrt(dX**2 + dY**2)
            self.forward(dist)
        else:
            alpha = self.theta
        
        #final rotation to new point
        self.rotate(self.angleSub(alpha, ntheta))
        #set current position
        self.x = nx
        self.y = ny
        self.theta = ntheta

    #Added by CLG
    def trajectory(self):     
        #create table of all end points from current point
        x = np.zeros(11)
        y = np.zeros(11)
        theta = np.zeros(11) 
        
        horizon = 2
        dt = 0.2
        num_steps = int(horizon/dt)
        
        for vdex in range(0, 6):
            for odex in range (0, 11):
                for index in range(1,num_steps+1):
                    x[index] = x[index-1] + self.v[vdex]*np.cos(theta[index-1])*dt  #calculate value at each step
                    y[index] = y[index-1] + self.v[vdex]*np.sin(theta[index-1])*dt
                    theta[index] = theta[index-1] + self.omega[odex]*dt
                if vdex==5 and not odex ==5:
                    continue #all speed values when velocity = .5 except when omega = 0 are invalid and should be left at 0
                else:   
                    self.xcoord[vdex][odex] = x[10] #set point in table to point reached after 2 seconds
                    self.ycoord[vdex][odex] = y[10] #set point in table to point reached after 2 seconds
                        
    #Added by CJG
    #trajectory method must be called before use
    def goToGoal(self, xGoal, yGoal):
    	
        #should be a 6 x 11 matrix of distances between trajectory end points and goal points
        dist = ((self.xcoord - xGoal)**2 + (self.ycoord - yGoal)**2)**.5
        
        #finds the point at which minimum cost occurs
        #if cost is <.1, it does not move
        
        #realized there is strange logic after implementation
        #left in because this yielded best results from when we tried to fix it
        if(dist.flatten().argmin() < .1):
            self.setvel(0,0)
            return;
        
        index = dist.flatten().argmin()
        
        #find row and column of minimum value based off of flattened index
        rowNum = index/11
        colNum = index % 11
        mult = 1
        if abs(self.vel-self.v[rowNum])>0.1:
            mult = (self.vel+0.1)/self.v[rowNum]
        self.vel = mult*self.v[rowNum]
        #move
        self.setvel(mult*self.v[rowNum],mult*self.omega[colNum])                    
           



class iRobotCreate_real:

    def __init__(self, update_freq, port_number):
        """ constructor """
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
	
        if update_freq <= 0:
            raise InputError('Invalid Update Rate Argument: ', update_freq)

        #counters
        self.angle = 0
        self.distance = 0

        #constants
        self.__d = .3 #meters
        self.__w = 50 #deg/sec
        self.__v = .3 #meters/sec

        #attributes
        self.updateRate = update_freq
        self.robot_handler = None
        self.port = port_number

        #connect to the create
        self.robot_handler = self.auto_connect()

        self.sig_hand = signal.signal(signal.SIGINT, self.signal_handler)

        #start update rate timer
        self.tic = time.time()

    
    def auto_connect(self):
        #so far only compatible with windows, need to add code to handle linux port handling
##        try:
##            val = int(self.port)
##        except ValueError:
##            raise InputError('Port Argument is Invalid: ', self.port)
##        else:
##            port_name = "COM" + repr(val)

        #Allow create.py to determine if port_name is valid for either Linux or Windows
        return create.Create(self.port)

    # v should be in meters/second
    # omega should be in radians/second
    def setvel(self, v, omega):
        wheel = numpy.linalg.solve(numpy.array([[.5, .5],[1.0/(self.__d), -1.0/(self.__d)]]),numpy.array([v,omega]))
        wheel = numpy.int16(wheel * 1000)
        if -500 > wheel[0] or wheel[0] > 500 or -500 > wheel[1] or wheel[1] > 500:
            raise InputError('The speed of each wheel cannot exceed 0.5m/s (consider both v and omega)')
        else:
            t_elapsed = time.time()
            t_elapsed = t_elapsed - self.tic
            update_seconds = float(1) / self.updateRate
            sleep_time = update_seconds - t_elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
            self.tic = time.time()

            self.robot_handler.Go((v*100.0), omega*(180.0/math.pi))


    #v1 and v2 should be in meters/second
    def direct_drive(self, v1, v2):
        #wheel = numpy.linalg.solve(numpy.array([[.5, .5],[1.0/(self.__d), -1.0/(self.__d)]]),numpy.array([v,omega]))
        wheel1 = numpy.int16(v1 * 1000)
        wheel2 = numpy.int16(v2 * 1000)
        if -500 > wheel1 or wheel1 > 500 or -500 > wheel2 or wheel2 > 500:
            raise InputError('The speed of each wheel cannot exceed 0.5m/s (consider both v and omega)')
        else:
            t_elapsed = time.time()
            t_elapsed = t_elapsed - self.tic
            update_seconds = float(1) / self.updateRate
            sleep_time = update_seconds - t_elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
            self.tic = time.time()
            
            self.robot_handler.setWheelVelocities(wheel1/10.0, wheel2/10.0)

   
    def angle_sensor(self):
        #read create's angle sensor in degrees
        angle = self.robot_handler.getRawSensorDataAsList([20])

        #convert to integer
        return self.robot_handler._getTwoBytesSigned(angle[0],angle[1])
        #returns angle in degrees

    def distance_sensor(self):
        #read create's distance sensor 
        distance = self.robot_handler.getRawSensorDataAsList([19])

        #convert to integer
        return (self.robot_handler._getTwoBytesSigned(distance[0],distance[1])/1000.0)
	# returns in meters

    def isbumped(self):
        #read create's bumper sensors
        bumped = self.robot_handler.getRawSensorDataAsList([7])

        #if either bumper senors is set return true
        if create.bitOfByte(1, bumped[0]) or create.bitOfByte(0, bumped[0]):
            return True
        else:
            return False
        
    # angle_rad should be in radians
    def rotate(self, angle_rad):
        try:
            val = int(angle_rad)
        except ValueError:
            #self.delete()
            raise InputError('Angle Argument must be a Numeric Value: ', angle_rad)

        angle_deg = angle_rad * (180.0/math.pi)
        while angle_deg > 360:
            angle_deg = angle_deg - 360
        while angle_deg < -360:
            angle_deg = angle_deg + 360
            
        angle_total = 0
        self.angle_sensor()

        if angle_rad < 0:
            self.robot_handler.Go(0, -self.__w)
        else:
            self.robot_handler.Go(0, self.__w)

        while abs(angle_total) < abs(angle_deg):
			angle_total = angle_total + self.angle_sensor()
			# print abs(angle_total), abs(angle_deg)
			if self.isbumped():
				break;

        self.robot_handler.Stop()
        

    def resume_control(self):
        self.robot_handler.toSafeMode()
        #light up the LEDs


    # distance_m should be in meters
    def forward(self, distance_m):
        try:
            val = int(distance_m)
        except ValueError:
            #self.delete()
            raise InputError('Distance Argument must be a Numeric Value: ', distance_m)

        if abs(distance_m)>10:
            self.delete()
            raise InputError('Distance is too large: ', distance_m)
        else:

            if distance_m < 0:
                v = -self.__v * 100
            else:
                v = self.__v * 100

            distance_total = 0
            self.distance_sensor()
            
            self.robot_handler.Go(v, 0)

            while abs(distance_total) < abs(distance_m):
                distance_total = distance_total + self.distance_sensor()
                if self.isbumped():
                    break;

            self.robot_handler.Stop()
            

    def delete(self):
        if self.robot_handler:
            self.robot_handler.close()
            self.robot_handler = None
            

    def signal_handler(self, signal, frame):
        self.delete()
        print 'Gracefully Exiting! Create connection Terminated. \nOpen up a new connection to continue using the Create.\n'
        sys.exit(0)


    #Added by CLG
    #returns position in x, y, theta            
    def whereAmI(self):
        """returns current position"""
        coordinates = [self.x, self.y, self.theta]
        return coordinates

    #Added by CJG
    #returns difference between -pi and pi        
    def angleSub(self, startAng, endAng):
        #startAng and endAng must be in radians
        alpha = endAng - startAng
        if(alpha > np.pi):
            alpha -= (2 * np.pi)
        elif(alpha < -np.pi):
            alpha += (2 * np.pi)
        return alpha

    #Added by CJG and CLG
    #move to a point x, y, theta (rads)
    def moveTo(self, nx, ny, ntheta):
        """moves to a point"""
        dX = nx - self.x
        dY = ny - self.y
        #forces ntheta to equivalent angle between -pi and pi
        ntheta = ntheta % (2*np.pi)
        if ntheta > np.pi:
            ntheta -= 2*np.pi
        
        #finds the angle between current and new point
        alpha = math.atan2(dY, dX)
        #decides to rotate and move or stay in place
        if not math.fabs(dX) < .01 or not math.fabs(dY) < .01: 
            self.rotate(self.angleSub(self.theta, alpha))
            dist = np.sqrt(dX**2 + dY**2)
            self.forward(dist)
        else:
            alpha = self.theta
        
        #final rotation to new point
        self.rotate(self.angleSub(alpha, ntheta))
        self.x = nx
        self.y = ny
        self.theta = ntheta

    #Added by CLG
    def trajectory(self):     
        #create table of all end points from current point
        x = np.zeros(11)
        y = np.zeros(11)
        theta = np.zeros(11) 
        
        horizon = 2
        dt = 0.2
        num_steps = int(horizon/dt)
        
        for vdex in range(0, 6):
            for odex in range (0, 11):
                for index in range(1,num_steps+1):
                    x[index] = x[index-1] + self.v[vdex]*np.cos(theta[index-1])*dt
                    y[index] = y[index-1] + self.v[vdex]*np.sin(theta[index-1])*dt
                    theta[index] = theta[index-1] + self.omega[odex]*dt
                if vdex==5 and not odex ==5:
                    continue
                else:   
                    self.xcoord[vdex][odex] = x[10]
                    self.ycoord[vdex][odex] = y[10]
                        
    #Added by CJG
    #trajectory method must be called before use
    def goToGoal(self, xGoal, yGoal):    
        #should be a 6 x 11 matrix of distances between trajectory end points and goal points
        dist = ((self.xcoord - xGoal)**2 + (self.ycoord - yGoal)**2)**.5
        
        #finds the point at which minimum cost occurs
        #if cost is <.1, it does not move
        
        #realized there is strange logic after implementation
        #left in because this yielded best results from when we tried to fix it
        if(dist.flatten().argmin() < .1):
            self.vel=self.vel-0.1
            self.w = self.w*(self.vel/(self.vel-0.1))
            if abs(self.vel)<0.11:
                self.setvel(0,0)
            else:
                self.setvel(self.vel,self.w)
            return;
        
        index = dist.flatten().argmin()
        
        #find row and column of minimum value based off of flattened index
        rowNum = index/11
        colNum = index % 11
        mult = 1
        if abs(self.vel-self.v[rowNum])>0.1:
            mult = (self.vel+0.1)/self.v[rowNum]
        self.vel = mult*self.v[rowNum]
        #move
        self.setvel(mult*self.v[rowNum],mult*self.omega[colNum])                        
    
class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """

    def __init__(self, msg, expr = ''):
        self.expr = expr
        self.msg = msg

    def __str__(self):
        return self.msg + repr(self.expr)



class iRobotSim():
	''' Simulator class for iRobot create
	Creates a graphical representation of the robot and responds to the same
	commands as a real robot, emulating the behaviour of a robot.
	Methods:
	sim()
	set_noise()
	setvel()
	direct_drive()
	set_workspace()
	set_update_rate()
	forward()
	rotate()
	angle_sensor()
	distance_snsor()
	move_roomba()
	position()
	get_pose()
	set_robot_frame()
	set_world_frame()
	set_trail_size()'''

	def __init__(self,update_rate = 5):
			'''Initializing the simulator
			In this function, we initialize all the required
			constants and variables.'''
			# Simulation  update rate
			self.update_rate = update_rate
			# Default starting point of the robot
			self.origin = [0,0]
			# Roomba wheelbase
			self.wheelBase = 0.3
			# Sensor variables
			self.distance = 0
			self.angle = 0 
			self.totaldist = 0
			self.totalangle = 0
			# Location specifiers
			self.x_pose = []
			self.y_pose = []
			self.orientation = []
			# Velocity related variables
			self.v = 0.5
			self.omega = 0
			self.sigma_v = 0
			self.sigma_omega = 0
			# Workspace limits			
			self.x_axis_lim = [-10,10]
			self.y_axis_lim = [-10,10]
			# Simulation related variables
			self.Robot_frame = False
			self.trail = 10
			self.radius = 0.6
			self.time_elapsed=0
			self.sim_count = 0
			self.real_time = False
			
	def sim(self): 
		'''SIM draws and simulates the robot motion based on the commands
		This method needs to be called at the end of the complete program.
		'''
		# Initialize a figure
		fig = plt.figure()
		
		# Initialize and set the axis propeties
		ax = fig.add_subplot(111, aspect='equal',xlim=self.x_axis_lim, ylim=self.y_axis_lim)
		ax.xaxis.set_major_locator(MaxNLocator(20))
		ax.yaxis.set_major_locator(MaxNLocator(20))
		ax.grid()
		
		# Initialize the list of artists
		artist_list=[]
		
		# Initialize the list of x and y coordinates of the line
		xdata, ydata=[], []
		
		count = len(self.x_pose)
		# Generating the list of artists to be drawn
		for i in range(0,count):
			# Get the position and orientation of the robot
			# for each frame of the animation
			x, y, angle = self.position(i)
			
			# Sets the list of x and y coordinates of the line
			# while keeping in account the trail_size
			xdata.append(x)
			ydata.append(y)
			
			trail = int(self.trail*self.update_rate)
			
			if len(xdata) > trail :
				while len(xdata) != trail:
					xdata.pop(0)					
			
			if len(ydata) > trail:
				while len(ydata) != trail:
					ydata.pop(0)
					
			# Trail line 
			trail_line = ax.add_line(Line2D.Line2D(xdata,ydata, c= 'black', lw =3,marker = '.', zorder = 1))
			
			# coordinates for the arrow
			x_const = -0.8 * self.radius
			y_const = self.radius/2
			arrow_p1  = [ (cos(angle) * x_const - sin(angle) * y_const) +x , (sin(angle) * x_const + cos(angle) * y_const)+y]
			arrow_p2  = [ (cos(angle) * x_const + sin(angle) * y_const) +x, (sin(angle) * x_const - cos(angle) * y_const)+y]
			arrow_p3  = [ cos(angle) * self.radius +x, sin(angle) * self.radius +y]
			
			# Artists needed to draw the robot
			arrow_body = ax.add_patch(patches.Polygon( [ arrow_p1 , arrow_p2, arrow_p3] , fc = 'brown', zorder = 3)) 
			
			circle_body = ax.add_patch(plt.Circle([x,y], radius=self.radius,fc = 'yellow', zorder = 2))
			
			
			# Appending the artists to the list
			artist_list.append([ trail_line,circle_body,arrow_body])
		
		# animation 
		s = time.time()
		def robot_frame_plot(count):
			# get the position and orientation of the robot
			try:
				if count > self.sim_count:
					
					ax.set_title(int(time.time() - s))
						
					# t=time.time()
					x, y, angle = self.position(self.sim_count)
					ax.set_xlim(x+self.x_axis_lim[0],x+self.x_axis_lim[1])
					ax.set_ylim(y+self.y_axis_lim[0],y+self.y_axis_lim[1])
					
						# print( time.time() -t)
					# else:
						# time.sleep(0.12 - 2* self.v)
					self.sim_count +=1
					
			except WindowsError:
				pass
				
			
		if self.Robot_frame:
			if self.real_time:
				timer = fig.canvas.new_timer(interval =int(1000 *(1./self.update_rate- self.time_elapsed)))
			else:
				timer = fig.canvas.new_timer(interval =int(100))
			timer.add_callback(robot_frame_plot,count)
			timer.start()	
			
		if self.real_time:
			ani = animation.ArtistAnimation(fig, artist_list, interval= 1000*(1./self.update_rate - self.time_elapsed), repeat = False)
		else:
			ani = animation.ArtistAnimation(fig, artist_list, interval= 100, repeat = False)
		# displaying the plot
		
		plt.show()	
	
	def set_noise(self,v = 0.0152, omega = 0.5098):
		'''SET_NOISE Sets the amount of noise in the simulation
        Can take two arguments, noise on linear velocity
        and noise on angular velocity. The default values for this
        function should be (0.0152, .5098)'''
		self.sigma_v = v
		self.sigma_omega = omega
			
	def setvel(self,v,omega):
		'''SETVEL Sets the velocity of the simulation Roomba. 
           Takes two arguments, linear and angular velocity.
           The speeds cannot exceed 0.5 m/s.'''
		
		# Start the timer
		start_time = time.time()
		
		# Calculate and check if the velocities are in the valid range 
		# If not, set v=0.5 m/s and omega = 0 rad/s
		wheel = np.linalg.solve(np.array([[.5, .5],[1/self.wheelBase, -1/self.wheelBase]]),np.array([v,omega]) * 1000)
		
		if -500 > wheel[0] or wheel[0] > 500 or -500 > wheel[1] or wheel[1] > 500:
			#print("ERROR: The speed of each wheel cannot exceed 0.5m/s (consider both v and omega).'\n'")
			self.v = 0.5
			self.omega = 0

		# If velocities are in valid range 		
		else:
			self.v = v + (self.sigma_v * v * np.random.randn())
			self.omega = omega + (self.sigma_omega * omega * np.random.randn())
		
		# Calculating the angular and linear displacements
		dtheta = self.omega/self.update_rate
		
		dx = self.v/self.update_rate
		xdisp = dx*cos(self.totalangle + dtheta/2)
		ydisp = dx*sin(self.totalangle + dtheta/2)
		
		# Updating the displacement lists
		(x_or,y_or) = self.origin
		x_or = x_or + xdisp
		y_or = y_or + ydisp
		
		# Updating the location coordinates
		self.x_pose.append(x_or)
		self.y_pose.append(y_or)
		self.orientation.append(self.totalangle + dtheta)
		
		# Updating the current location of the robot
		self.origin = [x_or,y_or]
		
		# Updating the distance and angular sensor readings 
		self.distance = self.distance + (xdisp**2 + ydisp**2)**0.5
		self.totaldist = (xdisp**2 + ydisp**2)**0.5 + self.totaldist
		
		self.totalangle = self.totalangle + dtheta
		self.angle = self.angle + dtheta
		
		# Recording the execution time for calculating the position of the robot
		end_time = time.time()
		self.time_elapsed = end_time-start_time
	
	def direct_drive (self,v1,v2):
		'''DIRECTDRIVE Sets the differential velocity of the Roomba.
           Takes two arguments, one for each wheel. This translates
           the velocities to a linear and angular velocity.
           Convert the velocity of each wheel into a linear and angular velocity'''
		
		# Calculating the linear velocity
		v = (v1 + v2)/2
		
		# Calculating the angular velocity
		omega = (v1 - v2)/self.wheelBase
		
		# Calculate and check if the velocities are in the valid range 
		# If not, set v=0.5 m/s and omega = 0 rad/s, else set the calculated linear and angular velociies
		wheel = np.linalg.solve(np.array([[.5, .5],[1/self.wheelBase, -1/self.wheelBase]]),np.array([v,omega]) * 1000)
		
		if -500 > wheel[0] or wheel[0] > 500 or -500 > wheel[1] or wheel[1] > 500:
			print("ERROR: The speed of each wheel cannot exceed 0.5m/s (consider both v and omega).'\n'")
			self.setvel(0.5,0)
		else:
			self.setvel(v,omega)
		
		
	def set_workspace(self,x_min,x_max,y_min,y_max):
		'''SET_WORKSPACE Takes in the bounds of the workspace
           This will change the bounds of the workspace. This must be 
           inputted in the form ([XMin XMax YMin YMax])
           If nothing is inputted, it will default to the original 
           workspace ([-10,10,-10,10])'''
		self.x_axis_lim = [x_min,x_max]
		self.y_axis_lim = [y_min,y_max]
		
	def set_update_rate(self, update_rate):
		'''SET_UPDATE_RATE Sets the update rate.
        This function sets the update rate. Initially, the update
        rate defaults to 5 Hz, if not defined within the
        constructor.
        The update rate must be set between 1 and 20'''
		
		# Check if the given updte rate is within the range
		# If not set it to default i.e., 5
		if update_rate >=1 and update_rate<=20:
			self.update_rate = update_rate
		else:
			print("Error: Update Rate should lie between 1 and 20."\
			+ "Setting update rate to default value of 5")
			self.update_rate = 5
		
		
	def forward(self,dist):
		'''FORWARD Makes the robot move forward.
        Takes one argument, the distance to move forward. 
		A positive distance means it is moving forward.
		A negative distance indicates movement backwards.
		Blocks until finished, uses the setvel method'''
		
		d=0
		init_distance = self.totaldist
		# Runs the setvel command at 0.5 m/s until it has gone the correct distance
		if dist > 0 :
			while dist - 0.01  > d:
				self.setvel(0.5,0)
				d = self.totaldist - init_distance 
		else:
			while dist - 0.01 < d:
				self.setvel(-0.5,0)
				d = self.totaldist - init_distance
		
	
							
	def rotate(self,theta):
		'''ROTATE Rotate the robot.
		Takes one argument, the angle to turn in radians.
		A positive angle means anticlockwise rotation
		A negative angle means clockwise rotation. 
		The angle should be in the range of -pi to pi, if it is not, it will be translated to
		this range. 
		Blocks until finished, uses the setvel method.
		'''
		current_angle = 0
		init_angle = self.totalangle
		theta = theta
		
		# Convert the angle to lie within the range -pi and pi.
		if np.pi < theta:
			theta = theta - 2 * np.pi
		if theta < -np.pi:
			theta = theta + 2 * np.pi
		
		# If the angle is positive, direction of rotation is counter clockwise
		if theta > 0:
			while theta > current_angle:
				self.setvel(0,np.pi/8)
				current_angle = self.totalangle - init_angle
				
		# If the angle is negative, direction of rotation is clockwise
		else :
			while theta < current_angle:
				self.setvel(0,-np.pi/8)
				current_angle = self.totalangle - init_angle
				
	def move_roomba ( self,x,y,theta):
		'''
		MOVEROOMBA Moves the graphical Roomba from the current spot to
        the specified position.
		Takes 3 arguments: x- coordinate, y- coordinate and the orientation
		'''
		self.x_pose.append(x)
		self.y_pose.append(y)
		self.orientation.append(math.radians(theta))
	

	
	def angle_sensor(self):
		'''
		ANGLESENSOR Returns the angle the Roomba has rotated since the
        the last time the function was called.
		'''
		a = self.angle
		self.angle = 0
		return a
	
	def distance_sensor(self):
		'''
		DISTANCESENSOR Returns the distance the Roomba has moved since
        the last time the function was called.
		'''
		d = self.distance
		self.distance = 0
		return d
		
			
	def position(self,i):	
		''' POSITION Returns the i th index position of the robot
		'''
		return self.x_pose[i],self.y_pose[i],self.orientation[i]
			
				
	
	def get_pose(self):
		'''
		GETPOSE Returns the robot's position and orientation.		
		'''
		# Get the last position index 
		count = len(self.x_pose)
		# Return the position coordinates 
		return round(self.x_pose[count-1],2),round(self.y_pose[count-1],2),round(np.degrees(self.orientation[count-1]),2)

	def set_robot_frame(self):
		'''SET_ROBOT_FRAME Changes frame to the robot frame.
		This will be robot - centered simulation.
		The default frame is the world frame.
		'''
		self.Robot_frame = True
	
	
	def set_world_frame(self):
		'''SET_WORLD_FRAME Changes frame to world frame.
		This will change the axis to what the user has defined
        The default frame is the world frame.'''
		self.Robot_frame = False
		
	def set_trail_size(self,trail_size):
		'''TRAILSIZE Changes the trail length to the inputted number.
        Takes 1 argument, the new trail length. The trail length
        defaults to 10. However, this function can change that. If
        the user inputs inf as the trail length, the trail length
        will be infinite.'''
		if trail_size == 'inf':
			set_trail = np.inf
		else:
			self.trail=trail_size
	
	def set_real_time(self):
		self.real_time = True
