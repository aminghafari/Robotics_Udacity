import numpy as np


# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!
    print(Rover.mode)
    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        if Rover.total_time - Rover.time_passed> 10:
            Rover.time_passed = Rover.total_time
            Rover.pos2 = Rover.pos
            diffpos = np.array(Rover.pos2) - np.array(Rover.pos1)
            if np.sqrt(np.sum(pos**2 for pos in diffpos))<0.3 and Rover.throttle_set>0:
                Rover.mode = 'stuck'
                Rover.pos_stuck = Rover.pos
                Rover.yaw_stuck = Rover.yaw
            Rover.pos1 = Rover.pos2
                       
        
        if Rover.samples_collected == 6 and Rover.mode != 'stuck' and Rover.mode != 'stop_home':
            Rover.mode = 'home'
        
        if Rover.mode == 'home':
            dest = np.array([99, 85])
            dirct = dest - np.array(Rover.pos)
            if np.sqrt(np.sum(pos**2 for pos in dirct))>2:
                angle = np.angle(dirct[0]+1j*dirct[1], deg=True)
                if np.abs(angle-Rover.yaw)>10 and Rover.total_time - Rover.time_home>5:
                    Rover.throttle = 0
                    Rover.brake = 0
                    Rover.steer = -15
                    Rover.time_home = Rover.total_time
                else :
                    if len(Rover.nav_angles) >= Rover.stop_forward:  
                        if Rover.vel < Rover.max_vel:
                            # Set throttle value to throttle setting
                            Rover.throttle = Rover.throttle_set
                        else: # Else coast
                            Rover.throttle = 0
                        Rover.brake = 0
                        # Set steering to average angle clipped to the range +/- 15
                        Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                
                    # If there's a lack of navigable terrain pixels then go to 'stop' mode
                    else:#elif len(Rover.nav_angles) < Rover.stop_forward:
                            # Set mode to "stop" and hit the brakes!
                            Rover.throttle = 0
                            # Set brake to stored brake value
                            Rover.brake = Rover.brake_set
                            Rover.steer = 0
                            Rover.mode = 'stop_home'
            else:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
                print('Done!!!')
        
        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop_home':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15
                # If we're stopped but see sufficient navigable terrain in front then go!
                else: #if len(Rover.nav_angles) >= Rover.go_forward :
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'home'
                    
                    
        elif Rover.mode == 'forward': 
            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward and np.mean(Rover.nav_dists)> 10 \
             and np.abs(np.mean(Rover.nav_angles*180/np.pi))<35:  
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                #Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                Rover.steer = np.percentile(Rover.nav_angles * 180/np.pi, 70)
                
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            else:#elif len(Rover.nav_angles) < Rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'
                    
            ## if there is a rock    
            if Rover.rock_angles.any() and Rover.mode == 'forward':
                if np.min(Rover.rock_dists)<40 and np.mean(Rover.rock_angles)>-5:
                    Rover.throttle = 0
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'aiming'
        
        
        elif Rover.mode == 'aiming':
            if Rover.vel > 1:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 1:
                if Rover.rock_angles.any():
                    Rover.rock_dir = np.mean(Rover.rock_angles* 180/np.pi)
                    if(np.abs(np.mean(Rover.rock_angles* 180/np.pi))<20):
                        Rover.brake = 0
                        Rover.steer = 0
                        Rover.mode = 'approaching'
                    else:
                        Rover.brake = 0
                        Rover.steer = 15*np.sign(Rover.rock_dir)
                else:
                    Rover.brake = 0
                    Rover.steer = 15*Rover.rock_dir
                    
                    
        elif Rover.mode == 'approaching':
            if Rover.rock_angles.any():
                if(np.abs(np.mean(Rover.rock_angles* 180/np.pi))>30):
                    Rover.mode = 'aiming'
                else:
                    if not Rover.near_sample:
                        Rover.throttle = Rover.throttle_set
                        Rover.brake = 0
                        Rover.steer = 0
                    else:
                        Rover.throttle = 0
                        Rover.brake = Rover.brake_set
                        Rover.send_pickup = True
                        Rover.mode = 'stop'
            elif  Rover.picking_up:
                Rover.mode = 'stop'
            else:
                Rover.mode = 'aiming'
                    
        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward or np.mean(Rover.nav_dists) < 15\
            or np.abs(np.mean(Rover.nav_angles*180/np.pi))>30 :
                #np.mean(Rover.nav_dists[Rover.nav_angles* 180/np.pi>10]) < 25 
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15
                # If we're stopped but see sufficient navigable terrain in front then go!
                else: #if len(Rover.nav_angles) >= Rover.go_forward :
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'
                
                
        elif Rover.mode == 'stuck':
            if np.abs(Rover.yaw_stuck-Rover.yaw)<15:
                Rover.throttle = 0
                Rover.brake = 0
                Rover.steer = -15
            else:
                Rover.mode = 'stop'
                Rover.time_passed = Rover.total_time
                Rover.pos1 = Rover.pos
    # Just to make the rover do something 
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0
        
    # If in a state where want to pickup a rock send pickup command
   # if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
   #     Rover.send_pickup = True
    
    return Rover

