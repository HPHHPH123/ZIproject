from zhinst.toolkit import Session

session = Session("localhost")

device = session.connect_device("dev4625")
Rate_DT_read = device.session.daq_server.getDouble("dev4625/imps/0/demod/rate")
print(Rate_DT_read)


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


# Execute the measurement

ts0 = np.nan
timeout = 1.5 * 1
start_time = time.time()
results = {x: [] for x in sample_nodes}

fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.set_xlabel("Time ($s$)")
ax1.set_ylabel("Subscribed signals")
ax1.set_xlim([0, BURST_DURATION])
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
# Saving the data

daq_module.save.save.wait_for_state_change(0, timeout=10)