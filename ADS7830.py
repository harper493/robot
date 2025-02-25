try:
        import smbus as smb    #type: ignore[import-not-found]
except ImportError:
        try:
                import smbus2 as smb
        except ImportError:
                pass
        
import time
class ADS7830:
	def __init__(self):
		# Get I2C bus
		self.bus = smb.SMBus(1)    #type: ignore[assiognment]
		# I2C address of the device
		self.ADS7830_DEFAULT_ADDRESS			= 0x48
		# ADS7830 Command Set
		self.ADS7830_CMD				= 0x84 # Single-Ended Inputs
	def readAdc(self,channel) -> int:
		"""Select the Command data from the given provided value above"""
		COMMAND_SET = self.ADS7830_CMD | ((((channel<<2)|(channel>>1))&0x07)<<4)
		self.bus.write_byte(self.ADS7830_DEFAULT_ADDRESS, COMMAND_SET)
		data = self.bus.read_byte(self.ADS7830_DEFAULT_ADDRESS)
		return data
	def power(self,channel: int) -> float:
		data = [ self.readAdc(channel) for i in range(9) ]
		data.sort()
		battery_voltage=data[4]/255.0*5.0*2
		return battery_voltage

