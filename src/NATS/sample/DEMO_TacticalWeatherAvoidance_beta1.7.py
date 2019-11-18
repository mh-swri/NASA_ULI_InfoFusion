# NATS sample
#
# Optimal Synthesis Inc.
#
# Oliver Chen
# 10.02.2019
#
# Demo of Tactical Weather Avoidance during simulation
#
# 1. The program will run two simulation(without and with tactical weather avoidance) and output a result trajectory file, respectively.
# 2. Finally, you can see the difference of the two trajectories in plotting.

from NATS_Python_Header import *

#NATS_DIR = "PLEASE_SPECIFY_PATH"
NATS_DIR = "."

clsNATSStandalone = JClass('NATSStandalone')
# Start NATS Standalone environment
natsStandalone = clsNATSStandalone.start()

if (natsStandalone is None) :
    print "Can't start NATS Standalone"
    quit()

simulationInterface = natsStandalone.getSimulationInterface()

entityInterface = natsStandalone.getEntityInterface()
controllerInterface = entityInterface.getControllerInterface()
pilotInterface = entityInterface.getPilotInterface()

environmentInterface = natsStandalone.getEnvironmentInterface()
weatherInterface = environmentInterface.getWeatherInterface()

equipmentInterface = natsStandalone.getEquipmentInterface()
aircraftInterface = equipmentInterface.getAircraftInterface()

planned_dirname = ""
output_filename_before = ""
output_filename_after = ""

if not (os.path.isdir(NATS_DIR)) :
    print "Directory NATS_DIR does not exist"
else :
    if simulationInterface is None:
        print "Can't get SimulationInterface"

    else:
        simulationInterface.clear_trajectory()
        environmentInterface.load_rap("share/tg/rap")

        print ""
        print "************************************************"
        print "First simulation: No tactical weather avoidance"
        print "************************************************"
        print ""

        aircraftInterface.load_aircraft("share/tg/trx/TRX_DEMO_SFO_PHX_GateToGate.trx", "share/tg/trx/TRX_DEMO_SFO_PHX_mfl.trx")

        simulationInterface.setupSimulation(11000, 30) # SFO - PHX
    
        simulationInterface.start()

        while True:
            runtime_sim_status = simulationInterface.get_runtime_sim_status()
            if (runtime_sim_status == NATS_SIMULATION_STATUS_ENDED) :
                break
            else:
                time.sleep(1)

                millis = int(round(time.time() * 1000))
                print "Outputting trajectory data.  Please wait...."
    
        planned_dirname = os.path.splitext(os.path.basename(__file__))[0] + "_" + str(millis)
        output_filename_before = planned_dirname + ".csv"

        # Output the trajectory result file
        simulationInterface.write_trajectories(output_filename_before)

        aircraftInterface.release_aircraft()

        # =========================================================
    
        print ""
        print "*****************************************************"
        print "Second simulation: Enable tactical weather avoidance"
        print "*****************************************************"
        print ""

        simulationInterface.clear_trajectory()

        aircraftInterface.load_aircraft("share/tg/trx/TRX_DEMO_SFO_PHX_GateToGate.trx", "share/tg/trx/TRX_DEMO_SFO_PHX_mfl.trx")

        simulationInterface.setupSimulation(11000, 30) # SFO - PHX
    
        simulationInterface.start(3060)

        while True:
            runtime_sim_status = simulationInterface.get_runtime_sim_status()
            if (runtime_sim_status == NATS_SIMULATION_STATUS_PAUSE) :
                break
            else:
                time.sleep(1)
    
        # Set tactical weather avoidance
        controllerInterface.setTacticalWeatherAvoidance("LOSHN", 100.0)
        controllerInterface.setTacticalWeatherAvoidance("TOTIE", 200.0)
    
        simulationInterface.resume()
    
        while True:
            runtime_sim_status = simulationInterface.get_runtime_sim_status()
            if (runtime_sim_status == NATS_SIMULATION_STATUS_ENDED) :
                break
            else:
                time.sleep(1)

        millis = int(round(time.time() * 1000))
        print "Outputting trajectory data.  Please wait...."
    
        planned_dirname = os.path.splitext(os.path.basename(__file__))[0] + "_" + str(millis)
        output_filename_after = planned_dirname + ".csv"
    
        # Output the trajectory result file
        simulationInterface.write_trajectories(output_filename_after)


        aircraftInterface.release_aircraft()
        environmentInterface.release_rap()


# Stop NATS Standalone environment
natsStandalone.stop()

# =========================================================

# The following statements read the result trajectory files and display plotting.

# Create temp directory and copy the result trajectory file into it
planned_dirname = "tmp_" + planned_dirname
os.makedirs(NATS_DIR + "/" + planned_dirname)
copyfile(NATS_DIR + "/" + output_filename_before, NATS_DIR + "/" + planned_dirname + "/" + output_filename_before)
copyfile(NATS_DIR + "/" + output_filename_after, NATS_DIR + "/" + planned_dirname + "/" + output_filename_after)

post_process = pp.PostProcessor(file_path = NATS_DIR + "/" + planned_dirname,
                                ac_name = 'SWA1897');
post_process.plotSingleAircraftTrajectory();

# Delete temp directory
print "Deleting directory:", planned_dirname
rmtree(NATS_DIR + "/" + planned_dirname) 

shutdownJVM()
