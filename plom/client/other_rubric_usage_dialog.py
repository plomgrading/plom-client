from PyQt6.QtWidgets import (
    QDialog,
    QListWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QMessageBox,
)


class RubricUsageDialog(QDialog):
    def __init__(self, parent, paper_numbers):
        super().__init__()
        self._parent = parent

        self.setWindowTitle("Other rubric usages")

        # Create a label for the list
        self.label = QLabel("Paper Numbers:")

        # Create the list widget
        self.list_widget = QListWidget()
        for number in paper_numbers:
            self.list_widget.addItem(str(number))

        # Create the view button
        self.view_button = QPushButton("View")
        self.view_button.clicked.connect(self.view_paper)

        # Layouts
        v_layout = QVBoxLayout()
        v_layout.addWidget(self.label)
        v_layout.addWidget(self.list_widget)

        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(self.view_button)

        v_layout.addLayout(h_layout)

        self.setLayout(v_layout)

    def view_paper(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "No Selection", "Please select a paper number to view."
            )
            return
        paper_number = selected_items[0].text()
        self._parent.view_other_paper(paper_number)
