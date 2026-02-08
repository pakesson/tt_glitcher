import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

from cocotbext.uart import UartSink, UartSource

@cocotb.test()
async def test_uart_handler_echo(dut):
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

    dut._log.info("Test UART handler echo")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)
    uart_sink = UartSink(dut.uart_tx, baud=115200, bits=8)

    # Unrecognized command bytes will be echoed back
    for x in range(0x10, 0x20):
        await uart_source.write(bytes([x]))
        await uart_source.wait()

        data = await uart_sink.read()
        assert data == bytes([x]), f"Expected {x:#02x}, got {data[0]:#02x}"

@cocotb.test()
async def test_uart_set_delay(dut):
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

    dut._log.info("Test UART handler set delay")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'\x00\x12\x34') # Set delay command (0x00), high byte of delay (0x12), low byte of delay (0x34)
    await uart_source.wait()
    assert dut.pulse_delay.value == 0x1234, f"Expected pulse_delay to be 0x1234, got {dut.pulse_delay.value}"

    await uart_source.write(b'\x00\x00\x00') # Set delay command (0x00), high byte of delay (0x00), low byte of delay (0x00)
    await uart_source.wait()
    assert dut.pulse_delay.value == 0x0000, f"Expected pulse_delay to be 0x0000, got {dut.pulse_delay.value}"

    await uart_source.write(b'\x00\xff\xff') # Set delay command (0x00), high byte of delay (0xff), low byte of delay (0xff)
    await uart_source.wait()
    assert dut.pulse_delay.value == 0xffff, f"Expected pulse_delay to be 0xffff, got {dut.pulse_delay.value}"

@cocotb.test()
async def test_uart_set_width(dut):
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

    dut._log.info("Test UART handler set width")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'\x01\x12') # Set width command (0x01), width (0x12)
    await uart_source.wait()
    assert dut.pulse_width.value == 0x12, f"Expected pulse_width to be 0x12, got {dut.pulse_width.value}"

    await uart_source.write(b'\x01\x00') # Set width command (0x01), width (0x00)
    await uart_source.wait()
    assert dut.pulse_width.value == 0x00, f"Expected pulse_width to be 0x00, got {dut.pulse_width.value}"

    await uart_source.write(b'\x01\xff') # Set width command (0x01), width (0xff)
    await uart_source.wait()
    assert dut.pulse_width.value == 0xff, f"Expected pulse_width to be 0xff, got {dut.pulse_width.value}"

@cocotb.test()
async def test_uart_set_num_pulses(dut):
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

    dut._log.info("Test UART handler set num pulses")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'\x02\x12') # Set num pulses command (0x02), num pulses (0x12)
    await uart_source.wait()
    assert dut.num_pulses.value == 0x12, f"Expected num_pulses to be 0x12, got {dut.num_pulses.value}"

    await uart_source.write(b'\x02\x00') # Set num pulses command (0x02), num pulses (0x00)
    await uart_source.wait()
    assert dut.num_pulses.value == 0x00, f"Expected num_pulses to be 0x00, got {dut.num_pulses.value}"

    await uart_source.write(b'\x02\xff') # Set num pulses command (0x02), num pulses (0xff)
    await uart_source.wait()
    assert dut.num_pulses.value == 0xff, f"Expected num_pulses to be 0xff, got {dut.num_pulses.value}"

@cocotb.test()
async def test_uart_set_pulse_spacing(dut):
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

    dut._log.info("Test UART handler set pulse spacing")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)

    await uart_source.write(b'\x03\x12\x34') # Set pulse spacing command (0x03), pulse spacing (0x1234)
    await uart_source.wait()
    assert dut.pulse_spacing.value == 0x1234, f"Expected pulse spacing to be 0x1234, got {dut.pulse_spacing.value}"

    await uart_source.write(b'\x03\x00\x00') # Set pulse spacing command (0x03), pulse spacing (0x0000)
    await uart_source.wait()
    assert dut.pulse_spacing.value == 0x0000, f"Expected pulse spacing to be 0x0000, got {dut.pulse_spacing.value}"

    await uart_source.write(b'\x03\xff\xff') # Set pulse spacing command (0x03), pulse spacing (0xffff)
    await uart_source.wait()
    assert dut.pulse_spacing.value == 0xffff, f"Expected pulse spacing to be 0xffff, got {dut.pulse_spacing.value}"