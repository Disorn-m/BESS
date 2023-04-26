import os

class optimiser:
    def __init__(self, controller):  # empty storing params
        i = controller.iteration
        self.energy_total_no_bess = 0.0
        self.energy_total_bess = 0.0
        self.gain = 0 / 100
        self.sol_increment_MW = 0.0
        self.wind_increment_MW = 0.0
        self.bess_p_increment_kW = 0.0
        self.bess_sizing_increment_kWh = 0.0

        # result from 1st simulation
        self.opt_target_energy = controller.opt_target_energy
        self.target_increase_energy = controller.target_increase_energy
        self.energy_total_no_bess = controller.total_e_input
        self.energy_total_bess = controller.total_grid_output

    def get_increment(self, controller):
        self.pre_gain = self.gain
        # update the result from previous simulation
        self.energy_total_no_bess = controller.total_e_input
        self.energy_total_bess = controller.total_grid_output
        outcome = self.opt(controller)
        return outcome

    def opt(self, controller):
        if controller.sim_status == 'DONE':
            # self.set_opt()
            self.gain = (self.energy_total_bess /
                         self.energy_total_no_bess) - 1
            if self.gain == self.target_increase_energy:  # exact optimisation
                print("optimisation done - exact")
                self.sim_increment = [0, 0]
                return self.sim_increment
            if self.gain - self.target_increase_energy < controller.opt_energy_thres:  # allowed optimisation
                print("optimisation done - allowed")
                self.sim_increment = [0, 0]
                return self.sim_increment
            else:
                self.sim_increment = sim_increment()
                return self.sim_increment
        else:
            return "simulation not done - recheck the controller"

    def sim_increment(self, controller):
        self.pre_diff = self.pre_gain - self.target_increase_energy
        self.diff = self.gain - self.target_increase_energy
        print("before previous sim" + self.pre_diff + " pp")
        print("previous sim" + self.diff + " pp")

        ######################## optimisation order#################################
        def opt_order(self, controller):
            if controller.adjust_cap_first == "Y":
                self.adj_cap_1st = True
            else:
                self.adj_cap_1st = False
            return self.adj_cap_1st

        #################################### increment##############################
        def increment(self, controller):
            # very coarse - cap first
            if self.diff > controller.opt_energy_thres * controller.very_coarse_sensitivity and self.adj_cap_1st == True:
                self.bess_sizing_increment_kWh = controller.ini_bess_cap_kWh * \
                    controller.very_coarse_adj
                self.bess_p_increment_kW = controller.ini_bess_cap_kWh * controller.very_coarse_adj * ( 
                    controller.c_rate)
            # very coarse - power first
            elif self.diff > controller.opt_energy_thres * controller.very_coarse_sensitivity and self.adj_cap_1st == False:
                self.bess_p_increment_kW = controller.ini_bess_power_kW * controller.very_coarse_adj
                self.bess_sizing_increment_kWh = controller.ini_bess_power_kW * controller.very_coarse_adj * (
                    1 / controller.c_rate)
            # coarse  - cap first
            elif controller.opt_energy_thres * controller.coarse_sensitivity <= self.diff < controller.opt_energy_thres * controller.very_coarse_sensitivity and self.adj_cap_1st == True:
                self.bess_sizing_increment_kWh = controller.ini_bess_cap_kWh * controller.coarse_adj
                self.bess_p_increment_kW = controller.ini_bess_cap_kWh * controller.coarse_adj * (
                    controller.c_rate)
            # coarse - power first
            elif controller.opt_energy_thres * controller.coarse_sensitivity <= self.diff < controller.opt_energy_thres * controller.very_coarse_sensitivity and self.adj_cap_1st == False:
                self.bess_p_increment_kW = controller.ini_bess_power_kW * controller.coarse_adj
                self.bess_sizing_increment_kWh = controller.ini_bess_power_kW * controller.coarse_adj * (
                    1 / controller.c_rate)
            # fine - cap first
            elif controller.opt_energy_thres * controller.fine_sensitivity <= self.diff < controller.opt_energy_thres * controller.coarse_sensitivity and self.adj_cap_1st == True:
                self.bess_sizing_increment_kWh = controller.ini_bess_cap_kWh * controller.fine_adj
                self.bess_p_increment_kW = controller.ini_bess_cap_kWh * controller.fine_adj * (
                    controller.c_rate)
            # fine - power first
            elif controller.opt_energy_thres * controller.fine_sensitivity <= self.diff < controller.opt_energy_thres * controller.coarse_sensitivity and self.adj_cap_1st == False:
                self.bess_p_increment_kW = controller.ini_bess_power_kW * controller.fine_adj
                self.bess_sizing_increment_kWh = controller.ini_bess_power_kW * controller.fine_adj * (
                    1 / controller.c_rate)
            # very fine - cap first
            elif controller.opt_energy_thres * controller.very_fine_sensitivity <= self.diff < controller.opt_energy_thres * controller.fine_sensitivity and self.adj_cap_1st == True:
                self.bess_sizing_increment_kWh = controller.ini_bess_cap_kWh * controller.very_fine_adj
                self.bess_p_increment_kW = controller.ini_bess_cap_kWh * controller.very_fine_adj * (
                    controller.c_rate)
            # very fine - power first
            elif controller.opt_energy_thres * controller.very_fine_sensitivity <= self.diff < controller.opt_energy_thres * controller.fine_sensitivity and self.adj_cap_1st == False:
                self.bess_p_increment_kW = controller.ini_bess_power_kW * controller.very_fine_adj
                self.bess_sizing_increment_kWh = controller.ini_bess_power_kW * controller.very_fine_adj * (
                    1 / controller.c_rate)

        ############################### direction (increase/decrease)################
        def incre_direction(self):
            if self.pre_diff > self.diff and self.pre_diff > 0 and self.diff > 0:
                print("closer gap")
                self.opt_direction = -1  # gap is narrower - decreasing the simulation cap for lower gap
            if self.pre_diff < self.diff and self.pre_diff < 0 and self.diff > 0:
                print("closer gap")
                self.opt_direction = -1  # gap is narrower - decreasing the simulation cap for lower gap
            if self.pre_diff > self.diff and self.pre_diff > 0 and self.diff < 0:
                print("wider gap")
                self.opt_direction = +1  # gap is wider - increasing the simulation cap for lower gap
            if self.pre_diff < self.diff and self.pre_diff < 0 and self.diff < 0:
                print("wider gap")
                self.opt_direction = +1  # gap is wider - increasing the simulation cap for lower gap
            else:
                print("error")
                self.opt_direction = 0
            return self.opt_direction

        #############################################################################
        self.opt_order(controller)
        self.increment()
        self.increment = [
            self.bess_p_increment_kW * incre_direction(),
            self.bess_sizing_increment_kWh * incre_direction()
        ]
        return self.increment
