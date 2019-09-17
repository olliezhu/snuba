import pytest
import pytz

from datetime import datetime
from typing import Any, Mapping, Optional, Tuple
from uuid import uuid1

from base import FakeKafkaProducer, message as build_msg
from snuba.consumers.snapshot_worker import SnapshotAwareWorker
from snuba.datasets.factory import get_dataset
from snuba.processor import MessageProcessor
from snuba.stateful_consumer.control_protocol import TransactionData


INSERT_MSG = (
    '{"event":"change","xid": %(xid)s,"kind":"insert","schema":"public",'
    '"table":"sentry_groupedmessage","columnnames":["id","logger","level","message",'
    '"view","status","times_seen","last_seen","first_seen","data","score","project_id",'
    '"time_spent_total","time_spent_count","resolved_at","active_at","is_public","platform",'
    '"num_comments","first_release_id","short_id"],"columntypes":["bigint","character varying(64)",'
    '"integer","text","character varying(200)","integer","integer","timestamp with time zone",'
    '"timestamp with time zone","text","integer","bigint","integer","integer",'
    '"timestamp with time zone","timestamp with time zone","boolean","character varying(64)","integer",'
    '"bigint","bigint"],"columnvalues":[74,"",40,'
    '"<module> ZeroDivisionError integer division or modulo by zero client3.py __main__ in <module>",'
    '"__main__ in <module>",0,2,"2019-06-19 06:46:28+00","2019-06-19 06:45:32+00",'
    '"eJyT7tuwzAM3PkV2pzJiO34VRSdmvxAgA5dCtViDAGyJEi0AffrSxrZOlSTjrzj3Z1MrOBekCWHBcQaPj4xhXe72WyDv6YU0ouynnDGpMxzrEJSSzCrC+p7Vz8sgNhAvhdOZ/pKOKHd0PC5C9yqtjuPddcPQ9n0w8hPiLRHsWvZGsWD/91xI'
    'ya2IFxz7vJWfTUlHHnwSCEBUkbTZrxCCcOf2baY/XTU1VJm9cjHL4JriHPYvOnliyP0Jt2q4SpLkz7v6owW9E9rEOvl0PawczxcvkLIWppxg==",'
    '1560926969,2,0,0,null,"2019-06-19 06:45:32+00",false,"python",0,null,20]'
    '}'
)

PROCESSED = {
    'offset': 1,
<<<<<<< HEAD
=======
    'project_id': 2,
>>>>>>> master
    'id': 74,
    'record_deleted': 0,
    'status': 0,
    'last_seen': datetime(2019, 6, 19, 6, 46, 28, tzinfo=pytz.UTC),
    'first_seen': datetime(2019, 6, 19, 6, 45, 32, tzinfo=pytz.UTC),
    'active_at': datetime(2019, 6, 19, 6, 45, 32, tzinfo=pytz.UTC),
    'first_release_id': None,
}


class TestSnapshotWorker:

    test_data = [
        (
            INSERT_MSG % {"xid": 90},
            None,
        ),
        (
            INSERT_MSG % {"xid": 100},
            None,
        ),
        (
            INSERT_MSG % {"xid": 110},
            None,
        ),
        (
            INSERT_MSG % {"xid": 120},
            (
                MessageProcessor.INSERT,
                PROCESSED,
            )
        ),
        (
            INSERT_MSG % {"xid": 210},
            (
                MessageProcessor.INSERT,
                PROCESSED,
            )
        )
    ]

    @pytest.mark.parametrize("message, expected", test_data)
    def test_send_message(
        self,
        message: bytes,
        expected: Optional[Tuple[int, Mapping[str, Any]]],
    ) -> None:
        dataset = get_dataset("groupedmessage")
        snapshot_id = uuid1()
        transact_data = TransactionData(
            xmin=100,
            xmax=200,
            xip_list=[120, 130]
        )

        worker = SnapshotAwareWorker(
            dataset=dataset,
            producer=FakeKafkaProducer(),
            snapshot_id=str(snapshot_id),
            transaction_data=transact_data,
            replacements_topic=None,
            metrics=None
        )

        ret = worker.process_message(
            build_msg(1, 0, message)
        )
        assert ret == expected
