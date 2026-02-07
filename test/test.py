import os
from pathlib import Path

from cocotb_tools.runner import get_runner

PDK_ROOT = Path(os.getenv("PDK_ROOT"))

def test_project_runner():
    sim = os.getenv("SIM", "icarus")
    waves = os.getenv("WAVES", 1)
    gl_test = os.getenv("GATES", False)

    test_dir = Path(__file__).resolve().parent
    src_dir = test_dir.parent / "src"

    sources = []
    if gl_test == "yes" or gl_test == "1" or gl_test == "true":
        sources += [test_dir / "gate_level_netlist.v"]
        sources += [PDK_ROOT / "ihp-sg13g2/libs.ref/sg13g2_io/verilog/sg13g2_io.v"]
        sources += [PDK_ROOT / "ihp-sg13g2/libs.ref/sg13g2_stdcell/verilog/sg13g2_stdcell.v"]

    else:
        sources += list(src_dir.glob("*.v"))

    sources += [test_dir / "tb_tt.v"]

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="tb_tt",
        always=True
    )

    runner.test(hdl_toplevel="tb_tt", test_module="test_tt", waves=waves)

def test_pulser_runner():
    sim = os.getenv("SIM", "icarus")
    waves = os.getenv("WAVES", 1)

    test_dir = Path(__file__).resolve().parent
    src_dir = test_dir.parent / "src"

    sources = [
        src_dir / "pulser.v",
        test_dir / "tb_pulser.v"
    ]

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="tb_pulser",
        always=True
    )

    runner.test(hdl_toplevel="tb_pulser", test_module="test_pulser", waves=waves)

def test_uart_runner():
    sim = os.getenv("SIM", "icarus")
    waves = os.getenv("WAVES", 1)

    test_dir = Path(__file__).resolve().parent
    src_dir = test_dir.parent / "src"

    sources = [
        src_dir / "uart_rx.v",
        src_dir / "uart_tx.v",
        test_dir / "tb_uart.v"
    ]

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="tb_uart",
        always=True
    )

    runner.test(hdl_toplevel="tb_uart", test_module="test_uart", waves=waves)


if __name__ == "__main__":
    test_project_runner()
    test_pulser_runner()
    test_uart_runner()