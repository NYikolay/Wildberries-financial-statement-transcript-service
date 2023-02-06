from datetime import datetime

from pythonjsonlogger.jsonlogger import JsonFormatter


class CustomJsonFormatter(JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('asctime'):
            log_record['timestamp'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
