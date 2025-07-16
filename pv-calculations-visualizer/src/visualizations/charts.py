from matplotlib import pyplot as plt
import numpy as np

class PVCalculationsVisualizer:
    def __init__(self, calculations_data):
        self.calculations_data = calculations_data

    def plot_extended_calculations(self):
        labels = list(self.calculations_data['extended'].keys())
        values = list(self.calculations_data['extended'].values())

        plt.figure(figsize=(10, 6))
        plt.bar(labels, values, color='skyblue')
        plt.title('Extended Calculations Results')
        plt.xlabel('Metrics')
        plt.ylabel('Values')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_advanced_calculations(self):
        labels = list(self.calculations_data['advanced'].keys())
        values = list(self.calculations_data['advanced'].values())

        x = np.arange(len(labels))
        width = 0.35

        fig, ax = plt.subplots()
        bars1 = ax.bar(x - width/2, values, width, label='Advanced Calculations', color='lightgreen')

        ax.set_ylabel('Values')
        ax.set_title('Advanced Calculations Results')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        plt.tight_layout()
        plt.show()

    def save_plot_to_pdf(self, filename):
        from matplotlib.backends.backend_pdf import PdfPages

        with PdfPages(filename) as pdf:
            self.plot_extended_calculations()
            pdf.savefig()
            plt.close()
            self.plot_advanced_calculations()
            pdf.savefig()
            plt.close()