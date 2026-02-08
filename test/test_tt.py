# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

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

    for x in range(0, 0x10):
        await uart_source.write(bytes([x]))
        await uart_source.wait()

        data = await uart_sink.read()
        assert data == bytes([x]), f"Expected {x:#02x}, got {data[0]:#02x}"
