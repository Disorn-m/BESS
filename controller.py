import os
import pandas as pd
import numpy as np
import datetime
import os
from bus import Bus
from bess import bess
from optimiser import optimiser

gen_profile_name = "gen_profile.csv"
output_filename = "optimisation_output.csv"
class controller:

    # controller receives inputs from the view


    ###################################################################################################
    # temporary replacement of the view - this should be the connector between the GUI and the view
    ###################################################################################################

    def __init__(self, filename, path):             #gets all the data from setting.csv and gen_profile.csv
        def read_setup(filename, path):
            os.chdir(path)
            print(os.getcwd())
            setting = pd.read_csv(filename)
            df_setting = pd.DataFrame(setting)
            print(df_setting)
            return df_setting

        # setting global parameters from setting#
        self.df_setting = read_setup(
            filename, path
        )  # can be replaced to other function getting data from the view

        ## simulation setting##
        self.name = str(self.df_setting['value'][0])
        self.time_step = float(self.df_setting['value'][1])
        self.temp = 0 ###################################
        # print(self.time_step)
        # timestep generation
        if self.time_step == float(1):
            self.timestamp = '5T'
            # print(self.timestamp)
        elif self.time_step < float(1):
            self.x = round(self.time_step * 60)
            self.timestamp = str(self.x) + "min"
            # print(self.timestamp)
        else:
            print("more than hourly resolution! - not support")

        self.start_timestep = pd.to_datetime(self.df_setting['value'][35])
        self.end_timestep = pd.to_datetime(self.df_setting['value'][36])

        # other simulation parameters
        self.location = str(self.df_setting['value'][2])
        self.base_year = float(self.df_setting['value'][3])
        self.plant_type = str(self.df_setting['value'][4])
        self.opt_target_energy = str(self.df_setting['value'][5])
        self.target_increase_energy = float(
            self.df_setting['value'][6].strip("%")) / 100
        self.opt_target_LCOE = str(self.df_setting['value'][7])
        self.target_LCOE = float(
            self.df_setting['value'][8])  # LCOE optimisaiton to be implemented
        self.gen_profile_loc = path
        self.gen_profile = gen_profile_name

        ## solar PV plant setting##
        self.annual_degradation_sol = float(
            self.df_setting['value'][9].strip('%')) / 100
        self.extra_loss_sol = float(
            self.df_setting['value'][10].strip('%')) / 100
        self.unavailability_sol = float(
            self.df_setting['value'][11].strip('%')) / 100

        ##############################################################################################
        ## possible optimise with solar PV and wind sizing (not implemented)##
        self.changable_sol = str(self.df_setting['value'][17])
        self.dc_cap_sol_upper = float(self.df_setting['value'][15])
        self.dc_cap_sol_lower = float(
            self.df_setting['value']
            [16])  # this should be initial cap for Sol profile
        self.ac_cap_sol_upper = float(self.df_setting['value'][33])
        self.ac_cap_sol_lower = float(self.df_setting['value'][34])

        ## wind plant setting##
        #########################################################################

        ## grid setting and operation scheme##
        # Golf: we might have to relook at this when implementing wind
        self.MEC = float(
            self.df_setting['value'][12])  # Maximum Export Capacity
        self.evening_dc = float(self.df_setting['value'][13])
        self.start_ops = float(self.df_setting['value'][14])

        ## battery operation##  #### Explain input parameters
        self.ini_bess_cap_kWh = float(self.df_setting['value'][21])
        self.ini_bess_power_kW = float(self.df_setting['value'][22])
        self.ini_SoC = float(self.df_setting['value'][23].strip('%')) / 100
        self.SoC_upper_lim = float(
            self.df_setting['value'][24].strip('%')) / 100
        self.SoC_lower_lim = float(
            self.df_setting['value'][25].strip('%')) / 100
        self.ini_c_eff = float(self.df_setting['value'][26].strip('%')) 
        self.ini_dc_eff = float(self.df_setting['value'][27].strip('%')) 
        self.bess_lifetime = float(self.df_setting['value'][28])
        self.ini_cap_deg = float(self.df_setting['value'][29].strip('%')) / 100
        self.ini_rt_eff_deg = float(
            self.df_setting['value'][30].strip('%')) / 100
        self.min_SoC = float(self.df_setting['value'][31].strip(
            '%')) / 100  # minimum SoC to discharge energy in the evening
        self.rr_control_kw = float(self.df_setting['value'][32])
        self.power_increment = 0.001
        self.capacity_increment = 0.001
        print(self.power_increment)
        print(self.capacity_increment)

        ##############################################
        #### setting to be included in setting file####
        ##############################################
        self.print_output = 'Y'
        self.create_logger = 'Y'
        self.opt_energy_thres = 0.1 / \
            100  # how much higher than target %gain allowed default 0.1%
        self.consider_ratio_bess = 'Y'
        # manufacturing limit on the bess power vs capacity default 0.5 (capacity = 2*power)
        self.c_rate_lower_lim = 0.5
        # manufacturing limit on the bess power vs capacity default 0.5 (capacity = 2*power)
        self.c_rate_upper_lim = 5
        # increment for C-rate at each optimasimation iteration (fixed C-rate)
        self.c_rate_step = 0.5
        # adjusting the cap by +/- percentage of input value
        self.very_coarse_adj = 25 / 100
        self.coarse_adj = 10 / 100  # adjusting the cap by +/- percentage of input value
        self.fine_adj = 1 / 100  # adjusting the cap by +/- percentage of input value
        self.very_fine_adj = 0.1 / 100  # adjusting the cap by +/- percentage of input value
        self.adjust_cap_first = "Y"  # if this is yes then "adjust_power_first" will be "N"
        self.very_coarse_sensitivity = 20  # times of optimisation treshold
        self.coarse_sensitivity = 10
        self.fine_sensitivity = 2.5
        self.very_fine_sensitivity = 1
        ##############################################
        # initialising logger for output record - logger to be implemented
        # if  (create_logger == 'Y'):
        #self.log = logger (self)

        # initialising key output record
        if (self.print_output == 'Y'):
            self.cap_record = []
            self.power_record = []
            self.power_gain_record = []
            self.c_rate_record = []
            self.opt_record = []
        # to be further adding the setting as we include more and more application

        # initialising c-rate iteration
        self.round = 0

    ############################################################################
    ############################################################################

    ########################## controller process################################
    ### The main fuction of the controller is per the following###
    # 1.sim_start => initialising the bus object and perform first simulation
    # 2.ini_opt => initialising optimiser and record the result from first simulation
    # 3.set_sim => set the simulation parameter for the next simulation
    # 4.start_opt_same_c_rate => calling above function to find "optimal" capacity and power for a fixed c-rate
    # 5.start_opt_varia_c_rate => iterate through "start_opt_same_c_rate" to find "optimal" capacity and power for a fixed c-rate

    def gen_timestep(self):
        self.start = pd.to_datetime(self.start_timestep)
        self.end = pd.to_datetime(self.end_timestep)
        self.timestep_sim = pd.date_range(start=self.start,
                                          end=self.end,
                                          freq=self.timestamp)
        return self.timestep_sim

    def sim_start(   
        self
    ):  ##### 3. command the bus to calculate all timesteps and sending output to optimiser
        # initialising relevant bus and optimiser at first timestep and taking result from first time step

        self.iteration = 0
        self.working_bess_cap_kWh = self.ini_bess_cap_kWh + self.capacity_increment
        self.temp2=0
        self.timestep_sim = self.gen_timestep()

        self.i = 0
        self.main = Bus(self)  # creating bus
        # self.bess = bess(self.main)
        self.total_grid_output = self.main.grid_output()  #### 4. calculation of 1st timestamp grid output, see bus.py
        self.total_grid_output_wo_BESS = self.main.grid_output_wo_BESS()   #### 5. calculation of grid output without batt, see bus.py
        self.total_grid_output_wo_limit = self.main.grid_output_wo_limit() #### 6. calculation of grid output without limit, see bus.py
        
        self.total_Battery_output = self.main.get_batt() #### 7. calculates total battery output, see bus.py
        self.total_e_input = self.main.e_input  #### 8. calculation of 1st timestamp e-input, see bus.py

        df2 = pd.DataFrame(columns=['time','e_input','net output','total output']) 
        self.i += 1

        while self.i < len(self.timestep_sim):
            #### iterate through all the timestep and record the energy to grid at each timestep and energy input (to calculate gain)
            
            df2 = df2.append(dict(zip(df2.columns,[self.timestep_sim[self.i],self.main.e_input, self.main.grid_output(), self.total_grid_output])), ignore_index=True)
            
            self.main.set_bus(self, self.timestep_sim[self.i])
            self.total_grid_output += self.main.grid_output()
            self.total_grid_output_wo_BESS += self.main.grid_output_wo_BESS()
            self.total_Battery_output += self.main.get_batt()
            self.total_grid_output_wo_limit += self.main.grid_output_wo_limit()
            self.total_e_input += self.main.e_input


            print('################',self.i,'#############################')
           
            print("########### IF #################")
            if self.main.get_batt() < 0:
                print("Battery: ",  self.main.get_batt())  
                print("C eff: ", self.main.bat.c_eff)
                print("ini cap deg: ", self.ini_cap_deg)
                self.working_bess_cap_kWh = self.working_bess_cap_kWh + ((self.main.get_batt() * self.main.bat.c_eff * 
                                                                        self.time_step) * self.ini_cap_deg)
                self.temp = ((self.main.get_batt() * self.main.bat.c_eff * 
                                                                        self.time_step) * self.ini_cap_deg)
                self.temp2 = self.main.get_batt() * self.main.bat.c_eff * self.time_step
                print('temp2: ',self.temp2)
                print('working cap: ', self.working_bess_cap_kWh)
            print('time step: ', self.time_step)
            print('temp: ', self.temp)
            print('##################IF END##############')
                
            

           
            print("net output is",  self.main.grid_output())
            print("Total grid",  self.total_grid_output) 
            # print("grid wo BESS",  self.main.grid_output_wo_BESS()) 
            # print("Total grid wo BESS",  self.total_grid_output_wo_BESS)
            # print("grid wo limit",  self.main.grid_output_wo_limit()) 
            # print("Total grid wo limit",  self.total_grid_output_wo_limit) # problem
            print("e_input",  self.main.e_input)
            # print("Total e_input",  self.total_e_input)
            print("Battery",  self.main.get_batt())  
            print("Total Battery",  self.total_Battery_output) 
            # print("c_rate: ",self.bess.c_rate)
            # print("dc_power: ",self.bess.dc_power)

            print("########## BATTERY #################")
            print('permitted charge: ',self.main.bat.permitted_charge)
            print('charge req: ',self.main.bat.charge_req)
            print('ramp req: ', self.main.bat.ramp_rate(self.main))
            print('pre soc: ', self.main.bat.pre_SoC)
            print('pre grid: ', self.main.bat.pre_grid)
            print('pre eff cap: ', self.main.bat.pre_eff_cap)
            print('eff cap: ', self.main.bat.eff_cap)
            # print('c_power: ', self.main.bat.c_power)
            print('evening dc: ', self.main.bat.evening_dc(self.main))
            # print('new_SoC_kwh: ',self.bess.SoC)
            # if self.main.grid_output_wo_limit() < self.main.e_input:
            #     print("########### GRID OUTPUT WITHOUT LIMIT IS NOT EQUAL TO E INPUT###############")
            print("###########################################################")
            
            ## batt_out variables such as permitted charge are printed in the bus file.
            # print("net output is", self.main.grid_output())
            # print("Batt", bess.bat_outcome())
            # might need to add more parameters as we include more optimisation
            self.i += 1

        df2.to_csv('new_output.csv')
        self.sim_status = 'DONE'

        print("simulation status: " + self.sim_status +
              "\ntotal timestep ran: " + str(self.i))
        print("total grid output without BESS: " +
              str(self.total_grid_output_wo_BESS))
        print("total grid output: " + str(self.total_grid_output) +
              "\ntotal_e_input: " + str(self.total_e_input))
        print("total battery output: " + str(self.total_Battery_output))
        print("current gain = " +
              str(abs((self.total_grid_output / self.total_e_input) - 1)))

    def ini_opt(self):
        self.optimizer = optimiser(self)
        self.key_result = pd.DataFrame()

    ### communication with optimiser, getting increment and adjust initial sizing to later battery creation ###
    def new_bess_sizing(self):
        self.increment = self.optimizer.get_increment(self)
        self.power_increment = self.increment[
            0]  # global parameter will be used in BESS object
        self.capacity_increment = self.increment[
            1]  # global parameter will be used in BESS object
        print("got increment")

        self.working_bess_cap_kWh = self.ini_bess_cap_kWh + self.capacity_increment
        self.working_bess_power_kW = self.ini_bess_power_kW + self.power_increment

    ### c-rate change - renew optimiser and adjust the simulation ###
    def get_c_rate(self):
        if self.round == 0:  # first simulation c-rate equals to lower limit
            self.c_rate = self.c_rate_lower_lim
        if self.c_rate > self.c_rate_lower_lim and self.c_rate < self.c_rate_upper_lim:
            self.c_rate = self.c_rate_lower_lim + (self.round -
                                                   1) * self.c_rate_increment
        return self.c_rate

    ### shell function to start the optimisation: first simulation, re-adjust, second simulation til the end of the first c-rate ###
    def start_opt_same_c_rate(self):

        self.iteration = 0
        print("iteration no." + str(self.iteration))
        self.sim_start()  # run 8761 files
        self.ini_opt()  # initializing optimiser
        # self.new_bess_sizing() #calculate new BESS sizing
        self.c_rate = self.get_c_rate()  # get c-rate value
        while self.power_increment != 0 and self.capacity_increment != 0:
            self.sim_start()
            self.ini_opt()
            self.new_bess_sizing()
            self.iteration += 1
            print("iteration no." + str(self.iteration))
        self.opt_power = self.working_bess_power_kW
        self.opt_cap = self.working_bess_cap_kWh
        print("optimal capacity at c-rate " + str(self.c_rate) + " is " +
              str(self.opt_cap))
        print("optimal power at c-rate " + str(self.c_rate) + " is " +
              str(self.opt_power))
        self.record_output()

    def start_opt_varia_c_rate(self):
        self.round = 0
        self.c_rate_increment = self.c_rate_upper_lim / self.c_rate_step
        while self.round < self.c_rate_step:
            self.c_rate(self.round)    
            self.start_opt_same_c_rate()
            self.round += 1
        self.report_export()

    ### log the  BESS cap, power final energy gain at a C-rate per sheet ###
    def record_output(self):
        self.opt_record.append(self.iteration)
        self.cap_record.append(self.opt_cap)
        self.power_record.append(self.opt_power)
        self.power_gain_record.append(1 - (self.total_grid_output /
                                           self.total_e_input))
        self.c_rate_record.append(self.c_rate)

    ############################## TEMPORARY REPLACEMENT OF THE VIEW########################
    # export the above input to CSV file
    def record_export(self):
        self.key_result.assign(sim_no=self.opt_record)
        self.key_result.assign(capacity=self.cap_record)
        self.key_result.assign(power=self.power_record)
        self.key_result.assign(power_gain=self.power_gain_record)
        self.key_result.assign(c_rate=self.c_rate_record)
        self.writer = pd.ExcelWriter(self.output_filename)
        self.key_result.to_excel(self.writer, 'Sheet1')   
        self.writer.save()