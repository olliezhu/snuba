from snuba.stateful_consumer import StateOutput
from snuba.stateful_consumer.state_context import State

from typing import Any, Tuple


class CatchingUpState(State[StateOutput]):
    """
    In this state the consumer consumes the main topic but
    it discards the transacitons that were present in the
    snapshot (xid < xmax and not in xip_list).
    Once this phase is done the consumer goes back to normal
    consumption.
    """

    def handle(self, input: Any) -> Tuple[StateOutput, Any]:
        # TODO: Actually consume cdc topic while discarding xids that were
        # already in the dump
        return (StateOutput.SNAPSHOT_CATCHUP_COMPLETED, None)