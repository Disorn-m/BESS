from generators import Generator, Solar, Wind
from optimiser import optimiser

class bess:
    # BESS constructor - to link to the input from the bus in the below
    def __init__(self, bus):

        # initial parameters (no change over timesteps)
        self.ini_bess_cap = bus.ini_bess_cap_kWh
        self.ini_bess_power = bus.ini_bess_power_kW
        self.ini_SoC = bus.ini_SoC
        self.cap_fade = 0.00
        self.ini_cycle_count = 0.00
        self.SoC_upper_lim = bus.SoC_upper_lim
        self.SoC_lower_lim = bus.SoC_lower_lim
        self.ini_c_eff = bus.ini_c_eff
        self.ini_dc_eff = bus.ini_dc_eff
        self.ini_rt_eff = self.cal_rt_eff(bus.ini_c_eff, bus.ini_dc_eff)
        self.bess_lifetime = bus.bess_lifetime
        self.ini_cap_deg = bus.ini_cap_deg  # percentage
        self.ini_rt_eff_deg = bus.ini_rt_eff_deg  # percentage

        # dynamic parameters (changing over timesteps)
        self.c_rate = self.cal_c_rate(bus.ini_bess_power_kW,
                                      bus.ini_bess_cap_kWh)
        self.dc_power = bus.ini_bess_power_kW
        self.c_power = bus.ini_bess_power_kW
        self.active_rt_eff = self.active_rt_eff()
        self.eff_cap = bus.ini_bess_cap_kWh
        self.c_eff = bus.ini_c_eff
        self.dc_eff = bus.ini_dc_eff
        self.pre_SoC = bus.ini_SoC
        self.hour = bus.hour
        self.e_input = bus.e_input
        self.action_flag = bus.action_flag
        self.pre_grid = bus.pre_grid
        self.pre_SoC_kwh = self.pre_SoC * self.eff_cap
        self.pre_cycle_count = self.ini_cycle_count
        # self.bat_output= self.bat_outcome(bus)

    def active_c_eff(self):  # to be further account for degradation
        self.c_eff = self.ini_c_eff
        return self.c_eff

    def active_dc_eff(self):  # to be further account for degradation
        self.dc_eff = self.ini_dc_eff
        return self.dc_eff

    def active_c_power(self, controller):
        # calculate active capacity of the BESS based on year and degradation
        # battery degradation to be implmented
        if controller.iteration > 0:
            self.c_power = controller.working_bess_power_kW
        print('active c power: ', self.c_power)
        return self.c_power

    def active_dc_power(self, controller):
        # calculate active capacity of the BESS based on year and degradation
        # battery degradation to be implmented
        if controller.iteration > 0:
            self.dc_power = controller.working_bess_power_kW
        return self.dc_power

    def active_cap(self, controller):
        # calculate active capacity of the BESS based on year and degradation
        # battery degradation to be implmented
        if controller.iteration > 0:
            self.eff_cap = controller.working_bess_cap_kWh

        return self.eff_cap



    def active_rt_eff(self):
        # calculate active round-trip effieciency of BESS based on year and degradation
        self.active_rt_eff = self.ini_rt_eff
        return self.active_rt_eff

    def cal_rt_eff(self, c_eff, dc_eff):
        return dc_eff * c_eff

    def cal_c_rate(self, power, capacity):
        return power / capacity

    # Function ############################################################# LOOK AT THIS
    def ramp_rate(self, bus):  # calculation of ramp_rate request
        # if self.action_flag == -1:
        #   ramp = min(self.e_input, bus.MEC) - min(self.pre_grid, bus.MEC)
        # print (ramp)
        # else:
        #    ramp = 0
        # print (ramp)
        # (+) = discharge (-) = charge as looking from BESS perspective
        ramp = self.e_input - self.pre_grid
        if self.action_flag == -1 and (abs(ramp) > bus.rr_control_kw):

            if (ramp < 0):  # battery has to discharge to support on ramp rate
                self.ramp_request = min(
                    abs(ramp) - bus.rr_control_kw, self.dc_power)
                # print (self.ramp_request)
                return self.ramp_request
            if (ramp > 0):  # battery has to charge to support on ramp rate
                self.ramp_request = max(-(abs(ramp) - bus.rr_control_kw),
                                        -self.c_power)
                # print (self.ramp_request)
                return self.ramp_request
            else:
                self.ramp_request = 0
                # print (self.ramp_request)
                return self.ramp_request
        else:
            self.ramp_request = 0
            return self.ramp_request

    def charge(self, bus):
        if self.action_flag == 1:
            ramp = self.e_input - self.pre_grid
            # to ensure that excessenergy is charged to the battery regardeless of ramp rate
            if (abs(ramp) > bus.rr_control_kw) and ((bus.rr_control_kw + self.pre_grid) > bus.MEC):

                self.charge_req = max(-(abs(ramp) - (bus.MEC - self.pre_grid)),
                                      -self.c_power)
                return self.charge_req
            if (abs(ramp) > bus.rr_control_kw):
                self.charge_req = max(-(abs(ramp) - bus.rr_control_kw),
                                      -self.c_power)
                return self.charge_req

            else:
                self.charge_req = bus.MEC - self.e_input
                return self.charge_req
        else:
            return "Error"

    def evening_dc(self, bus):
        if self.action_flag == -99 and self.pre_SoC > bus.min_SoC:
            self.evening_dc_req = self.dc_power * 0.5  # why 0.5?
            # print('evening dc: ',self.evening_dc_req)
        else:
            self.evening_dc_req = 0
            # print('evening dc: ',self.evening_dc_req)
        return self.evening_dc_req

    def bat_outcome(self, bus):  # to be added as more application applied 
        # charge with respect to Ramprate request and excess energy request
        self.permitted_dcharge = 0
        self.permitted_charge = 0
        # print("action flag", self.action_flag)


        if self.action_flag == -1:
            # print ("ramp_rate")
            self.ramp_request = self.ramp_rate(bus)
            # print ("self.ramp_request =" + str(self.ramp_request))
        else:
            self.ramp_request = 0
            # print ("self.ramp_request =" + str(self.ramp_request))

        if self.action_flag == 1:
            # print ("charge")
            self.charge_req = self.charge(bus)
            # print ("self.charge_req =" + str(self.charge_req))
        else:
            self.charge_req = 0
            # print ("self.charge_req =" + str(self.charge_req))

        if self.action_flag == -99:
            # print ("evening_dc")
            self.evening_dc_req = self.evening_dc(bus)
            # print ("self.evening_dc_req =" + str(self.evening_dc_req))
        else:
            self.evening_dc_req = 0
            # print ("self.evening_dc_req =" + str(self.evening_dc_req))

        if self.ramp_request == 0 and self.charge_req == 0:
            self.permitted_charge = 0

        if self.ramp_request < 0 and self.charge_req < 0:
            # use max since charge is (-) so the smallest negative will be the result
            self.permitted_charge = max(
                self.charge_rdueq + self.ramp_request,
                -1 * (self.SoC_upper_lim - self.pre_SoC) *
                (self.eff_cap / (bus.time_step * self.c_eff)), -self.c_power)
            #print ("permit charge1 = "+ str(self.permitted_charge))
        if self.ramp_request < 0 and self.charge_req == 0:
            # use max since charge is (-) so the smallest negative will be the result
            self.permitted_charge = max(
                self.charge_req + self.ramp_request,
                -1 * (self.SoC_upper_lim - self.pre_SoC) *
                ((self.eff_cap) / (bus.time_step * self.c_eff)), -self.c_power)
            #print ("permit charge2 = "+ str(self.permitted_charge))
        if self.ramp_request == 0 and self.charge_req < 0:
            # use max since charge is (-) so the smallest negative will be the result
            self.permitted_charge = max(
                self.charge_req + self.ramp_request,
                -1 * (self.SoC_upper_lim - self.pre_SoC) *
                (self.eff_cap / (bus.time_step * self.c_eff)), -self.c_power)
            #print ("permit charge3 = "+ str(self.permitted_charge))

    # discharge with respect to ramp rate or evening discharge
        if self.ramp_request == 0 and self.evening_dc_req == 0:
            self.permitted_dcharge = 0
            #print ("permit dcharge1 = "+ str(self.permitted_dcharge))
        if self.ramp_request > 0 and self.evening_dc_req > 0:
            # use min since discharge is (+) so the smallest postive will be the result - pending robert clarification
            self.permitted_dcharge = min(
                (self.evening_dc_req + self.ramp_request),
                (self.pre_SoC - self.SoC_lower_lim) *
                (self.eff_cap / bus.time_step) * (self.dc_eff), self.dc_power)
            #print ("permit dcharge2 = "+ str(self.permitted_dcharge))
        if self.ramp_request == 0 and self.evening_dc_req > 0:
            # use min since discharge is (+) so the smallest postive will be the result - pending robert clarification
            self.permitted_dcharge = min(
                (self.evening_dc_req + self.ramp_request),
                (self.pre_SoC - self.SoC_lower_lim) *
                (self.eff_cap / bus.time_step) * (self.dc_eff), self.dc_power)
            #print ("permit dcharge3 = "+ str(self.permitted_dcharge))
        if self.ramp_request > 0 and self.evening_dc_req == 0:
             # use min since discharge is (+) so the smallest postive will be the result - pending robert clarification
            self.permitted_dcharge = min(
                (self.evening_dc_req + self.ramp_request),
                (self.pre_SoC - self.SoC_lower_lim) *
                (self.eff_cap / bus.time_step) * (self.dc_eff), self.dc_power)
            #print ("permit dcharge3 = "+ str(self.permitted_dcharge))


        # logic to sense check permitted charge/discharge
        if (self.permitted_dcharge > 0 and self.permitted_charge == 0):
            self.bat_output = self.permitted_dcharge
            #print ("bat_output1 = " + str(self.bat_output))
            return self.bat_output

        if (self.permitted_dcharge == 0 and self.permitted_charge < 0):
            self.bat_output = self.permitted_charge
            #print ("bat_output2 = " + str(self.bat_output))
            return self.bat_output

        if (self.permitted_dcharge == 0 and self.permitted_charge == 0):
            self.bat_output = 0
            #print ("bat_output3 = " + str(self.bat_output))
            return self.bat_output
        
        

        else:
            #print ("error check output")
            return self.bat_output
        
        
        
        
        

    def cal_SoC(self, bus):

        if (self.pre_SoC == self.ini_SoC):
            self.pre_SoC_kwh = 500

        if (self.bat_output > 0):
            self.new_SoC_kwh = max(
                self.pre_SoC_kwh -
                (self.bat_output * bus.time_step / self.dc_eff),
                (self.eff_cap * bus.min_SoC))
            #print (self.new_SoC_kwh)

        if (self.bat_output < 0):
            self.new_SoC_kwh = min(
                self.pre_SoC_kwh - 
                (self.bat_output * bus.time_step * self.c_eff),
                (self.eff_cap))
            print('c_eff: ',self.c_eff)
            #print (self.new_SoC_kwh)

        if (self.bat_output == 0):
            self.new_SoC_kwh = self.pre_SoC_kwh

        self.SoC = self.new_SoC_kwh / self.ini_bess_cap

        print("SoC: ",self.SoC*100)
        return self.SoC

    def cal_capfade(self):
        # battery lifetime assessment (from discharging energy)
        if (self.bat_output < 0):
            self.cap_fade = self.discharged * self.ini_cap_deg
            return self.cap_fade
        else:
            self.cap_fade = 0
            return self.cap_fade

    def cal_cycle(self, bus):
        if (self.bat_output < 0):
            self.discharged = self.bat_output * bus.time_step
            #print (self.discharged)
            self.cycle_count = self.pre_cycle_count - (self.discharged /
                                                       self.ini_bess_cap)
            self.cap_fade = self.cal_capfade()
            #print (self.cap_fade)
        else:
            self.cycle_count = self.pre_cycle_count
        #print (self.cycle_count)
        return self.cycle_count

    # set the value for next timestep
    def set_bess(self, controller, bus):
        # values from previous timestep
        self.pre_cycle_count = self.cal_cycle(bus)
        self.pre_grid = bus.net_output
        self.pre_SoC = self.cal_SoC(bus)
        self.pre_SoC_kwh = self.pre_SoC * self.eff_cap
        self.pre_eff_cap = self.eff_cap

        # values for new timestep calculation
        self.eff_cap = self.active_cap(controller)
        self.dc_power = self.active_dc_power(controller)
        self.c_power = self.active_c_power(controller)
        self.c_eff = self.active_c_eff()
        self.dc_eff = self.active_dc_eff()
        self.hour = bus.get_hour()
        self.e_input = bus.get_einput()
        self.action_flag = bus.get_act_flag()
        #self.bat_output= self.bat_outcome(bus)

    # Functions for troubleshoot/value checking
    def print_bess(self):
        print("the following parameter are recorded for this timestep: ")
        print("\nself.pre_cycle_count =" + str(self.pre_cycle_count))
        print("self.pre_grid =" + str(self.pre_grid))
        print("self.pre_SoC =" + str(self.pre_SoC))
        print("self.pre_SoC_kwh =" + str(self.pre_SoC_kwh))
        print("self.eff_cap =" + str(self.eff_cap))
        print("self.dc_power =" + str(self.dc_power))
        print("self.c_power =" + str(self.pre_cycle_count))
        print("self.c_eff =" + str(self.c_eff))
        print("self.dc_eff =" + str(self.dc_eff))
        print("self.hour =" + str(self.hour))
        print("self.e_input =" + str(self.e_input))
        print("self.action_flag =" + str(self.action_flag))
        return 'Done'
