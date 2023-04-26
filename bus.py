# imports
import pandas as pd
import numpy as np
from pandas import DataFrame as df
import datetime
from datetime import datetime
import os
from datetime import timedelta
from generators import Solar
from bess import bess


# Bus class oversee BESS and Generator classes by CT and VD
class Bus:



    # The operation of this bus is the excess energy from solar is stored in the BESS
    # The bus will also request ramp rate control according to the allowable ramp rate control
    # The bus will also request the BESS to discharge the energy at the evening (if SoC is above the set criteria)

    # def bess_action(
    #    self
    # ):  # action flag to be passed on to BESS object through the controller
    #    if (self.hour < self.start_ops):
    #        self.action_flag = 0
    #        return self.action_flag
    #    if (self.hour >= self.evening_dc):
    #        self.action_flag = -99
    #        return self.action_flag
    #    if (self.excess_e > 0):  # charge excess energy during operation
    #        self.action_flag = 1
    #        return self.action_flag
    #    if (self.excess_e < 0):  # discharge for ramp_rate during operation
    #        self.action_flag = -1
    #        return self.action_flag
    #    else:
    #        self.action_flag = 1111
    #        return self.action_flag

    def bess_action(
        self
    ):  # a fixed version pending checking
        # Daytime
        if (self.hour >= self.start_ops) and (self.hour < self.evening_dc):
            if (self.excess_e > 0):  # charge excess energy during operation
                self.action_flag = 1
                return self.action_flag
                # WHAT HAPPENS IF EXCESS_E IS 0?
            if (self.excess_e < 0):  # discharge for ramp_rate during operation
                self.action_flag = -1
                return self.action_flag
            else:
                self.action_flag = 1111
                return self.action_flag
        # Night time
        if (self.hour >= self.evening_dc):
            self.action_flag = -99
            return self.action_flag
        else:
            self.action_flag = 1111
            return self.action_flag

    # constructor
    def __init__(self, controller):  # e_input is from solar

        # reading setting from controller
        self.i = controller.i
        self.timestep = controller.timestep_sim[self.i]
        self.plant_type = controller.plant_type
        self.name = controller.name
        self.dc_cap_sol = controller.dc_cap_sol_lower
        self.ac_cap_sol = controller.ac_cap_sol_lower
        self.location = controller.location
        self.base_year = controller.base_year
        self.gen_profile_loc = controller.gen_profile_loc
        self.gen_profile = controller.gen_profile
        self.ini_bess_cap_kWh = controller.ini_bess_cap_kWh
        self.ini_bess_power_kW = controller.ini_bess_power_kW
        self.ini_SoC = controller.ini_SoC
        self.SoC_upper_lim = controller.SoC_upper_lim
        self.SoC_lower_lim = controller.SoC_lower_lim
        self.ini_c_eff = controller.ini_c_eff
        self.ini_dc_eff = controller.ini_dc_eff
        self.bess_lifetime = controller.bess_lifetime
        self.ini_cap_deg = controller.ini_cap_deg
        self.ini_rt_eff_deg = controller.ini_rt_eff_deg
        self.start_ops = controller.start_ops
        self.evening_dc = controller.evening_dc
        self.MEC = controller.MEC
        self.rr_control_kw = controller.rr_control_kw
        self.time_step = controller.time_step * (60 / 60)
        self.min_SoC = controller.min_SoC

        # initial grid output = 0
        self.pre_grid = 0

        # datetime processing
        self._timestep = pd.to_datetime(self.timestep)
        self.day = self._timestep.day
        self.month = self._timestep.month
        self.year = self._timestep.year
        self.hour = self._timestep.hour
        self.minute = self._timestep.minute
        self.second = self._timestep.second

        # creating powerplant and load generation data
        if (controller.plant_type == "solar"):
            self._solar = Solar(self.name, self.dc_cap_sol, self.ac_cap_sol,
                                self.location, self.base_year)
            self._solar.load_generation_data(self.gen_profile_loc,
                                             self.gen_profile)
            self._wind = None
        # if (controller.plant_type == "wind"): #Golf: not yet tested
        #self._wind = Wind (name, wind_cap, ac_cap_wind, location, base_year)
        # self._wind.load_generation_data(gen_profile_loc,gen_profile)
        #self._solar = None
        # if (controller.plant_type == "solar and wind"):#Golf: not yet tested
        #self._solar = Solar (name, dc_cap_sol, ac_cap_sol, location, base_year)
        # self._solar.load_generation_data(gen_profile_loc,gen_profile)
        #self._wind = Wind (name, wind_cap, ac_cap_wind, location, base_year)
        # self._wind.load_generation_data(gen_profile_loc,gen_profile)

        self.e_input = self.get_generation_timestep()
        self.excess_e = self.e_input - self.MEC
        self.flag_action = self.bess_action()

        # creating battery
        self.bat = bess(self)

    # get functions
    def get_pre_SoC(self):
        return self.bat.pre_SoC

    def get_pre_cap(self):
        return self.bat.pre_eff_cap

    def get_plant(self):
        return self.plant

    def get_hour(self):
        return self.hour

    def get_act_flag(self):
        return self.flag_action

    def get_einput(self):
        return self.e_input

    def get_generation_timestep(self) -> float:
        generation = 0
        if (self._solar != None):
            generation += (self._solar.get_generation_datetime(self._timestep)/1000) # Convert watt to kW
        if (self._wind != None):
            generation += self._wind.get_generation_datetime(self._timestep)
        return generation

    #### currently not being use####
    # def get_generation_between(self, startDateTime, endDateTime):
    #currentDateTime = startDateTime;
    # print(startDateTime);
    # print(endDateTime);

    # if(endDateTime > currentDateTime):
    # while(endDateTime > currentDateTime):
    # self.get_generation_timestep(currentDateTime)
    #currentDateTime = currentDateTime + self._timestep
    # print("Done")

    #### currently not being use####
    # def get_generation_year(self, year):
    # if(self._solar != None):
    #solar_generation = self._solar.get_generation_full(year)
    # if(self._wind != None):
    #wind_generation = self._wind.get_generation_full(year)
    # sum the values
    #generator_sum = sum(solar_generation[SOLAR_COL_NAMES[1]], wind_generation[SOLAR_COL_NAMES[1]])
    # return the total generation
    # return pd.concat([solar_generation[SOLAR_COL_NAMES[0]],generator_sum], axis=1, join='inner')

    #####  USED BY CONTROLLER to call on grid output
    def grid_output(self): 
        self.net_output = min((self.bat.bat_outcome(self) + self.e_input),self.MEC)
        #print("net output is", self.net_output)
        #print("Batt", self.bat.bat_outcome(self))
        #print("net without limit", (self.bat.bat_outcome(self) + self.e_input))
        #print("e_input", self.e_input)

        return self.net_output

    def grid_output_wo_limit(self):
        self.net_output_wo_limit = (self.bat.bat_outcome(self) + self.e_input)
        return self.net_output_wo_limit

    def get_batt(self):
        self.batt = self.bat.bat_outcome(self)
        # print("########## BATTERY #################")
        # # self.permitted_charge = max(
        # #     self.charge_req + self.ramp_request,
        # #     -1 * (self.SoC_upper_lim - self.pre_SoC) *
        # #     ((self.eff_cap) / (bus.time_step * self.c_eff)), -self.c_power)
        # print('permitted charge: ',self.bat.permitted_charge)
        # print('charge req: ',self.bat.charge_req)
        # print('ramp req: ', self.bat.ramp_request)
        # print('pre soc: ', self.bat.pre_SoC)
        # print('eff cap: ', self.bat.eff_cap)
        # print('c_power: ', self.bat.c_power)
        return self.batt

    def grid_output_wo_BESS(self):
        self.net_output = min((self.e_input),
                              self.MEC)
        return self.net_output
    # set function

    def set_bus(self, controller, timestep):

        # record previous timestep (Golf: can add more)
        self.pre_timestep = self._timestep
        self.pre_gen = self.get_generation_timestep()
        self.pre_grid = self.grid_output()

        # updating new timestep when called
        self._timestep = pd.to_datetime(timestep)
        self.day = self._timestep.day
        self.month = self._timestep.month
        self.year = self._timestep.year
        self.hour = self._timestep.hour
        self.minute = self._timestep.minute
        self.second = self._timestep.second

        # updating energy
        self.e_input = self.get_generation_timestep()
        self.excess_e = self.e_input - self.MEC
        self.flag_action = self.bess_action()

        # updating battery to new value
        self.bat.set_bess(controller, self)