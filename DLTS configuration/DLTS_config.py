"""
This is a demo to confgure the DLTS setiings and show the DAQ result
"""


from zhinst.toolkit import Session
from zhinst.toolkit.nodetree.nodetree import Connection
import zhinst.utils
import numpy as np
import matplotlib.pyplot as plt
import time


class DLTS_exp():

    def DLTS_setting(device_id:str,
                     frequency: float,
                     amp_AC:float,
                     amp_pulse:float,
                     TC:float, Rate_DT:int ,
                     Duration_pulse:float,
                     Duty_cycle_pulse:float,
                     Window_burst:float,
                     Percent_relaxation:float
                     ):
        session = Session("localhost")
        device = session.connect_device(device_id,interface = '1GbE')
        imp_index = 0

        #Config of the DLTS experiment

        Deactivationtime_TU1 = Percent_relaxation *  Window_burst
        Activationtime_TU1 = Duration_pulse - (1-Percent_relaxation) * Window_burst
        with device.set_transaction():
         device.imps[imp_index].enable(1)
         device.imps[imp_index].output.amplitude(amp_AC)
         device.imps[imp_index].freq(frequency)
         device.imps[imp_index].demod.timeconstant(TC)
         device.imps[imp_index].demod.order(8)
         device.imps[imp_index].demod.rate(Rate_DT)
         device.imps[imp_index].auto.bw(0)
         device.imps[imp_index].auto.output(0)
         device.imps[imp_index].current.range(100e-6)
         device.imps[imp_index].voltage.range(3.0)
         device.imps[imp_index].auto.inputrange(0)
         device.imps[imp_index].output.range(10.0)
         device.demods[0].trigger(32)
         device.demods[2].trigger(32)
         device.sigouts[imp_index].add(1)
         device.auxouts[0].limitupper(1.5)
         device.auxouts[1].limitupper(5.0)
         device.auxouts[0].scale(1.5)
         device.auxouts[1].scale(5.0)
         device.auxouts[0].demodselect(0)
         device.auxouts[1].demodselect(1)
         device.auxouts[0].outputselect(13)
         device.auxouts[1].outputselect(13)
         device.tu.thresholds[0].input(59)
         device.tu.thresholds[1].input(59)
         device.tu.thresholds[0].activationtime(Duration_pulse)
         device.tu.thresholds[0].deactivationtime(Duration_pulse/Duty_cycle_pulse-Duration_pulse )
         device.tu.thresholds[1].activationtime(Activationtime_TU1)
         device.tu.thresholds[1].deactivationtime(Deactivationtime_TU1)
    # We subscribe the capacitance in parallel.

        session.daq_server.setInt('/dev4625/tu/logicunits/0/inputs/0/not', 1)


        sample_nodes = [
        device.imps[0].sample.param1.avg
        #device.demods[0].sample.auxin0.avg
        #device.imps[0].sample.Param1
        ]

        #Create and configure the Data Acquisition module


        Rate_DT_read = device.session.daq_server.getDouble("%s/demods/0/rate" % device_id )

        print(Rate_DT_read)

        BURST_DURATION = (Duration_pulse + Activationtime_TU1) # Time in seconds for each data burst/segment.
        TOTAL_DURATION = 8e-3
        num_bursts = int(np.ceil(TOTAL_DURATION / BURST_DURATION))

        num_cols = int(np.ceil(Rate_DT_read * BURST_DURATION))


        #Module creation

        daq_module = session.modules.daq
        daq_module.device(device)
        daq_module.triggernode('/dev4625/demods/0/sample.AuxIn0')
        daq_module.type(1)
        daq_module.edge(1)
        daq_module.level(amp_pulse/2)
        daq_module.grid.mode(4)
        daq_module.count(1)
        daq_module.grid.cols(num_cols)
        daq_module.grid.repetitions(1)
        #daq_module.delay(0)


        for node in sample_nodes:
            daq_module.subscribe(node)
            print(node)

        ts0 = np.nan
        # Recording and plotting the data in edge mode
        start_time = time.time()
        timeout = 5
        daq_module.execute()

        clockbase = device.clockbase()

        results = {x: [] for x in sample_nodes}


        def read_and_plot_data(daq_module_input, results_measure,ts_0):
            daq_data = daq_module_input.read(raw=False, clk_rate=clockbase)
            for node in sample_nodes:

                if node in daq_data.keys():
                    for sig_burst in daq_data[node]:
                        if  np.isnan(ts_0):
                            results_measure[node].append(sig_burst)
                            t_0 = sig_burst.header['createdtimestamp'][0] / clockbase

                    value_cap = sig_burst.value[0, :]
            t = []
            value_plot=[]
            #print(value_cap)

            for i in range(len(value_cap)):
                if not np.isnan(value_cap[i]):
                    value_plot.append(value_cap[i])
                    t.append( sig_burst.time[i])

            t= t-t[0]
            ax1.plot(t, value_plot)
            fig.canvas.draw()
            plt.pause(0.001)
            return t,value_plot


        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xlabel("Time ($s$)")
        ax1.set_ylabel("Capacitance(F)")
        ax1.ticklabel_format(style='sci', scilimits=(-1, 2), axis='both',useMathText=True)
        #ax2 = fig.add_subplot(111)

        while time.time() - start_time < timeout:
            if daq_module.raw_module.finished():

                result = read_and_plot_data(daq_module, results, ts0)
                plt.pause(2)

                return result


