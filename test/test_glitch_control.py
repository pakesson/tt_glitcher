import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

from cocotbext.uart import UartSink, UartSource

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_glitch_control_echo(dut):
    dut._log.info("Start")

    # Set the clock period to 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Initial values
    dut.trigger_in.value = 0

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut._log.info("Test glitch control echo")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)
    uart_sink = UartSink(dut.uart_tx, baud=115200, bits=8)

    # Unrecognized command bytes will be echoed back
    for x in range(0x10, 0x20):
        await uart_source.write(bytes([x]))
        await uart_source.wait()

        data = await uart_sink.read()
        assert data == bytes([x]), f"Expected {x:#02x}, got {data[0]:#02x}"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_glitch_control_hello(dut):
    dut._log.info("Start")

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

    dut._log.info("Test glitch control hello")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)
    uart_sink = UartSink(dut.uart_tx, baud=115200, bits=8)

    await uart_source.write(b'h')
    await uart_source.wait()

    # uart_sink.read(5) should return b'Erika', but it only waits for the first byte
    # and then throws an exception because the queue is empty.
    # Let's just read one byte at a time instead.
    data = await uart_sink.read()
    assert data == b'E', f"Expected 'E', got {data}"
    data = await uart_sink.read()
    assert data == b'r', f"Expected 'r', got {data}"
    data = await uart_sink.read()
    assert data == b'i', f"Expected 'i', got {data}"
    data = await uart_sink.read()
    assert data == b'k', f"Expected 'k', got {data}"
    data = await uart_sink.read()
    assert data == b'a', f"Expected 'a', got {data}"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_project_full_glitch_sequence_without_reset(dut):
    dut._log.info("Start")

    # Set the clock period to 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Initial values
    dut.trigger_in.value = 0

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut._log.info("Test glitch control full glitch sequence without reset")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'd\x00\x12') # Set delay
    await uart_source.write(b'w\x01')     # Set width
    await uart_source.write(b'n\x02')     # Set num pulses
    await uart_source.write(b's\x00\x03') # Set pulse spacing
    await uart_source.write(b't')         # Trigger pulse

    await RisingEdge(dut.glitch_ctrl.pulse_en)
    await ClockCycles(dut.clk, 1)

    for _ in range(0x13): # Delay + 1
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"

    for _ in range(2): # Width + 1
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1"

    for _ in range(4): # Spacing + 1
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"

    for _ in range(2): # Width + 1
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_glitch_control_full_glitch_sequence_with_reset(dut):
    dut._log.info("Start")

    # Set the clock period to 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Initial values
    dut.trigger_in.value = 0

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut._log.info("Test glitch control full glitch sequence with reset")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'd\x00\x12') # Set delay
    await uart_source.write(b'w\x01')     # Set width
    await uart_source.write(b'n\x02')     # Set num pulses
    await uart_source.write(b's\x00\x03') # Set pulse spacing
    await uart_source.write(b'r\x00\x50') # Set reset length
    await uart_source.write(b'p')         # Reset target and then pulse

    await RisingEdge(dut.target_reset_out)
    await ClockCycles(dut.clk, 1)

    for x in range(0x50): # Reset
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1" # The pulse should also be high during the reset
        assert dut.target_reset_out.value == 1, "Expected target_reset_out to be 1"

    for _ in range(0x13): # Delay + 1
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"
        assert dut.target_reset_out.value == 0, "Expected target_reset_out to be 0"

    for _ in range(2): # Width + 1
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1"
        assert dut.target_reset_out.value == 0, "Expected target_reset_out to be 0"

    for _ in range(4): # Spacing + 1
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"
        assert dut.target_reset_out.value == 0, "Expected target_reset_out to be 0"

    for _ in range(2): # Width + 1
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1"
        assert dut.target_reset_out.value == 0, "Expected target_reset_out to be 0"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"
    assert dut.target_reset_out.value == 0, "Expected target_reset_out to be 0"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_glitch_control_trigger(dut):
    dut._log.info("Start")

    # Set the clock period to 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Initial values
    dut.trigger_in.value = 0

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut._log.info("Test glitch control full glitch sequence")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'd\x00\x12') # Set delay
    await uart_source.write(b'w\x01')     # Set width
    await uart_source.write(b'n\x02')     # Set num pulses
    await uart_source.write(b's\x00\x03') # Set pulse spacing
    await uart_source.write(b'a')         # Arm
    await uart_source.wait()

    await ClockCycles(dut.clk, 1)

    dut.trigger_in.value = 1
    await ClockCycles(dut.clk, 1)
    dut.trigger_in.value = 0

    for _ in range(0x13): # Delay + 1
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"

    for _ in range(2): # Width + 1
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1"

    for _ in range(4): # Spacing + 1
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"

    for _ in range(2): # Width + 1
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"

@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_glitch_control_target_reset_only(dut):
    dut._log.info("Start")

    # Set the clock period to 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Initial values
    dut.trigger_in.value = 0

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut._log.info("Test glitch control target reset only")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)
    await uart_source.write(b'y')         # Reset mode 'none' (reset only)
    await uart_source.write(b'r\x12\x34') # Set reset length
    await uart_source.write(b'p')         # Power cycle (reset) target

    await RisingEdge(dut.target_reset_out)
    await ClockCycles(dut.clk, 1)

    for _ in range(0x1234): # Reset
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1" # The pulse should also be high during the reset
        assert dut.target_reset_out.value == 1, "Expected target_reset_out to be 1"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"
    assert dut.target_reset_out.value == 0, "Expected target_reset_out to be 0"


@cocotb.test(timeout_time=10, timeout_unit="ms")
async def test_glitch_control_reset_arm_trigger(dut):
    dut._log.info("Start")

    # Set the clock period to 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Initial values
    dut.trigger_in.value = 0

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut._log.info("Test glitch control reset, arm and trigger")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)
    await uart_source.write(b'i')         # Reset mode 'arm'
    await uart_source.write(b'd\x00\x12') # Set delay
    await uart_source.write(b'w\x01')     # Set width
    await uart_source.write(b'r\x00\x80') # Set reset length
    await uart_source.write(b'p')         # Power cycle (reset) target

    await RisingEdge(dut.target_reset_out)
    await ClockCycles(dut.clk, 1)

    for _ in range(0x80): # Reset
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1" # The pulse should also be high during the reset
        assert dut.target_reset_out.value == 1, "Expected target_reset_out to be 1"
        assert dut.armed_out.value == 0, "Expected armed_out to be 0"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"
    assert dut.target_reset_out.value == 0, "Expected target_reset_out to be 0"

    # Trigger should now be armed
    assert dut.armed_out.value == 1, "Expected armed_out to be 1"

    await ClockCycles(dut.clk, 1)
    dut.trigger_in.value = 1
    await ClockCycles(dut.clk, 1)
    dut.trigger_in.value = 0

    for _ in range(0x13): # Delay + 1
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"
        assert dut.armed_out.value == 0, "Expected armed_out to be 0"

    for _ in range(2): # Width + 1
        await ClockCycles(dut.clk, 1)
        assert dut.pulse_out.value == 1, "Expected pulse_out to be 1"
        assert dut.armed_out.value == 0, "Expected armed_out to be 0"

    await ClockCycles(dut.clk, 1)
    assert dut.pulse_out.value == 0, "Expected pulse_out to be 0"
    assert dut.armed_out.value == 0, "Expected armed_out to be 0"
