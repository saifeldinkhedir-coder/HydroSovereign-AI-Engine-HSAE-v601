"""
HSAE v6.0.14 - Observed Data Mode Panel
==============================================
Provenance-bound computation from REAL observed discharge.

Unlike the interactive Scenario Mode (heuristic parameter sliders), this
panel lets a user enter documented, observation-grade discharge values
with their source, and computes HIFD from the clean engine
(core/indices.py). When required observations are absent it reports
INSUFFICIENT_DATA rather than a fabricated number.

This realises the open-data design in QGIS: anyone holding real, sourced
records can contribute them and get a provenance-carrying result.

Pure Qt (no WebEngine) - works in all QGIS versions.

Author: Seifeldin M.G. Alkhedir - ORCID: 0000-0003-0821-2991
"""
from __future__ import annotations

from hsae_qgis.core.provenance import DataPoint, DataQuality
from hsae_qgis.core.ingestion import DataRegistry, RejectedContribution
from hsae_qgis.core.indices import hifd_for_basin


try:
    from qgis.PyQt.QtWidgets import (
        QDockWidget, QWidget, QVBoxLayout, QFormLayout,
        QLabel, QPushButton, QLineEdit, QComboBox,
        QGroupBox, QTextEdit)
    HAS_QT = True
except ImportError:
    HAS_QT = False


class HSAEObservedDataPanel(QDockWidget if HAS_QT else object):
    """Dock panel: enter observation-grade discharge, compute HIFD."""

    def __init__(self, iface):
        if not HAS_QT:
            return
        super().__init__("HSAE - Observed Data Mode", iface.mainWindow())
        self.iface = iface
        self._registry = DataRegistry()
        self.setMinimumWidth(440)
        self.setFloating(True)

        root = QWidget()
        self.setWidget(root)
        layout = QVBoxLayout(root)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel(
            "<b style='font-size:13px;color:#0E6B6A'>"
            "Provenance-Bound Computation</b>")
        layout.addWidget(title)

        note = QLabel(
            "Enter <b>documented, observed</b> discharge with its source. "
            "Results are computed from the clean engine and carry full "
            "provenance. Without independent observed Q_nat and Q_obs the "
            "result is <b>INSUFFICIENT_DATA</b> - never a fabricated number.")
        note.setWordWrap(True)
        note.setStyleSheet("color:#444;font-size:11px;")
        layout.addWidget(note)

        layout.addWidget(self._build_entry_form())

        compute_btn = QPushButton("Compute HIFD from observed data")
        compute_btn.clicked.connect(self._on_compute)
        layout.addWidget(compute_btn)

        self._result = QTextEdit()
        self._result.setReadOnly(True)
        self._result.setMinimumHeight(160)
        self._result.setStyleSheet("font-family:monospace;font-size:11px;")
        layout.addWidget(self._result)

        layout.addStretch(1)

    def _build_entry_form(self) -> "QGroupBox":
        box = QGroupBox("Observed discharge entry")
        form = QFormLayout(box)

        self._basin = QLineEdit("GERD")
        form.addRow("Basin ID:", self._basin)

        self._variable = QComboBox()
        self._variable.addItems(["Q_obs", "Q_nat"])
        form.addRow("Variable:", self._variable)

        self._value = QLineEdit()
        self._value.setPlaceholderText("e.g. 1248.0")
        form.addRow("Value (m3/s):", self._value)

        self._source = QLineEdit()
        self._source.setPlaceholderText("e.g. GRDC station 1577100")
        form.addRow("Source:", self._source)

        self._ref = QLineEdit()
        self._ref.setPlaceholderText("e.g. https://grdc.bafg.de/")
        form.addRow("Source ref (URL/DOI):", self._ref)

        self._d0 = QLineEdit()
        self._d0.setPlaceholderText("YYYY-MM-DD")
        form.addRow("Date start:", self._d0)

        self._d1 = QLineEdit()
        self._d1.setPlaceholderText("YYYY-MM-DD")
        form.addRow("Date end:", self._d1)

        self._contributor = QLineEdit()
        self._contributor.setPlaceholderText("name / ORCID")
        form.addRow("Contributor:", self._contributor)

        submit = QPushButton("Submit observation to registry")
        submit.clicked.connect(self._on_submit)
        form.addRow(submit)

        return box

    def _on_submit(self):
        try:
            value = float(self._value.text().strip())
        except ValueError:
            self._result.setText("ERROR: value must be a number.")
            return
        try:
            dp = DataPoint(
                value=value,
                variable=self._variable.currentText(),
                unit="m3/s",
                source=self._source.text().strip(),
                source_ref=self._ref.text().strip(),
                date_start=self._d0.text().strip(),
                date_end=self._d1.text().strip(),
                quality=DataQuality.OBSERVED,
            )
            rec = self._registry.submit(
                self._basin.text().strip(), dp,
                self._contributor.text().strip())
        except RejectedContribution as exc:
            self._result.setText("REJECTED: " + str(exc))
            return
        msg = "Accepted record " + rec.record_id + "\n" + dp.citation()
        self._result.setText(msg)

    def _on_compute(self):
        basin = self._basin.text().strip()
        result = hifd_for_basin(self._registry, basin)
        if result.ok:
            lines = [
                "HIFD = " + str(result.value) + "%   [OK]",
                "method: " + result.method,
                "",
                "Provenance:",
            ]
            lines.extend("  - " + c for c in result.provenance())
            self._result.setText("\n".join(lines))
        else:
            hint = ("\n\nSubmit independent observation-grade Q_nat "
                    "and Q_obs for this basin first.")
            self._result.setText(result.status + "\n" + result.detail + hint)
