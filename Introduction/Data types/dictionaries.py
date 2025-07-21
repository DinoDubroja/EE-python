# dictionaries.py
# Demonstration of Python dict operations with EE-focused examples and printed results

# 1. Basic creation & access
devices = {"SG":"192.168.0.10",  # Signal Generator
           "OSC":"USB0::0x0957::0x1798::MY1234567::INSTR",  # Oscilloscope
           "PSU":"GPIB0::5::INSTR"}  # Power Supply
print("device addresses:", devices)
print("Oscilloscope address:", devices["OSC"])

# .get() with default
print("Multimeter address:", devices.get("DMM", "Not found"))

# 2. Adding and updating entries
devices["DMM"] = "USB0::0x1AB1::0x0E11::DM123456::INSTR"
print("After adding DMM:", devices)
# bulk update
devices.update({"FunctionGen":"USB0::0x1234::0x5678::FG1111::INSTR"})
print("After update with FunctionGen:", devices)

# 3. Removing entries
addr = devices.pop("PSU")
print("Removed PSU, address was:", addr)
devices.pop("NONEXISTENT", None)  # safe pop
print("After pop operations:", devices)

# 4. Iteration over keys, values, items
print("All instrument keys:", list(devices.keys()))
print("All addresses:", list(devices.values()))
print("All device entries:")
for name, addr in devices.items():
    print(f"  {name} -> {addr}")

# 5. Defaultdict for grouping measurements
from collections import defaultdict
measurements = [(1, 0.12), (2, 0.47), (1, 0.15), (3, 0.78), (2, 0.51)]
by_channel = defaultdict(list)
for ch, val in measurements:
    by_channel[ch].append(val)
print("Grouped measurements by channel:")
for ch, vals in by_channel.items():
    avg = sum(vals)/len(vals)
    print(f"  CH{ch}: readings={vals}, avg={avg:.3f} V")

# 6. Nested dict: device configurations
device_configs = {
    "SG": {"voltage": 5.0, "frequency": 1e6, "output": True},
    "PSU": {"voltage": 12.0, "current_limit": 1.5},
}
print("Device configurations:", device_configs)
# Access nested
print("SG freq:", device_configs["SG"]["frequency"], "Hz")

# 7. Dict comprehension: invert mapping (assuming unique values)
inverted = {addr: name for name, addr in devices.items()}
print("Inverted devices dict (addr->name):", inverted)

# 8. Counting error codes with Counter
from collections import Counter
error_log = [404, 500, 404, 403, 500, 404]
counts = Counter(error_log)
print("Error code occurrences:", counts)

# 9. Clearing a dict
temp = devices.copy()
temp.clear()
print("Cleared copy of devices:", temp)

# 10. Edge-case: using mutable keys raises TypeError
try:
    bad = {[1,2,3]: "list-as-key"}
except TypeError as e:
    print("Cannot use mutable types as dict keys:", e)
