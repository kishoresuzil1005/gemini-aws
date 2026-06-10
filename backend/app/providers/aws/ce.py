from .auth import get_aws_client
import datetime

class CEAdapter:
    def __init__(self, cloud_account_id):
        self.client = get_aws_client("ce", cloud_account_id)

    def get_cost_and_usage(self):
        now = datetime.datetime.utcnow()
        start = now.replace(day=1).strftime('%Y-%m-%d')
        end = now.strftime('%Y-%m-%d')
        
        # If today is the 1st day of the month, or we want a robust period
        if start == end:
            prev_month = now.replace(day=1) - datetime.timedelta(days=1)
            start = prev_month.replace(day=1).strftime('%Y-%m-%d')
            end = now.replace(day=1).strftime('%Y-%m-%d')
            
        try:
            # First attempt: Current month aggregated by Service
            response = self.client.get_cost_and_usage(
                TimePeriod={'Start': start, 'End': end},
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
            )
            # If we received groups, return this response
            if response.get("ResultsByTime") and len(response["ResultsByTime"]) > 0:
                groups = response["ResultsByTime"][0].get("Groups", [])
                if groups:
                    print("Successfully fetched current month cost data.")
                    return response
        except Exception as e:
            print(f"Current month Cost Explorer API fetch skipped or failed: {e}")

        # Second attempt (Fallback): Sliding last 30 days window aggregated by Service
        try:
            end_date = datetime.datetime.utcnow().date()
            start_date = end_date - datetime.timedelta(days=30)
            
            # If sliding window start is somehow equal to end
            if start_date == end_date:
                start_date = end_date - datetime.timedelta(days=1)
                
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
            )
            return response
        except Exception as e:
            print(f"Fallback 30-day sliding window Cost Explorer API fetch skipped or failed: {e}")
            return {"ResultsByTime": []}

