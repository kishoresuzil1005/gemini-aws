import boto3
import logging
logger = logging.getLogger(__name__)

class SNSDiscovery:

    @staticmethod
    def discover(region: str) -> list[dict]:
        resources = []
        try:
            client = boto3.client('sns', region_name=region)
            paginator = client.get_paginator('list_topics')
            for page in paginator.paginate():
                for topic in page.get('Topics', []):
                    topic_arn = topic['TopicArn']
                    topic_name = topic_arn.split(':')[-1]
                    attrs = {}
                    try:
                        attrs_resp = client.get_topic_attributes(TopicArn=topic_arn)
                        attrs = attrs_resp.get('Attributes', {})
                    except Exception:
                        pass
                    resources.append({'resource_id': topic_arn, 'resource_type': 'SNSTopic', 'region': region, 'name': topic_name, 'provider': 'AWS', 'metadata': {'arn': topic_arn, 'display_name': attrs.get('DisplayName', ''), 'subscription_count': int(attrs.get('SubscriptionsConfirmed', 0)), 'pending_subscription_count': int(attrs.get('SubscriptionsPending', 0)), 'kms_key_id': attrs.get('KmsMasterKeyId', ''), 'fifo': topic_name.endswith('.fifo'), 'content_deduplication': attrs.get('ContentBasedDeduplication', 'false') == 'true'}, 'dependencies': []})
                    try:
                        sub_paginator = client.get_paginator('list_subscriptions_by_topic')
                        for sub_page in sub_paginator.paginate(TopicArn=topic_arn):
                            for sub in sub_page.get('Subscriptions', []):
                                if sub.get('SubscriptionArn') in ('PendingConfirmation', 'Deleted'):
                                    continue
                                resources.append({'resource_id': sub['SubscriptionArn'], 'resource_type': 'SNSSubscription', 'region': region, 'name': f"{topic_name}-{sub.get('Protocol')}", 'provider': 'AWS', 'metadata': {'arn': sub['SubscriptionArn'], 'topic_arn': topic_arn, 'protocol': sub.get('Protocol'), 'endpoint': sub.get('Endpoint', '')}, 'dependencies': []})
                    except Exception:
                        pass
        except Exception:
            logger.exception('SNS discovery failed for region %s', region)
        return resources