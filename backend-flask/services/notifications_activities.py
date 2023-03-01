from datetime import datetime, timedelta, timezone
from aws_xray_sdk.core import xray_recorder

# Start a segment
segment = xray_recorder.begin_segment('user_activities')
dict = {
    "customer_category" : 124,
    "zip_code" : 98101,
    "country" : "United States",
    "internal" : False
  }
# Add metadata or annotation here if necessary
segment.put_metadata('people', dict, 'namespace')
# Close the segment
xray_recorder.end_segment()

# Start a segment
subsegment = xray_recorder.begin_subsegment('annotations')
subsegment.put_annotation('id', 12345)
# Close the subsegment
xray_recorder.end_subsegment()

class NotificationsActivities:
  def run():
    now = datetime.now(timezone.utc).astimezone()
    results = [{
      'uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',
      'handle':  'Uzumaki Naruto',
      'message': 'Yondaime no Hokage c-est arrrive!',
      'created_at': (now - timedelta(days=2)).isoformat(),
      'expires_at': (now + timedelta(days=5)).isoformat(),
      'likes_count': 5,
      'replies_count': 1,
      'reposts_count': 0,
      'replies': [{
        'uuid': '26e12864-1c26-5c3a-9658-97a10f8fea67',
        'reply_to_activity_uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',
        'handle':  'Worf',
        'message': 'This post has no honor!',
        'likes_count': 0,
        'replies_count': 0,
        'reposts_count': 0,
        'created_at': (now - timedelta(days=2)).isoformat()
      }],
    }
    ]
    return results
