import os
from pathlib import Path

from cocotb_tools.runner import get_runner
import pytest

PDK_ROOT = Path(os.getenv("PDK_ROOT"))

SIM = os.getenv("SIM", "icarus")
WAVES = os.getenv("WAVES", 1)
GL_TEST = os.getenv("GATES", False) in ["yes", "1", "true", True]

def test_project_runner():
    test_dir = Path(__file__).resolve().parent
    src_dir = test_dir.parent / "src"

    sources = []
    if GL_TEST:
        sources += [test_dir / "gate_level_netlist.v"]
        sources += [PDK_ROOT / "ihp-sg13g2/libs.ref/sg13g2_io/verilog/sg13g2_io.v"]
        sources += [PDK_ROOT / "ihp-sg13g2/libs.ref/sg13g2_stdcell/verilog/sg13g2_stdcell.v"]

    else:
        sources += [
            src_dir / "tt_um_pakesson_glitcher.v",
            src_dir / "glitch_control.v",
            src_dir / "uart_handler.v",
            src_dir / "uart_rx.v",
            src_dir / "uart_tx.v"
        ]

    sources += [test_dir / "tb_tt.v"]

    runner = get_runner(SIM)
    runner.build(
        sources=sources,
        hdl_toplevel="tb_tt",
        always=True
    )

    runner.test(hdl_toplevel="tb_tt", test_module="test_tt", waves=WAVES)

@pytest.mark.skipif(GL_TEST, reason="Gate-level test not supported")
def test_uart_runner():
    test_dir = Path(__file__).resolve().parent
    src_dir = test_dir.parent / "src"

    sources = [
        src_dir / "uart_rx.v",
        src_dir / "uart_tx.v",
        test_dir / "tb_uart.v"
    ]

    runner = get_runner(SIM)
    runner.build(
        sources=sources,
        hdl_toplevel="tb_uart",
        always=True
    )

    runner.test(hdl_toplevel="tb_uart", test_module="test_uart", waves=WAVES)

@pytest.mark.skipif(GL_TEST, reason="Gate-level test not supported")
def test_uart_handler_runner():
    test_dir = Path(__file__).resolve().parent
    src_dir = test_dir.parent / "src"

    sources = [
        src_dir / "uart_handler.v",
        src_dir / "uart_rx.v",
        src_dir / "uart_tx.v",
        test_dir / "tb_uart_handler.v"
    ]

    runner = get_runner(SIM)
    runner.build(
        sources=sources,
        hdl_toplevel="tb_uart_handler",
        always=True
    )

    runner.test(hdl_toplevel="tb_uart_handler", test_module="test_uart_handler", waves=WAVES)

@pytest.mark.skipif(GL_TEST, reason="Gate-level test not supported")
def test_glitch_control_runner():
    test_dir = Path(__file__).resolve().parent
    src_dir = test_dir.parent / "src"

    sources = [
        src_dir / "glitch_control.v",
        src_dir / "uart_handler.v",
        src_dir / "uart_rx.v",
        src_dir / "uart_tx.v",
        test_dir / "tb_glitch_control.v"
    ]

    runner = get_runner(SIM)
    runner.build(
        sources=sources,
        hdl_toplevel="tb_glitch_control",
        always=True
    )

    runner.test(hdl_toplevel="tb_glitch_control", test_module="test_glitch_control", waves=WAVES)

if __name__ == "__main__":
    test_project_runner()
    test_uart_runner()
    test_uart_handler_runner()
    test_glitch_control_runner()