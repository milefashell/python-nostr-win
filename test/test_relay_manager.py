import pytest
from nostr.event import Event
from nostr.key import PrivateKey
from nostr.subscription import Subscription, Filters
from nostr.relay_manager import RelayManager, RelayException


def test_only_relay_valid_events():
    """ publish_event raise a RelayException if an Event fails verification """
    pk = PrivateKey()
    event = Event(
        public_key=pk.public_key.hex(),
        content="Hello, world!",
    )
    
    relay_manager = RelayManager()

    # Deliberately forget to sign the Event
    with pytest.raises(RelayException) as e:
        relay_manager.publish_event(event)
    assert "must be signed" in str(e)

    # Attempt to relay with a nonsense signature
    event.signature = '0' * 32
    with pytest.raises(RelayException) as e:
        relay_manager.publish_event(event)
    assert "failed to verify" in str(e)

    # Properly signed Event can be relayed
    pk.sign_event(event)
    relay_manager.publish_event(event)


def test_add_multiple_relays_add_subscription_to_one_relay():
    relay_manager = RelayManager()

    relay1 = "wss://dummmy1.dummmy"
    relay2 = "wss://dummmy2.dummmy"

    relay_manager.add_relay(relay1)
    relay_manager.add_relay(relay2)

    subscription_id = "qwertyytrewq"
    filters = Filters()

    relay_manager.relays[relay1].add_subscription(subscription_id, filters)
    assert relay_manager.relays[relay1].subscriptions[subscription_id].id == subscription_id
    assert len(relay_manager.relays[relay1].subscriptions) == 1
    assert len(relay_manager.relays[relay2].subscriptions) == 0
