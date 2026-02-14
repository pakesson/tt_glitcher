# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

from cocotbext.uart import UartSink, UartSource

@cocotb.test()
async def test_project_echo(dut):
    dut._log.info("Start")

    # Set the clock period to 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 1
    dut.uio_in.value = 0

    # Reset
    dut._log.info("Reset")
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    dut._log.info("Test project echo")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8)
    uart_sink = UartSink(dut.uart_tx, baud=115200, bits=8)

    # Unrecognized command bytes will be echoed back
    for x in range(0x10, 0x20):
        await uart_source.write(bytes([x]))
        await uart_source.wait()

        data = await uart_sink.read()
        assert data == bytes([x]), f"Expected {x:#02x}, got {data[0]:#02x}"

@cocotb.test()
async def test_project_full_glitch_sequence(dut):
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

    dut._log.info("Test project full glitch sequence")

    uart_source = UartSource(dut.uart_rx, baud=115200, bits=8, stop_bits=1)

    await uart_source.write(b'\x00\x00\x12') # Set delay
    await uart_source.write(b'\x01\x01')     # Set width
    await uart_source.write(b'\x02\x02')     # Set num pulses
    await uart_source.write(b'\x03\x00\x03') # Set pulse spacing
    await uart_source.write(b'\x04')         # Trigger pulse

    await RisingEdge(dut.pulse_en)
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