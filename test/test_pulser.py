import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

@cocotb.test()
async def test_pulser_single_pulse(dut):
    dut._log.info("Start")

    # Initial values
    dut.pulse_en.value = 0
    dut.delay.value = 0
    dut.pulse_width.value = 0
    dut.num_pulses.value = 0
    dut.pulse_spacing.value = 0
    dut.rst_n.value = 1

    # Set the clock period to 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut._log.info("Test single pulse")

    dut.delay.value = 20 # Delay of 20+1 clock cycles before the pulse starts
    dut.pulse_width.value = 5 # Pulse width of 5+1 clock cycles
    dut.num_pulses.value = 1
    dut.pulse_spacing.value = 0

    dut.pulse_en.value = 1
    await ClockCycles(dut.clk, 1)
    dut.pulse_en.value = 0
    await ClockCycles(dut.clk, 1)

    await ClockCycles(dut.clk, 21) # Delay of 20+1 clock cycles before the first pulse starts

    # Check that the output pulse is generated with the correct width
    for _ in range(6):
        assert dut.pulse_out.value == 1
        await ClockCycles(dut.clk, 1)

    assert dut.pulse_out.value == 0
    await ClockCycles(dut.clk, 1)
    assert dut.ready.value == 1

@cocotb.test()
async def test_pulser_multiple_pulses(dut):
    dut._log.info("Start")

    # Initial values
    dut.pulse_en.value = 0
    dut.delay.value = 0
    dut.pulse_width.value = 0
    dut.num_pulses.value = 0
    dut.pulse_spacing.value = 0
    dut.rst_n.value = 1

    # Set the clock period to 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut._log.info("Test multiple pulses")

    dut.delay.value = 20 # Delay of 20+1 clock cycles before the first pulse starts
    dut.pulse_width.value = 5 # Pulse width of 5+1 clock cycles
    dut.num_pulses.value = 3
    dut.pulse_spacing.value = 10 # Spacing of 10+1 clock cycles

    dut.pulse_en.value = 1
    await ClockCycles(dut.clk, 1)
    dut.pulse_en.value = 0
    await ClockCycles(dut.clk, 1)

    await ClockCycles(dut.clk, 21) # Delay of 20+1 clock cycles before the first pulse starts

    for x in range(3):
        for _ in range(6):
            assert dut.pulse_out.value == 1
            await ClockCycles(dut.clk, 1)
        if x < 2:
             for _ in range(11):
                assert dut.pulse_out.value == 0
                await ClockCycles(dut.clk, 1)

    assert dut.pulse_out.value == 0
    await ClockCycles(dut.clk, 1)
    assert dut.ready.value == 1