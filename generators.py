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

import pandas as pd
import numpy as np
from pandas import DataFrame as df
import datetime
from datetime import datetime
import os
from datetime import timedelta
from typing import Tuple

class Generator:



    # base class for generators. We can expand this for solar, wind, geothermal etc.
    def __init__(self, name: str, AC_cap: float, location: tuple[float, float],
                 base_year: int, **kwargs) -> None:
        # set the class variables
        self._name = name
        self._ac_cap = AC_cap
        self._location = location
        self._gen_profile = []
        self._base_year = base_year

    # Load csv file
    def loadcsv(self, profile, profile_loc):
        os.chdir(profile_loc)
        # print(os.getcwd())
        profile_data = pd.read_csv(profile)
        df_profile = pd.DataFrame(profile_data)
        return df_profile

    def load_generation_data(self, location, filename):
        csv_data = self.loadcsv(filename, location)
        genprofile = csv_data.iloc[:, [0, 5]]

        # rename the columns to what we want
        genprofile.columns = [SOLAR_COL_NAMES[0], SOLAR_COL_NAMES[1]]
        self._gen_profile = pd.concat([
            pd.to_datetime(genprofile[SOLAR_COL_NAMES[0]]),
            genprofile[SOLAR_COL_NAMES[1]]
        ],
            axis=1,
            join='inner')
        print("Successfully loaded file")

    def get_generation_full(self, year) -> pd.DataFrame:
        # gets the generation profile for the year
        if len(self._gen_profile) == 0:
            raise Exception("No generation profile for the plant")
        diff_year = year - self._base_year
        s = pd.concat([
            self._gen_profile[SOLAR_COL_NAMES[0]] +
            pd.offsets.DateOffset(years=diff_year),
            self._gen_profile.select_dtypes(include=[np.number]).round(20) *
            self.get_multiplier(year)
        ],
            axis=1,
            join='inner')
        # df = pd.DataFrame(self._gen_profile)
        # df.to_csv("output.csv")
        return s

    def get_multiplier(self, year: int) -> int:
        # base generator class has a multiplier of 1 - no losses, unavailability etc
        multiplier = 1
        return multiplier

    def get_generation_datetime(self, datetimeVal):
        datetimeVal = pd.to_datetime(datetimeVal)
        day = datetimeVal.day
        month = datetimeVal.month
        year = datetimeVal.year
        hour = datetimeVal.hour
        minute = datetimeVal.minute
        second = datetimeVal.second

        # get the generation for the date and time requested
        if len(self._gen_profile) == 0:
            # if we don't have a gen profile, then raise error
            raise Exception("No generation profile for the plant")
        else:
            #result = self._gen_profile.query("{} == '{}/{}/{} {}:{:02}'".format(SOLAR_COL_NAMES[0], day, month, year, hour, minute));
            get_profile = self.get_generation_full(year)
            result = get_profile[get_profile[SOLAR_COL_NAMES[0]] ==
                                 datetimeVal]
            if (len(result) != 0):
                return result.iloc[0, 1]
            else:
                raise Exception("Invalid Date Time Input")


############################################################ Solar Generator Implementation ##########################################################################


class Solar(Generator):
    # inherets from the generator class
    def __init__(self, name: str, DC_cap: float, AC_cap: float,
                 location: tuple[float, float], base_year: int, **kwargs) -> None:
        super().__init__(name, AC_cap, location, base_year)
        # solar specific parameters
        self._dc_cap = DC_cap
        self._solar_technical = {}
        # add the attributes we want

        for attribute in SOLAR_ATTRIBUTES:
            self._solar_technical[attribute] = NO_INPUT

        for args in kwargs.keys():
            print(args)
            if args in self._solar_technical.keys():
                self._solar_technical[args] = kwargs[args]

    def get_multiplier(self, year: int) -> int:  # Golf: not yet tested
        # get the final multiplyer after adjusting for unavailability, extra_loss and annual degradation
        # overwriting the base generator class

        multiplier = 1

        # get the multiplier value for degradation
        if (self._solar_technical["annual_degradation"] != NO_INPUT):
            # if there is a value specified for annual degradation
            if (year < self._base_year):
                # if year is before base year - raise error
                raise Exception("Invalid year input")

            else:
                # annual degradation
                degradation_base_multiplier = 1 - self._solar_technical[
                    "annual_degradation"]
                diff_year = year - self._base_year

                # update the multiplier for the annual degredation
                multiplier = multiplier * degradation_base_multiplier**diff_year

    # get the multiplier value for unavailability
        if (self._solar_technical["unavailability"] != NO_INPUT):
            # if there is a value specified for unavailability
            availability_percentage = 1 - self._solar_technical[
                "unavailability"]

            # update the multiplier for the annual degredation
            multiplier = multiplier * availability_percentage

        # get the multiplier value for extra loss
        if (self._solar_technical["extra_loss"] != NO_INPUT):
            # if there is a value specified for unavailability
            actual_output_percentage = 1 - self._solar_technical["extra_loss"]

            # update the multiplier for the annual degredation
            multiplier = multiplier * actual_output_percentage
        return multiplier
    
############################################################ Wind Generator Implementation ##########################################################################

class Wind(Generator):  # Golf: not yet tested
# Inherets from the generator class
    def __init__(self, name: str, wind_cap: float, AC_cap: float,
                location: tuple[float, float], base_year: int, **kwargs) -> None:
        super().__init__(name, AC_cap, location, base_year)

        # wind specific parameters
        self._wind_cap = wind_cap  # nominal capacity of the wind turbines
        self._wind_technical = {}

        # add the attributes we want
        for attribute in WIND_ATTRIBUTES:
            self._wind_technical[attribute] = NO_INPUT

        for args in kwargs.keys():
            print(args)
            if args in self._wind_technical.keys():
                self._wind_technical[args] = kwargs[args]

    def get_multiplier(self, year: int) -> int:
        # get the final multiplyer after adjusting for unavailability, extra_loss
        # overwriting the base generator class
        multiplier = 1
        # get the multiplier value for unavailability
        if (self._wind_technical["unavailability"] != NO_INPUT):
            # if there is a value specified for unavailability
            availability_percentage = 1 - \
                self._wind_technical["unavailability"]

            # update the multiplier for the annual degredation
            multiplier = multiplier * availability_percentage

        # get the multiplier value for extra loss
        if (self._wind_technical["extra_loss"] != NO_INPUT):
            # if there is a value specified for unavailability
            actual_output_percentage = 1 - self._wind_technical["extra_loss"]

            # update the multiplier for the annual degredation
            multiplier = multiplier * actual_output_percentage

        return multiplier
