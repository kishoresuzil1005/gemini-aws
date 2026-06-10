class ExecutiveSummary:

    @staticmethod
    def generate(data):

        return (
            f"Cloud environment contains "
            f"{len(data['recommendations'])} "
            f"optimization opportunities "
            f"with potential annual savings of "
            f"${data['savings']['annual_savings']}."
        )
