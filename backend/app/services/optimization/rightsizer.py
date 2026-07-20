class Rightsizer:

    @staticmethod
    def recommend(
        instance_type,
        avg_cpu
    ):

        # Only recommend downscaling if we start from a larger size
        if "large" in instance_type.lower():
            if avg_cpu < 10:
                return "t3.small"
            if avg_cpu < 25:
                return "t3.medium"

        if "medium" in instance_type.lower():
            if avg_cpu < 8:
                return "t3.small"

        return None