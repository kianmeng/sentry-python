import pytest
import gc

from sentry_sdk import start_span, start_transaction
from sentry_sdk.tracing import Transaction


# def test_span_trimming(sentry_init, capture_events):
#     sentry_init(traces_sample_rate=1.0, _experiments={"max_spans": 3})
#     events = capture_events()

#     with start_transaction(name="hi"):
#         for i in range(10):
#             with start_span(op="foo{}".format(i)):
#                 pass

#     (event,) = events

#     # the transaction is its own first span (which counts for max_spans) but it
#     # doesn't show up in the span list in the event, so this is 1 less than our
#     # max_spans value
#     assert len(event["spans"]) == 2

#     span1, span2 = event["spans"]
#     assert span1["op"] == "foo0"
#     assert span2["op"] == "foo1"


# def test_transaction_method_signature(sentry_init, capture_events):
#     sentry_init(traces_sample_rate=1.0)
#     events = capture_events()

#     with pytest.raises(TypeError):
#         start_span(name="foo")
#     assert len(events) == 0

#     with start_transaction() as transaction:
#         pass
#     assert transaction.name == "<unlabeled transaction>"
#     assert len(events) == 1

#     with start_transaction() as transaction:
#         transaction.name = "name-known-after-transaction-started"
#     assert len(events) == 2

#     with start_transaction(name="a"):
#         pass
#     assert len(events) == 3

#     with start_transaction(Transaction(name="c")):
#         pass
#     assert len(events) == 4


def test_circular_references(sentry_init, request):

    print("initial gc.garbage:", gc.garbage)

    print("\n(top of function) collecting...")
    num_collected = gc.collect()
    print("number of items collected:", num_collected)
    if num_collected > 0:
        print("gc.garbage after collection:", gc.garbage)

    gc.set_debug(gc.DEBUG_LEAK)
    gc.disable()
    request.addfinalizer(gc.enable)

    sentry_init(traces_sample_rate=1.0)

    dogpark_transaction = start_transaction(name="dogpark")

    sniffing_span = dogpark_transaction.start_child(op="sniffing")

    wagging_span = dogpark_transaction.start_child(op="wagging")

    sniffing_span.finish()

    print("\n(about to finish transaction) collecting...")
    num_collected = gc.collect()
    print("number of items collected:", num_collected)
    if num_collected > 0:
        print("gc.garbage after collection:", gc.garbage)

    dogpark_transaction.finish()

    print("\n(just finished transaction, about to delete transaction) collecting...")
    num_collected = gc.collect()
    print("number of items collected:", num_collected)
    if num_collected > 0:
        print("gc.garbage after collection:", gc.garbage)

    del dogpark_transaction

    print("\n(just deleted transaction) collecting...")
    num_collected = gc.collect()
    print("number of items collected:", num_collected)
    if num_collected > 0:
        print("gc.garbage after collection:", gc.garbage)

    wagging_span.finish()

    print("\n(finished dangling span) collecting...")
    num_collected = gc.collect()
    print("number of items collected:", num_collected)
    if num_collected > 0:
        print("gc.garbage after collection:", gc.garbage)
