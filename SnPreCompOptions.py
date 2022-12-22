"""
SnPreCompOptions.py

Python module containing main code settings. Check that each variable is
defined. Only define a variable True or False, NOT both!

Set CHIPBOARD appropriately depending on board type!

Author: Manuel Pasqual Paul [mppaul@uci.edu]
Last Updated: 08-11-22
"""

# Whether to send Debugging output from Main.py only to terminal
# screen. Other files with DEBUG may need to be defined True to
# receive output. Debug is primarily used.

DEBUG = True
#DEBUG = False

# Whether to Disable Configuration Safety Nets. In field, this is
# not normally True. In lab settings, disabling safety nets can be
# useful. Leaving it False is safer.

#DISABLE_CONFIG_SAFETYNETS = True
DISABLE_CONFIG_SAFETYNETS = False

#
# // choose which communication peripherals will be used in the comms loop
# // for now, twitter is completely not working.
# // NOTE: remember to set kNcomms in SnConstants.h so it equals the number
# // of comms enabled!!
ENABLE_SBD_COMM = True

# // use MODSERIAL (a buffered serial interface) instead of the
# // "standard" serial (unbuffered) provided by mbed
# #define USE_MODSERIAL

'''
Available CHIPBOARDs.
Values should NEVER change! Variables must be set equal to a constant.
'''
SST8CH  =   1  # Set CHIPBOARD for 2023 RPi Firmware with a 2 SST chip running at 1GHz sampling

'''
Select CHIPBOARD.
'''
CHIPBOARD = SST8CH

'''
How many bits are there per DAC register
'''
DAC_BITS = 16


# // whether or not to use the flash memory on the mbed board, to call
# // the mbed provided function that gets the MAC address, etc.
# // these functions all use the mbed interface chip. it has been found
# // that once in while, functions accessing the interface chip will block
# // forever and never return, resulting in a "brain dead" station.
# // therefore, this should almost certainly be disabled (commented out)
# // for stations installed in the ice.
# #define USE_INTERFACE_CHIP
#
# // if defined, try to read the default config from the SD card
# // instead of the interface chip
# //#define LOAD_DEFAULT_CONFIG_FROM_SD
#
# // if defined, will start with both AFAR and SBD powered up during the
# // first comm win after boot up. otherwise, only SBD will be powered
# //#define AFAR_ON_FIRST_COMM_HARDCONF
#
# // whether or not to try to load the default config (wherever it's
# // located -- SD card or interface_chip) immediately -- that is, before
# // even the first communication. Be careful! It's possible this can fail
# // and prevent any communications, possibly resulting in a "brain dead"
# // station? Safer to leave this commented out.
# #define LOAD_DEFAULT_CONFIG_IMMEDIATELY
#
# // whether or not to use the lookup tables to speed up the FFTs
# #define USE_DFFT_LUTS
#

