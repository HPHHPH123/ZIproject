from zhinst.toolkit import Session
import numpy as np

session = Session("localhost")
device = session.connect_device("DEV4625")

device.demods[0].enable(True)

sample_nodes = [
    device.imps[0].sample.param1


]

TOTAL_DURATION = 1 # [s]
SAMPLING_RATE = 100e3 # Number of points/second
BURST_DURATION = 0.001 # Time in seconds for each data burst/segment.

num_cols = int(np.ceil(SAMPLING_RATE * BURST_DURATION))
num_bursts = int(np.ceil(TOTAL_DURATION / BURST_DURATION))

daq_module = session.modules.daq
daq_module.device(device)
daq_module.type(0) # continuous acquisition
daq_module.grid.mode(4)
daq_module.count(num_bursts)
daq_module.duration(BURST_DURATION)
daq_module.grid.cols(num_cols)


daq_module.save.fileformat(1)
daq_module.save.filename('zi_toolkit_acq_example')
daq_module.save.saveonread(1)

for node in sample_nodes:
    daq_module.subscribe(node)
clockbase = device.clockbase()

import matplotlib.pyplot as plt
def read_and_plot_data(daq_module, results, ts0):
    daq_data = daq_module.read(raw=False, clk_rate=clockbase)
    progress = daq_module.raw_module.progress()[0]
    for node in sample_nodes:
        # Check if node data available
        if node in daq_data.keys():
            for sig_burst in daq_data[node]:

                results[node].append(sig_burst)
                if np.any(np.isnan(ts0)):
                  ts0 = sig_burst.header['createdtimestamp'][0] / clockbase
                # Convert from device ticks to time in seconds.
                t0_burst = sig_burst.header['createdtimestamp'][0] / clockbase
                t = (sig_burst.time + t0_burst) - ts0
                value = sig_burst.value[0, :]
                # Plot the data
                ax1.plot(t, value)
                ax1.set_title(f"Progress of data acquisition: {100 * progress:.2f}%.")
                fig.canvas.draw()
                plt.pause(0.001)
    return results, ts0
import time

ts0 = np.nan
timeout = 1.5 * TOTAL_DURATION
start_time = time.time()
results = {x: [] for x in sample_nodes}

fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.set_xlabel("Time ($s$)")
ax1.set_ylabel("Subscribed signals")
ax1.set_xlim([0, TOTAL_DURATION])
ax1.grid()

# Start recording data
daq_module.execute()

while time.time() - start_time < timeout:
    results, ts0 = read_and_plot_data(daq_module, results, ts0)

    if daq_module.raw_module.finished():
        # Once finished, call once more to get the potential remaining data.
        results, ts0 = read_and_plot_data(daq_module, results, ts0)
        break

    time.sleep(BURST_DURATION)
plt.pause(0)