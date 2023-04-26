#!/usr/bin/env python
# coding: utf-8

# BESS optimisation draft script\
#
# Developed by: CT (Golf), VD\
# \
# Version notes:
# - Available battery function: ramp rate control, discharge at a specific time, excess energy charge
# - Available powerplant profile: solar PV
# - Available BESS sizing optimisation: fixed solar PV sizing under target energy gain (total energy     without BESS vs with BESS)
# \
# Further improvements:
# - See comments in the code
# - Calculation is pending verification and debugging
# - post processing graphic and output

# In[1]:

import pandas as pd
import numpy as np
from pandas import DataFrame as df
import datetime
from datetime import datetime
import os
from controller import controller


# import streamlit as st

# User to input filename and file location

# In[2]:

filename = "setting.csv"
path = r"C:\Users\SIV106800\Documents\GitHub\Solar-BESS-optimisation-tool-development"
output_filename = "optimisation_output.csv"
gen_profile_name = "gen_profile.csv"

# In[3]:


# class bess:
#     # BESS constructor - to link to the input from the bus in the below
#     def __init__(self, bus):

#         # initial parameters (no change over timesteps)
#         self.ini_bess_cap = bus.ini_bess_cap_kWh
#         self.ini_bess_power = bus.ini_bess_power_kW
#         self.ini_SoC = bus.ini_SoC
#         self.cap_fade = 0.00
#         self.ini_cycle_count = 0.00
#         self.SoC_upper_lim = bus.SoC_upper_lim
#         self.SoC_lower_lim = bus.SoC_lower_lim
#         self.ini_c_eff = bus.ini_c_eff
#         self.ini_dc_eff = bus.ini_dc_eff
#         self.ini_rt_eff = self.cal_rt_eff(bus.ini_c_eff, bus.ini_dc_eff)
#         self.bess_lifetime = bus.bess_lifetime
#         self.ini_cap_deg = bus.ini_cap_deg  # percentage
#         self.ini_rt_eff_deg = bus.ini_rt_eff_deg  # percentage

#         # dynamic parameters (changing over timesteps)
#         self.c_rate = self.cal_c_rate(bus.ini_bess_power_kW,
#                                       bus.ini_bess_cap_kWh)
#         self.dc_power = bus.ini_bess_power_kW
#         self.c_power = bus.ini_bess_power_kW
#         self.active_rt_eff = self.active_rt_eff()
#         self.eff_cap = bus.ini_bess_cap_kWh
#         self.c_eff = bus.ini_c_eff
#         self.dc_eff = bus.ini_dc_eff
#         self.pre_SoC = bus.ini_SoC
#         self.hour = bus.hour
#         self.e_input = bus.e_input
#         self.action_flag = bus.action_flag
#         self.pre_grid = bus.pre_grid
#         self.pre_SoC_kwh = self.pre_SoC * self.eff_cap
#         self.pre_cycle_count = self.ini_cycle_count
#         # self.bat_output= self.bat_outcome(bus)

#     def active_c_eff(self):  # to be further account for degradation
#         self.c_eff = self.ini_c_eff
#         return self.c_eff

#     def active_dc_eff(self):  # to be further account for degradation
#         self.dc_eff = self.ini_dc_eff
#         return self.dc_eff

#     def active_c_power(self, controller):
#         # calculate active capacity of the BESS based on year and degradation
#         # battery degradation to be implmented
#         if controller.iteration > 0:
#             self.c_power = controller.working_bess_power_kW
#         return self.c_power

#     def active_dc_power(self, controller):
#         # calculate active capacity of the BESS based on year and degradation
#         # battery degradation to be implmented
#         if controller.iteration > 0:
#             self.dc_power = controller.working_bess_power_kW
#         return self.dc_power

#     def active_cap(self, controller):
#         # calculate active capacity of the BESS based on year and degradation
#         # battery degradation to be implmented
#         if controller.iteration > 0:
#             self.eff_cap = controller.working_bess_cap_kWh
#         return self.eff_cap

#     def active_rt_eff(self):
#         # calculate active round-trip effieciency of BESS based on year and degradation
#         self.active_rt_eff = self.ini_rt_eff
#         return self.active_rt_eff

#     def cal_rt_eff(self, c_eff, dc_eff):
#         return dc_eff * c_eff

#     def cal_c_rate(self, power, capacity):
#         return power / capacity

#     # Function
#     def ramp_rate(self, bus):  # calculation of ramp_rate request
#         # if self.action_flag == -1:
#         #   ramp = min(self.e_input, bus.MEC) - min(self.pre_grid, bus.MEC)
#         # print (ramp)
#         # else:
#         #    ramp = 0
#         # print (ramp)
#         # (+) = discharge (-) = charge as looking from BESS perspective
#         ramp = self.e_input - self.pre_grid
#         if self.action_flag == -1 and (abs(ramp) > bus.rr_control_kw):

#             if (ramp < 0):  # battery has to discharge to support on ramp rate
#                 self.ramp_request = min(
#                     abs(ramp) - bus.rr_control_kw, self.dc_power)
#                 # print (self.ramp_request)
#                 return self.ramp_request
#             if (ramp > 0):  # battery has to charge to support on ramp rate
#                 self.ramp_request = max(-(abs(ramp) - bus.rr_control_kw),
#                                         -self.c_power)
#                 # print (self.ramp_request)
#                 return self.ramp_request
#             else:
#                 self.ramp_request = 0
#                 # print (self.ramp_request)
#                 return self.ramp_request
#         else:
#             self.ramp_request = 0
#             return self.ramp_request

#     def charge(self, bus):
#         if self.action_flag == 1:
#             ramp = self.e_input - self.pre_grid
#             # to ensure that excessenergy is charged to the battery regardeless of ramp rate
#             if (abs(ramp) > bus.rr_control_kw) and ((bus.rr_control_kw + self.pre_grid) > bus.MEC):

#                 self.charge_req = max(-(abs(ramp) - (bus.MEC - self.pre_grid)),
#                                       -self.c_power)
#                 return self.charge_req
#             if (abs(ramp) > bus.rr_control_kw):
#                 self.charge_req = max(-(abs(ramp) - bus.rr_control_kw),
#                                       -self.c_power)
#                 return self.charge_req

#             else:
#                 self.charge_req = bus.MEC - self.e_input
#                 return self.charge_req
#         else:
#             return "Error"

#     def evening_dc(self, bus):
#         if self.action_flag == -99 and self.pre_SoC > bus.min_SoC:
#             self.evening_dc_req = self.dc_power * 0.5  # why 0.5?
#         else:
#             self.evening_dc_req = 0
#         return self.evening_dc_req

#     def bat_outcome(self, bus):  # to be added as more application applied
#         # charge with respect to Ramprate request and excess energy request
#         self.permitted_dcharge = 0
#         self.permitted_charge = 0

#         if self.action_flag == -1:
#             # print ("ramp_rate")
#             self.ramp_request = self.ramp_rate(bus)
#             # print ("self.ramp_request =" + str(self.ramp_request))
#         else:
#             self.ramp_request = 0
#             # print ("self.ramp_request =" + str(self.ramp_request))

#         if self.action_flag == 1:
#             # print ("charge")
#             self.charge_req = self.charge(bus)
#             # print ("self.charge_req =" + str(self.charge_req))
#         else:
#             self.charge_req = 0
#             # print ("self.charge_req =" + str(self.charge_req))

#         if self.action_flag == -99:
#             # print ("evening_dc")
#             self.evening_dc_req = self.evening_dc(bus)
#             # print ("self.evening_dc_req =" + str(self.evening_dc_req))
#         else:
#             self.evening_dc_req = 0
#             # print ("self.evening_dc_req =" + str(self.evening_dc_req))

#         if self.ramp_request == 0 and self.charge_req == 0:
#             self.permitted_charge = 0

#         if self.ramp_request < 0 and self.charge_req < 0:
#             # use max since charge is (-) so the smallest negative will be the result
#             self.permitted_charge = max(
#                 self.charge_rdueq + self.ramp_request,
#                 -1 * (self.SoC_upper_lim - self.pre_SoC) *
#                 (self.eff_cap / (bus.time_step * self.c_eff)), -self.c_power)
#             #print ("permit charge1 = "+ str(self.permitted_charge))
#         if self.ramp_request < 0 and self.charge_req == 0:
#             # use max since charge is (-) so the smallest negative will be the result
#             self.permitted_charge = max(
#                 self.charge_req + self.ramp_request,
#                 -1 * (self.SoC_upper_lim - self.pre_SoC) *
#                 ((self.eff_cap) / (bus.time_step * self.c_eff)), -self.c_power)
#             #print ("permit charge2 = "+ str(self.permitted_charge))
#         if self.ramp_request == 0 and self.charge_req < 0:
#             # use max since charge is (-) so the smallest negative will be the result
#             self.permitted_charge = max(
#                 self.charge_req + self.ramp_request,
#                 -1 * (self.SoC_upper_lim - self.pre_SoC) *
#                 (self.eff_cap / (bus.time_step * self.c_eff)), -self.c_power)
#             #print ("permit charge3 = "+ str(self.permitted_charge))

#     # discharge with respect to ramp rate or evening discharge
#         if self.ramp_request == 0 and self.evening_dc_req == 0:
#             self.permitted_dcharge = 0
#             #print ("permit dcharge1 = "+ str(self.permitted_dcharge))
#         if self.ramp_request > 0 and self.evening_dc_req > 0:
#             # use min since discharge is (+) so the smallest postive will be the result - pending robert clarification
#             self.permitted_dcharge = min(
#                 (self.evening_dc_req + self.ramp_request),
#                 (self.pre_SoC - self.SoC_lower_lim) *
#                 (self.eff_cap / bus.time_step) * (self.dc_eff), self.dc_power)
#             #print ("permit dcharge2 = "+ str(self.permitted_dcharge))
#         if self.ramp_request == 0 and self.evening_dc_req > 0:
#             # use min since discharge is (+) so the smallest postive will be the result - pending robert clarification
#             self.permitted_dcharge = min(
#                 (self.evening_dc_req + self.ramp_request),
#                 (self.pre_SoC - self.SoC_lower_lim) *
#                 (self.eff_cap / bus.time_step) * (self.dc_eff), self.dc_power)
#             #print ("permit dcharge3 = "+ str(self.permitted_dcharge))

#         # logic to sense check permitted charge/discharge
#         if (self.permitted_dcharge > 0 and self.permitted_charge == 0):
#             self.bat_output = self.permitted_dcharge
#             #print ("bat_output1 = " + str(self.bat_output))
#             return self.bat_output

#         if (self.permitted_dcharge == 0 and self.permitted_charge < 0):
#             self.bat_output = self.permitted_charge
#             #print ("bat_output2 = " + str(self.bat_output))
#             return self.bat_output

#         if (self.permitted_dcharge == 0 and self.permitted_charge == 0):
#             self.bat_output = 0
#             #print ("bat_output3 = " + str(self.bat_output))
#             return self.bat_output

#         else:
#             #print ("error check output")
#             return self.bat_output

#     def cal_SoC(self, bus):

#         if (self.pre_SoC == self.ini_SoC):
#             self.pre_SoC_kwh = 0

#         if (self.bat_output > 0):
#             self.new_SoC_kwh = max(
#                 self.pre_SoC_kwh -
#                 (self.bat_output * bus.time_step / self.dc_eff),
#                 (self.eff_cap * bus.min_SoC))
#             #print (self.new_SoC_kwh)

#         if (self.bat_output < 0):
#             self.new_SoC_kwh = min(
#                 self.pre_SoC_kwh - (self.bat_output * bus.time_step),
#                 (self.eff_cap))
#             #print (self.new_SoC_kwh)

#         if (self.bat_output == 0):
#             self.new_SoC_kwh = self.pre_SoC_kwh

#         self.SoC = self.new_SoC_kwh / self.ini_bess_cap

#         #print (self.SoC)
#         return self.SoC

#     def cal_capfade(self):
#         # battery lifetime assessment (from discharging energy)
#         if (self.bat_output < 0):
#             self.cap_fade = self.discharged * self.ini_cap_deg
#             return self.cap_fade
#         else:
#             self.cap_fade = 0
#             return self.cap_fade

#     def cal_cycle(self, bus):
#         if (self.bat_output < 0):
#             self.discharged = self.bat_output * bus.time_step
#             #print (self.discharged)
#             self.cycle_count = self.pre_cycle_count - (self.discharged /
#                                                        self.ini_bess_cap)
#             self.cap_fade = self.cal_capfade()
#             #print (self.cap_fade)
#         else:
#             self.cycle_count = self.pre_cycle_count
#         #print (self.cycle_count)
#         return self.cycle_count

#     # set the value for next timestep
#     def set_bess(self, controller, bus):
#         # values from previous timestep
#         self.pre_cycle_count = self.cal_cycle(bus)
#         self.pre_grid = bus.net_output
#         self.pre_SoC = self.cal_SoC(bus)
#         self.pre_SoC_kwh = self.pre_SoC * self.eff_cap
#         self.pre_cap = self.eff_cap

#         # values for new timestep calculation
#         self.eff_cap = self.active_cap(controller)
#         self.dc_power = self.active_dc_power(controller)
#         self.c_power = self.active_c_power(controller)
#         self.c_eff = self.active_c_eff()
#         self.dc_eff = self.active_dc_eff()
#         self.hour = bus.get_hour()
#         self.e_input = bus.get_einput()
#         self.action_flag = bus.get_act_flag()
#         #self.bat_output= self.bat_outcome(bus)

#     # Functions for troubleshoot/value checking
#     def print_bess(self):
#         print("the following parameter are recorded for this timestep: ")
#         print("\nself.pre_cycle_count =" + str(self.pre_cycle_count))
#         print("self.pre_grid =" + str(self.pre_grid))
#         print("self.pre_SoC =" + str(self.pre_SoC))
#         print("self.pre_SoC_kwh =" + str(self.pre_SoC_kwh))
#         print("self.eff_cap =" + str(self.eff_cap))
#         print("self.dc_power =" + str(self.dc_power))
#         print("self.c_power =" + str(self.pre_cycle_count))
#         print("self.c_eff =" + str(self.c_eff))
#         print("self.dc_eff =" + str(self.dc_eff))
#         print("self.hour =" + str(self.hour))
#         print("self.e_input =" + str(self.e_input))
#         print("self.action_flag =" + str(self.action_flag))
#         return 'Done'


# In[4]:

#global constants
SOLAR_COL_NAMES = ["x", "y"]
NO_INPUT = -1

# Possible attributes that solar can have
SOLAR_ATTRIBUTES = [
    'annual_degradation', 'unavailability', "ops_start", "ops_stop",
    "extra_loss", "inverter_object", "pv_module_object"
]

# Possible attributes that wind can have
WIND_ATTRIBUTES = [
    'unavailability', "ops_start", "ops_stop", "extra_loss", "turbine_object"
]


# class Generator:

#     import pandas as pd
#     import numpy as np
#     from pandas import DataFrame as df
#     import datetime
#     from datetime import datetime
#     import os
#     from datetime import timedelta
#     from typing import Tuple

#     # base class for generators. We can expand this for solar, wind, geothermal etc.
#     def __init__(self, name: str, AC_cap: float, location: Tuple[float, float],
#                  base_year: int, **kwargs) -> None:
#         # set the class variables
#         self._name = name
#         self._ac_cap = AC_cap
#         self._location = location
#         self._gen_profile = []
#         self._base_year = base_year

#     # Load csv file
#     def loadcsv(self, profile, profile_loc):
#         os.chdir(profile_loc)
#         # print(os.getcwd())
#         profile_data = pd.read_csv(profile)
#         df_profile = pd.DataFrame(profile_data)
#         return df_profile

#     def load_generation_data(self, location, filename):
#         csv_data = self.loadcsv(filename, location)
#         genprofile = csv_data.iloc[:, [0, 5]]

#         # rename the columns to what we want
#         genprofile.columns = [SOLAR_COL_NAMES[0], SOLAR_COL_NAMES[1]]
#         self._gen_profile = pd.concat([
#             pd.to_datetime(genprofile[SOLAR_COL_NAMES[0]]),
#             genprofile[SOLAR_COL_NAMES[1]]
#         ],
#             axis=1,
#             join='inner')
#         print("Successfully loaded file")

#     def get_generation_full(self, year) -> pd.DataFrame:
#         # gets the generation profile for the year
#         if len(self._gen_profile) == 0:
#             raise Exception("No generation profile for the plant")
#         diff_year = year - self._base_year
#         s = pd.concat([
#             self._gen_profile[SOLAR_COL_NAMES[0]] +
#             pd.offsets.DateOffset(years=diff_year),
#             self._gen_profile.select_dtypes(include=[np.number]) *
#             self.get_multiplier(year)
#         ],
#             axis=1,
#             join='inner')
#         return s

#     def get_multiplier(self, year: int) -> int:
#         # base generator class has a multiplier of 1 - no losses, unavailability etc
#         multiplier = 1
#         return multiplier

#     def get_generation_datetime(self, datetimeVal):
#         datetimeVal = pd.to_datetime(datetimeVal)
#         day = datetimeVal.day
#         month = datetimeVal.month
#         year = datetimeVal.year
#         hour = datetimeVal.hour
#         minute = datetimeVal.minute
#         second = datetimeVal.second

#         # get the generation for the date and time requested
#         if len(self._gen_profile) == 0:
#             # if we don't have a gen profile, then raise error
#             raise Exception("No generation profile for the plant")
#         else:
#             #result = self._gen_profile.query("{} == '{}/{}/{} {}:{:02}'".format(SOLAR_COL_NAMES[0], day, month, year, hour, minute));
#             get_profile = self.get_generation_full(year)
#             result = get_profile[get_profile[SOLAR_COL_NAMES[0]] ==
#                                  datetimeVal]
#             if (len(result) != 0):
#                 return result.iloc[0, 1]
#             else:
#                 raise Exception("Invalid Date Time Input")


# ############################################################ Solar Generator Implementation ##########################################################################


# class Solar(Generator):
#     # inherets from the generator class
#     def __init__(self, name: str, DC_cap: float, AC_cap: float,
#                  location: (float, float), base_year: int, **kwargs) -> None:
#         super().__init__(name, AC_cap, location, base_year)
#         # solar specific parameters
#         self._dc_cap = DC_cap
#         self._solar_technical = {}
#         # add the attributes we want

#         for attribute in SOLAR_ATTRIBUTES:
#             self._solar_technical[attribute] = NO_INPUT

#         for args in kwargs.keys():
#             print(args)
#             if args in self._solar_technical.keys():
#                 self._solar_technical[args] = kwargs[args]

#     def get_multiplier(self, year: int) -> int:  # Golf: not yet tested
#         # get the final multiplyer after adjusting for unavailability, extra_loss and annual degradation
#         # overwriting the base generator class

#         multiplier = 1

#         # get the multiplier value for degradation
#         if (self._solar_technical["annual_degradation"] != NO_INPUT):
#             # if there is a value specified for annual degradation
#             if (year < self._base_year):
#                 # if year is before base year - raise error
#                 raise Exception("Invalid year input")

#             else:
#                 # annual degradation
#                 degradation_base_multiplier = 1 - self._solar_technical[
#                     "annual_degradation"]
#                 diff_year = year - self._base_year

#                 # update the multiplier for the annual degredation
#                 multiplier = multiplier * degradation_base_multiplier**diff_year

#     # get the multiplier value for unavailability
#         if (self._solar_technical["unavailability"] != NO_INPUT):
#             # if there is a value specified for unavailability
#             availability_percentage = 1 - self._solar_technical[
#                 "unavailability"]

#             # update the multiplier for the annual degredation
#             multiplier = multiplier * availability_percentage

#         # get the multiplier value for extra loss
#         if (self._solar_technical["extra_loss"] != NO_INPUT):
#             # if there is a value specified for unavailability
#             actual_output_percentage = 1 - self._solar_technical["extra_loss"]

#             # update the multiplier for the annual degredation
#             multiplier = multiplier * actual_output_percentage
#         return multiplier


# class PV_Module:  # Golf: not yet tested
#     def __init__(self, warranty_lifetime: int, module_no: int,
#                  pv_rating: float):
#         self._warranty_duration = warranty_lifetime
#         self._module_no = module_no
#         self._pv_rating = pv_rating

#     def get_dc_cap(self) -> float:
#         return self._module_no * self._pv_rating

#     def generation_lifetime_check(self) -> bool:
#         # ? not sure what to put here
#         pass


# class Inverter:  # Golf: not yet tested
#     def __init__(self, inverter_no: int, inverter_rating: float) -> None:
#         self._inverter_no = inverter_no
#         self._inverter_rating = inverter_rating

#     def get_ac_cap(self) -> float:
#         # ? what is the formula for this?
#         pass


############################################################ Wind Generator Implementation ##########################################################################


# class Wind(Generator):  # Golf: not yet tested
#     # Inherets from the generator class
#     def __init__(self, name: str, wind_cap: float, AC_cap: float,
#                  location: (float, float), base_year: int, **kwargs) -> None:
#         super().__init__(name, AC_cap, location, base_year)

#         # wind specific parameters
#         self._wind_cap = wind_cap  # nominal capacity of the wind turbines
#         self._wind_technical = {}

#         # add the attributes we want
#         for attribute in WIND_ATTRIBUTES:
#             self._wind_technical[attribute] = NO_INPUT

#         for args in kwargs.keys():
#             print(args)
#             if args in self._wind_technical.keys():
#                 self._wind_technical[args] = kwargs[args]

#     def get_multiplier(self, year: int) -> int:
#         # get the final multiplyer after adjusting for unavailability, extra_loss
#         # overwriting the base generator class
#         multiplier = 1
#         # get the multiplier value for unavailability
#         if (self._wind_technical["unavailability"] != NO_INPUT):
#             # if there is a value specified for unavailability
#             availability_percentage = 1 - \
#                 self._wind_technical["unavailability"]

#             # update the multiplier for the annual degredation
#             multiplier = multiplier * availability_percentage

#         # get the multiplier value for extra loss
#         if (self._wind_technical["extra_loss"] != NO_INPUT):
#             # if there is a value specified for unavailability
#             actual_output_percentage = 1 - self._wind_technical["extra_loss"]

#             # update the multiplier for the annual degredation
#             multiplier = multiplier * actual_output_percentage

#         return multiplier


############################################################ Hybrid Generator Implementation ##########################################################################

# class SolWind(Generator): #Golf: Vishy to implement based on above Sol and Wind Generator assuming same name and location

# In[5]:


# Bus class oversee BESS and Generator classes by CT and VD
# class Bus:

#     # imports
#     import pandas as pd
#     import numpy as np
#     from pandas import DataFrame as df
#     import datetime
#     from datetime import datetime
#     import os
#     from datetime import timedelta

#     # The operation of this bus is the excess energy from solar is stored in the BESS
#     # The bus will also request ramp rate control according to the allowable ramp rate control
#     # The bus will also request the BESS to discharge the energy at the evening (if SoC is above the set criteria)

#     # def bess_action(
#     #    self
#     # ):  # action flag to be passed on to BESS object through the controller
#     #    if (self.hour < self.start_ops):
#     #        self.action_flag = 0
#     #        return self.action_flag
#     #    if (self.hour >= self.evening_dc):
#     #        self.action_flag = -99
#     #        return self.action_flag
#     #    if (self.excess_e > 0):  # charge excess energy during operation
#     #        self.action_flag = 1
#     #        return self.action_flag
#     #    if (self.excess_e < 0):  # discharge for ramp_rate during operation
#     #        self.action_flag = -1
#     #        return self.action_flag
#     #    else:
#     #        self.action_flag = 1111
#     #        return self.action_flag

#     def bess_action(
#         self
#     ):  # a fixed version pending checking
#         # Daytime
#         if (self.hour >= self.start_ops) and (self.hour < self.evening_dc):
#             if (self.excess_e > 0):  # charge excess energy during operation
#                 self.action_flag = 1
#                 return self.action_flag
#                 # WHAT HAPPENS IF EXCESS_E IS 0?
#             if (self.excess_e < 0):  # discharge for ramp_rate during operation
#                 self.action_flag = -1
#                 return self.action_flag
#             else:
#                 self.action_flag = 1111
#                 return self.action_flag
#         # Night time
#         if (self.hour >= self.evening_dc):
#             self.action_flag = -99
#             return self.action_flag
#         else:
#             self.action_flag = 1111
#             return self.action_flag

#     # constructor
#     def __init__(self, controller):  # e_input is from solar

#         # reading setting from controller
#         self.i = controller.i
#         self.timestep = controller.timestep_sim[self.i]
#         self.plant_type = controller.plant_type
#         self.name = controller.name
#         self.dc_cap_sol = controller.dc_cap_sol_lower
#         self.ac_cap_sol = controller.ac_cap_sol_lower
#         self.location = controller.location
#         self.base_year = controller.base_year
#         self.gen_profile_loc = controller.gen_profile_loc
#         self.gen_profile = controller.gen_profile
#         self.ini_bess_cap_kWh = controller.ini_bess_cap_kWh
#         self.ini_bess_power_kW = controller.ini_bess_power_kW
#         self.ini_SoC = controller.ini_SoC
#         self.SoC_upper_lim = controller.SoC_upper_lim
#         self.SoC_lower_lim = controller.SoC_lower_lim
#         self.ini_c_eff = controller.ini_c_eff
#         self.ini_dc_eff = controller.ini_dc_eff
#         self.bess_lifetime = controller.bess_lifetime
#         self.ini_cap_deg = controller.ini_cap_deg
#         self.ini_rt_eff_deg = controller.ini_rt_eff_deg
#         self.start_ops = controller.start_ops
#         self.evening_dc = controller.evening_dc
#         self.MEC = controller.MEC
#         self.rr_control_kw = controller.rr_control_kw
#         self.time_step = controller.time_step * (60 / 60)
#         self.min_SoC = controller.min_SoC

#         # initial grid output = 0
#         self.pre_grid = 0

#         # datetime processing
#         self._timestep = pd.to_datetime(self.timestep)
#         self.day = self._timestep.day
#         self.month = self._timestep.month
#         self.year = self._timestep.year
#         self.hour = self._timestep.hour
#         self.minute = self._timestep.minute
#         self.second = self._timestep.second

#         # creating powerplant and load generation data
#         if (controller.plant_type == "solar"):
#             self._solar = Solar(self.name, self.dc_cap_sol, self.ac_cap_sol,
#                                 self.location, self.base_year)
#             self._solar.load_generation_data(self.gen_profile_loc,
#                                              self.gen_profile)
#             self._wind = None
#         # if (controller.plant_type == "wind"): #Golf: not yet tested
#         #self._wind = Wind (name, wind_cap, ac_cap_wind, location, base_year)
#         # self._wind.load_generation_data(gen_profile_loc,gen_profile)
#         #self._solar = None
#         # if (controller.plant_type == "solar and wind"):#Golf: not yet tested
#         #self._solar = Solar (name, dc_cap_sol, ac_cap_sol, location, base_year)
#         # self._solar.load_generation_data(gen_profile_loc,gen_profile)
#         #self._wind = Wind (name, wind_cap, ac_cap_wind, location, base_year)
#         # self._wind.load_generation_data(gen_profile_loc,gen_profile)

#         self.e_input = self.get_generation_timestep()
#         self.excess_e = self.e_input - self.MEC
#         self.flag_action = self.bess_action()

#         # creating battery
#         self.bat = bess(self)

#     # get functions
#     def get_pre_SoC(self):
#         return self.pre_SoC

#     def get_pre_cap(self):
#         return self.pre_cap

#     def get_plant(self):
#         return self.plant

#     def get_hour(self):
#         return self.hour

#     def get_act_flag(self):
#         return self.flag_action

#     def get_einput(self):
#         return self.e_input

#     def get_generation_timestep(self) -> float:
#         generation = 0
#         if (self._solar != None):
#             generation += self._solar.get_generation_datetime(self._timestep)
#         if (self._wind != None):
#             generation += self._wind.get_generation_datetime(self._timestep)
#         return generation

#     #### currently not being use####
#     # def get_generation_between(self, startDateTime, endDateTime):
#     #currentDateTime = startDateTime;
#     # print(startDateTime);
#     # print(endDateTime);

#     # if(endDateTime > currentDateTime):
#     # while(endDateTime > currentDateTime):
#     # self.get_generation_timestep(currentDateTime)
#     #currentDateTime = currentDateTime + self._timestep
#     # print("Done")

#     #### currently not being use####
#     # def get_generation_year(self, year):
#     # if(self._solar != None):
#     #solar_generation = self._solar.get_generation_full(year)
#     # if(self._wind != None):
#     #wind_generation = self._wind.get_generation_full(year)
#     # sum the values
#     #generator_sum = sum(solar_generation[SOLAR_COL_NAMES[1]], wind_generation[SOLAR_COL_NAMES[1]])
#     # return the total generation
#     # return pd.concat([solar_generation[SOLAR_COL_NAMES[0]],generator_sum], axis=1, join='inner')

#     # for the controller to call on grid output
#     def grid_output(self):
#         self.net_output = min((self.bat.bat_outcome(self) + self.e_input),
#                               self.MEC)
#         #print("net output is", self.net_output)
#         #print("Batt", self.bat.bat_outcome(self))
#         #print("net without limit", (self.bat.bat_outcome(self) + self.e_input))
#         #print("e_input", self.e_input)

#         return self.net_output

#     def grid_output_wo_limit(self):
#         self.net_output_wo_limit = (self.bat.bat_outcome(self) + self.e_input)
#         return self.net_output_wo_limit

#     def get_batt(self):
#         self.batt = self.bat.bat_outcome(self)
#         return self.batt

#     def grid_output_wo_BESS(self):
#         self.net_output = min((self.e_input),
#                               self.MEC)
#         return self.net_output
#     # set function

#     def set_bus(self, controller, timestep):

#         # record previous timestep (Golf: can add more)
#         self.pre_timestep = self._timestep
#         self.pre_gen = self.get_generation_timestep()
#         self.pre_grid = self.grid_output()

#         # updating new timestep when called
#         self._timestep = pd.to_datetime(timestep)
#         self.day = self._timestep.day
#         self.month = self._timestep.month
#         self.year = self._timestep.year
#         self.hour = self._timestep.hour
#         self.minute = self._timestep.minute
#         self.second = self._timestep.second

#         # updating energy
#         self.e_input = self.get_generation_timestep()
#         self.excess_e = self.e_input - self.MEC
#         self.flag_action = self.bess_action()

#         # updating battery to new value
#         self.bat.set_bess(controller, self)

#         # Vishy = please have a quick thought on if there is a need to update the generator? I feel like there is no need for now unless we plan to update any calculation


# In[6]:

# logger to store calculation of every timestep and simulation (in separate sheets)
# logger stores all data from every timestep but not communicating back and forth - intend to use for later graphical or more detailed analysis
# for VD
# class logger:

# In[7]:


# class controller:

#     # controller receives inputs from the view
#     # imports
#     import pandas as pd
#     import numpy as np
#     import datetime
#     import os

#     ###################################################################################################
#     # temporary replacement of the view - this should be the connector between the GUI and the view
#     ###################################################################################################

#     def __init__(self, filename, path):
#         def read_setup(filename, path):
#             os.chdir(path)
#             print(os.getcwd())
#             setting = pd.read_csv(filename)
#             df_setting = pd.DataFrame(setting)
#             print(df_setting)
#             return df_setting

#         # setting global parameters from setting#
#         self.df_setting = read_setup(
#             filename, path
#         )  # can be replaced to other function getting data from the view

#         ## simulation setting##
#         self.name = str(self.df_setting['value'][0])
#         self.time_step = float(self.df_setting['value'][1])
#         # print(self.time_step)
#         # timestep generation
#         if self.time_step == float(1):
#             self.timestamp = '5T'
#             # print(self.timestamp)
#         elif self.time_step < float(1):
#             self.x = round(time_step * 60)
#             self.timestamp = str(self.x) + "min"
#             # print(self.timestamp)
#         else:
#             print("more than hourly resolution! - not support")

#         self.start_timestep = pd.to_datetime(self.df_setting['value'][35])
#         self.end_timestep = pd.to_datetime(self.df_setting['value'][36])

#         # other simulation parameters
#         self.location = str(self.df_setting['value'][2])
#         self.base_year = float(self.df_setting['value'][3])
#         self.plant_type = str(self.df_setting['value'][4])
#         self.opt_target_energy = str(self.df_setting['value'][5])
#         self.target_increase_energy = float(
#             self.df_setting['value'][6].strip("%")) / 100
#         self.opt_target_LCOE = str(self.df_setting['value'][7])
#         self.target_LCOE = float(
#             self.df_setting['value'][8])  # LCOE optimisaiton to be implemented
#         self.gen_profile_loc = path
#         self.gen_profile = gen_profile_name

#         ## solar PV plant setting##
#         self.annual_degradation_sol = float(
#             self.df_setting['value'][9].strip('%')) / 100
#         self.extra_loss_sol = float(
#             self.df_setting['value'][10].strip('%')) / 100
#         self.unavailability_sol = float(
#             self.df_setting['value'][11].strip('%')) / 100

#         ##############################################################################################
#         ## possible optimise with solar PV and wind sizing (not implemented)##
#         self.changable_sol = str(self.df_setting['value'][17])
#         self.dc_cap_sol_upper = float(self.df_setting['value'][15])
#         self.dc_cap_sol_lower = float(
#             self.df_setting['value']
#             [16])  # this should be initial cap for Sol profile
#         self.ac_cap_sol_upper = float(self.df_setting['value'][33])
#         self.ac_cap_sol_lower = float(self.df_setting['value'][34])

#         ## wind plant setting##
#         #########################################################################

#         ## grid setting and operation scheme##
#         # Golf: we might have to relook at this when implementing wind
#         self.MEC = float(
#             self.df_setting['value'][12])  # Maximum Export Capacity
#         self.evening_dc = float(self.df_setting['value'][13])
#         self.start_ops = float(self.df_setting['value'][14])

#         ## battery operation##
#         self.ini_bess_cap_kWh = float(self.df_setting['value'][21])
#         self.ini_bess_power_kW = float(self.df_setting['value'][22])
#         self.ini_SoC = float(self.df_setting['value'][23].strip('%')) / 100
#         self.SoC_upper_lim = float(
#             self.df_setting['value'][24].strip('%')) / 100
#         self.SoC_lower_lim = float(
#             self.df_setting['value'][25].strip('%')) / 100
#         self.ini_c_eff = float(self.df_setting['value'][26].strip('%')) / 100
#         self.ini_dc_eff = float(self.df_setting['value'][27].strip('%')) / 100
#         self.bess_lifetime = float(self.df_setting['value'][28])
#         self.ini_cap_deg = float(self.df_setting['value'][29].strip('%')) / 100
#         self.ini_rt_eff_deg = float(
#             self.df_setting['value'][30].strip('%')) / 100
#         self.min_SoC = float(self.df_setting['value'][31].strip(
#             '%')) / 100  # minimum SoC to discharge energy in the evening
#         self.rr_control_kw = float(self.df_setting['value'][32])
#         self.power_increment = 0.001
#         self.capacity_increment = 0.001
#         print(self.power_increment)
#         print(self.capacity_increment)

#         ##############################################
#         #### setting to be included in setting file####
#         ##############################################
#         self.print_output = 'Y'
#         self.create_logger = 'Y'
#         self.opt_energy_thres = 0.1 / \
#             100  # how much higher than target %gain allowed default 0.1%
#         self.consider_ratio_bess = 'Y'
#         # manufacturing limit on the bess power vs capacity default 0.5 (capacity = 2*power)
#         self.c_rate_lower_lim = 0.5
#         # manufacturing limit on the bess power vs capacity default 0.5 (capacity = 2*power)
#         self.c_rate_upper_lim = 5
#         # increment for C-rate at each optimasimation iteration (fixed C-rate)
#         self.c_rate_step = 0.5
#         # adjusting the cap by +/- percentage of input value
#         self.very_coarse_adj = 25 / 100
#         self.coarse_adj = 10 / 100  # adjusting the cap by +/- percentage of input value
#         self.fine_adj = 1 / 100  # adjusting the cap by +/- percentage of input value
#         self.very_fine_adj = 0.1 / 100  # adjusting the cap by +/- percentage of input value
#         self.adjust_cap_first = "Y"  # if this is yes then "adjust_power_first" will be "N"
#         self.very_coarse_sensitivity = 20  # times of optimisation treshold
#         self.coarse_sensitivity = 10
#         self.fine_sensitivity = 2.5
#         self.very_fine_sensitivity = 1
#         ##############################################
#         # initialising logger for output record - logger to be implemented
#         # if  (create_logger == 'Y'):
#         #self.log = logger (self)

#         # initialising key output record
#         if (self.print_output == 'Y'):
#             self.cap_record = []
#             self.power_record = []
#             self.power_gain_record = []
#             self.c_rate_record = []
#             self.opt_record = []
#         # to be further adding the setting as we include more and more application

#         # initialising c-rate iteration
#         self.round = 0

#     ############################################################################
#     ############################################################################

#     ########################## controller process################################
#     ### The main fuction of the controller is per the following###
#     # 1.sim_start => initialising the bus object and perform first simulation
#     # 2.ini_opt => initialising optimiser and record the result from first simulation
#     # 3.set_sim => set the simulation parameter for the next simulation
#     # 4.start_opt_same_c_rate => calling above function to find "optimal" capacity and power for a fixed c-rate
#     # 5.start_opt_varia_c_rate => iterate through "start_opt_same_c_rate" to find "optimal" capacity and power for a fixed c-rate

#     def gen_timestep(self):
#         self.start = pd.to_datetime(self.start_timestep)
#         self.end = pd.to_datetime(self.end_timestep)
#         self.timestep_sim = pd.date_range(start=self.start,
#                                           end=self.end,
#                                           freq=self.timestamp)
#         return self.timestep_sim

#     def sim_start(
#         self
#     ):  # command the bus to calculate all timesteps and sending output to optimiser
#         # initialising relevant bus and optimiser at first timestep and taking result from first time step

#         self.iteration = 0

#         self.timestep_sim = self.gen_timestep()

#         self.i = 0
#         self.main = Bus(self)  # creating bus
#         self.total_grid_output = self.main.grid_output(
#         )  # calculation of 1st timestamp grid output
#         self.total_grid_output_wo_BESS = self.main.grid_output_wo_BESS()
#         self.total_grid_output_wo_limit = self.main.grid_output_wo_limit()
        
#         self.total_Battery_output = self.main.get_batt()
#         self.total_e_input = self.main.e_input  # calculation of 1st timestamp e-input

#         self.i += 1
#         while self.i < len(self.timestep_sim):
#             # iterate through all the timestep and record the energy to grid at each timestep and energy input (to calculate gain)
            
#             self.main.set_bus(self, self.timestep_sim[self.i])
#             self.total_grid_output += self.main.grid_output()
#             self.total_grid_output_wo_BESS += self.main.grid_output_wo_BESS()
#             self.total_Battery_output += self.main.get_batt()
#             self.total_grid_output_wo_limit += self.main.grid_output_wo_limit()
#             self.total_e_input += self.main.e_input
#             print(self.i)
#             print("net output is",  self.main.grid_output())
#             print("Total grid",  self.total_grid_output)
#             print("grid wo BESS",  self.main.grid_output_wo_BESS())
#             print("Total grid wo BESS",  self.total_grid_output_wo_BESS)
#             print("grid wo limit",  self.main.grid_output_wo_limit())
#             print("Total grid wo limit",  self.total_grid_output_wo_limit)
#             print("e_input",  self.main.e_input)
#             print("Total e_input",  self.total_e_input)
#             print("Battery",  self.main.get_batt())
#             print("Total Battery",  self.total_Battery_output)
#             #print("net output is", Bus.grid_output)
#             #print("Batt", bess.bat_outcome)
#             #print("e_input", Bus.get_generation_timestep)
#             # might need to add more parameters as we include more optimisation
#             self.i += 1
#         self.sim_status = 'DONE'
#         print("simulation status: " + self.sim_status +
#               "\ntotal timestep ran: " + str(self.i))
#         print("total grid output without BESS: " +
#               str(self.total_grid_output_wo_BESS))
#         print("total grid output: " + str(self.total_grid_output) +
#               "\ntotal_e_input: " + str(self.total_e_input))
#         print("total battery output: " + str(self.total_Battery_output))
#         print("current gain = " +
#               str(abs((self.total_grid_output / self.total_e_input) - 1)))

#     def ini_opt(self):
#         self.optimizer = optimiser(self)
#         self.key_result = pd.DataFrame()

#     ### communication with optimiser, getting increment and adjust initial sizing to later battery creation ###
#     def new_bess_sizing(self):
#         self.increment = self.optimizer.get_increment(self)
#         self.power_increment = self.increment[
#             0]  # global parameter will be used in BESS object
#         self.capacity_increment = self.increment[
#             1]  # global parameter will be used in BESS object
#         print("got increment")

#         self.working_bess_cap_kWh = self.ini_bess_cap_kWh + self.capacity_increment
#         self.working_bess_power_kW = self.ini_bess_power_kW + self.power_increment

#     ### c-rate change - renew optimiser and adjust the simulation ###
#     def get_c_rate(self):
#         if self.round == 0:  # first simulation c-rate equals to lower limit
#             self.c_rate = self.c_rate_lower_lim
#         if self.c_rate > self.c_rate_lower_lim and self.c_rate < self.c_rate_upper_lim:
#             self.c_rate = self.c_rate_lower_lim + (self.round -
#                                                    1) * self.c_rate_increment
#         return self.c_rate

#     ### shell function to start the optimisation: first simulation, re-adjust, second simulation til the end of the first c-rate ###
#     def start_opt_same_c_rate(self):

#         self.iteration = 0
#         print("iteration no." + str(self.iteration))
#         self.sim_start()  # run 8761 files
#         self.ini_opt()  # initializing optimiser
#         # self.new_bess_sizing() #calculate new BESS sizing
#         self.c_rate = self.get_c_rate()  # get c-rate value
#         while self.power_increment != 0 and self.capacity_increment != 0:
#             self.sim_start()
#             self.ini_opt()
#             self.new_bess_sizing()
#             self.iteration += 1
#             print("iteration no." + str(self.iteration))
#         self.opt_power = self.working_bess_power_kW
#         self.opt_cap = self.working_bess_cap_kWh
#         print("optimal capacity at c-rate " + str(self.c_rate) + " is " +
#               str(self.opt_cap))
#         print("optimal power at c-rate " + str(self.c_rate) + " is " +
#               str(self.opt_power))
#         self.record_output()

#     def start_opt_varia_c_rate(self):
#         self.round = 0
#         self.c_rate_increment = self.c_rate_upper_lim / self.c_rate_step
#         while self.round < c_rate_step:
#             c_rate(self.round)
#             start_opt_same_c_rate()
#             self.round += 1
#         self.report_export()

#     ### log the  BESS cap, power final energy gain at a C-rate per sheet ###
#     def record_output(self):
#         self.opt_record.append(self.iteration)
#         self.cap_record.append(self.opt_cap)
#         self.power_record.append(self.opt_power)
#         self.power_gain_record.append(1 - (self.total_grid_output /
#                                            self.total_e_input))
#         self.c_rate_record.append(self.c_rate)

#     ############################## TEMPORARY REPLACEMENT OF THE VIEW########################
#     # export the above input to CSV file
#     def record_export(self):
#         self.key_result.assign(sim_no=self.opt_record)
#         self.key_result.assign(capacity=self.cap_record)
#         self.key_result.assign(power=self.power_record)
#         self.key_result.assign(power_gain=self.power_gain_record)
#         self.key_result.assign(c_rate=self.c_rate_record)
#         self.writer = pd.ExcelWriter(self.output_filename)
#         self.key_result.to_excel(writer, 'Sheet1')
#         self.writer.save()


# In[8]:


# class optimiser:
#     def __init__(self, controller):  # empty storing params
#         i = controller.iteration
#         self.energy_total_no_bess = 0.0
#         self.energy_total_bess = 0.0
#         self.gain = 0 / 100
#         self.sol_increment_MW = 0.0
#         self.wind_increment_MW = 0.0
#         self.bess_p_increment_kW = 0.0
#         self.bess_sizing_increment_kWh = 0.0

#         # result from 1st simulation
#         self.opt_target_energy = controller.opt_target_energy
#         self.target_increase_energy = controller.target_increase_energy
#         self.energy_total_no_bess = controller.total_e_input
#         self.energy_total_bess = controller.total_grid_output

#     def get_increment(self, controller):
#         self.pre_gain = self.gain
#         # update the result from previous simulation
#         self.energy_total_no_bess = controller.total_e_input
#         self.energy_total_bess = controller.total_grid_output
#         outcome = self.opt(controller)
#         return outcome

#     def opt(self, controller):
#         if controller.sim_status == 'DONE':
#             # self.set_opt()
#             self.gain = (self.energy_total_bess /
#                          self.energy_total_no_bess) - 1
#             if self.gain == self.target_increase_energy:  # exact optimisation
#                 print("optimisation done - exact")
#                 self.sim_increment = [0, 0]
#                 return self.sim_increment
#             if self.gain - self.target_increase_energy < controller.opt_energy_thres:  # allowed optimisation
#                 print("optimisation done - allowed")
#                 self.sim_increment = [0, 0]
#                 return self.sim_increment
#             else:
#                 self.sim_increment = sim_increment()
#                 return self.sim_increment
#         else:
#             return "simulation not done - recheck the controller"

#     def sim_increment(self, controller):
#         self.pre_diff = self.pre_gain - self.target_increase_energy
#         self.diff = self.gain - self.target_increase_energy
#         print("before previous sim" + self.pre_diff + " pp")
#         print("previous sim" + self.diff + " pp")

#         ######################## optimisation order#################################
#         def opt_order(self, controller):
#             if controller.adjust_cap_first == "Y":
#                 self.adj_cap_1st = True
#             else:
#                 self.adj_cap_1st = False
#             return self.adj_cap_1st

#         #################################### increment##############################
#         def increment(self, controller):
#             # very coarse - cap first
#             if self.diff > controller.opt_energy_thres * controller.very_coarse_sensitivity and self.adj_cap_1st == True:
#                 self.bess_sizing_increment_kWh = controller.ini_bess_cap_kWh * \
#                     controller.very_coarse_adj
#                 self.bess_p_increment_kW = controller.ini_bess_cap_kWh * controller.very_coarse_adj * (
#                     c_rate)
#             # very coarse - power first
#             elif self.diff > controller.opt_energy_thres * controller.very_coarse_sensitivity and self.adj_cap_1st == False:
#                 self.bess_p_increment_kW = controller.ini_bess_power_kW * controller.very_coarse_adj
#                 self.bess_sizing_increment_kWh = controller.ini_bess_power_kW * controller.very_coarse_adj * (
#                     1 / controller.c_rate)
#             # coarse  - cap first
#             elif controller.opt_energy_thres * controller.coarse_sensitivity <= self.diff < controller.opt_energy_thres * controller.very_coarse_sensitivity and self.adj_cap_1st == True:
#                 self.bess_sizing_increment_kWh = controller.ini_bess_cap_kWh * controller.coarse_adj
#                 self.bess_p_increment_kW = controller.ini_bess_cap_kWh * controller.coarse_adj * (
#                     controller.c_rate)
#             # coarse - power first
#             elif controller.opt_energy_thres * controller.coarse_sensitivity <= self.diff < controller.opt_energy_thres * controller.very_coarse_sensitivity and self.adj_cap_1st == False:
#                 self.bess_p_increment_kW = controller.ini_bess_power_kW * controller.coarse_adj
#                 self.bess_sizing_increment_kWh = controller.ini_bess_power_kW * controller.coarse_adj * (
#                     1 / controller.c_rate)
#             # fine - cap first
#             elif controller.opt_energy_thres * controller.fine_sensitivity <= self.diff < controller.opt_energy_thres * controller.coarse_sensitivity and self.adj_cap_1st == True:
#                 self.bess_sizing_increment_kWh = controller.ini_bess_cap_kWh * controller.fine_adj
#                 self.bess_p_increment_kW = controller.ini_bess_cap_kWh * controller.fine_adj * (
#                     controller.c_rate)
#             # fine - power first
#             elif controller.opt_energy_thres * controller.fine_sensitivity <= self.diff < controller.opt_energy_thres * controller.coarse_sensitivity and self.adj_cap_1st == False:
#                 self.bess_p_increment_kW = controller.ini_bess_power_kW * controller.fine_adj
#                 self.bess_sizing_increment_kWh = controller.ini_bess_power_kW * controller.fine_adj * (
#                     1 / controller.c_rate)
#             # very fine - cap first
#             elif controller.opt_energy_thres * controller.very_fine_sensitivity <= self.diff < controller.opt_energy_thres * controller.fine_sensitivity and self.adj_cap_1st == True:
#                 self.bess_sizing_increment_kWh = controller.ini_bess_cap_kWh * controller.very_fine_adj
#                 self.bess_p_increment_kW = controller.ini_bess_cap_kWh * controller.very_fine_adj * (
#                     controller.c_rate)
#             # very fine - power first
#             elif controller.opt_energy_thres * controller.very_fine_sensitivity <= self.diff < controller.opt_energy_thres * controller.fine_sensitivity and self.adj_cap_1st == False:
#                 self.bess_p_increment_kW = controller.ini_bess_power_kW * controller.very_fine_adj
#                 self.bess_sizing_increment_kWh = controller.ini_bess_power_kW * controller.very_fine_adj * (
#                     1 / controller.c_rate)

#         ############################### direction (increase/decrease)################
#         def incre_direction(self):
#             if self.pre_diff > self.diff and self.pre_diff > 0 and self.diff > 0:
#                 print("closer gap")
#                 self.opt_direction = -1  # gap is narrower - decreasing the simulation cap for lower gap
#             if self.pre_diff < self.diff and self.pre_diff < 0 and self.diff > 0:
#                 print("closer gap")
#                 self.opt_direction = -1  # gap is narrower - decreasing the simulation cap for lower gap
#             if self.pre_diff > self.diff and self.pre_diff > 0 and self.diff < 0:
#                 print("wider gap")
#                 self.opt_direction = +1  # gap is wider - increasing the simulation cap for lower gap
#             if self.pre_diff < self.diff and self.pre_diff < 0 and self.diff < 0:
#                 print("wider gap")
#                 self.opt_direction = +1  # gap is wider - increasing the simulation cap for lower gap
#             else:
#                 print("error")
#                 self.opt_direction = 0
#             return self.opt_direction

#         #############################################################################
#         self.opt_order(controller)
#         self.increment()
#         self.increment = [
#             self.bess_p_increment_kW * incre_direction(),
#             self.bess_sizing_increment_kWh * incre_direction()
#         ]
#         return self.increment


# In[9]:

########## Command Board##########
system = controller(filename, path)  # 1. initialize controller
print("initialised the controller")
# iterate c-rate
# system.start_opt_varia_c_rate()
# In[10]:

# same c-rate
# system.start_opt_same_c_rate()
system.sim_start() # 2. Start the simulation --> see controller.py


