import json
import sys
from datetime import datetime

from loguru import logger


class CloudRunHandler:

    def write(self, message):
        # Build structured log messages as an object.
        # global_log_fields = {}

        # Add log correlation to nest all log messages.
        # trace_header = request.headers.get("X-Cloud-Trace-Context")

        # if trace_header and PROJECT:
        #     trace = trace_header.split("/")
        #     global_log_fields[
        #         "logging.googleapis.com/trace"
        #     ] = f"projects/{PROJECT}/traces/{trace[0]}"

        record = message.record
        entry = dict(
            severity=record["level"].name,
            message=record["message"],
            timestamp=datetime.utcnow().isoformat("T") + "Z"
            # Log viewer accesses 'component' as jsonPayload.component'.
            # component="arbitrary-property",
            # **global_log_fields,
        )
        print(json.dumps(entry), file=sys.stderr)


logger.configure(handlers=[{"sink": CloudRunHandler()}])

# Exposing the configured logger outside.
log = logger
